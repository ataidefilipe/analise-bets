"""
tests/test_api.py
-----------------
Testes do backend da POC contra um banco sintético em arquivo temporário.

O que estes testes guardam é o modelo de autorização (documento 01): identidade vinda do
token, perfil que não enxerga o que não deve, nome que não vaza para a camada aberta e
consulta a atleta que sempre deixa rastro.
"""

import os

os.environ.setdefault("ANALISE_BETS_AMBIENTE", "dev")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from src.api import db
from src.api.clientes import criar_cliente
from src.api.main import app
from src.api.modelo import (
    atletas, cartoes, consultas_atleta, metadata, minutos_em_campo, nominaveis, partidas,
    risco_pre_jogo,
)


@pytest.fixture
def api(tmp_path):
    eng = db.criar_engine(f"sqlite:///{(tmp_path / 'api.db').as_posix()}")
    metadata.create_all(eng)
    with eng.begin() as conn:
        conn.execute(partidas.insert(), [
            {"serie": "A", "temporada": 2026, "partida_id": 1, "rodada": 7, "data": "2026-05-01",
             "clube_mandante": "Alfa", "clube_mandante_slug": "alfa",
             "clube_visitante": "Beta", "clube_visitante_slug": "beta",
             "gols_mandante": 2, "gols_visitante": 1,
             "sumula_url": "https://conteudo.cbf.com.br/sumulas/2026/1421se.pdf",
             "sumula_sha256": "ab" * 32, "baixado_em": "2026-05-02T05:00:00-03:00"},
        ])
        conn.execute(atletas.insert(), [
            {"registro_cbf": "111", "nome_completo": "João da Silva", "apelido": "Joãozinho",
             "atleta_slug": "joao_da_silva", "apelido_slug": "joaozinho",
             "busca_texto": "joao da silva joaozinho", "clubes": "alfa", "clube_atual": "alfa",
             "ultima_temporada": 2026},
            {"registro_cbf": "222", "nome_completo": "Pedro Souza", "apelido": "Pedrão",
             "atleta_slug": "pedro_souza", "apelido_slug": "pedrao",
             "busca_texto": "pedro souza pedrao", "clubes": "beta", "clube_atual": "beta",
             "ultima_temporada": 2026},
        ])
        conn.execute(risco_pre_jogo.insert(), [
            {"serie": "A", "temporada": 2026, "rodada": 7, "partida_id": 1, "clube_slug": clube,
             "registro_cbf": reg, "num_camisa": camisa, "condicao": "Titular",
             "minutos_previos": 900.0, "cartoes_1t_previos": 3.0, "taxa_1t_ajustada": 0.002,
             "minutos_esperados": 82.0, "score_pre_jogo": score, "percentil": pct, "tier": "t"}
            for reg, clube, camisa, score, pct in (("111", "alfa", 5, 0.2, 99.0),
                                                   ("222", "beta", 8, 0.1, 80.0))
        ])
        conn.execute(cartoes.insert(), [
            {"serie": "A", "temporada": 2026, "partida_id": 1, "rodada": 7, "clube_slug": "beta",
             "num_camisa": 8, "registro_cbf": "222", "atleta": "Pedro Souza", "cartao": "Amarelo",
             "minuto_continuo": 20, "periodo": "1T", "motivo_completo": None},
        ])
        conn.execute(minutos_em_campo.insert(), [
            {"serie": "A", "temporada": 2026, "clube_slug": "beta", "registro_cbf": "222",
             "partidas_jogadas": 7, "minutos_em_campo": 600},
        ])
        conn.execute(nominaveis.insert(), [
            {"atleta_slug": "condenado", "registro_cbf": None, "atleta": "Condenado",
             "sancao": "Banido", "fonte": "STJD"},
        ])
    chaves = {
        perfil: criar_cliente(eng, perfil, perfil, "alfa" if perfil == "clube" else None)["api_key"]
        for perfil in ("federacao_stjd", "clube", "operadora_integrity", "imprensa_academia")
    }
    anterior = db._engine
    db.definir_engine(eng)
    with TestClient(app) as cliente:
        def get(url, perfil=None):
            cabecalho = {"Authorization": f"Bearer {chaves[perfil]}"} if perfil else {}
            return cliente.get(url, headers=cabecalho)
        get.engine = eng
        yield get
    db.definir_engine(anterior)


FILA = "/v1/rodadas/A/2026/7/fila"


def test_sem_chave_ou_chave_invalida_e_401(api):
    assert api("/v1/me").status_code == 401
    assert api("/v1/me").json() == {"erro": "nao_autenticado"}


