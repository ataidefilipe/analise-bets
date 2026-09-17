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

# =============================================================================
# ESPECIFICAÇÃO CANÔNICA DO ÍNDICE DE ANOMALIA (tarefas F1-01 e F1-02)
# -----------------------------------------------------------------------------
# Este bloco é a fonte única da verdade da fórmula. Ele deve espelhar exatamente o
# que está publicado em reports/analysis/07_sistema_triagem_anomalias_integridade.md.
# Qualquer alteração aqui obriga a atualizar aquele relatório e o teste
# tests/test_anomaly_detection.py, que fixa estes valores.
# =============================================================================

# Recorte temporal da base de referência publicada (4.559 partidas). Explícito para que a
# extensão da base (tarefas F2-02 e F2-03) seja uma decisão deliberada, e não um efeito
# colateral de uma reingestão.
SERIE_A_TEMPORADA_MIN = 2015
SERIE_A_TEMPORADA_MAX = 2024
SERIE_B_TEMPORADAS = (2022, 2023)

# Chave de junção entre partidas, cartões e gols. A `partida_id` da Série B reinicia em 1 a
# cada temporada (1-380 em 2022 e de novo em 2023), de modo que (serie, partida_id) NÃO
# identifica uma partida: a temporada é parte obrigatória da chave.
CHAVE_PARTIDA = ["serie", "temporada", "partida_id"]

# Probabilidades basais estimadas na própria base harmonizada (24.220 cartões das Séries A e
# B no recorte acima), usando o minuto de jogo corrido (ver MINUTO_PARTIDA_COL).
P0_CARTAO_1T = 0.353
P0_CARTAO_30MIN = 0.156
LIMITE_CARTAO_PRECOCE_MIN = 30

# Coluna de minuto harmonizada entre as duas séries. A Série A registra o minuto nominal já
# em escala de jogo (0-90); a Série B, herdada das súmulas da CBF, registra o minuto DENTRO
# do tempo (1-45), de modo que um cartão aos 20' do 2º tempo aparecia como minuto 20. Só o
# `minuto_continuo` tem a mesma semântica nas duas séries.
MINUTO_PARTIDA_COL = "minuto_continuo"

# Conversão de p-valor em pontos: p = 0,01 -> 50 pontos; p <= 0,0001 -> 100 pontos.
LOG_P_MULTIPLICADOR = 25.0
LOG_P_EPSILON = 1e-5

# Volume de cartões: desvio padronizado dentro de temporada x série.
# Z = 0 (partida média) -> 0 pontos; Z = +4 -> 100 pontos.
Z_VOLUME_MULTIPLICADOR = 25.0

# Pênaltis no 1º tempo: faixas (mínimo de pênaltis, pontos), da mais alta para a mais baixa.
PENALTI_1T_FAIXAS = ((2, 80.0), (1, 40.0))

# Pesos do índice composto de partida. A tarefa F1-02 removeu o subscore de exposição
# comercial a casas de apostas (S_bet) e redistribuiu o seu peso proporcionalmente entre os
# quatro subscores de campo, preservando a razão entre eles.
MATCH_SCORE_WEIGHTS = {
    "score_tempo": 0.39,
    "score_precoce": 0.28,
    "score_volume": 0.22,
    "score_penalti": 0.11,
}

ATHLETE_SCORE_WEIGHTS = {
    "score_atleta_tempo": 0.50,
    "score_atleta_taxa": 0.30,
    "score_atleta_minuto": 0.20,
}

# Colunas preservadas na base para estratificação e leitura de contexto e que, por decisão
# metodológica registrada na F1-02, NÃO podem compor nenhum escore de suspeição.
COLUNAS_CONTEXTO_NAO_COMPONENTE = ("exposure_total_partida", "exposure_clube_partida")

# Tiers de triagem por percentil empírico da própria distribuição. Limiares absolutos fixos
# (80/65/50) deixaram de discriminar quando o escore mudou de escala: a carga operacional
# passa a ser um parâmetro explícito, e não uma consequência acidental da fórmula.
TIERS_PARTIDA = (
    (99.0, "Extrema Anomalia (Top 1%)"),
    (95.0, "Alta Prioridade de Escrutínio (Top 5%)"),
    (90.0, "Média Prioridade (Top 10%)"),
)
TIER_PARTIDA_BASAL = "Típico / Baixa Prioridade"

