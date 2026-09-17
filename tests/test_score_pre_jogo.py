"""
tests/test_score_pre_jogo.py
----------------------------
Testes do escore de risco pré-jogo por atleta escalado (F3-01):
1. Ausência de vazamento temporal — o maior risco técnico da tarefa.
2. Comportamento do encolhimento bayesiano em amostra pequena.
3. Integridade dos artefatos publicados e da ressalva interpretativa.
"""

import json
import os
import sqlite3

import pandas as pd
import pytest

from src.models import score_pre_jogo as spj

TABLES_DIR = os.path.join("reports", "tables")
FEED_DIR = os.path.join("data", "processed", "product_feed")


def _base_sintetica() -> pd.DataFrame:
    """
    Quatro atletas em seis rodadas. O atleta A recebe cartão no 1º tempo em toda rodada
    ímpar; o D, nunca. É o suficiente para exercitar acúmulo, encolhimento e cronologia.
    """
    linhas = []
    for rodada in range(1, 7):
        for i, registro in enumerate(["A", "B", "C", "D"]):
            linhas.append({
                "serie": "B", "temporada": 2022, "rodada": rodada,
                "partida_id": 100 + rodada, "clube_slug": "clube", "num_camisa": i + 1,
                "apelido": registro, "atleta_slug": registro.lower(), "registro_cbf": registro,
                "condicao": "Titular", "minutos_em_campo": 90, "participou": True,
                "cartao": registro == "A" and rodada % 2 == 1,
                "cartao_1t": registro == "A" and rodada % 2 == 1,
                "cartao_30m": False,
            })
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 1. Vazamento temporal
# ---------------------------------------------------------------------------

def test_historico_da_primeira_rodada_e_vazio():
    """Na primeira aparição de um atleta não existe histórico anterior. Zero, não NaN."""
    df = spj.calcular_score(_base_sintetica())
    primeira = df[df["rodada"] == 1]
    assert (primeira["minutos_previos"] == 0).all()
    assert (primeira["cartoes_1t_previos"] == 0).all()
    assert primeira["score_pre_jogo"].notna().all()


def test_historico_acumula_apenas_o_passado():
    """Na rodada r, o acumulado tem de ser exatamente o que ocorreu até r-1."""
    df = spj.calcular_score(_base_sintetica())
    atleta = df[df["registro_cbf"] == "A"].sort_values("rodada")

    # A recebe cartão nas rodadas 1, 3 e 5 — o acumulado anterior segue 0,1,1,2,2,3.
    assert list(atleta["cartoes_1t_previos"]) == [0, 1, 1, 2, 2, 3]
    assert list(atleta["minutos_previos"]) == [0, 90, 180, 270, 360, 450]


def test_corromper_o_futuro_nao_altera_o_passado():
    """
    O teste central da tarefa: alterar o alvo depois do corte não pode mexer em nenhum escore
    anterior a ele. Vale para a base sintética e para a base real.
    """
    resultado = spj.teste_de_vazamento(_base_sintetica(), fracao_de_corte=0.5)
    assert bool(resultado["aprovado"].iloc[0]), resultado.to_dict("records")
    assert resultado["linhas_comparadas"].iloc[0] > 0


def test_teste_de_vazamento_na_base_real_publicado():
    """O artefato do teste de vazamento precisa existir e estar aprovado."""
    caminho = os.path.join(TABLES_DIR, "tabela_23b_score_pre_jogo_teste_vazamento.csv")
    if not os.path.exists(caminho):
        pytest.skip("teste de vazamento não executado sobre a base real")

    df = pd.read_csv(caminho)
    assert bool(df["aprovado"].iloc[0]), (
        f"vazamento detectado: {int(df['linhas_divergentes'].iloc[0])} escores mudaram "
        f"ao corromper o futuro"
    )
    assert df["linhas_comparadas"].iloc[0] > 1000


def test_taxa_populacional_tambem_e_walk_forward():
    """
    A taxa basal para a qual o escore encolhe não pode ser estimada sobre a base inteira: é um
    agregado, mas ainda assim informação do futuro. Ela precisa crescer com o tempo.
    """
    df = spj.calcular_score(_base_sintetica())
    por_rodada = df.groupby("rodada")["taxa_populacional"].first()
    assert por_rodada.iloc[0] == 0.0, "a primeira rodada não tem população anterior"
    assert por_rodada.nunique() > 1, "a taxa populacional está congelada — sinal de vazamento"


# ---------------------------------------------------------------------------
# 2. Comportamento do modelo
# ---------------------------------------------------------------------------

