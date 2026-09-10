import json
import logging
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


def slugify(text: Optional[str]) -> str:
    if pd.isna(text) or text is None:
        return ''
    text = str(text).strip()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^a-zA-Z0-9]+', '_', text)
    text = re.sub(r'_+', '_', text).strip('_')
    return text.lower()


def parse_minute(val: Any) -> Tuple[int, int, int, str]:
    if pd.isna(val):
        return (0, 0, 0, 'Desconhecido')
    s = str(val).strip().replace("'", "")
    if '+' in s:
        parts = s.split('+')
        try:
            nominal = int(parts[0].strip())
            acrescimo = int(parts[1].strip())
            continuo = nominal + acrescimo
            periodo = '1T' if nominal <= 45 else '2T'
            return (continuo, nominal, acrescimo, periodo)
        except (ValueError, IndexError):
            pass
    try:
        nominal = int(float(s))
        periodo = '1T' if nominal <= 45 else '2T'
        return (nominal, nominal, 0, periodo)
    except ValueError:
        return (0, 0, 0, 'Desconhecido')


def parse_percent(val: Any) -> Optional[float]:
    if pd.isna(val) or val is None:
        return None
    s = str(val).replace('%', '').strip()
    try:
        num = float(s)
        if num > 1.0:
            return round(num / 100.0, 4)
        return round(num, 4)
    except ValueError:
        return None


