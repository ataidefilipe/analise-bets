"""
src/analysis/comparacao_reconciliacao_score.py
----------------------------------------------
Auditoria de impacto da reconciliação do MATCH_ANOMALY_SCORE (tarefas F1-01 e F1-02).

Decompõe a variação do índice em dois efeitos independentes e exporta o registro exigido
pela Definition of Done das duas tarefas:

  Efeito 1 — Correção de junção e harmonização da base (chave (serie, temporada, partida_id),
             janela temporal explícita da Série A e minuto de jogo corrido nas duas séries).
  Efeito 2 — Reconciliação da fórmula: remoção do subscore de exposição comercial (S_bet),
             redistribuição proporcional dos pesos, S_volume sem piso de 50 pontos,
             S_penalti em três faixas, p0 estimados na base e tiers por percentil.

Saídas:
  reports/tables/comparacao_f1_reconciliacao_migracao_tier.csv
  reports/tables/comparacao_f1_reconciliacao_ground_truth.csv
  reports/tables/comparacao_f1_reconciliacao_resumo.csv
"""

import os
import numpy as np
import pandas as pd
from scipy import stats

from src.models import anomaly_detection as ad
from src.models.anomaly_detection import (
    GROUND_TRUTH_PATH,
    PROCESSED_INTEGRITY_DIR,
    TABLES_DIR,
    TIER_PARTIDA_BASAL,
)

# Especificação ANTERIOR do índice, tal como estava implementada antes da F1-01/F1-02.
# Mantida aqui exclusivamente como contrafactual de auditoria — não é usada em produção.
LEGADO_P0_1T = 0.35
LEGADO_P0_30MIN = 0.18
LEGADO_LOG_MULT = 25.0
LEGADO_PESOS = {
    "score_tempo": 0.35,
    "score_precoce": 0.25,
    "score_volume": 0.20,
    "score_bet": 0.10,
    "score_penalti": 0.10,
}
LEGADO_TIERS_ABSOLUTOS = ((80.0, "Extrema Anomalia (Top Priority)"),
                          (65.0, "Alta Prioridade de Escrutínio"),
                          (50.0, "Média Prioridade"))


def _p_binom(k: pd.Series, n: pd.Series, p0: float) -> np.ndarray:
    """P(X >= k | n, p0), com p = 1,0 quando não há cartão."""
    out = np.ones(len(n))
    for i, (ki, ni) in enumerate(zip(k.values, n.values)):
        if ni > 0 and ki > 0:
            out[i] = stats.binomtest(int(ki), int(ni), p0, alternative="greater").pvalue
    return out


def calcular_score_legado(matches: pd.DataFrame) -> pd.DataFrame:
    """Reproduz o índice anterior sobre a base informada, para comparação controlada."""
    df = matches.copy()
    p1t = _p_binom(df["cartoes_1t"], df["total_cartoes"], LEGADO_P0_1T)
    p30 = _p_binom(df["cartoes_30m"], df["total_cartoes"], LEGADO_P0_30MIN)

    df["score_tempo"] = np.clip(-LEGADO_LOG_MULT * np.log10(p1t + 1e-5), 0.0, 100.0)
    df["score_precoce"] = np.clip(-LEGADO_LOG_MULT * np.log10(p30 + 1e-5), 0.0, 100.0)
    df["score_volume"] = np.clip(50.0 + 20.0 * df["z_cartoes"], 0.0, 100.0)
    df["score_bet"] = np.clip(df["exposure_total_partida"] * 100.0, 0.0, 100.0)
    df["score_penalti"] = np.where(df["penaltis_1t"] > 0, 100.0, 0.0)

    df["score_legado"] = sum(peso * df[col] for col, peso in LEGADO_PESOS.items()).round(2)
    df["percentil_legado"] = (df["score_legado"].rank(pct=True) * 100.0).round(2)

    conditions = [df["score_legado"] >= corte for corte, _ in LEGADO_TIERS_ABSOLUTOS]
    choices = [rotulo for _, rotulo in LEGADO_TIERS_ABSOLUTOS]
    df["tier_legado"] = np.select(conditions, choices, default="Típico / Baixa Prioridade")
    return df


