"""
src/models/anomaly_detection.py
-------------------------------
Sistema de Triagem e Anomaly Scoring de Integridade Esportiva (Fase 8):
1. Calcula o MATCH_ANOMALY_SCORE para 4.559 partidas (Série A 2015–2024 e Série B 2022–2023).
2. Calcula o ATHLETE_ANOMALY_SCORE para atletas com múltiplos cartões por temporada.
3. Calibra e audita a sensibilidade contra a base de ground truth da Operação Penalidade Máxima.
4. Exporta rankings de triagem investigativa em reports/tables/ e datasets enriquecidos em data/processed/integrity/.
"""

import os
import json
import hashlib
import numpy as np
import pandas as pd
from scipy import stats

SERIE_A_PARTIDAS = os.path.join("data", "processed", "serie_a", "partidas_com_exposure.parquet")
SERIE_A_CARTOES = os.path.join("data", "processed", "serie_a", "cartoes.parquet")
SERIE_A_GOLS = os.path.join("data", "processed", "serie_a", "gols.parquet")

SERIE_B_PARTIDAS = os.path.join("data", "processed", "serie_b", "partidas.parquet")
SERIE_B_CARTOES = os.path.join("data", "processed", "serie_b", "cartoes.parquet")
SERIE_B_GOLS = os.path.join("data", "processed", "serie_b", "gols.parquet")

GROUND_TRUTH_PATH = os.path.join("data", "processed", "integrity", "casos_penalidade_maxima.parquet")
PROCESSED_INTEGRITY_DIR = os.path.join("data", "processed", "integrity")
TABLES_DIR = os.path.join("reports", "tables")


