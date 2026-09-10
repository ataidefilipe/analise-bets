"""
tests/test_anomaly_detection.py
-------------------------------
Testes unitários e de integração para o Sistema de Triagem e Anomaly Scoring
de Integridade Esportiva (Fase 8):
1. Integridade e consistência dos datasets de scoring de partidas e atletas.
2. Limites matemáticos, monotonicidade e ausência de NaNs nos scores [0, 100].
3. Calibração e sensibilidade empírica contra os 14 casos da Operação Penalidade Máxima.
4. Integridade das tabelas analíticas exportadas (Tabela 15, 16 e 17).
"""

import os
import pytest
import pandas as pd
import numpy as np

DATA_PARTIDAS = os.path.join("data", "processed", "integrity", "partidas_anomaly_scored.parquet")
DATA_ATLETAS = os.path.join("data", "processed", "integrity", "atletas_anomaly_scored.parquet")
TABLES_DIR = os.path.join("reports", "tables")


@pytest.fixture(scope="module")
def partidas_scored():
    assert os.path.exists(DATA_PARTIDAS), f"Dataset não encontrado: {DATA_PARTIDAS}"
    return pd.read_parquet(DATA_PARTIDAS)


@pytest.fixture(scope="module")
def atletas_scored():
    assert os.path.exists(DATA_ATLETAS), f"Dataset não encontrado: {DATA_ATLETAS}"
    return pd.read_parquet(DATA_ATLETAS)


def test_partidas_scored_structure(partidas_scored):
    """Valida volume, colunas essenciais e ausência de NaNs no scoring de partidas."""
    assert len(partidas_scored) == 4559, f"Esperado 4559 partidas, obtido {len(partidas_scored)}"
    
    score_cols = [
        "score_tempo", "score_precoce", "score_volume", "score_bet", "score_penalti",
        "match_anomaly_score", "percentil_anomalia"
    ]
    for col in score_cols:
        assert col in partidas_scored.columns, f"Coluna ausente: {col}"
        assert partidas_scored[col].isnull().sum() == 0, f"Coluna {col} contém NaNs"
        assert (partidas_scored[col] >= 0).all(), f"Valores negativos em {col}"
        assert (partidas_scored[col] <= 100.0001).all(), f"Valores acima de 100 em {col}"

    assert "prioridade_triagem" in partidas_scored.columns
    assert set(partidas_scored["prioridade_triagem"].unique()).issubset({
        "Alta Prioridade de Escrutínio", "Média Prioridade", "Típico / Baixa Prioridade"
    })


def test_atletas_scored_structure(atletas_scored):
    """Valida integridade e intervalos dos scores individuais de atletas."""
    assert len(atletas_scored) >= 3500, f"Esperado >= 3500 atleta-temporadas, obtido {len(atletas_scored)}"
    
    score_cols = [
        "score_atleta_tempo", "score_atleta_taxa", "score_atleta_minuto",
        "athlete_anomaly_score", "percentil_atleta"
    ]
    for col in score_cols:
        assert col in atletas_scored.columns, f"Coluna ausente: {col}"
        assert atletas_scored[col].isnull().sum() == 0, f"Coluna {col} contém NaNs"
        assert (atletas_scored[col] >= 0).all(), f"Valores negativos em {col}"
        assert (atletas_scored[col] <= 100.0001).all(), f"Valores acima de 100 em {col}"

    # Somente atletas com >= 3 cartões foram pontuados
    assert (atletas_scored["total_cartoes"] >= 3).all()
    assert "classificacao_atleta" in atletas_scored.columns


def test_tables_generation():
    """Valida formato, ordenação e preenchimento das tabelas 15, 16 e 17."""
    t15_path = os.path.join(TABLES_DIR, "tabela_15_ranking_partidas_anomalas.csv")
    t16_path = os.path.join(TABLES_DIR, "tabela_16_ranking_atletas_anomalos.csv")
    t17_path = os.path.join(TABLES_DIR, "tabela_17_validacao_ground_truth_pm.csv")

    assert os.path.exists(t15_path), "Tabela 15 ausente"
    assert os.path.exists(t16_path), "Tabela 16 ausente"
    assert os.path.exists(t17_path), "Tabela 17 ausente"

    df_t15 = pd.read_csv(t15_path)
    df_t16 = pd.read_csv(t16_path)
    df_t17 = pd.read_csv(t17_path)

    # Ordenação decrescente por score
    assert len(df_t15) == 50
    assert df_t15["match_anomaly_score"].is_monotonic_decreasing

    assert len(df_t16) == 50
    assert df_t16["athlete_anomaly_score"].is_monotonic_decreasing

    # Tabela 17: exatamente 14 casos reais da Operação Penalidade Máxima
    assert len(df_t17) == 14
    assert df_t17["status_triagem"].str.startswith("Detectado").all()


def test_ground_truth_sensitivity_serie_a():
    """
    Testa se 100% dos atletas investigados na Série A (Operação Penalidade Máxima)
    são capturados no Top 10% (Percentil >= 90%) da distribuição histórica.
    """
    df_t17 = pd.read_csv(os.path.join(TABLES_DIR, "tabela_17_validacao_ground_truth_pm.csv"))
    serie_a = df_t17[df_t17["serie"] == "A"]
    
    assert len(serie_a) == 9  # 9 incidentes de Série A (PM-006 a PM-014)
    for _, row in serie_a.iterrows():
        assert row["athlete_percentil"] >= 90.0, (
            f"Caso {row['caso_id']} ({row['atleta']}) obteve percentil {row['athlete_percentil']:.1f}% "
            f"(esperado >= 90% no Top 10%)"
        )
        assert "Alta Prioridade" in row["status_triagem"]


def test_ground_truth_overall_detection():
    """Valida que todos os 14 casos mapeados estão marcados como Detectados nos tiers de prioridade."""
    df_t17 = pd.read_csv(os.path.join(TABLES_DIR, "tabela_17_validacao_ground_truth_pm.csv"))
    assert df_t17["status_triagem"].str.startswith("Detectado").all(), (
        "Existem casos investigados que caíram fora dos tiers de detecção!"
    )
    # Todos devem estar em Alta Prioridade ou Média Prioridade
    for status in df_t17["status_triagem"]:
        assert ("Alta Prioridade" in status) or ("Média Prioridade" in status)