def calcular_score_atleta_legado() -> pd.DataFrame:
    """
    Recalcula o ATHLETE_ANOMALY_SCORE com a semantica de minuto anterior a harmonizacao
    (`minuto_nominal`), em que o 2o tempo da Serie B era registrado como minuto DENTRO do
    tempo. Isola o efeito da harmonizacao sobre o escore de atleta.
    """
    col_original = ad.MINUTO_PARTIDA_COL
    try:
        ad.MINUTO_PARTIDA_COL = "minuto_nominal"
        _, df_cards, _ = ad.load_unified_data()
        legado = ad.compute_athlete_anomaly_scores(df_cards)
    finally:
        ad.MINUTO_PARTIDA_COL = col_original

    return legado[["temporada", "serie", "atleta_slug", "atleta", "minuto_medio_partida",
                   "athlete_anomaly_score", "percentil_atleta"]].rename(columns={
        "minuto_medio_partida": "minuto_medio_anterior",
        "athlete_anomaly_score": "score_atleta_anterior",
        "percentil_atleta": "percentil_atleta_anterior",
    })


def comparar_atletas_ground_truth() -> pd.DataFrame:
    """Efeito da harmonizacao de minuto sobre os atletas dos 14 casos conhecidos."""
    novo = pd.read_parquet(os.path.join(PROCESSED_INTEGRITY_DIR, "atletas_anomaly_scored.parquet"))
    legado = calcular_score_atleta_legado()
    df_pm = pd.read_parquet(GROUND_TRUTH_PATH)

    alias = {"mateusinho": "mateus_da_silva_duarte", "moraes_jr": "moraes", "moraes": "moraes"}
    linhas = []
    for slug in df_pm["atleta_slug"].unique():
        busca = alias.get(slug, slug).split("_")[0]
        temporadas = df_pm.loc[df_pm["atleta_slug"] == slug, "temporada"].unique()
        alvo = novo[(novo["temporada"].isin(temporadas)) &
                    (novo["atleta_slug"].str.contains(busca, case=False, na=False))]
        if alvo.empty:
            continue
        linha_novo = alvo.iloc[0]
        par = legado[(legado["temporada"] == linha_novo["temporada"]) &
                     (legado["atleta_slug"] == linha_novo["atleta_slug"])]
        if par.empty:
            continue
        linha_legado = par.iloc[0]
        linhas.append({
            "atleta": linha_novo["atleta"],
            "serie": linha_novo["serie"],
            "temporada": int(linha_novo["temporada"]),
            "minuto_medio_anterior": linha_legado["minuto_medio_anterior"],
            "minuto_medio_harmonizado": linha_novo["minuto_medio_partida"],
            "score_anterior": linha_legado["score_atleta_anterior"],
            "percentil_anterior": linha_legado["percentil_atleta_anterior"],
            "score_novo": linha_novo["athlete_anomaly_score"],
            "percentil_novo": linha_novo["percentil_atleta"],
        })
    df = pd.DataFrame(linhas).sort_values(["serie", "percentil_novo"], ascending=[True, False])
    df["delta_percentil"] = (df["percentil_novo"] - df["percentil_anterior"]).round(2)
    return df