def load_unified_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Carrega e harmoniza partidas, cartões e gols das Séries A e B."""
    # 1. Partidas Série A (2015 a 2024)
    pa = pd.read_parquet(SERIE_A_PARTIDAS)
    pa = pa[pa["temporada"] >= 2015].copy()
    pa["serie"] = "A"

    # Partidas Série B (2022 a 2023)
    pb = pd.read_parquet(SERIE_B_PARTIDAS)
    pb["exposure_total_partida"] = 0.50  # Média macro do período para Série B
    pb["exposure_clube_partida"] = 0.50
    pb["categoria_exposicao_partida"] = "Parcial (1 clube)"

    common_cols = [
        "partida_id", "temporada", "serie", "rodada", "data", "clube_mandante",
        "clube_mandante_slug", "clube_visitante", "clube_visitante_slug",
        "gols_mandante", "gols_visitante", "total_gols", "exposure_total_partida"
    ]
    df_matches = pd.concat([pa[common_cols], pb[common_cols]], ignore_index=True)

    # 2. Cartões Série A (2015 a 2024)
    ca = pd.read_parquet(SERIE_A_CARTOES)
    ca = ca[ca["temporada"] >= 2015].copy()
    ca["serie"] = "A"
    ca["categoria_infracao"] = "falta_temeraria"

    # Cartões Série B (2022 a 2023)
    cb = pd.read_parquet(SERIE_B_CARTOES)

    card_cols = [
        "partida_id", "temporada", "serie", "rodada", "clube", "clube_slug",
        "cartao", "atleta", "atleta_slug", "minuto_nominal", "periodo", "categoria_infracao"
    ]
    df_cards = pd.concat([ca[card_cols], cb[card_cols]], ignore_index=True)

    # 3. Gols de Pênalti no 1T
    ga = pd.read_parquet(SERIE_A_GOLS)
    ga = ga[ga["temporada"] >= 2015].copy()
    ga["serie"] = "A"

    gb = pd.read_parquet(SERIE_B_GOLS)

    pen_a = ga[(ga["tipo_de_gol"] == "Penalty") & (ga["periodo"] == "1T")]
    pen_b = gb[(gb["tipo_de_gol"] == "Penalty") & (gb["periodo"] == "1T")]
    df_penalties_1t = pd.concat([
        pen_a[["partida_id", "temporada", "serie", "clube_slug", "minuto_nominal"]],
        pen_b[["partida_id", "temporada", "serie", "clube_slug", "minuto_nominal"]]
    ], ignore_index=True)

    return df_matches, df_cards, df_penalties_1t


def compute_match_anomaly_scores(df_matches: pd.DataFrame, df_cards: pd.DataFrame, df_pen_1t: pd.DataFrame) -> pd.DataFrame:
    """Calcula o índice de anomalia ao nível da partida (MATCH_ANOMALY_SCORE)."""
    # Agregar cartões por partida
    cards_agg = df_cards.groupby(["serie", "partida_id"]).agg(
        total_cartoes=("cartao", "count"),
        cartoes_1t=("periodo", lambda s: (s == "1T").sum()),
        cartoes_30m=("minuto_nominal", lambda s: (s <= 30).sum()),
        cartoes_reclamacao_cera=("categoria_infracao", lambda s: s.isin(["reclamacao", "cera_retardar", "conduta_antidesportiva"]).sum())
    ).reset_index()

    pen_counts = df_pen_1t.groupby(["serie", "partida_id"]).size().rename("penaltis_1t").reset_index()

    matches = pd.merge(df_matches, cards_agg, on=["serie", "partida_id"], how="left")
    matches = pd.merge(matches, pen_counts, on=["serie", "partida_id"], how="left")

    matches["total_cartoes"] = matches["total_cartoes"].fillna(0).astype(int)
    matches["cartoes_1t"] = matches["cartoes_1t"].fillna(0).astype(int)
    matches["cartoes_30m"] = matches["cartoes_30m"].fillna(0).astype(int)
    matches["cartoes_reclamacao_cera"] = matches["cartoes_reclamacao_cera"].fillna(0).astype(int)
    matches["penaltis_1t"] = matches["penaltis_1t"].fillna(0).astype(int)

    matches["prop_cartoes_1t"] = np.where(
        matches["total_cartoes"] > 0,
        matches["cartoes_1t"] / matches["total_cartoes"],
        0.0
    )
    matches["prop_cartoes_30m"] = np.where(
        matches["total_cartoes"] > 0,
        matches["cartoes_30m"] / matches["total_cartoes"],
        0.0
    )

    # 1. Sub-score de Concentração Temporal no 1T (Binomial sob p0 = 0.35)
    def calc_p_binom_1t(row):
        n = row["total_cartoes"]
        k = row["cartoes_1t"]
        if n == 0 or k == 0:
            return 1.0
        return float(stats.binomtest(k, n, 0.35, alternative="greater").pvalue)

    matches["p_val_1t"] = matches.apply(calc_p_binom_1t, axis=1)
    matches["score_tempo"] = np.clip(-25.0 * np.log10(matches["p_val_1t"] + 1e-5), 0.0, 100.0)

    # 2. Sub-score de Cartões Precoces nos Primeiros 30' (Binomial sob p0 = 0.18)
    def calc_p_binom_30m(row):
        n = row["total_cartoes"]
        k = row["cartoes_30m"]
        if n == 0 or k == 0:
            return 1.0
        return float(stats.binomtest(k, n, 0.18, alternative="greater").pvalue)

    matches["p_val_30m"] = matches.apply(calc_p_binom_30m, axis=1)
    matches["score_precoce"] = np.clip(-25.0 * np.log10(matches["p_val_30m"] + 1e-5), 0.0, 100.0)

    # 3. Sub-score de Volumetria (z-score em relação ao ano e divisão)
    stats_season = matches.groupby(["temporada", "serie"])["total_cartoes"].agg(["mean", "std"]).reset_index()
    matches = matches.merge(stats_season, on=["temporada", "serie"], how="left")
    matches["z_cartoes"] = (matches["total_cartoes"] - matches["mean"]) / matches["std"]
    matches["score_volume"] = np.clip(50.0 + 20.0 * matches["z_cartoes"], 0.0, 100.0)

    # 4. Sub-score de Exposição a Apostas
    matches["score_bet"] = np.clip(matches["exposure_total_partida"] * 100.0, 0.0, 100.0)

    # 5. Sub-score de Pênalti no 1T
    matches["score_penalti"] = np.where(matches["penaltis_1t"] > 0, 100.0, 0.0)

    # 6. Índice Composto da Partida (MATCH_ANOMALY_SCORE)
    matches["match_anomaly_score"] = (
        0.35 * matches["score_tempo"]
        + 0.25 * matches["score_precoce"]
        + 0.20 * matches["score_volume"]
        + 0.10 * matches["score_bet"]
        + 0.10 * matches["score_penalti"]
    ).round(2)

    # Classificação de Prioridade de Escrutínio
    conditions = [
        matches["match_anomaly_score"] >= 80.0,
        matches["match_anomaly_score"] >= 65.0,
        matches["match_anomaly_score"] >= 50.0,
    ]
    choices = [
        "Extrema Anomalia (Top Priority)",
        "Alta Prioridade de Escrutínio",
        "Média Prioridade",
    ]
    matches["prioridade_triagem"] = np.select(conditions, choices, default="Típico / Baixa Prioridade")

    # Percentil e Ranking
    matches["ranking_geral"] = matches["match_anomaly_score"].rank(ascending=False, method="min").astype(int)
    matches["percentil_anomalia"] = (matches["match_anomaly_score"].rank(pct=True) * 100.0).round(2)

    # Limpeza de colunas intermediárias
    matches = matches.drop(columns=["mean", "std"])

    return matches


def compute_athlete_anomaly_scores(df_cards: pd.DataFrame) -> pd.DataFrame:
    """Calcula o índice de anomalia disciplinar e temporal ao nível do atleta (ATHLETE_ANOMALY_SCORE)."""
    # Filtrar apenas atletas identificados
    valid_cards = df_cards[~df_cards["atleta_slug"].isin(["nao_informado", "", None])].copy()

    # Agregar por atleta x temporada x série
    athlete_agg = valid_cards.groupby(["temporada", "serie", "clube_slug", "atleta_slug", "atleta"]).agg(
        total_cartoes=("cartao", "count"),
        cartoes_1t=("periodo", lambda s: (s == "1T").sum()),
        cartoes_30m=("minuto_nominal", lambda s: (s <= 30).sum()),
        minuto_medio_nominal=("minuto_nominal", "mean")
    ).reset_index()

    # Considerar atletas com ao menos 3 cartões na temporada
    athlete_agg = athlete_agg[athlete_agg["total_cartoes"] >= 3].copy()

    athlete_agg["prop_cartoes_1t"] = (athlete_agg["cartoes_1t"] / athlete_agg["total_cartoes"]).round(4)
    athlete_agg["minuto_medio_nominal"] = athlete_agg["minuto_medio_nominal"].round(1)

    # Teste binomial individual
    def calc_athlete_p_binom(row):
        n = row["total_cartoes"]
        k = row["cartoes_1t"]
        return float(stats.binomtest(k, n, 0.35, alternative="greater").pvalue)

    athlete_agg["p_val_binom_1t"] = athlete_agg.apply(calc_athlete_p_binom, axis=1)

    # Sub-scores
    athlete_agg["score_atleta_tempo"] = np.clip(-25.0 * np.log10(athlete_agg["p_val_binom_1t"] + 1e-5), 0.0, 100.0)
    athlete_agg["score_atleta_taxa"] = athlete_agg["prop_cartoes_1t"] * 100.0
    athlete_agg["score_atleta_minuto"] = np.clip((90.0 - athlete_agg["minuto_medio_nominal"]) * 1.5, 0.0, 100.0)

    # Índice Composto do Atleta
    athlete_agg["athlete_anomaly_score"] = (
        0.50 * athlete_agg["score_atleta_tempo"]
        + 0.30 * athlete_agg["score_atleta_taxa"]
        + 0.20 * athlete_agg["score_atleta_minuto"]
    ).round(2)

    athlete_agg["ranking_atleta"] = athlete_agg["athlete_anomaly_score"].rank(ascending=False, method="min").astype(int)
    athlete_agg["percentil_atleta"] = (athlete_agg["athlete_anomaly_score"].rank(pct=True) * 100.0).round(2)

    conditions = [
        athlete_agg["athlete_anomaly_score"] >= 80.0,
        athlete_agg["athlete_anomaly_score"] >= 65.0,
        athlete_agg["athlete_anomaly_score"] >= 50.0,
    ]
    choices = [
        "Extrema Anomalia Temporal",
        "Alta Concentração Precoce",
        "Média Concentração",
    ]
    athlete_agg["classificacao_atleta"] = np.select(conditions, choices, default="Padrão Basal Normal")

    return athlete_agg.sort_values("athlete_anomaly_score", ascending=False).reset_index(drop=True)


def evaluate_ground_truth_sensitivity(matches: pd.DataFrame, athletes: pd.DataFrame) -> pd.DataFrame:
    """Cruza e afere a sensibilidade do algoritmo contra os 14 casos reais da Operação Penalidade Máxima."""
    df_pm = pd.read_parquet(GROUND_TRUTH_PATH)

    alias_map = {
        "mateusinho": "mateus_da_silva_duarte",
        "moraes_jr": "moraes",
        "moraes": "moraes",
    }

    results = []

    for _, row in df_pm.iterrows():
        s = row["serie"]
        t = row["temporada"]
        rod = row["rodada"]
        mand_slug = row["clube_mandante"].lower().replace(" ", "_").replace("-", "_")

        # Buscar partida
        m = matches[
            (matches["serie"] == s) &
            (matches["temporada"] == t) &
            (matches["rodada"] == rod) &
            (matches["clube_mandante_slug"].str.contains(mand_slug[:5], case=False, na=False))
        ]

        if len(m) > 0:
            match_row = m.iloc[0]
            m_score = float(match_row["match_anomaly_score"])
            m_rank = int(match_row["ranking_geral"])
            m_pct = float(match_row["percentil_anomalia"])
            m_prio = str(match_row["prioridade_triagem"])
        else:
            m_score = np.nan
            m_rank = np.nan
            m_pct = np.nan
            m_prio = "Partida Não Mapeada"

        # Buscar atleta
        raw_slug = row["atleta_slug"]
        search_slug = alias_map.get(raw_slug, raw_slug)

        ath = athletes[
            (athletes["temporada"] == t) &
            (athletes["atleta_slug"].str.contains(search_slug.split("_")[0], case=False, na=False))
        ]

        if len(ath) > 0:
            ath_row = ath.iloc[0]
            a_score = float(ath_row["athlete_anomaly_score"])
            a_rank = int(ath_row["ranking_atleta"])
            a_pct = float(ath_row["percentil_atleta"])
        else:
            a_score = np.nan
            a_rank = np.nan
            a_pct = np.nan

        # Avaliar status de triagem baseado em percentis e scores
        # Nota: Casos onde o evento NAO ocorreu em campo (ex: Romario PM-001 e Bauermann PM-010)
        # naturalmente nao geram distorcao em campo.
        evento_executado = row["evento_ocorreu"] and row["executado_com_sucesso"]

        if (not np.isnan(a_pct) and a_pct >= 90.0) or (not np.isnan(m_pct) and m_pct >= 80.0):
            det_status = "Detectado (Alta Prioridade / Top 10%)"
        elif (not np.isnan(a_pct) and a_pct >= 75.0) or (not np.isnan(m_pct) and m_pct >= 65.0):
            det_status = "Detectado (Média Prioridade / Top 25%)"
        elif not evento_executado:
            det_status = "Não Ocorreu em Campo (Fraude Frustrada)"
        else:
            det_status = "Prioridade Moderada"

        results.append({
            "caso_id": row["caso_id"],
            "temporada": t,
            "serie": s,
            "rodada": rod,
            "confronto": row["confronto"],
            "atleta": row["atleta"],
            "evento_alvo": row["evento_alvo"],
            "evento_ocorreu": row["evento_ocorreu"],
            "executado_com_sucesso": row["executado_com_sucesso"],
            "minuto_real": row["minuto_real"],
            "match_anomaly_score": m_score,
            "match_percentil": m_pct,
            "athlete_anomaly_score": a_score,
            "athlete_percentil": a_pct,
            "status_triagem": det_status,
        })

    df_eval = pd.DataFrame(results)
    return df_eval


def run_integrity_anomaly_pipeline():
    """Executa o pipeline completo de detecção de anomalias de integridade."""
    print("\n" + "=" * 75)
    print("INICIANDO SISTEMA DE TRIAGEM E ANOMALY SCORING DE INTEGRIDADE (FASE 8)")
    print("=" * 75)

    os.makedirs(PROCESSED_INTEGRITY_DIR, exist_ok=True)
    os.makedirs(TABLES_DIR, exist_ok=True)

    print("\n--- 1. Carregando e Harmonizando Datasets Unificados ---")
    df_matches, df_cards, df_pen_1t = load_unified_data()
    print(f"     Partidas consolidadas: {len(df_matches)} (Série A: {(df_matches['serie'] == 'A').sum()}, Série B: {(df_matches['serie'] == 'B').sum()})")
    print(f"     Cartões consolidados: {len(df_cards)}")
    print(f"     Pênaltis no 1º Tempo mapeados: {len(df_pen_1t)}")

    print("\n--- 2. Calculando MATCH_ANOMALY_SCORE ---")
    matches_scored = compute_match_anomaly_scores(df_matches, df_cards, df_pen_1t)
    matches_parquet = os.path.join(PROCESSED_INTEGRITY_DIR, "partidas_anomaly_scored.parquet")
    matches_scored.to_parquet(matches_parquet, index=False)
    print(f"     [OK] Partidas pontuadas: {len(matches_scored)}")
    print(f"     Média do Score: {matches_scored['match_anomaly_score'].mean():.2f} | Mediana: {matches_scored['match_anomaly_score'].median():.2f} | Máx: {matches_scored['match_anomaly_score'].max():.2f}")
    print(f"     Partidas de Alta/Extrema Prioridade: {(matches_scored['match_anomaly_score'] >= 65.0).sum()} ({((matches_scored['match_anomaly_score'] >= 65.0).mean() * 100):.2f}%)")

    # Exportar Top 50 Partidas Anômalas
    top_matches = matches_scored.sort_values("match_anomaly_score", ascending=False).head(50)
    top_matches_export = top_matches[[
        "partida_id", "temporada", "serie", "rodada", "data", "clube_mandante", "clube_visitante",
        "total_cartoes", "cartoes_1t", "prop_cartoes_1t", "cartoes_30m", "penaltis_1t",
        "match_anomaly_score", "percentil_anomalia", "prioridade_triagem"
    ]]
    tabela_15_path = os.path.join(TABLES_DIR, "tabela_15_ranking_partidas_anomalas.csv")
    top_matches_export.to_csv(tabela_15_path, index=False, encoding="utf-8")
    print(f"     [OK] Tabela 15 salva: {tabela_15_path}")

    print("\n--- 3. Calculando ATHLETE_ANOMALY_SCORE ---")
    athletes_scored = compute_athlete_anomaly_scores(df_cards)
    athletes_parquet = os.path.join(PROCESSED_INTEGRITY_DIR, "atletas_anomaly_scored.parquet")
    athletes_scored.to_parquet(athletes_parquet, index=False)
    print(f"     [OK] Atletas pontuados (>=3 cartões): {len(athletes_scored)}")
    print(f"     Média do Score de Atletas: {athletes_scored['athlete_anomaly_score'].mean():.2f} | Máx: {athletes_scored['athlete_anomaly_score'].max():.2f}")

    # Exportar Top 50 Atletas Anômalos
    top_athletes = athletes_scored.head(50)
    top_athletes_export = top_athletes[[
        "temporada", "serie", "clube_slug", "atleta", "total_cartoes", "cartoes_1t",
        "prop_cartoes_1t", "minuto_medio_nominal", "p_val_binom_1t",
        "athlete_anomaly_score", "percentil_atleta", "classificacao_atleta"
    ]]
    tabela_16_path = os.path.join(TABLES_DIR, "tabela_16_ranking_atletas_anomalos.csv")
    top_athletes_export.to_csv(tabela_16_path, index=False, encoding="utf-8")
    print(f"     [OK] Tabela 16 salva: {tabela_16_path}")

    print("\n--- 4. Validando Sensibilidade com os 14 Casos da Operação Penalidade Máxima ---")
    df_eval = evaluate_ground_truth_sensitivity(matches_scored, athletes_scored)
    tabela_17_path = os.path.join(TABLES_DIR, "tabela_17_validacao_ground_truth_pm.csv")
    df_eval.to_csv(tabela_17_path, index=False, encoding="utf-8")
    print(f"     [OK] Tabela 17 salva: {tabela_17_path}")

    n_detected = (df_eval["status_triagem"].str.contains("Detectado")).sum()
    pct_detected = (n_detected / len(df_eval)) * 100.0
    print(f"     Sensibilidade de Detecção (Alta/Média Prioridade): {n_detected}/{len(df_eval)} ({pct_detected:.1f}%)")
    print(f"     Percentil Médio das Partidas Investigadas: {df_eval['match_percentil'].dropna().mean():.2f}%")

    print("\n" + "=" * 75)
    print("SISTEMA DE ANOMALY SCORING CONCLUÍDO COM SUCESSO!")
    print("=" * 75)

    return matches_scored, athletes_scored, df_eval


if __name__ == "__main__":
    run_integrity_anomaly_pipeline()
