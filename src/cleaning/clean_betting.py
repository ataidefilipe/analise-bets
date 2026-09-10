"""
src/cleaning/clean_betting.py
-----------------------------
Normaliza e calcula a Camada de Exposição às Bets (MVP 2):
1. Processa as séries temporais de interesse do Google Trends (mensal e anual).
2. Calcula o índice BET_EXPOSURE para cada clube x temporada (2015–2024):
   - bet_exposure_clube (estritamente contratual)
   - bet_exposure_total (contratual + transbordamento macro do mercado)
3. Enriquece a base consolidada de partidas da Série A com a exposição das equipes.
4. Exporta em Parquet e CSV com manifesto de integridade.
"""

import os
import hashlib
import json
import pandas as pd
import numpy as np

RAW_BETTING_DIR = os.path.join("data", "raw", "betting")
PROCESSED_BETTING_DIR = os.path.join("data", "processed", "betting")
PROCESSED_SERIE_A_DIR = os.path.join("data", "processed", "serie_a")


def get_regulatory_phase(year: int) -> str:
    if year <= 2017:
        return "Pre-Legalizacao"
    elif year <= 2022:
        return "Legalizacao_Expansao"
    elif year <= 2024:
        return "Regulamentacao"
    else:
        return "Mercado_Regulado"


def process_google_trends():
    trends_raw_path = os.path.join(RAW_BETTING_DIR, "google_trends_brasil_2015_2025.csv")
    df_trends_monthly = pd.read_csv(trends_raw_path)
    df_trends_monthly["data"] = pd.to_datetime(df_trends_monthly["data"])
    df_trends_monthly["fase_regulatoria"] = df_trends_monthly["ano"].apply(get_regulatory_phase)

    # Normalização mensal [0.0, 1.0]
    df_trends_monthly["trends_normalizado"] = (
        df_trends_monthly["google_trends_score"] / 100.0
    ).round(4)

    # Agregação Anual
    df_trends_annual = df_trends_monthly.groupby("ano").agg(
        trends_score_medio=("google_trends_score", "mean"),
        trends_score_max=("google_trends_score", "max"),
        trends_score_min=("google_trends_score", "min"),
        trends_score_std=("google_trends_score", "std")
    ).reset_index()

    df_trends_annual["fase_regulatoria"] = df_trends_annual["ano"].apply(get_regulatory_phase)
    df_trends_annual["trends_normalizado_medio"] = (df_trends_annual["trends_score_medio"] / 100.0).round(4)
    df_trends_annual["trends_normalizado_max"] = (df_trends_annual["trends_score_max"] / 100.0).round(4)

    return df_trends_monthly, df_trends_annual


