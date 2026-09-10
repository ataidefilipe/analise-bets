"""
tests/test_clean_betting.py
---------------------------
Suíte de testes para validação da integridade, limites matemáticos
e compatibilidade relacional da Camada de Exposição às Bets (MVP 2).
"""

import os
import pytest
import pandas as pd
import numpy as np

PROCESSED_BETTING_DIR = os.path.join("data", "processed", "betting")
PROCESSED_SERIE_A_DIR = os.path.join("data", "processed", "serie_a")


@pytest.fixture(scope="module")
def trends_anual():
    p = os.path.join(PROCESSED_BETTING_DIR, "trends_anual.parquet")
    assert os.path.exists(p), f"Arquivo não encontrado: {p}"
    return pd.read_parquet(p)


@pytest.fixture(scope="module")
def exposicao_clubes():
    p = os.path.join(PROCESSED_BETTING_DIR, "exposicao_clubes_temporada.parquet")
    assert os.path.exists(p), f"Arquivo não encontrado: {p}"
    return pd.read_parquet(p)


@pytest.fixture(scope="module")
def partidas_exposure():
    p = os.path.join(PROCESSED_SERIE_A_DIR, "partidas_com_exposure.parquet")
    assert os.path.exists(p), f"Arquivo não encontrado: {p}"
    return pd.read_parquet(p)


def test_trends_anual_integrity(trends_anual):
    """Verifica se a série anual do Google Trends cobre 2015-2025 com limites válidos."""
    anos_esperados = set(range(2015, 2026))
    assert set(trends_anual["ano"]) == anos_esperados, "Anos da série de Trends divergentes do esperado"
    assert (trends_anual["trends_score_medio"] >= 0).all()
    assert (trends_anual["trends_score_medio"] <= 100).all()
    assert (trends_anual["trends_normalizado_medio"] >= 0.0).all()
    assert (trends_anual["trends_normalizado_medio"] <= 1.0).all()


def test_exposicao_clubes_volume_e_chaves(exposicao_clubes):
    """Verifica se há exatamente 200 registros (20 clubes x 10 temporadas 2015-2024)."""
    assert len(exposicao_clubes) == 200, f"Esperado 200 registros, obtido {len(exposicao_clubes)}"
    assert set(exposicao_clubes["temporada"]) == set(range(2015, 2025))

    # Cada temporada deve ter exatamente 20 clubes distintos
    for ano, grp in exposicao_clubes.groupby("temporada"):
        assert len(grp) == 20, f"Temporada {ano} não possui 20 clubes"
        assert grp["clube_slug"].nunique() == 20, f"Clube duplicado na temporada {ano}"


def test_exposicao_clubes_limites_matematicos(exposicao_clubes):
    """Valida se os índices estão estritamente dentro do intervalo [0.0, 1.0]."""
    assert (exposicao_clubes["bet_exposure_clube"] >= 0.0).all()
    assert (exposicao_clubes["bet_exposure_clube"] <= 1.0).all()
    assert (exposicao_clubes["bet_exposure_total"] >= 0.0).all()
    assert (exposicao_clubes["bet_exposure_total"] <= 1.0).all()


def test_exposicao_clubes_regras_negocio(exposicao_clubes):
    """Valida se clubes sem patrocínio têm índice estritamente zero e master tem pontuação alta."""
    # Sem patrocínio -> bet_exposure_clube DEVE ser 0.0
    sem_patr = exposicao_clubes[~exposicao_clubes["tem_patrocinio_bet"]]
    assert (sem_patr["bet_exposure_clube"] == 0.0).all(), "Clube sem bet com exposure_clube > 0"

    # Master -> bet_exposure_clube >= 0.75
    master = exposicao_clubes[exposicao_clubes["tipo_patrocinio_bet"] == "master"]
    assert (master["bet_exposure_clube"] >= 0.75).all(), "Clube master com exposure_clube < 0.75"

    # 2015-2018: todos os clubes devem ter tem_patrocinio_bet == False
    pre_bets = exposicao_clubes[exposicao_clubes["temporada"] <= 2018]
    assert (~pre_bets["tem_patrocinio_bet"]).all(), "Identificado patrocínio de aposta em 2015-2018"


def test_partidas_exposure_volume_e_schema(partidas_exposure):
    """Verifica se a base de partidas preservou todas as 8.785 linhas e adicionou as colunas esperadas."""
    assert len(partidas_exposure) == 8785, f"Esperado 8.785 partidas, obtido {len(partidas_exposure)}"

    novas_colunas = [
        "tem_bet_mandante", "tipo_bet_mandante", "marca_bet_mandante",
        "exposure_clube_mandante", "exposure_total_mandante", "categoria_exp_mandante",
        "tem_bet_visitante", "tipo_bet_visitante", "marca_bet_visitante",
        "exposure_clube_visitante", "exposure_total_visitante", "categoria_exp_visitante",
        "exposure_clube_partida", "exposure_total_partida",
        "ambos_patrocinados_bet", "algum_patrocinado_bet", "categoria_exposicao_partida"
    ]
    for col in novas_colunas:
        assert col in partidas_exposure.columns, f"Coluna ausente: {col}"


def test_partidas_exposure_periodos_historicos(partidas_exposure):
    """Verifica se o histórico pré-2019 reflete ausência de patrocínio e 2024 reflete saturação."""
    partidas_antigas = partidas_exposure[partidas_exposure["temporada"] <= 2018]
    assert (partidas_antigas["exposure_clube_partida"] == 0.0).all()
    assert (~partidas_antigas["ambos_patrocinados_bet"]).all()

    partidas_2024 = partidas_exposure[partidas_exposure["temporada"] == 2024]
    # Em 2024, a maioria dos jogos deve ter ambos patrocinados por bets
    taxa_ambos_2024 = partidas_2024["ambos_patrocinados_bet"].mean()
    assert taxa_ambos_2024 > 0.70, f"Taxa de jogos com ambas as equipes patrocinadas em 2024 muito baixa: {taxa_ambos_2024}"