TIERS_ATLETA = (
    (99.0, "Extrema Anomalia Temporal (Top 1%)"),
    (95.0, "Alta Concentração Precoce (Top 5%)"),
    (90.0, "Média Concentração (Top 10%)"),
)
TIER_ATLETA_BASAL = "Padrão Basal Normal"


def _score_log_p(p_values: pd.Series | np.ndarray) -> np.ndarray:
    """Converte p-valores em pontos [0, 100] na escala log decimal da especificação."""
    return np.clip(-LOG_P_MULTIPLICADOR * np.log10(np.asarray(p_values, dtype=float) + LOG_P_EPSILON), 0.0, 100.0)


def _aplicar_tiers(percentis: pd.Series, tiers: tuple, basal: str) -> np.ndarray:
    """Classifica em tiers a partir do percentil empírico do próprio escore."""
    conditions = [percentis >= corte for corte, _ in tiers]
    choices = [rotulo for _, rotulo in tiers]
    return np.select(conditions, choices, default=basal)


def load_unified_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Carrega e harmoniza partidas, cartões e gols das Séries A e B.

    O recorte temporal vem de SERIE_A_TEMPORADA_MIN e SERIE_B_TEMPORADAS: a base de
    referência publicada tem 4.559 partidas, e a inclusão de novas temporadas é uma decisão
    das tarefas F2-02 / F2-03, não um efeito colateral de reingestão.

    A coluna `minuto_partida` é o minuto de jogo corrido, comparável entre as duas séries
    (ver MINUTO_PARTIDA_COL).
    """
    # 1. Partidas Série A
    pa = pd.read_parquet(SERIE_A_PARTIDAS)
    pa = pa[pa["temporada"].between(SERIE_A_TEMPORADA_MIN, SERIE_A_TEMPORADA_MAX)].copy()
    pa["serie"] = "A"

    # Partidas Série B
    pb = pd.read_parquet(SERIE_B_PARTIDAS)
    pb = pb[pb["temporada"].isin(SERIE_B_TEMPORADAS)].copy()
    pb["exposure_total_partida"] = 0.50  # Média macro do período para Série B
    pb["exposure_clube_partida"] = 0.50
    pb["categoria_exposicao_partida"] = "Parcial (1 clube)"

    common_cols = [
        "partida_id", "temporada", "serie", "rodada", "data", "clube_mandante",
        "clube_mandante_slug", "clube_visitante", "clube_visitante_slug",
        "gols_mandante", "gols_visitante", "total_gols", "exposure_total_partida"
    ]
    df_matches = pd.concat([pa[common_cols], pb[common_cols]], ignore_index=True)

    # 2. Cartões Série A
    ca = pd.read_parquet(SERIE_A_CARTOES)
    ca = ca[ca["temporada"].between(SERIE_A_TEMPORADA_MIN, SERIE_A_TEMPORADA_MAX)].copy()
    ca["serie"] = "A"
    ca["categoria_infracao"] = "falta_temeraria"

    # Cartões Série B
    cb = pd.read_parquet(SERIE_B_CARTOES)
    cb = cb[cb["temporada"].isin(SERIE_B_TEMPORADAS)].copy()

    card_cols = [
        "partida_id", "temporada", "serie", "rodada", "clube", "clube_slug",
        "cartao", "atleta", "atleta_slug", "minuto_nominal", "minuto_continuo",
        "periodo", "categoria_infracao"
    ]
    df_cards = pd.concat([ca[card_cols], cb[card_cols]], ignore_index=True)
    df_cards["minuto_partida"] = df_cards[MINUTO_PARTIDA_COL].astype(float)

    # 3. Gols de Pênalti no 1T
    ga = pd.read_parquet(SERIE_A_GOLS)
    ga = ga[ga["temporada"].between(SERIE_A_TEMPORADA_MIN, SERIE_A_TEMPORADA_MAX)].copy()
    ga["serie"] = "A"

    gb = pd.read_parquet(SERIE_B_GOLS)
    gb = gb[gb["temporada"].isin(SERIE_B_TEMPORADAS)].copy()

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
    cards_agg = df_cards.groupby(CHAVE_PARTIDA).agg(
        total_cartoes=("cartao", "count"),
        cartoes_1t=("periodo", lambda s: (s == "1T").sum()),
        cartoes_30m=("minuto_partida", lambda s: (s <= LIMITE_CARTAO_PRECOCE_MIN).sum()),
        cartoes_reclamacao_cera=("categoria_infracao", lambda s: s.isin(["reclamacao", "cera_retardar", "conduta_antidesportiva"]).sum())
    ).reset_index()

    pen_counts = df_pen_1t.groupby(CHAVE_PARTIDA).size().rename("penaltis_1t").reset_index()

    matches = pd.merge(df_matches, cards_agg, on=CHAVE_PARTIDA, how="left")
    matches = pd.merge(matches, pen_counts, on=CHAVE_PARTIDA, how="left")

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

    # 1. Sub-score de Concentração Temporal no 1T (Binomial sob P0_CARTAO_1T)
    def calc_p_binom_1t(row):
        n = row["total_cartoes"]
        k = row["cartoes_1t"]
        if n == 0 or k == 0:
            return 1.0
        return float(stats.binomtest(k, n, P0_CARTAO_1T, alternative="greater").pvalue)

    matches["p_val_1t"] = matches.apply(calc_p_binom_1t, axis=1)
    matches["score_tempo"] = _score_log_p(matches["p_val_1t"])

    # 2. Sub-score de Cartões Precoces nos Primeiros 30' (Binomial sob P0_CARTAO_30MIN)
    def calc_p_binom_30m(row):
        n = row["total_cartoes"]
        k = row["cartoes_30m"]
        if n == 0 or k == 0:
            return 1.0
        return float(stats.binomtest(k, n, P0_CARTAO_30MIN, alternative="greater").pvalue)

    matches["p_val_30m"] = matches.apply(calc_p_binom_30m, axis=1)
    matches["score_precoce"] = _score_log_p(matches["p_val_30m"])

    # 3. Sub-score de Volumetria (z-score em relação ao ano e divisão).
    # A partida de volume médio (Z = 0) recebe 0 ponto: o subscore mede excesso, não nível.
    stats_season = matches.groupby(["temporada", "serie"])["total_cartoes"].agg(["mean", "std"]).reset_index()
    matches = matches.merge(stats_season, on=["temporada", "serie"], how="left")
    matches["z_cartoes"] = (matches["total_cartoes"] - matches["mean"]) / matches["std"]
    matches["score_volume"] = np.clip(Z_VOLUME_MULTIPLICADOR * matches["z_cartoes"], 0.0, 100.0)

    # 4. Sub-score de Pênalti no 1T (faixas de PENALTI_1T_FAIXAS).
    # NOTA (F1-02): não existe subscore de exposição comercial a casas de apostas. A coluna
    # `exposure_total_partida` permanece na base como CONTEXTO e variável de estratificação,
    # e não compõe o índice de suspeição.
    matches["score_penalti"] = 0.0
    for minimo, pontos in sorted(PENALTI_1T_FAIXAS, key=lambda f: f[0]):
        matches.loc[matches["penaltis_1t"] >= minimo, "score_penalti"] = pontos

    # 5. Índice Composto da Partida (MATCH_ANOMALY_SCORE)
    composto = sum(peso * matches[coluna] for coluna, peso in MATCH_SCORE_WEIGHTS.items())
    matches["match_anomaly_score"] = composto.round(2)

    # Percentil, Ranking e Prioridade de Escrutínio (tiers por percentil empírico)
    matches["ranking_geral"] = matches["match_anomaly_score"].rank(ascending=False, method="min").astype(int)
    matches["percentil_anomalia"] = (matches["match_anomaly_score"].rank(pct=True) * 100.0).round(2)
    matches["prioridade_triagem"] = _aplicar_tiers(
        matches["percentil_anomalia"], TIERS_PARTIDA, TIER_PARTIDA_BASAL
    )

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
        cartoes_30m=("minuto_partida", lambda s: (s <= LIMITE_CARTAO_PRECOCE_MIN).sum()),
        minuto_medio_partida=("minuto_partida", "mean")
    ).reset_index()

    # Considerar atletas com ao menos 3 cartões na temporada
    athlete_agg = athlete_agg[athlete_agg["total_cartoes"] >= 3].copy()

    athlete_agg["prop_cartoes_1t"] = (athlete_agg["cartoes_1t"] / athlete_agg["total_cartoes"]).round(4)
    athlete_agg["minuto_medio_partida"] = athlete_agg["minuto_medio_partida"].round(1)

    # Teste binomial individual
    def calc_athlete_p_binom(row):
        n = row["total_cartoes"]
        k = row["cartoes_1t"]
        return float(stats.binomtest(k, n, P0_CARTAO_1T, alternative="greater").pvalue)

    athlete_agg["p_val_binom_1t"] = athlete_agg.apply(calc_athlete_p_binom, axis=1)

    # Sub-scores
    athlete_agg["score_atleta_tempo"] = _score_log_p(athlete_agg["p_val_binom_1t"])
    athlete_agg["score_atleta_taxa"] = athlete_agg["prop_cartoes_1t"] * 100.0
    athlete_agg["score_atleta_minuto"] = np.clip((90.0 - athlete_agg["minuto_medio_partida"]) * 1.5, 0.0, 100.0)

    # Índice Composto do Atleta
    athlete_agg["athlete_anomaly_score"] = sum(
        peso * athlete_agg[coluna] for coluna, peso in ATHLETE_SCORE_WEIGHTS.items()
    ).round(2)

    athlete_agg["ranking_atleta"] = athlete_agg["athlete_anomaly_score"].rank(ascending=False, method="min").astype(int)
    athlete_agg["percentil_atleta"] = (athlete_agg["athlete_anomaly_score"].rank(pct=True) * 100.0).round(2)
    athlete_agg["classificacao_atleta"] = _aplicar_tiers(
        athlete_agg["percentil_atleta"], TIERS_ATLETA, TIER_ATLETA_BASAL
    )

    return athlete_agg.sort_values("athlete_anomaly_score", ascending=False).reset_index(drop=True)


def evaluate_ground_truth_sensitivity(matches: pd.DataFrame, athletes: pd.DataFrame,
                                      df_cards: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Afere a sensibilidade dos escores estatísticos contra os 14 casos da Operação Penalidade
    Máxima, usando o resolvedor de identidade explícito (`ground_truth_resolver`).

    A versão anterior casava os casos por correspondência parcial de nome e associava atletas
    errados; ver a auditoria em `reports/tables/auditoria_ground_truth_atletas.csv`.
    """
    from src.models.ground_truth_resolver import resolver_partidas, resolver_atletas

    df_pm = pd.read_parquet(GROUND_TRUTH_PATH)
    if df_cards is None:
        _, df_cards, _ = load_unified_data()

    res_partidas = resolver_partidas(matches, df_pm).set_index("caso_id")
    res_atletas = resolver_atletas(df_cards, athletes, df_pm).set_index("atleta_slug_ground_truth")

    results = []
    for _, row in df_pm.iterrows():
        rp = res_partidas.loc[row["caso_id"]]
        m_score = m_pct = m_prio = None
        if pd.notna(rp["partida_id"]):
            alvo = matches[(matches["serie"] == row["serie"]) &
                           (matches["temporada"] == row["temporada"]) &
                           (matches["partida_id"] == rp["partida_id"])]
            if len(alvo) > 0:
                m_score = float(alvo.iloc[0]["match_anomaly_score"])
                m_pct = float(alvo.iloc[0]["percentil_anomalia"])
                m_prio = str(alvo.iloc[0]["prioridade_triagem"])

        ra = res_atletas.loc[row["atleta_slug"]]
        a_score = a_pct = None
        status_atleta = ra["status_atleta"]
        if status_atleta == "resolvido":
            alvo = athletes[(athletes["serie"] == ra["serie"]) &
                            (athletes["temporada"] == ra["temporada"]) &
                            (athletes["atleta_slug"] == ra["atleta_slug_base"])]
            if len(alvo) > 0:
                a_score = float(alvo.iloc[0]["athlete_anomaly_score"])
                a_pct = float(alvo.iloc[0]["percentil_atleta"])

        evento_executado = bool(row["evento_ocorreu"]) and bool(row["executado_com_sucesso"])

        if (a_pct is not None and a_pct >= 90.0) or (m_pct is not None and m_pct >= 90.0):
            det_status = "Detectado (Alta Prioridade / Top 10%)"
        elif (a_pct is not None and a_pct >= 75.0) or (m_pct is not None and m_pct >= 75.0):
            det_status = "Detectado (Média Prioridade / Top 25%)"
        elif not evento_executado:
            det_status = "Não Ocorreu em Campo (Fraude Frustrada)"
        elif a_pct is None and m_pct is None:
            det_status = "Sem âncora na base (não avaliável)"
        else:
            det_status = "Prioridade Basal (não sinalizado)"

        results.append({
            "caso_id": row["caso_id"],
            "temporada": row["temporada"],
            "serie": row["serie"],
            "rodada": rp["rodada_utilizada"],
            "confronto": row["confronto"],
            "atleta": row["atleta"],
            "evento_alvo": row["evento_alvo"],
            "evento_ocorreu": row["evento_ocorreu"],
            "executado_com_sucesso": row["executado_com_sucesso"],
            "minuto_real": row["minuto_real"],
            "partida_id": rp["partida_id"],
            "status_partida": rp["status_partida"],
            "atleta_slug_base": ra["atleta_slug_base"],
            "status_atleta": status_atleta,
            "confianca_identidade": ra["confianca"],
            "match_anomaly_score": m_score,
            "match_percentil": m_pct,
            "prioridade_partida": m_prio,
            "athlete_anomaly_score": a_score,
            "athlete_percentil": a_pct,
            "status_triagem": det_status,
        })

    return pd.DataFrame(results)


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
    for tier in [rotulo for _, rotulo in TIERS_PARTIDA] + [TIER_PARTIDA_BASAL]:
        n_tier = (matches_scored["prioridade_triagem"] == tier).sum()
        print(f"     {tier}: {n_tier} ({n_tier / len(matches_scored) * 100:.2f}%)")

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
        "prop_cartoes_1t", "minuto_medio_partida", "p_val_binom_1t",
        "athlete_anomaly_score", "percentil_atleta", "classificacao_atleta"
    ]]
    tabela_16_path = os.path.join(TABLES_DIR, "tabela_16_ranking_atletas_anomalos.csv")
    top_athletes_export.to_csv(tabela_16_path, index=False, encoding="utf-8")
    print(f"     [OK] Tabela 16 salva: {tabela_16_path}")

    print("\n--- 4. Validando Sensibilidade com os 14 Casos da Operação Penalidade Máxima ---")
    df_eval = evaluate_ground_truth_sensitivity(matches_scored, athletes_scored, df_cards)
    tabela_17_path = os.path.join(TABLES_DIR, "tabela_17_validacao_ground_truth_pm.csv")
    df_eval.to_csv(tabela_17_path, index=False, encoding="utf-8")
    print(f"     [OK] Tabela 17 salva: {tabela_17_path}")

    n_detected = (df_eval["status_triagem"].str.startswith("Detectado")).sum()
    pct_detected = (n_detected / len(df_eval)) * 100.0
    print(f"     Sensibilidade de Detecção (Alta/Média Prioridade): {n_detected}/{len(df_eval)} ({pct_detected:.1f}%)")
    print(f"     Percentil Médio das Partidas Investigadas: {df_eval['match_percentil'].dropna().mean():.2f}%")

    print("\n" + "=" * 75)
    print("SISTEMA DE ANOMALY SCORING CONCLUÍDO COM SUCESSO!")
    print("=" * 75)

    return matches_scored, athletes_scored, df_eval


if __name__ == "__main__":
    run_integrity_anomaly_pipeline()