def compute_club_bet_exposure(df_sponsors: pd.DataFrame, df_trends_annual: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula as métricas de exposição:
    - S_pos: Relevância do patrocínio (master=1.0, mangas=0.5, secundario=0.3, nenhum=0.0)
    - S_qtd: Multiplicidade de parcerias min(1.0, num_marcas/2)
    - S_macro: Índice anual normalizado do Google Trends
    - bet_exposure_clube: 0.75 * S_pos + 0.25 * S_qtd
    - bet_exposure_total: 0.60 * S_pos + 0.15 * S_qtd + 0.25 * S_macro
    """
    df = df_sponsors.copy()

    # Mapeamento do peso da posição
    peso_pos = {
        "master": 1.0,
        "mangas": 0.5,
        "secundario": 0.3,
        "nenhum": 0.0
    }
    df["score_posicao"] = df["tipo_patrocinio_bet"].map(peso_pos).fillna(0.0)
    df["score_quantidade"] = df["num_marcas_bet"].apply(lambda n: min(1.0, n / 2.0))

    # Merge com trends anual
    df = df.merge(
        df_trends_annual[["ano", "trends_normalizado_medio", "fase_regulatoria"]],
        left_on="temporada",
        right_on="ano",
        how="left"
    ).drop(columns=["ano"])

    df["score_macro"] = df["trends_normalizado_medio"].fillna(0.0)

    # 1. bet_exposure_clube (estritamente contratual, 0.0 se não tiver patrocínio)
    df["bet_exposure_clube"] = np.where(
        df["tem_patrocinio_bet"],
        (0.75 * df["score_posicao"] + 0.25 * df["score_quantidade"]).round(4),
        0.0
    )

    # 2. bet_exposure_total (combinação contratual + ambiente macro)
    df["bet_exposure_total"] = (
        0.60 * df["score_posicao"] + 0.15 * df["score_quantidade"] + 0.25 * df["score_macro"]
    ).round(4)

    # Categoria de exposição do clube
    conditions = [
        (df["bet_exposure_clube"] == 0.0),
        (df["bet_exposure_clube"] > 0.0) & (df["bet_exposure_clube"] < 0.70),
        (df["bet_exposure_clube"] >= 0.70)
    ]
    choices = ["Nenhuma", "Baixa/Media", "Alta"]
    df["categoria_exposicao_clube"] = np.select(conditions, choices, default="Nenhuma")

    return df


def enrich_matches_with_exposure(df_matches: pd.DataFrame, df_exposure: pd.DataFrame) -> pd.DataFrame:
    """
    Enriquece a base de partidas da Série A com a exposição do mandante e visitante.
    """
    df = df_matches.copy()

    cols_to_merge = [
        "temporada", "clube_slug", "tem_patrocinio_bet", "tipo_patrocinio_bet",
        "marca_principal_bet", "bet_exposure_clube", "bet_exposure_total", "categoria_exposicao_clube"
    ]
    df_exp_sub = df_exposure[cols_to_merge].copy()

    # Merge Mandante
    df = df.merge(
        df_exp_sub.rename(columns={
            "clube_slug": "clube_mandante_slug",
            "tem_patrocinio_bet": "tem_bet_mandante",
            "tipo_patrocinio_bet": "tipo_bet_mandante",
            "marca_principal_bet": "marca_bet_mandante",
            "bet_exposure_clube": "exposure_clube_mandante",
            "bet_exposure_total": "exposure_total_mandante",
            "categoria_exposicao_clube": "categoria_exp_mandante"
        }),
        on=["temporada", "clube_mandante_slug"],
        how="left"
    )

    # Merge Visitante
    df = df.merge(
        df_exp_sub.rename(columns={
            "clube_slug": "clube_visitante_slug",
            "tem_patrocinio_bet": "tem_bet_visitante",
            "tipo_patrocinio_bet": "tipo_bet_visitante",
            "marca_principal_bet": "marca_bet_visitante",
            "bet_exposure_clube": "exposure_clube_visitante",
            "bet_exposure_total": "exposure_total_visitante",
            "categoria_exposicao_clube": "categoria_exp_visitante"
        }),
        on=["temporada", "clube_visitante_slug"],
        how="left"
    )

    # Preencher anos anteriores a 2015 com valores padrão (sem bets)
    df["tem_bet_mandante"] = df["tem_bet_mandante"].fillna(False).astype(bool)
    df["tipo_bet_mandante"] = df["tipo_bet_mandante"].fillna("nenhum")
    df["marca_bet_mandante"] = df["marca_bet_mandante"].fillna("Nenhum")
    df["exposure_clube_mandante"] = df["exposure_clube_mandante"].fillna(0.0)
    df["exposure_total_mandante"] = df["exposure_total_mandante"].fillna(0.0)
    df["categoria_exp_mandante"] = df["categoria_exp_mandante"].fillna("Nenhuma")

    df["tem_bet_visitante"] = df["tem_bet_visitante"].fillna(False).astype(bool)
    df["tipo_bet_visitante"] = df["tipo_bet_visitante"].fillna("nenhum")
    df["marca_bet_visitante"] = df["marca_bet_visitante"].fillna("Nenhum")
    df["exposure_clube_visitante"] = df["exposure_clube_visitante"].fillna(0.0)
    df["exposure_total_visitante"] = df["exposure_total_visitante"].fillna(0.0)
    df["categoria_exp_visitante"] = df["categoria_exp_visitante"].fillna("Nenhuma")

    # Métricas consolidadas da partida
    df["exposure_clube_partida"] = (
        (df["exposure_clube_mandante"] + df["exposure_clube_visitante"]) / 2.0
    ).round(4)

    df["exposure_total_partida"] = (
        (df["exposure_total_mandante"] + df["exposure_total_visitante"]) / 2.0
    ).round(4)

    df["ambos_patrocinados_bet"] = df["tem_bet_mandante"] & df["tem_bet_visitante"]
    df["algum_patrocinado_bet"] = df["tem_bet_mandante"] | df["tem_bet_visitante"]

    # Categoria de exposição da partida
    conditions_match = [
        (~df["algum_patrocinado_bet"]),
        (df["algum_patrocinado_bet"] & ~df["ambos_patrocinados_bet"]),
        (df["ambos_patrocinados_bet"])
    ]
    choices_match = ["Nenhuma", "Parcial (1 clube)", "Total (2 clubes)"]
    df["categoria_exposicao_partida"] = np.select(conditions_match, choices_match, default="Nenhuma")

    return df


def compute_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main():
    os.makedirs(PROCESSED_BETTING_DIR, exist_ok=True)
    os.makedirs(PROCESSED_SERIE_A_DIR, exist_ok=True)
    print("=" * 70)
    print("PROCESSANDO CAMADA DE EXPOSIÇÃO ÀS BETS (MVP 2)")
    print("=" * 70)

    # 1. Processar Google Trends
    df_trends_m, df_trends_a = process_google_trends()

    p_trends_m_parquet = os.path.join(PROCESSED_BETTING_DIR, "trends_mensal.parquet")
    p_trends_m_csv = os.path.join(PROCESSED_BETTING_DIR, "trends_mensal.csv")
    df_trends_m.to_parquet(p_trends_m_parquet, index=False)
    df_trends_m.to_csv(p_trends_m_csv, index=False, encoding="utf-8")

    p_trends_a_parquet = os.path.join(PROCESSED_BETTING_DIR, "trends_anual.parquet")
    p_trends_a_csv = os.path.join(PROCESSED_BETTING_DIR, "trends_anual.csv")
    df_trends_a.to_parquet(p_trends_a_parquet, index=False)
    df_trends_a.to_csv(p_trends_a_csv, index=False, encoding="utf-8")
    print(f"-> Trends processado: {len(df_trends_m)} meses e {len(df_trends_a)} anos.")

    # 2. Processar Patrocínios e Exposição dos Clubes
    sponsors_raw_path = os.path.join(RAW_BETTING_DIR, "serie_a_patrocinios_2015_2024.csv")
    df_sponsors_raw = pd.read_csv(sponsors_raw_path)
    df_exposure = compute_club_bet_exposure(df_sponsors_raw, df_trends_a)

    p_exp_parquet = os.path.join(PROCESSED_BETTING_DIR, "exposicao_clubes_temporada.parquet")
    p_exp_csv = os.path.join(PROCESSED_BETTING_DIR, "exposicao_clubes_temporada.csv")
    df_exposure.to_parquet(p_exp_parquet, index=False)
    df_exposure.to_csv(p_exp_csv, index=False, encoding="utf-8")
    print(f"-> Exposição calculada para {len(df_exposure)} registros de clube x temporada.")

    # 3. Enriquecer Partidas da Série A
    matches_path = os.path.join(PROCESSED_SERIE_A_DIR, "partidas.parquet")
    df_matches = pd.read_parquet(matches_path)
    df_matches_enriched = enrich_matches_with_exposure(df_matches, df_exposure)

    p_matches_exp_parquet = os.path.join(PROCESSED_SERIE_A_DIR, "partidas_com_exposure.parquet")
    p_matches_exp_csv = os.path.join(PROCESSED_SERIE_A_DIR, "partidas_com_exposure.csv")
    df_matches_enriched.to_parquet(p_matches_exp_parquet, index=False)
    df_matches_enriched.to_csv(p_matches_exp_csv, index=False, encoding="utf-8")
    print(f"-> Partidas enriquecidas com exposição a bets: {len(df_matches_enriched)} partidas x {df_matches_enriched.shape[1]} colunas.")

    # 4. Gerar Manifesto Processado
    files_to_track = [
        p_trends_m_parquet, p_trends_m_csv,
        p_trends_a_parquet, p_trends_a_csv,
        p_exp_parquet, p_exp_csv,
        p_matches_exp_parquet, p_matches_exp_csv
    ]

    manifest = {
        "dataset": "Betting Exposure Processed Data (MVP 2)",
        "created_at": "2026-09-06",
        "files": {
            os.path.basename(f): {
                "sha256": compute_sha256(f),
                "bytes": os.path.getsize(f)
            } for f in files_to_track
        }
    }
    manifest_path = os.path.join(PROCESSED_BETTING_DIR, "manifest_processed.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"-> Manifesto de dados processados gravado: {manifest_path}")

    print("=" * 70)
    print("PROCESSAMENTO DO MVP 2 CONCLUÍDO COM SUCESSO!")
    print("=" * 70)


if __name__ == "__main__":
    main()
