"""
tests/test_perfis_de_acesso.py
------------------------------
Testes do controle técnico de granularidade por perfil de cliente (F4-03).

Uma cláusula contratual sem controle técnico não se sustenta. Estes testes são o controle:
falham se o segmento de trading voltar a ser atendido, se nome de atleta escapar para uma
camada aberta, ou se o feed servido por padrão deixar de ser o de menor exposição.
"""

import json
import os
import sqlite3

import pandas as pd
import pytest

from src.pipeline import perfis_de_acesso as pa

FEED_DIR = os.path.join("data", "processed", "product_feed")
PERFIL_TRADING = "operadora_trading"


@pytest.fixture
def amostra():
    return pd.DataFrame([
        {"serie": "B", "temporada": 2022, "rodada": 10, "partida_id": 1,
         "clube_slug": "juventude", "num_camisa": 10, "apelido": "Fulano",
         "atleta_slug": "fulano", "registro_cbf": "111111", "condicao": "Titular",
         "score_pre_jogo": 0.12, "minutos_previos": 450},
        {"serie": "B", "temporada": 2022, "rodada": 10, "partida_id": 1,
         "clube_slug": "juventude", "num_camisa": 7, "apelido": "Beltrano",
         "atleta_slug": "beltrano", "registro_cbf": "222222", "condicao": "Reserva",
         "score_pre_jogo": 0.03, "minutos_previos": 60},
        {"serie": "B", "temporada": 2022, "rodada": 10, "partida_id": 1,
         "clube_slug": "sport", "num_camisa": 4, "apelido": "Sicrano",
         "atleta_slug": "sicrano", "registro_cbf": "333333", "condicao": "Titular",
         "score_pre_jogo": 0.09, "minutos_previos": 300},
    ])


# ---------------------------------------------------------------------------
# 1. Segmento de trading
# ---------------------------------------------------------------------------

def test_mesa_de_trading_nao_e_atendida(amostra):
    """
    A recusa é decisão de posicionamento do projeto, e precisa falhar em tempo de execução —
    não depender de alguém lembrar da cláusula.
    """
    assert PERFIL_TRADING in pa.PERFIS
    assert pa.PERFIS[PERFIL_TRADING]["atendido"] is False

    with pytest.raises(pa.PerfilNaoAtendido) as erro:
        pa.aplicar_perfil(amostra, PERFIL_TRADING)
    assert "precifica" in str(erro.value).lower() or "trading" in str(erro.value).lower()


def test_recusa_do_trading_declara_o_motivo():
    """Uma recusa sem justificativa registrada não sobrevive a uma negociação comercial."""
    motivo = pa.PERFIS[PERFIL_TRADING]["motivo_da_recusa"]
    assert len(motivo) > 100
    assert "integridade" in motivo.lower()



# ---------------------------------------------------------------------------
# 2. Camadas de exposição
# ---------------------------------------------------------------------------

def test_camada_aberta_nao_carrega_nenhum_identificador(amostra):
    aberto = pa.aplicar_perfil(amostra, "imprensa_academia")
    for coluna in pa.CAMPOS_IDENTIFICADORES:
        assert coluna not in aberto.columns, f"identificador {coluna} vazou para a camada aberta"
    assert "atletas_no_agregado" in aberto.columns
    assert len(aberto) < len(amostra), "a camada aberta deveria agregar"


def test_camada_aberta_preserva_a_informacao_agregada(amostra):
    aberto = pa.aplicar_perfil(amostra, "operadora_integrity")
    juventude = aberto[aberto["clube_slug"] == "juventude"].iloc[0]
    assert juventude["atletas_no_agregado"] == 2
    assert juventude["score_pre_jogo"] == pytest.approx((0.12 + 0.03) / 2)


def test_clube_so_enxerga_o_proprio_elenco(amostra):
    do_clube = pa.aplicar_perfil(amostra, "clube", clube_do_cliente="juventude")
    assert set(do_clube["clube_slug"]) == {"juventude"}
    assert "Sicrano" not in set(do_clube["apelido"])


def test_clube_sem_elenco_declarado_e_recusado(amostra):
    with pytest.raises(ValueError):
        pa.aplicar_perfil(amostra, "clube")


