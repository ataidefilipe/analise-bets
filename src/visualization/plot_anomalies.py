"""
src/visualization/plot_anomalies.py
-----------------------------------
Gera gráficos analíticos em alta resolução para o sistema de triagem e detecção de anomalias (Fase 8):
1. 01_distribuicao_anomaly_scores.png: Distribuições de scores de partidas e atletas com percentis.
2. 02_dispersao_tempo_vs_volume.png: Dispersão bidimensional de cartões no 1T vs. volume total.
3. 03_validacao_sensibilidade_ground_truth.png: Ranking de sensibilidade dos 14 casos reais da Penalidade Máxima.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

FIGURES_DIR = os.path.join("reports", "figures", "integrity")
TABLES_DIR = os.path.join("reports", "tables")
INTEGRITY_DIR = os.path.join("data", "processed", "integrity")


def plot_score_distributions():
    """Gera histogramas e densidades comparando as distribuições populacionais com os casos investigados."""
    os.makedirs(FIGURES_DIR, exist_ok=True)

    matches = pd.read_parquet(os.path.join(INTEGRITY_DIR, "partidas_anomaly_scored.parquet"))
    athletes = pd.read_parquet(os.path.join(INTEGRITY_DIR, "atletas_anomaly_scored.parquet"))
    df_eval = pd.read_csv(os.path.join(TABLES_DIR, "tabela_17_validacao_ground_truth_pm.csv"))

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    plt.subplots_adjust(wspace=0.25)

    # Painel A: Partidas
    ax1 = axes[0]
    sns.histplot(matches["match_anomaly_score"], bins=40, kde=True, color="#1f77b4", ax=ax1, stat="density", alpha=0.5)

    p75_m = matches["match_anomaly_score"].quantile(0.75)
    p90_m = matches["match_anomaly_score"].quantile(0.90)
    p99_m = matches["match_anomaly_score"].quantile(0.99)

    ax1.axvline(p75_m, color="#ff7f0e", linestyle="--", linewidth=1.5, label=f"P75 = {p75_m:.1f}")
    ax1.axvline(p90_m, color="#d62728", linestyle="--", linewidth=1.5, label=f"P90 = {p90_m:.1f}")
    ax1.axvline(p99_m, color="#7b1fa2", linestyle=":", linewidth=2, label=f"P99 = {p99_m:.1f}")

    # Plotar os pontos dos casos da Penalidade Máxima
    pm_m_scores = df_eval["match_anomaly_score"].dropna().values
    ax1.scatter(pm_m_scores, [0.005] * len(pm_m_scores), color="#d62728", s=60, zorder=5, edgecolor="black", label="Casos Penalidade Máxima")

    ax1.set_title("Distribuição do MATCH_ANOMALY_SCORE (N = 4.559 partidas)\nSérie A (2015–2024) e Série B (2022–2023)", fontsize=12, fontweight="bold", pad=12)
    ax1.set_xlabel("Match Anomaly Score [0, 100]", fontsize=11)
    ax1.set_ylabel("Densidade", fontsize=11)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper right", fontsize=9)

    # Painel B: Atletas
    ax2 = axes[1]
    sns.histplot(athletes["athlete_anomaly_score"], bins=40, kde=True, color="#2ca02c", ax=ax2, stat="density", alpha=0.5)

    p75_a = athletes["athlete_anomaly_score"].quantile(0.75)
    p90_a = athletes["athlete_anomaly_score"].quantile(0.90)
    p99_a = athletes["athlete_anomaly_score"].quantile(0.99)

    ax2.axvline(p75_a, color="#ff7f0e", linestyle="--", linewidth=1.5, label=f"P75 = {p75_a:.1f}")
    ax2.axvline(p90_a, color="#d62728", linestyle="--", linewidth=1.5, label=f"P90 = {p90_a:.1f} (Threshold Alta Prioridade)")
    ax2.axvline(p99_a, color="#7b1fa2", linestyle=":", linewidth=2, label=f"P99 = {p99_a:.1f}")

    # Plotar atletas investigados
    pm_athletes_data = df_eval[["atleta", "athlete_anomaly_score"]].dropna().drop_duplicates()
    for _, r in pm_athletes_data.iterrows():
        ax2.scatter(r["athlete_anomaly_score"], 0.006, color="#d62728", s=70, zorder=5, edgecolor="black")
        if r["atleta"] in ["Nino Paraiba", "Gabriel Tota", "Paulo Miranda"]:
            ax2.annotate(
                r["atleta"].split()[0],
                (r["athlete_anomaly_score"], 0.006),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                fontsize=8,
                weight="bold",
                color="#8b0000"
            )

    ax2.set_title("Distribuição do ATHLETE_ANOMALY_SCORE (N = 3.586 atletas-temporada)\nAtletas com ≥ 3 cartões na edição", fontsize=12, fontweight="bold", pad=12)
    ax2.set_xlabel("Athlete Anomaly Score [0, 100]", fontsize=11)
    ax2.set_ylabel("Densidade", fontsize=11)
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="upper right", fontsize=9)

    plt.suptitle("Distribuição Empírica dos Anomaly Scores e Posicionamento dos Casos Reais", fontsize=14, fontweight="bold", y=1.02)
    output_path = os.path.join(FIGURES_DIR, "01_distribuicao_anomaly_scores.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Figura salva: {output_path}")


def plot_scatter_time_vs_volume():
    """Gera dispersão bidimensional de proporção de cartões no 1T vs volume total de cartões."""
    os.makedirs(FIGURES_DIR, exist_ok=True)
    matches = pd.read_parquet(os.path.join(INTEGRITY_DIR, "partidas_anomaly_scored.parquet"))
    df_eval = pd.read_csv(os.path.join(TABLES_DIR, "tabela_17_validacao_ground_truth_pm.csv"))

    fig, ax = plt.subplots(figsize=(12, 7))

    # Partidas normais (jitter para visualização de pontos sobrepostos)
    jitter_x = np.random.normal(0, 0.15, size=len(matches))
    jitter_y = np.random.normal(0, 0.015, size=len(matches))

    scatter = ax.scatter(
        matches["total_cartoes"] + jitter_x,
        matches["prop_cartoes_1t"] + jitter_y,
        c=matches["match_anomaly_score"],
        cmap="viridis",
        alpha=0.45,
        s=25,
        edgecolor="none",
        label="Partidas Regulares (Séries A e B)"
    )

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Match Anomaly Score [0, 100]", fontsize=10)

    # Linha basal da liga (35% no 1T)
    ax.axhline(0.35, color="black", linestyle="--", linewidth=1.5, label="Média Basal da Liga (35% no 1T)")

    # Casos reais da Penalidade Máxima
    pm_cases = matches[matches["partida_id"].isin(df_eval["match_percentil"].dropna().index)]
    # Usar partidas mapeadas no df_eval
    df_eval_valid = df_eval[df_eval["match_percentil"].notnull()]
    for _, r in df_eval_valid.iterrows():
        # Encontrar partida correspondente
        m_row = matches[
            (matches["temporada"] == r["temporada"]) &
            (matches["serie"] == r["serie"]) &
            (matches["rodada"] == r["rodada"])
        ]
        if len(m_row) > 0:
            m = m_row.iloc[0]
            ax.scatter(m["total_cartoes"], m["prop_cartoes_1t"], color="#ff0000", s=130, edgecolor="black", linewidth=1.5, zorder=6)
            ax.annotate(
                f"{r['atleta'].split()[0]}\n(R{r['rodada']})",
                (m["total_cartoes"], m["prop_cartoes_1t"]),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                fontsize=8,
                weight="bold",
                color="#b71c1c"
            )

    # Destacar quadrante crítico
    ax.fill_between([8, 18], 0.60, 1.05, color="#ffcdd2", alpha=0.35, label="Zona Crítica de Anomalia (Alto Volume + Alto 1T)")

    ax.set_title("Mapeamento Bidimensional de Integridade: Concentração no 1º Tempo vs. Total de Cartões\nEvidenciando os Casos Investigados da Operação Penalidade Máxima", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Total de Cartões na Partida", fontsize=11)
    ax.set_ylabel("Proporção de Cartões no 1º Tempo (1T / Total)", fontsize=11)
    ax.set_ylim(-0.05, 1.08)
    ax.set_xlim(-0.5, 18.5)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="lower left", fontsize=9)

    output_path = os.path.join(FIGURES_DIR, "02_dispersao_tempo_vs_volume.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Figura salva: {output_path}")


def plot_ground_truth_sensitivity():
    """Gera gráfico de barras horizontais exibindo o percentil de detecção de cada um dos 14 casos reais."""
    os.makedirs(FIGURES_DIR, exist_ok=True)
    df_eval = pd.read_csv(os.path.join(TABLES_DIR, "tabela_17_validacao_ground_truth_pm.csv"))

    # Usar o maior percentil entre atleta e partida como métrica de triagem combinada
    df_eval["max_percentil"] = df_eval[["athlete_percentil", "match_percentil"]].max(axis=1)
    df_eval["label"] = df_eval.apply(
        lambda r: f"{r['caso_id']}: {r['atleta']} ({r['confronto']}, R{r['rodada']})",
        axis=1
    )

    plot_df = df_eval.sort_values("max_percentil", ascending=True).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(13, 8))

    y_pos = np.arange(len(plot_df))
    colors = [
        "#d62728" if p >= 90.0 else ("#ff7f0e" if p >= 75.0 else "#7f7f7f")
        for p in plot_df["max_percentil"]
    ]

    bars = ax.barh(y_pos, plot_df["max_percentil"], color=colors, edgecolor="black", linewidth=1.1, alpha=0.85)

    ax.axvline(90.0, color="#d62728", linestyle="--", linewidth=1.5, label="Linha de Corte: Top 10% (Alta Prioridade)")
    ax.axvline(75.0, color="#ff7f0e", linestyle=":", linewidth=1.5, label="Linha de Corte: Top 25% (Média Prioridade)")

    for i, b in enumerate(bars):
        val = plot_df.loc[i, "max_percentil"]
        status = plot_df.loc[i, "status_triagem"]
        ax.text(
            val + 1.0, b.get_y() + b.get_height() / 2.0,
            f"{val:.1f}% ({status})",
            va="center", fontsize=9, color="#222222", weight="bold" if val >= 90.0 else "normal"
        )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(plot_df["label"], fontsize=10)
    ax.set_xlabel("Percentil Máximo de Anomalia na Liga (%)", fontsize=11)
    ax.set_xlim(0, 115)
    ax.set_title("Sensibilidade da Triagem Algorítmica nos 14 Casos da Operação Penalidade Máxima\nClassificação Hierárquica por Percentil na Distribuição Populacional", fontsize=12, fontweight="bold", pad=12)
    ax.grid(True, linestyle="--", alpha=0.4, axis="x")
    ax.legend(loc="lower right", fontsize=9)

    output_path = os.path.join(FIGURES_DIR, "03_validacao_sensibilidade_ground_truth.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Figura salva: {output_path}")


def generate_all_integrity_plots():
    print("\n--- Gerando Figuras de Integridade e Anomalias em Alta Resolução ---")
    plot_score_distributions()
    plot_scatter_time_vs_volume()
    plot_ground_truth_sensitivity()
    print("--- Figuras de Integridade Geradas com Sucesso! ---")


if __name__ == "__main__":
    generate_all_integrity_plots()