def executar_comparacao() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    novo = pd.read_parquet(os.path.join(PROCESSED_INTEGRITY_DIR, "partidas_anomaly_scored.parquet"))
    legado = calcular_score_legado(novo)

    # --- 1. Migração de tier -------------------------------------------------------------
    migracao = (
        pd.crosstab(legado["tier_legado"], novo["prioridade_triagem"])
        .rename_axis(index="tier_anterior", columns="tier_novo")
        .reset_index()
    )

    # --- 2. Estatísticas de deslocamento -------------------------------------------------
    rho = legado["score_legado"].corr(novo["match_anomaly_score"], method="spearman")
    resumo = pd.DataFrame([
        {"metrica": "partidas_na_base", "anterior": len(legado), "novo": len(novo)},
        {"metrica": "score_medio", "anterior": round(legado["score_legado"].mean(), 2),
         "novo": round(novo["match_anomaly_score"].mean(), 2)},
        {"metrica": "score_maximo", "anterior": round(legado["score_legado"].max(), 2),
         "novo": round(novo["match_anomaly_score"].max(), 2)},
        {"metrica": "partidas_tier_prioritario", "anterior": int((legado["tier_legado"] != "Típico / Baixa Prioridade").sum()),
         "novo": int((novo["prioridade_triagem"] != TIER_PARTIDA_BASAL).sum())},
        {"metrica": "correlacao_spearman_dos_rankings", "anterior": np.nan, "novo": round(float(rho), 4)},
        {"metrica": "partidas_que_mudam_de_tier",
         "anterior": np.nan,
         "novo": int((legado["tier_legado"] != novo["prioridade_triagem"]).sum())},
    ])

    # --- 3. Efeito nos 14 casos do ground truth ------------------------------------------
    df_pm = pd.read_parquet(GROUND_TRUTH_PATH)
    linhas = []
    for _, caso in df_pm.iterrows():
        mand = caso["clube_mandante"].lower().replace(" ", "_").replace("-", "_")
        filtro = (
            (novo["serie"] == caso["serie"]) &
            (novo["temporada"] == caso["temporada"]) &
            (novo["rodada"] == caso["rodada"]) &
            (novo["clube_mandante_slug"].str.contains(mand[:5], case=False, na=False))
        )
        if not filtro.any():
            continue
        idx = novo[filtro].index[0]
        linhas.append({
            "caso_id": caso["caso_id"],
            "serie": caso["serie"],
            "confronto": caso["confronto"],
            "atleta": caso["atleta"],
            "cartoes_partida": int(novo.loc[idx, "total_cartoes"]),
            "score_anterior": legado.loc[idx, "score_legado"],
            "percentil_anterior": legado.loc[idx, "percentil_legado"],
            "tier_anterior": legado.loc[idx, "tier_legado"],
            "score_novo": novo.loc[idx, "match_anomaly_score"],
            "percentil_novo": novo.loc[idx, "percentil_anomalia"],
            "tier_novo": novo.loc[idx, "prioridade_triagem"],
        })
    ground_truth = pd.DataFrame(linhas)
    ground_truth["mudou_de_tier"] = ground_truth["tier_anterior"] != ground_truth["tier_novo"]

    atletas = comparar_atletas_ground_truth()

    os.makedirs(TABLES_DIR, exist_ok=True)
    atletas.to_csv(os.path.join(TABLES_DIR, "comparacao_f1_reconciliacao_atletas_gt.csv"), index=False, encoding="utf-8")
    migracao.to_csv(os.path.join(TABLES_DIR, "comparacao_f1_reconciliacao_migracao_tier.csv"), index=False, encoding="utf-8")
    ground_truth.to_csv(os.path.join(TABLES_DIR, "comparacao_f1_reconciliacao_ground_truth.csv"), index=False, encoding="utf-8")
    resumo.to_csv(os.path.join(TABLES_DIR, "comparacao_f1_reconciliacao_resumo.csv"), index=False, encoding="utf-8")

    return migracao, ground_truth, resumo, atletas


if __name__ == "__main__":
    mig, gt, res, atl = executar_comparacao()
    print("\n=== RESUMO ===")
    print(res.to_string(index=False))
    print("\n=== MIGRACAO DE TIER (linha = anterior, coluna = novo) ===")
    print(mig.to_string(index=False))
    print("\n=== GROUND TRUTH (14 casos) ===")
    print(gt.to_string(index=False))
    print("\n=== GROUND TRUTH - ATLETAS (efeito da harmonizacao de minuto) ===")
    print(atl.to_string(index=False))