def test_federacao_recebe_dado_identificado(amostra):
    identificado = pa.aplicar_perfil(amostra, "federacao_stjd")
    assert "apelido" in identificado.columns
    assert len(identificado) == len(amostra)


def test_perfil_desconhecido_e_rejeitado(amostra):
    with pytest.raises(KeyError):
        pa.aplicar_perfil(amostra, "curioso")


# ---------------------------------------------------------------------------
# 3. Pseudonimização
# ---------------------------------------------------------------------------

def test_pseudonimo_e_estavel_e_distinto():
    assert pa.pseudonimizar("111111") == pa.pseudonimizar("111111")
    assert pa.pseudonimizar("111111") != pa.pseudonimizar("222222")
    assert pa.pseudonimizar("111111").startswith("atl_")


def test_pseudonimo_depende_do_segredo():
    """
    HMAC, e não hash simples: o espaço de registros da CBF é pequeno o bastante para que um
    SHA-256 puro fosse revertido por força bruta.
    """
    assert pa.pseudonimizar("111111", segredo="a") != pa.pseudonimizar("111111", segredo="b")


def test_condenados_com_transito_em_julgado_sao_nominaveis():
    """Fato público pode ser nominado; atleta apenas atípico, não."""
    publicos = pa.registros_publicos()
    if not publicos:
        pytest.skip("ground truth indisponível")
    assert len(publicos) <= 20, "a lista de nominaveis cresceu além dos casos julgados"


# ---------------------------------------------------------------------------
# 4. Feeds efetivamente gerados
# ---------------------------------------------------------------------------

def test_feed_servido_por_padrao_e_o_de_menor_exposicao():
    caminho = os.path.join(FEED_DIR, "risco_pre_jogo.json")
    if not os.path.exists(caminho):
        pytest.skip("feed de risco não gerado")

    with open(caminho, encoding="utf-8") as f:
        payload = json.load(f)

    assert payload["camada"] == pa.CAMADA_ABERTA
    bruto = json.dumps(payload, ensure_ascii=False).lower()
    for termo in ("apelido", "registro_cbf", "num_camisa"):
        assert termo not in bruto, f"o feed padrão expõe {termo}"


def test_camada_identificada_fica_em_diretorio_restrito_e_avisado():
    restrito = os.path.join(FEED_DIR, "restrito")
    if not os.path.isdir(restrito):
        pytest.skip("camada restrita não gerada")

    assert os.path.exists(os.path.join(restrito, "AVISO.md")), (
        "a camada identificada precisa vir acompanhada do aviso de restrição"
    )
    aviso = open(os.path.join(restrito, "AVISO.md"), encoding="utf-8").read().lower()
    assert "nunca foi investigada" in aviso or "nunca investigad" in aviso

    identificado = os.path.join(restrito, "risco_pre_jogo__federacao_stjd.json")
    if os.path.exists(identificado):
        with open(identificado, encoding="utf-8") as f:
            payload = json.load(f)
        assert payload["camada"] == pa.CAMADA_IDENTIFICADA
        assert "condicao_de_uso" in payload


def test_banco_do_feed_nao_expoe_nome_no_risco_pre_jogo():
    caminho = os.path.join(FEED_DIR, "brasileirao.db")
    if not os.path.exists(caminho):
        pytest.skip("banco do feed não gerado")

    conn = sqlite3.connect(caminho)
    try:
        tabelas = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "risco_pre_jogo" not in tabelas:
            pytest.skip("tabela de risco ainda não publicada")
        colunas = {r[1] for r in conn.execute("PRAGMA table_info(risco_pre_jogo)")}
        assert "atleta_pseudonimo" in colunas
        for proibida in ("apelido", "atleta", "registro_cbf", "num_camisa"):
            assert proibida not in colunas, f"a tabela de risco expõe {proibida}"
    finally:
        conn.close()


def test_matriz_de_granularidade_publicada():
    caminho = os.path.join("reports", "tables", "matriz_de_granularidade_por_segmento.csv")
    if not os.path.exists(caminho):
        pytest.skip("matriz não publicada")

    df = pd.read_csv(caminho)
    assert len(df) == len(pa.PERFIS)
    trading = df[df["perfil"] == PERFIL_TRADING].iloc[0]
    assert not bool(trading["atendido"])