def test_me_devolve_perfil_da_credencial(api):
    corpo = api("/v1/me", "clube").json()
    assert corpo["perfil"] == "clube" and corpo["clube_slug"] == "alfa"
    assert corpo["limiar_padrao"]["percentil"] == 90.0
    assert corpo["aviso_interpretativo"]


def test_perfil_ou_clube_na_query_e_400(api):
    r = api(FILA + "?clube=beta", "clube")
    assert r.status_code == 400 and r.json()["erro"] == "parametro_invalido"


def test_trading_nao_e_cadastravel(api):
    with pytest.raises(ValueError):
        criar_cliente(api.engine, "mesa", "operadora_trading")


def test_fila_da_federacao_aplica_corte_e_traz_componentes(api):
    corpo = api(FILA, "federacao_stjd").json()
    assert corpo["contexto"]["total_relacionados"] == 2
    assert [d["atleta_id"] for d in corpo["dados"]] == ["111", "222"]
    assert set(corpo["dados"][0]["componentes"]) == {
        "minutos_previos", "cartoes_1t_previos", "taxa_1t_ajustada", "minutos_esperados"}
    assert api(FILA + "?percentil=95", "federacao_stjd").json()["total"] == 1


def test_fila_do_clube_so_tem_o_proprio_elenco(api):
    corpo = api(FILA + "?percentil=0", "clube").json()
    assert {d["clube_slug"] for d in corpo["dados"]} == {"alfa"}
    assert corpo["contexto"]["total_relacionados"] == 1


def test_fila_negada_a_camada_aberta(api):
    assert api(FILA, "imprensa_academia").status_code == 403
    assert api(FILA, "operadora_integrity").status_code == 403


def test_rodada_sem_escalacao_e_422(api):
    r = api("/v1/rodadas/A/2026/30/fila", "federacao_stjd")
    assert r.status_code == 422 and r.json()["erro"] == "sem_escalacao"


def test_busca_exige_tres_caracteres_e_nao_traz_escore(api):
    assert api("/v1/atletas?busca=jo", "clube").status_code == 400
    corpo = api("/v1/atletas?busca=JOAO", "clube").json()
    assert corpo["total"] == 1 and corpo["dados"][0]["atleta_id"] == "111"
    assert not {"percentil", "tier", "score_pre_jogo"} & set(corpo["dados"][0])


def test_clube_consulta_atleta_de_terceiro_e_fica_registrado(api):
    r = api("/v1/atletas/222", "clube")
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["historico"][0]["cartoes_1t"] == 1
    assert corpo["cartoes"][0]["motivo_disponivel"] is False
    with api.engine.connect() as conn:
        log = conn.execute(select(consultas_atleta)).mappings().all()
    assert log[-1]["atleta_id"] == "222" and log[-1]["proprio_elenco"] is False


def test_busca_tambem_fica_registrada(api):
    api("/v1/atletas?busca=pedro", "federacao_stjd")
    with api.engine.connect() as conn:
        assert conn.execute(select(func.count()).select_from(consultas_atleta)
                            .where(consultas_atleta.c.termo_busca == "pedro")).scalar() == 1


def test_dossie_da_camada_aberta_nao_identifica_atleta(api):
    corpo = api("/v1/partidas/A/2026/1/dossie", "imprensa_academia").json()
    assert corpo["atletas_sinalizados"] is None
    assert all(c["atleta"] is None and c["atleta_id"] is None for c in corpo["cartoes"])
    assert corpo["procedencia"]["sha256"] == "ab" * 32


def test_dossie_identificado_traz_sinalizados(api):
    corpo = api("/v1/partidas/A/2026/1/dossie", "federacao_stjd").json()
    assert {s["atleta_id"] for s in corpo["atletas_sinalizados"]} == {"111", "222"}
    assert corpo["cartoes"][0]["atleta"] == "Pedro Souza"


def test_agregados_sem_atleta(api):
    corpo = api("/v1/agregados/A/2026", "imprensa_academia").json()
    assert {d["clube_slug"] for d in corpo["dados"]} == {"alfa", "beta"}
    assert not any("atleta" in k for d in corpo["dados"] for k in d)


def test_erro_de_validacao_segue_o_formato(api):
    r = api("/v1/agregados/C/2026", "imprensa_academia")
    assert r.status_code == 400 and r.json()["erro"] == "parametro_invalido"
    assert api("/v1/atletas/999", "federacao_stjd").json() == {"erro": "nao_encontrado"}
