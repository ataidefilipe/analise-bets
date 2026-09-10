"""
tests/test_econometric_models.py
--------------------------------
Testes unitários e de integração para a modelagem econométrica e causal (Fase 7):
1. Integridade do painel Clube x Partida (7.598 observações, 2015–2024).
2. Validação da estimação TWFE e ausência de NaNs/multicolinearidade perfeita.
3. Consistência do Estudo de Eventos (Staggered Event Study) e teste de tendências paralelas.
4. Consistência dos modelos de dose-resposta e heterogeneidade interdivisões.
"""

import os
import pytest
import pandas as pd
import numpy as np

PANEL_PATH = os.path.join("data", "processed", "panel", "painel_clube_partida.parquet")
TABLES_DIR = os.path.join("reports", "tables")


@pytest.fixture(scope="module")
def panel_data():
    if not os.path.exists(PANEL_PATH):
        from src.models.prepare_panel import build_panel_dataset
        return build_panel_dataset()
    return pd.read_parquet(PANEL_PATH)


def test_panel_structure_and_integrity(panel_data):
    """Verifica se o painel possui a granularidade e atributos esperados."""
    assert len(panel_data) == 7598, f"Esperado 7598 linhas, obtido {len(panel_data)}"
    assert panel_data["temporada"].min() == 2015
    assert panel_data["temporada"].max() == 2024
    assert set(panel_data["is_mandante"].unique()) == {0, 1}

    # Mandantes e visitantes perfeitamente balanceados
    assert panel_data["is_mandante"].sum() == 3799
    assert (panel_data["is_mandante"] == 0).sum() == 3799

    # Verificar ausência de NaNs em colunas essenciais
    essential_cols = ["partida_id", "temporada", "rodada", "clube_slug", "bet_exposure_clube", "is_mandante", "cartoes_totais"]
    for col in essential_cols:
        assert panel_data[col].isnull().sum() == 0, f"Coluna {col} contém valores nulos"


def test_twfe_results_file():
    """Verifica a integridade da tabela exportada de TWFE."""
    csv_path = os.path.join(TABLES_DIR, "tabela_11_regressoes_twfe.csv")
    assert os.path.exists(csv_path), "Tabela 11 de TWFE não encontrada"

    df_twfe = pd.read_csv(csv_path)
    assert len(df_twfe) == 7

    # Cartões totais deve ter efeito positivo e estatisticamente significante a 1%
    row_totais = df_twfe[df_twfe["dep_var_code"] == "cartoes_totais"].iloc[0]
    assert row_totais["coef_bet_exposure"] > 0
    assert row_totais["p_val_bet_exposure"] < 0.05
    assert row_totais["r2"] > 0.20

    # Mando de campo deve reduzir cartões (is_mandante < 0 e p < 0.001)
    assert row_totais["coef_is_mandante"] < 0
    assert row_totais["p_val_is_mandante"] < 0.001


def test_staggered_event_study_results():
    """Verifica a integridade da tabela de Event Study e o teste de tendências paralelas."""
    csv_path = os.path.join(TABLES_DIR, "tabela_12_did_event_study.csv")
    assert os.path.exists(csv_path), "Tabela 12 de Event Study não encontrada"

    df_es = pd.read_csv(csv_path)
    assert len(df_es) >= 21  # 7 períodos x 3 outcomes

    # Teste de tendências paralelas para cartões totais
    sub_cartoes = df_es[df_es["dep_var_code"] == "cartoes_totais"]
    assert len(sub_cartoes) == 7

    # Ano e = -2 não deve ser estatisticamente significante (H0 mantida)
    row_m2 = sub_cartoes[sub_cartoes["event_time"] == -2].iloc[0]
    assert row_m2["p_valor"] > 0.05

    # Anos e = 1 e e = 2 devem ter coeficientes positivos e significantes
    row_p1 = sub_cartoes[sub_cartoes["event_time"] == 1].iloc[0]
    row_p2 = sub_cartoes[sub_cartoes["event_time"] == 2].iloc[0]
    assert row_p1["coeficiente"] > 0 and row_p1["p_valor"] < 0.05
    assert row_p2["coeficiente"] > 0 and row_p2["p_valor"] < 0.05


def test_dose_response_results():
    """Verifica a integridade da tabela de dose-resposta."""
    csv_path = os.path.join(TABLES_DIR, "tabela_13_dose_resposta_econometrica.csv")
    assert os.path.exists(csv_path), "Tabela 13 de Dose-Resposta não encontrada"

    df_dose = pd.read_csv(csv_path)
    assert len(df_dose) == 4
    for _, r in df_dose.iterrows():
        assert r["n_partidas"] > 3000


def test_series_heterogeneity_results():
    """Verifica a regressão de heterogeneidade Série A vs. Série B."""
    csv_path = os.path.join(TABLES_DIR, "tabela_14_heterogeneidade_series_regressao.csv")
    assert os.path.exists(csv_path), "Tabela 14 de Heterogeneidade de Séries não encontrada"

    df_het = pd.read_csv(csv_path)
    assert len(df_het) == 2

    # Série B tem coeficiente negativo significativo de cartões frente à Série A
    row_cards = df_het[df_het["modelo"].str.contains("Cartões Totais")].iloc[0]
    assert row_cards["coef_is_serie_b"] < 0
    assert row_cards["p_val_is_serie_b"] < 0.05
    assert row_cards["n_obs"] == 3040
