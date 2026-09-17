"""
tests/test_precisao_e_carga_alerta.py
-------------------------------------
Testes da análise de precisão e carga operacional do sistema de triagem (F1-04):
1. Correção do teste hipergeométrico usado como referência de acaso.
2. Coerência interna da Tabela 21, da precisão@k e das curvas de carga.
3. Guardas contra as duas armadilhas da tarefa: inventar denominador de precisão e
   ler a precisão@k sem o seu teto aritmético.
"""

import os
import pandas as pd
import pytest

from src.analysis import precisao_e_carga_alerta as pca

TABLES_DIR = os.path.join("reports", "tables")
T21 = os.path.join(TABLES_DIR, "tabela_21_precisao_e_carga_de_alerta.csv")
T21B = os.path.join(TABLES_DIR, "tabela_21b_precisao_at_k.csv")
T21C = os.path.join(TABLES_DIR, "tabela_21c_curva_carga_operacional.csv")
T21D = os.path.join(TABLES_DIR, "tabela_21d_limiar_por_persona.csv")
T21E = os.path.join(TABLES_DIR, "tabela_21e_curva_carga_operacional_atleta.csv")


@pytest.fixture(scope="module")
def t21():
    assert os.path.exists(T21), f"Tabela 21 ausente: {T21}"
    return pd.read_csv(T21)


@pytest.fixture(scope="module")
def curvas():
    return pd.read_csv(T21C), pd.read_csv(T21E)


# ---------------------------------------------------------------------------
# 1. Referência de acaso
# ---------------------------------------------------------------------------

def test_hipergeometrico_reconhece_captura_indistinguivel_do_acaso():
    """Capturar a fração esperada por sorteio tem de produzir p-valor alto."""
    # 10% da base sinalizada, 10% dos positivos capturados: exatamente o acaso.
    p = pca._p_hipergeometrico(capturados=1, n_base=1000, n_sinalizados=100, n_positivos=10)
    assert p > 0.5, f"p-valor de {p} para uma captura no nível do acaso"


def test_hipergeometrico_reconhece_captura_muito_acima_do_acaso():
    p = pca._p_hipergeometrico(capturados=9, n_base=1000, n_sinalizados=100, n_positivos=10)
    assert p < 0.001, f"p-valor de {p} para uma captura muito acima do acaso"


def test_hipergeometrico_e_monotonico_na_captura():
    ps = [pca._p_hipergeometrico(k, 1000, 100, 10) for k in range(0, 10)]
    assert all(a >= b for a, b in zip(ps, ps[1:])), "p-valor deve cair conforme a captura sobe"


# ---------------------------------------------------------------------------
# 2. Coerência das tabelas
# ---------------------------------------------------------------------------

def test_tabela_21_cobre_os_dois_niveis_e_todos_os_tiers(t21):
    assert set(t21["nivel"]) == {"partida", "atleta"}
    for nivel in ("partida", "atleta"):
        sel = t21[(t21["nivel"] == nivel) & (t21["tier"] != "TOTAL SINALIZADO (todos os tiers)")]
        assert abs(sel["pct_da_base"].sum() - 100.0) < 0.1, (
            f"Os tiers de {nivel} não particionam a base: somam {sel['pct_da_base'].sum()}%"
        )
        assert sel["casos_conhecidos_no_tier"].sum() == sel["casos_conhecidos_totais"].iloc[0], (
            f"Casos conhecidos de {nivel} não somam o total"
        )


def test_precisao_at_k_respeita_o_teto_aritmetico():
    """
    Com no máximo 3 positivos em uma rodada de 10 partidas, a precisão@k não pode passar de
    `positivos/k`. Reportar a métrica sem esse teto convida a lê-la como desempenho ruim do
    modelo, quando parte do limite é aritmética.
    """
    t = pd.read_csv(T21B)
    assert "precisao_maxima_possivel" in t.columns
    assert (t["precisao_at_k"] <= t["precisao_maxima_possivel"] + 1e-9).all()
    assert (t["recall_at_k"] <= 1.0 + 1e-9).all()


def test_curvas_sao_monotonicas_em_volume(curvas):
    """Afrouxar o limiar só pode aumentar o volume sinalizado e nunca reduzir a captura."""
    for curva in curvas:
        ordenada = curva.sort_values("corte_percentil", ascending=False)
        assert ordenada["sinalizados"].is_monotonic_increasing
        assert ordenada["casos_capturados"].is_monotonic_increasing


def test_curvas_declaram_ganho_e_p_valor(curvas):
    """
    O entregável honesto da F1-04 não é a sensibilidade sozinha: é a sensibilidade contra o que
    se obteria sorteando a mesma quantidade de registros.
    """
    for curva in curvas:
        for coluna in ("ganho_sobre_aleatorio", "p_valor_vs_acaso", "pct_da_base", "sensibilidade"):
            assert coluna in curva.columns, f"Coluna ausente na curva: {coluna}"
        avaliaveis = curva[curva["casos_capturados"] > 0]
        assert avaliaveis["p_valor_vs_acaso"].notna().all()
        assert (avaliaveis["p_valor_vs_acaso"].between(0, 1)).all()


def test_ganho_sobre_aleatorio_bate_com_a_definicao(curvas):
    for curva in curvas:
        sel = curva[curva["pct_da_base"] > 0]
        esperado = sel["sensibilidade"] / (sel["pct_da_base"] / 100.0)
        assert ((sel["ganho_sobre_aleatorio"] - esperado).abs() < 0.02).all()


def test_limiar_por_persona_cabe_na_capacidade_declarada():
    """A recomendação não pode indicar um corte que estoura o orçamento de revisão da persona."""
    t = pd.read_csv(T21D)
    assert len(t) == len(pca.PERSONAS)
    validos = t[t["alertas_por_rodada"].notna()]
    assert (validos["alertas_por_rodada"] <= validos["capacidade_por_rodada"] + 1e-9).all()


# ---------------------------------------------------------------------------
# 3. Guardas de honestidade metodológica
# ---------------------------------------------------------------------------

def test_nenhuma_tabela_reporta_precisao_absoluta():
    """
    Sem falsos positivos rotulados, precisão absoluta não é estimável. Se alguma coluna com esse
    nome aparecer, é sinal de que um denominador foi inventado.
    """
    proibidas = {"precisao_absoluta", "precisao_global", "falsos_positivos", "especificidade"}
    for caminho in (T21, T21B, T21C, T21D, T21E):
        colunas = set(pd.read_csv(caminho).columns)
        assert not (colunas & proibidas), (
            f"{os.path.basename(caminho)} reporta métrica não estimável: {colunas & proibidas}"
        )


def test_figura_da_curva_publicada():
    caminho = os.path.join("reports", "figures", "integrity", "04_curva_carga_operacional.png")
    assert os.path.exists(caminho), f"Figura da curva de carga ausente: {caminho}"
    assert os.path.getsize(caminho) > 50_000, "Figura suspeita de estar vazia"
