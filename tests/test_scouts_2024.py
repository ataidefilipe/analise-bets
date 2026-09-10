"""
Testes unitários para validação do enriquecimento de scouts da Série A 2024 (Sofascore).
Garante integridade referencial, completude e limites estatísticos.
"""

from pathlib import Path
import pandas as pd
import pytest

DATA_DIR = Path("data/processed/serie_a")

@pytest.fixture(scope="module")
def df_stats():
    return pd.read_parquet(DATA_DIR / "estatisticas.parquet")

@pytest.fixture(scope="module")
def df_partidas():
    return pd.read_parquet(DATA_DIR / "partidas.parquet")

@pytest.fixture(scope="module")
def df_cartoes():
    return pd.read_parquet(DATA_DIR / "cartoes.parquet")

def test_2024_scouts_presence(df_stats):
    s2024 = df_stats[df_stats["temporada"] == 2024]
    assert len(s2024) == 760, f"Esperado 760 registros em 2024, obtido {len(s2024)}"
    assert s2024["scouts_validos"].sum() >= 750, "Ao menos 750 registros devem ter scouts_validos = True"

def test_2024_fouls_bounds(df_stats):
    s2024 = df_stats[(df_stats["temporada"] == 2024) & (df_stats["scouts_validos"])]
    total_faltas = s2024["faltas"].sum()
    assert total_faltas > 9000, f"Total de faltas ({total_faltas}) abaixo do esperado"
    
    mean_fouls_per_match = total_faltas / (len(s2024) / 2)
    assert 20.0 <= mean_fouls_per_match <= 32.0, f"Média de faltas/partida anormal: {mean_fouls_per_match:.2f}"

def test_2024_corners_and_shots(df_stats):
    s2024 = df_stats[(df_stats["temporada"] == 2024) & (df_stats["scouts_validos"])]
    assert s2024["escanteios"].sum() > 3000, "Escanteios 2024 abaixo do esperado"
    assert s2024["chutes"].sum() > 8000, "Chutes 2024 abaixo do esperado"

def test_2024_conversion_rate(df_stats, df_cartoes):
    s2024 = df_stats[(df_stats["temporada"] == 2024) & (df_stats["scouts_validos"])]
    c2024 = df_cartoes[df_cartoes["temporada"] == 2024]
    
    total_cartoes = len(c2024)
    total_faltas = s2024["faltas"].sum()
    
    tau = total_cartoes / total_faltas
    assert 0.15 <= tau <= 0.30, f"Taxa de conversão 2024 ({tau:.4f}) fora da faixa esperada"

def test_foreign_key_integrity(df_stats, df_partidas):
    p2024_ids = set(df_partidas[df_partidas["temporada"] == 2024]["partida_id"])
    s2024_ids = set(df_stats[df_stats["temporada"] == 2024]["partida_id"])
    
    assert s2024_ids == p2024_ids, "partida_id em estatisticas 2024 deve coincidir 100% com partidas 2024"