def calculate_season_mapping(df_matches: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[int, int]]:
    df = df_matches.copy()
    df['data_dt'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
    df['diff_days'] = df['data_dt'].diff().dt.days

    is_new_season = (df.index == 0) | (df['diff_days'] > 50)
    df['season_idx'] = is_new_season.cumsum()

    season_years = {idx: 2003 + (idx - 1) for idx in df['season_idx'].unique()}
    df['temporada'] = df['season_idx'].map(season_years)

    season_map = dict(zip(df['ID'], df['temporada']))
    logger.info('Mapeadas %d temporadas para %d partidas.', len(season_years), len(df))
    return df, season_map


def clean_matches(df_raw: pd.DataFrame, df_with_season: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()
    df['temporada'] = df_with_season['temporada']

    # Converter data existente para ISO 8601 YYYY-MM-DD
    df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
    df['mandante_slug'] = df['mandante'].apply(slugify)
    df['visitante_slug'] = df['visitante'].apply(slugify)

    def determine_result(row):
        gp_m = row['mandante_Placar']
        gp_v = row['visitante_Placar']
        if pd.isna(gp_m) or pd.isna(gp_v):
            return 'Nao Realizada'
        if gp_m > gp_v:
            return 'Vitoria Mandante'
        elif gp_m < gp_v:
            return 'Vitoria Visitante'
        return 'Empate'

    df['resultado'] = df.apply(determine_result, axis=1)
    df['total_gols'] = df['mandante_Placar'] + df['visitante_Placar']
    df['saldo_mandante'] = df['mandante_Placar'] - df['visitante_Placar']

    rename_cols = {
        'ID': 'partida_id',
        'rodata': 'rodada',
        'hora': 'horario',
        'mandante': 'clube_mandante',
        'visitante': 'clube_visitante',
        'mandante_slug': 'clube_mandante_slug',
        'visitante_slug': 'clube_visitante_slug',
        'mandante_Placar': 'gols_mandante',
        'visitante_Placar': 'gols_visitante',
        'mandante_Estado': 'mandante_uf',
        'visitante_Estado': 'visitante_uf',
    }
    df = df.rename(columns=rename_cols)

    final_cols = [
        'partida_id',
        'temporada',
        'rodada',
        'data',
        'horario',
        'clube_mandante',
        'clube_mandante_slug',
        'clube_visitante',
        'clube_visitante_slug',
        'gols_mandante',
        'gols_visitante',
        'total_gols',
        'saldo_mandante',
        'resultado',
        'vencedor',
        'arena',
        'mandante_uf',
        'visitante_uf',
        'formacao_mandante',
        'formacao_visitante',
        'tecnico_mandante',
        'tecnico_visitante',
    ]
    return df[final_cols]


def clean_cards(df_raw: pd.DataFrame, season_map: Dict[int, int]) -> pd.DataFrame:
    df = df_raw.copy()
    df['temporada'] = df['partida_id'].map(season_map)
    df['clube_slug'] = df['clube'].apply(slugify)
    df['atleta'] = df['atleta'].fillna('Nao Informado').str.strip()
    df['atleta_slug'] = df['atleta'].apply(slugify)

    pos_map = {'Zagueira': 'Zagueiro'}
    df['posicao'] = df['posicao'].replace(pos_map).fillna('Nao Informada')

    parsed_min = df['minuto'].apply(parse_minute)
    df['minuto_continuo'] = [m[0] for m in parsed_min]
    df['minuto_nominal'] = [m[1] for m in parsed_min]
    df['acrescimo'] = [m[2] for m in parsed_min]
    df['periodo'] = [m[3] for m in parsed_min]
    df['num_camisa'] = pd.to_numeric(df['num_camisa'], errors='coerce').astype('Int64')

    df = df.rename(columns={'rodata': 'rodada'})
    final_cols = [
        'partida_id',
        'temporada',
        'rodada',
        'clube',
        'clube_slug',
        'cartao',
        'atleta',
        'atleta_slug',
        'num_camisa',
        'posicao',
        'minuto_continuo',
        'minuto_nominal',
        'acrescimo',
        'periodo',
    ]
    return df[final_cols]


def clean_stats(
    df_raw: pd.DataFrame,
    season_map: Dict[int, int],
    df_matches_clean: Optional[pd.DataFrame] = None,
    sofascore_dir: Optional[Path] = Path('data/raw/sofascore'),
) -> pd.DataFrame:
    df = df_raw.copy()
    df['temporada'] = df['partida_id'].map(season_map)
    df['clube_slug'] = df['clube'].apply(slugify)
    df['posse_de_bola_pct'] = df['posse_de_bola'].apply(parse_percent)
    df['precisao_passes_pct'] = df['precisao_passes'].apply(parse_percent)

    # Injetar scouts de 2024 do Sofascore se disponível
    if (
        sofascore_dir is not None
        and (sofascore_dir / 'estatisticas.parquet').exists()
        and (sofascore_dir / 'partidas.parquet').exists()
        and df_matches_clean is not None
    ):
        try:
            df_sofa_stats = pd.read_parquet(sofascore_dir / 'estatisticas.parquet')
            df_sofa_matches = pd.read_parquet(sofascore_dir / 'partidas.parquet')
            s2024_stats = df_sofa_stats[df_sofa_stats['temporada'] == 2024].copy()
            s2024_matches = df_sofa_matches[df_sofa_matches['temporada'] == 2024].copy()

            s2024_matches['mandante_slug'] = s2024_matches['mandante'].apply(slugify)
            s2024_matches['visitante_slug'] = s2024_matches['visitante'].apply(slugify)

            p2024_our = df_matches_clean[df_matches_clean['temporada'] == 2024]

            match_mapping = pd.merge(
                s2024_matches[['partida_id', 'rodada', 'mandante_slug', 'visitante_slug']],
                p2024_our[['partida_id', 'rodada', 'clube_mandante_slug', 'clube_visitante_slug']],
                left_on=['rodada', 'mandante_slug', 'visitante_slug'],
                right_on=['rodada', 'clube_mandante_slug', 'clube_visitante_slug'],
                suffixes=('_sofa', '_our'),
            )

            sofa_to_our_pid = dict(zip(match_mapping['partida_id_sofa'], match_mapping['partida_id_our']))
            sofa_mandante = dict(zip(match_mapping['partida_id_sofa'], match_mapping['mandante_slug']))
            sofa_visitante = dict(zip(match_mapping['partida_id_sofa'], match_mapping['visitante_slug']))

            s2024_stats['our_partida_id'] = s2024_stats['partida_id'].map(sofa_to_our_pid)
            s2024_stats['resolved_clube_slug'] = s2024_stats.apply(
                lambda r: sofa_mandante.get(r['partida_id']) if r['clube'] == 'mandante' else sofa_visitante.get(r['partida_id']),
                axis=1,
            )

            s2024_stats['merge_key'] = s2024_stats['our_partida_id'].astype(str) + '_' + s2024_stats['resolved_clube_slug']
            df['merge_key'] = df['partida_id'].astype(str) + '_' + df['clube_slug']

            stat_cols_to_update = ['faltas', 'escanteios', 'chutes', 'passes', 'impedimentos']
            for col in stat_cols_to_update:
                if col in s2024_stats.columns:
                    col_map = s2024_stats.dropna(subset=['merge_key']).set_index('merge_key')[col].to_dict()
                    mask_2024 = (df['temporada'] == 2024) & (df['merge_key'].isin(col_map))
                    df.loc[mask_2024, col] = df.loc[mask_2024, 'merge_key'].map(col_map).fillna(0).astype(int)

            if 'posse_de_bola' in s2024_stats.columns:
                posse_map = s2024_stats.dropna(subset=['merge_key']).set_index('merge_key')['posse_de_bola'].apply(parse_percent).to_dict()
                mask_2024 = (df['temporada'] == 2024) & (df['merge_key'].isin(posse_map))
                df.loc[mask_2024, 'posse_de_bola_pct'] = df.loc[mask_2024, 'merge_key'].map(posse_map).astype(float)

            df.drop(columns=['merge_key'], inplace=True)
            logger.info('Scouts de 2024 enriquecidos com sucesso via Sofascore.')
        except Exception as e:
            logger.warning('Falha ao enriquecer scouts de 2024 via Sofascore: %s', e)

    df['scouts_validos'] = (
        (df['temporada'].between(2015, 2023))
        | ((df['temporada'] == 2024) & (df['faltas'].fillna(0) > 0))
    )

    df = df.rename(columns={'rodata': 'rodada'})
    final_cols = [
        'partida_id',
        'temporada',
        'rodada',
        'clube',
        'clube_slug',
        'chutes',
        'chutes_no_alvo',
        'posse_de_bola_pct',
        'passes',
        'precisao_passes_pct',
        'faltas',
        'cartao_amarelo',
        'cartao_vermelho',
        'impedimentos',
        'escanteios',
        'scouts_validos',
    ]
    return df[final_cols]


def clean_goals(df_raw: pd.DataFrame, season_map: Dict[int, int]) -> pd.DataFrame:
    df = df_raw.copy()
    df['temporada'] = df['partida_id'].map(season_map)
    df['clube_slug'] = df['clube'].apply(slugify)
    df['atleta'] = df['atleta'].fillna('Nao Informado').str.strip()
    df['atleta_slug'] = df['atleta'].apply(slugify)
    df['tipo_de_gol'] = df['tipo_de_gol'].fillna('Normal')

    parsed_min = df['minuto'].apply(parse_minute)
    df['minuto_continuo'] = [m[0] for m in parsed_min]
    df['minuto_nominal'] = [m[1] for m in parsed_min]
    df['acrescimo'] = [m[2] for m in parsed_min]
    df['periodo'] = [m[3] for m in parsed_min]

    df = df.rename(columns={'rodata': 'rodada'})
    final_cols = [
        'partida_id',
        'temporada',
        'rodada',
        'clube',
        'clube_slug',
        'atleta',
        'atleta_slug',
        'minuto_continuo',
        'minuto_nominal',
        'acrescimo',
        'periodo',
        'tipo_de_gol',
    ]
    return df[final_cols]


def run_pipeline(
    raw_dir: Path = Path('data/raw/adaoduque'),
    output_dir: Path = Path('data/processed/serie_a'),
    sofascore_dir: Optional[Path] = Path('data/raw/sofascore'),
) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info('Iniciando pipeline de limpeza da Série A...')

    df_raw_matches = pd.read_csv(raw_dir / 'campeonato-brasileiro-full.csv', encoding='utf-8')
    df_raw_cards = pd.read_csv(raw_dir / 'campeonato-brasileiro-cartoes.csv', encoding='utf-8')
    df_raw_stats = pd.read_csv(raw_dir / 'campeonato-brasileiro-estatisticas-full.csv', encoding='utf-8')
    df_raw_goals = pd.read_csv(raw_dir / 'campeonato-brasileiro-gols.csv', encoding='utf-8')

    df_with_season, season_map = calculate_season_mapping(df_raw_matches)

    df_clean_matches = clean_matches(df_raw_matches, df_with_season)
    df_clean_cards = clean_cards(df_raw_cards, season_map)
    df_clean_stats = clean_stats(df_raw_stats, season_map, df_clean_matches, sofascore_dir)
    df_clean_goals = clean_goals(df_raw_goals, season_map)

    datasets = {
        'partidas': df_clean_matches,
        'cartoes': df_clean_cards,
        'estatisticas': df_clean_stats,
        'gols': df_clean_goals,
    }

    manifest = {'datasets': {}}
    for name, df in datasets.items():
        csv_path = output_dir / f'{name}.csv'
        parquet_path = output_dir / f'{name}.parquet'

        df.to_csv(csv_path, index=False, encoding='utf-8')
        df.to_parquet(parquet_path, index=False, engine='pyarrow')

        manifest['datasets'][name] = {
            'linhas': len(df),
            'colunas': len(df.columns),
            'csv_bytes': csv_path.stat().st_size,
            'parquet_bytes': parquet_path.stat().st_size,
        }
        logger.info('Dataset [%s] gravado: %d linhas, %d colunas.', name, len(df), len(df.columns))

    manifest_path = output_dir / 'manifest_processed.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info('Pipeline de limpeza concluído com sucesso. Manifesto salvo em %s', manifest_path)
    return manifest


if __name__ == '__main__':
    run_pipeline()
