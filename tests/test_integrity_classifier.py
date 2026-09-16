"""
tests/test_integrity_classifier.py
----------------------------------
Testes unitários e de validação para o Modelo de Classificação de Integridade e Suspeição (ML):
1. Existência e integridade dos modelos serializados (.joblib).
2. Validação de estrutura e ausência de NaNs nas predições e probabilidades [0, 1].
3. Consistência da classificação em 3 tiers operacionais (Classe 0, 1 e 2).
4. Verificação da taxa de contaminação do Isolation Forest (~3%).
5. Avaliação de sensibilidade no Ground Truth da Operação Penalidade Máxima (Tabela 18).
6. Validação das tabelas exportadas (Tabela 18, 19 e 20).
"""

import os
import joblib
import pytest
import pandas as pd
import numpy as np
from src.models.integrity_classifier import BaggingPUClassifier

DATA_PARTIDAS_ML = os.path.join("data", "processed", "integrity", "partidas_ml_classified.parquet")
DATA_ATLETAS_ML = os.path.join("data", "processed", "integrity", "atletas_ml_classified.parquet")
MODELS_DIR = os.path.join("data", "processed", "integrity", "models")
TABLES_DIR = os.path.join("reports", "tables")


@pytest.fixture(scope="module")
def partidas_ml():
    assert os.path.exists(DATA_PARTIDAS_ML), f"Arquivo não encontrado: {DATA_PARTIDAS_ML}"
    return pd.read_parquet(DATA_PARTIDAS_ML)


@pytest.fixture(scope="module")
def atletas_ml():
    assert os.path.exists(DATA_ATLETAS_ML), f"Arquivo não encontrado: {DATA_ATLETAS_ML}"
    return pd.read_parquet(DATA_ATLETAS_ML)


def test_serialized_models_exist():
    """Verifica se todos os 4 modelos serializados (.joblib) foram gerados corretamente."""
    m_iforest = os.path.join(MODELS_DIR, "match_isolation_forest.joblib")
    m_pu = os.path.join(MODELS_DIR, "match_pu_classifier.joblib")
    a_iforest = os.path.join(MODELS_DIR, "athlete_isolation_forest.joblib")
    a_pu = os.path.join(MODELS_DIR, "athlete_pu_classifier.joblib")

    for path in [m_iforest, m_pu, a_iforest, a_pu]:
        assert os.path.exists(path), f"Modelo ausente: {path}"

    assert joblib.load(m_iforest) is not None
    assert BaggingPUClassifier.load(m_pu) is not None
    assert joblib.load(a_iforest) is not None
    assert BaggingPUClassifier.load(a_pu) is not None


def test_partidas_ml_structure(partidas_ml):
    """Valida formato, volume, intervalos e ausência de NaNs no dataset de partidas classificadas por ML."""
    assert len(partidas_ml) == 4559, f"Esperado 4559 partidas, obtido {len(partidas_ml)}"

    ml_cols = [
        "iforest_anomaly_score", "iforest_outlier", "prob_suspeicao_ml",
        "score_suspeicao_ml", "classificacao_ml", "ranking_ml"
    ]
    for col in ml_cols:
        assert col in partidas_ml.columns, f"Coluna ausente: {col}"
        assert partidas_ml[col].isnull().sum() == 0, f"Coluna {col} contém valores nulos"

    # Probabilidades no intervalo [0, 1]
    assert (partidas_ml["prob_suspeicao_ml"] >= 0.0).all()
    assert (partidas_ml["prob_suspeicao_ml"] <= 1.0).all()

    # Scores no intervalo [0, 100]
    assert (partidas_ml["iforest_anomaly_score"] >= 0.0).all()
    assert (partidas_ml["iforest_anomaly_score"] <= 100.0).all()

    # Outlier binário (0 ou 1)
    assert set(partidas_ml["iforest_outlier"].unique()).issubset({0, 1})
    contamination = partidas_ml["iforest_outlier"].mean()
    assert 0.025 <= contamination <= 0.035, f"Contaminação inesperada: {contamination}"

    # Classes operacionais válidas
    expected_classes = {
        "Classe 0: Basal / Conforme",
        "Classe 1: Monitoramento / Risco Moderado",
        "Classe 2: Alto Risco / Alerta Investigativo",
    }
    assert set(partidas_ml["classificacao_ml"].unique()).issubset(expected_classes)


def test_atletas_ml_structure(atletas_ml):
    """Valida formato, intervalos e ausência de NaNs no dataset de atletas classificados por ML."""
    assert len(atletas_ml) >= 3500, f"Esperado >= 3500 atletas, obtido {len(atletas_ml)}"

    ml_cols = [
        "iforest_anomaly_score", "iforest_outlier", "prob_suspeicao_ml",
        "score_suspeicao_ml", "classificacao_ml", "ranking_ml"
    ]
    for col in ml_cols:
        assert col in atletas_ml.columns, f"Coluna ausente: {col}"
        assert atletas_ml[col].isnull().sum() == 0, f"Coluna {col} contém valores nulos"

    assert (atletas_ml["prob_suspeicao_ml"] >= 0.0).all()
    assert (atletas_ml["prob_suspeicao_ml"] <= 1.0).all()

    assert (atletas_ml["iforest_anomaly_score"] >= 0.0).all()
    assert (atletas_ml["iforest_anomaly_score"] <= 100.0).all()

    contamination = atletas_ml["iforest_outlier"].mean()
    assert 0.025 <= contamination <= 0.035, f"Contaminação inesperada: {contamination}"


def test_ground_truth_ml_sensitivity():
    """Valida a sensibilidade empírica de 100% no ground truth da Tabela 18."""
    t18_path = os.path.join(TABLES_DIR, "tabela_18_classificador_integridade_resultados.csv")
    assert os.path.exists(t18_path), f"Tabela 18 ausente: {t18_path}"

    df_t18 = pd.read_csv(t18_path)
    assert len(df_t18) == 14, f"Esperado 14 casos reais da PM, obtido {len(df_t18)}"

    # 100% dos casos devem ser detectados em faixas de escrutínio ML
    n_detected = df_t18["status_deteccao_ml"].str.startswith("Detectado").sum()
    assert n_detected == 14, f"Esperado 14 casos detectados, obtido {n_detected}"

    # Probabilidade média de suspeição do modelo deve ser elevada (> 0.60)
    assert df_t18["prob_partida_ml"].mean() >= 0.60
    assert df_t18["prob_atleta_ml"].mean() >= 0.70


def test_top_rankings_tables():
    """Valida as Tabelas 19 e 20 com os rankings Top 50 gerados pelo modelo de ML."""
    t19_path = os.path.join(TABLES_DIR, "tabela_19_classificacao_partidas_ml.csv")
    t20_path = os.path.join(TABLES_DIR, "tabela_20_classificacao_atletas_ml.csv")

    assert os.path.exists(t19_path), f"Tabela 19 ausente: {t19_path}"
    assert os.path.exists(t20_path), f"Tabela 20 ausente: {t20_path}"

    df_t19 = pd.read_csv(t19_path)
    df_t20 = pd.read_csv(t20_path)

    assert len(df_t19) == 50
    assert len(df_t20) == 50

    # Ordenação decrescente por probabilidade de suspeição
    assert df_t19["prob_suspeicao_ml"].is_monotonic_decreasing
    assert df_t20["prob_suspeicao_ml"].is_monotonic_decreasing