def test_encolhimento_protege_contra_amostra_pequena():
    """
    Um atleta com um cartão em poucos minutos não pode liderar o ranking. Sem encolhimento,
    a taxa dele seria a maior da liga por construção.
    """
    base = _base_sintetica()
    novato = base[base["rodada"] == 6].iloc[0].copy()
    novato["registro_cbf"] = "NOVATO"
    novato["num_camisa"] = 99
    novato["minutos_em_campo"] = 10
    novato["cartao_1t"] = True
    base = pd.concat([base, pd.DataFrame([novato])], ignore_index=True)

    df = spj.calcular_score(base)
    ultimo = df[df["rodada"] == 6]
    lider = ultimo.sort_values("score_pre_jogo", ascending=False).iloc[0]
    assert lider["registro_cbf"] != "NOVATO", "atleta sem histórico liderou o ranking"


def test_score_cresce_com_historico_de_cartoes():
    """Entre dois atletas com os mesmos minutos, quem tem mais cartões prévios pontua mais."""
    df = spj.calcular_score(_base_sintetica())
    ultima = df[df["rodada"] == 6].set_index("registro_cbf")
    assert ultima.loc["A", "score_pre_jogo"] > ultima.loc["D", "score_pre_jogo"]


def test_reserva_pontua_menos_que_titular_com_mesmo_perfil():
    """O escore é uma expectativa na partida: quem joga menos tempo espera menos cartões."""
    base = _base_sintetica()
    base.loc[(base["rodada"] == 6) & (base["registro_cbf"] == "A"), "condicao"] = "Reserva"
    df = spj.calcular_score(base)
    linha = df[(df["rodada"] == 6) & (df["registro_cbf"] == "A")].iloc[0]
    assert linha["minutos_esperados"] == spj.MINUTOS_ESPERADOS["Reserva"]
    assert linha["score_pre_jogo"] < linha["taxa_1t_ajustada"] * spj.MINUTOS_ESPERADOS["Titular"]


# ---------------------------------------------------------------------------
# 3. Artefatos e ressalva interpretativa
# ---------------------------------------------------------------------------

def test_avaliacao_compara_com_linha_de_base_e_com_o_acaso():
    caminho = os.path.join(TABLES_DIR, "tabela_23_score_pre_jogo_avaliacao.csv")
    if not os.path.exists(caminho):
        pytest.skip("avaliação não executada")

    df = pd.read_csv(caminho)
    criterios = set(df["criterio"])
    assert any("pré-jogo" in c for c in criterios)
    assert any("base" in c for c in criterios), "falta a linha de base ingênua"
    for coluna in ("precisao_at_k", "taxa_base_da_populacao", "ganho_sobre_o_acaso"):
        assert coluna in df.columns
    assert set(df["k"]) == set(spj.KS_AVALIADOS)


def test_feed_de_risco_carrega_a_ressalva_interpretativa():
    """
    A ressalva de que o escore mede atipicidade, e não fraude, precisa acompanhar o dado em
    toda saída visível — é requisito de governança, não de estilo.

    Vale para as duas camadas: a aberta, servida por padrão, e a identificada, em diretório
    restrito. A estrutura dos dois arquivos difere desde a F4-03, que passou a segmentar o feed
    por perfil de cliente; a ressalva, não.
    """
    caminhos = [os.path.join(FEED_DIR, "risco_pre_jogo.json"),
                os.path.join(FEED_DIR, "restrito", "risco_pre_jogo__federacao_stjd.json")]
    existentes = [c for c in caminhos if os.path.exists(c)]
    if not existentes:
        pytest.skip("feed de risco não gerado")

    for caminho in existentes:
        with open(caminho, encoding="utf-8") as f:
            payload = json.load(f)
        aviso = payload.get("aviso", "").lower()
        assert "atipicidade" in aviso, f"{caminho} sem a ressalva"
        assert "não" in aviso and "fraude" in aviso
        assert payload["partidas"], f"{caminho} sem partidas"

    # Na camada identificada, cada partida traz os atletas pontuados.
    identificado = os.path.join(FEED_DIR, "restrito", "risco_pre_jogo__federacao_stjd.json")
    if os.path.exists(identificado):
        with open(identificado, encoding="utf-8") as f:
            payload = json.load(f)
        assert all("score_pre_jogo" in atleta
                   for p in payload["partidas"][:5] for atleta in p["atletas"])


def test_sqlite_expoe_risco_e_aviso():
    caminho = os.path.join(FEED_DIR, "brasileirao.db")
    if not os.path.exists(caminho):
        pytest.skip("banco do feed não gerado")

    conn = sqlite3.connect(caminho)
    try:
        tabelas = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "risco_pre_jogo" not in tabelas:
            pytest.skip("tabela de risco ainda não publicada")
        assert conn.execute("SELECT COUNT(*) FROM risco_pre_jogo").fetchone()[0] > 0
        assert "avisos" in tabelas, "o banco expõe o escore sem a ressalva"
        aviso = conn.execute("SELECT valor FROM avisos WHERE chave='aviso_interpretativo'").fetchone()
        assert aviso and "atipicidade" in aviso[0].lower()
    finally:
        conn.close()
