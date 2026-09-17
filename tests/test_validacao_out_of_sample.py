"""
tests/test_validacao_out_of_sample.py
-------------------------------------
Testes do protocolo de validação fora da amostra do classificador de integridade (F1-03):
1. Correção do intervalo de confiança de Wilson.
2. Ausência de vazamento no desenho dos protocolos (o grupo avaliado nunca está no treino).
3. Integridade da Tabela 22 e coerência entre in-sample e out-of-sample.

Os testes validam os artefatos já publicados e o desenho do protocolo; não reexecutam o
treinamento, que leva cerca de um minuto e meio.
"""

import os
import pandas as pd
import pytest

from src.models import validacao_out_of_sample as oos

TABLES_DIR = os.path.join("reports", "tables")
T22 = os.path.join(TABLES_DIR, "tabela_22_validacao_out_of_sample.csv")
T22B = os.path.join(TABLES_DIR, "tabela_22b_validacao_out_of_sample_detalhe.csv")


@pytest.fixture(scope="module")
def resumo():
    assert os.path.exists(T22), f"Tabela 22 ausente: {T22}"
    return pd.read_csv(T22)


@pytest.fixture(scope="module")
def detalhe():
    assert os.path.exists(T22B), f"Detalhe da Tabela 22 ausente: {T22B}"
    return pd.read_csv(T22B)


# ---------------------------------------------------------------------------
# 1. Intervalo de Wilson
# ---------------------------------------------------------------------------

def test_wilson_cobre_os_extremos():
    """Com k = 0 ou k = n o intervalo não pode escapar de [0, 1] — é o motivo de usar Wilson."""
    lo, hi = oos.intervalo_wilson(0, 7)
    assert lo == 0.0 and 0.0 < hi < 1.0
    lo, hi = oos.intervalo_wilson(7, 7)
    assert hi == 1.0 and 0.0 < lo < 1.0


def test_wilson_encolhe_com_mais_observacoes():
    """O intervalo precisa estreitar conforme N cresce, mantida a proporção."""
    largura_pequena = lambda n: (lambda t: t[1] - t[0])(oos.intervalo_wilson(n // 2, n))
    assert largura_pequena(14) > largura_pequena(140) > largura_pequena(1400)


def test_wilson_contem_a_proporcao_pontual():
    for k, n in ((5, 14), (3, 7), (1, 9)):
        lo, hi = oos.intervalo_wilson(k, n)
        assert lo <= k / n <= hi


# ---------------------------------------------------------------------------
# 2. Desenho dos protocolos: ausência de vazamento
# ---------------------------------------------------------------------------

def test_leave_one_out_nunca_treina_com_o_grupo_avaliado(detalhe):
    """
    Em cada dobra, o cenário é o próprio grupo retirado. Se o grupo avaliado aparecesse no
    treino, a métrica voltaria a ser in-sample disfarçada.
    """
    loo = detalhe[detalhe["protocolo"] == "leave_one_out"]
    assert len(loo) > 0
    assert (loo["cenario"] == loo["grupo_avaliado"]).all(), (
        "Ha dobras de leave-one-out cujo grupo avaliado nao coincide com o grupo retirado"
    )


def test_leave_one_out_agrupa_por_entidade(detalhe):
    """
    PM-006 e PM-007 sao o mesmo atleta: avaliar um com o outro no treino e vazamento. No nivel
    de atleta, cada grupo avaliado precisa aparecer em uma unica dobra.
    """
    loo = detalhe[(detalhe["protocolo"] == "leave_one_out") & (detalhe["nivel"] == "atleta")]
    dobras_por_grupo = loo.groupby("grupo_avaliado")["cenario"].nunique()
    assert (dobras_por_grupo == 1).all(), (
        f"Grupos avaliados em mais de uma dobra: {dobras_por_grupo[dobras_por_grupo > 1].to_dict()}"
    )


def test_separacao_por_serie_treina_e_avalia_em_series_distintas(detalhe):
    """O cenário de separação por série só é informativo se as divisões não se misturarem."""
    sep = detalhe[detalhe["protocolo"] == "separacao_por_serie"]
    assert len(sep) > 0
    assert set(sep["cenario"]).issubset({"treina_em_B_avalia_em_A", "treina_em_A_avalia_em_B"})
    for cenario, g in sep.groupby("cenario"):
        assert g["positivos_no_treino"].min() > 0, f"{cenario}: treino sem positivos"


# ---------------------------------------------------------------------------
# 3. Tabela 22 e coerência dos resultados
# ---------------------------------------------------------------------------

def test_tabela_22_tem_os_tres_protocolos(resumo):
    assert set(resumo["protocolo"]) == {"in_sample", "leave_one_out", "separacao_por_serie"}
    assert set(resumo["nivel"]) == {"partida", "atleta"}


def test_tabela_22_reporta_intervalo_de_confianca(resumo):
    """Com N = 14 a estimativa pontual sozinha é enganosa: o intervalo é obrigatório."""
    for coluna in ("sensibilidade", "ic95_inferior", "ic95_superior", "capturados", "avaliados"):
        assert coluna in resumo.columns
        assert resumo[coluna].notna().all()
    assert (resumo["ic95_inferior"] <= resumo["sensibilidade"]).all()
    assert (resumo["sensibilidade"] <= resumo["ic95_superior"]).all()


def test_sensibilidade_out_of_sample_nao_supera_a_in_sample(resumo):
    """
    Guarda metodológica: se o out-of-sample empatasse ou superasse o in-sample, o mais provável
    seria haver vazamento no protocolo — e não um modelo que generaliza melhor do que memoriza.
    """
    for (nivel, criterio), g in resumo.groupby(["nivel", "criterio"]):
        dentro = g[g["protocolo"] == "in_sample"]["sensibilidade"]
        fora = g[g["protocolo"] == "leave_one_out"]["sensibilidade"]
        if len(dentro) and len(fora):
            assert fora.iloc[0] <= dentro.iloc[0] + 1e-9, (
                f"{nivel}/{criterio}: leave-one-out ({fora.iloc[0]}) acima do in-sample "
                f"({dentro.iloc[0]}) — suspeita de vazamento"
            )
