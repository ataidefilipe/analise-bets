import json
from pathlib import Path
import pandas as pd
import pytest

from src.cleaning.clean_serie_a import (
    slugify,
    parse_minute,
    parse_percent,
    calculate_season_mapping,
    clean_matches,
    clean_cards,
    clean_stats,
    clean_goals,
    run_pipeline,
)


def test_slugify():
    assert slugify('São Paulo') == 'sao_paulo'
    assert slugify('Athletico-PR') == 'athletico_pr'
    assert slugify("Andrés D'Alessandro") == 'andres_d_alessandro'
    assert slugify('América-MG') == 'america_mg'
    assert slugify(None) == ''


def test_parse_minute():
    assert parse_minute('45+2') == (47, 45, 2, '1T')
    assert parse_minute('90+4') == (94, 90, 4, '2T')
    assert parse_minute('35') == (35, 35, 0, '1T')
    assert parse_minute('78') == (78, 78, 0, '2T')
    assert parse_minute("90+1'") == (91, 90, 1, '2T')


def test_parse_percent():
    assert parse_percent('47%') == 0.47
    assert parse_percent('53.5%') == 0.535
    assert parse_percent(0.47) == 0.47
    assert parse_percent(None) is None


def test_season_mapping_covid():
    raw_path = Path('data/raw/adaoduque/campeonato-brasileiro-full.csv')
    if not raw_path.exists():
        pytest.skip('Dados brutos de partidas não encontrados.')

    df_raw = pd.read_csv(raw_path, encoding='utf-8')
    df_with_season, season_map = calculate_season_mapping(df_raw)

    assert len(df_with_season) == 8785
    assert df_with_season['temporada'].isnull().sum() == 0

    # Validar temporadas únicas de 2003 a 2024
    seasons = sorted(df_with_season['temporada'].unique().tolist())
    assert seasons == list(range(2003, 2025))

    # Temporada 2020 deve ter exatamente 380 partidas
    t2020 = df_with_season[df_with_season['temporada'] == 2020]
    assert len(t2020) == 380

    # Partidas de fev/2021 do Brasileirão 2020 devem estar com temporada 2020
    dt = pd.to_datetime(t2020['data'], format='%d/%m/%Y')
    jogos_em_2021 = t2020[dt.dt.year == 2021]
    assert len(jogos_em_2021) == 112

    # Temporada 2021 deve ter exatamente 380 partidas
    t2021 = df_with_season[df_with_season['temporada'] == 2021]
    assert len(t2021) == 380


def test_pipeline_execution():
    manifest = run_pipeline()
    assert 'partidas' in manifest['datasets']
    assert 'cartoes' in manifest['datasets']
    assert 'estatisticas' in manifest['datasets']
    assert 'gols' in manifest['datasets']

    assert manifest['datasets']['partidas']['linhas'] == 8785
    assert manifest['datasets']['cartoes']['linhas'] == 20953
    assert manifest['datasets']['estatisticas']['linhas'] == 17570
    assert manifest['datasets']['gols']['linhas'] == 9861

    out_dir = Path('data/processed/serie_a')
    assert (out_dir / 'partidas.parquet').exists()
    assert (out_dir / 'cartoes.parquet').exists()
    assert (out_dir / 'estatisticas.parquet').exists()
    assert (out_dir / 'gols.parquet').exists()

    df_cards = pd.read_parquet(out_dir / 'cartoes.parquet')
    assert df_cards['temporada'].isnull().sum() == 0
    assert df_cards['minuto_continuo'].min() >= 0
    assert df_cards['clube_slug'].nunique() >= 30
