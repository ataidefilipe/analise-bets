"""
src/visualization/plot_econometrics.py
--------------------------------------
Gera gráficos analíticos em alta resolução para a modelagem econométrica (Fase 7):
1. 01_event_study_cartoes_e_taxa.png: Estudo de eventos dinâmico com testes de tendências paralelas.
2. 02_forest_plot_coeficientes_twfe.png: Forest plot dos coeficientes TWFE com IC 95%.
3. 03_dose_resposta_marginal.png: Comparação marginal de dose-resposta nas partidas.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

FIGURES_DIR = os.path.join("reports", "figures", "econometrics")
TABLES_DIR = os.path.join("reports", "tables")


def plot_event_study():
    """Gera gráfico duplo de Estudo de Eventos para Cartões Totais e Taxa de Conversão."""
    os.makedirs(FIGURES_DIR, exist_ok=True)
    df_es = pd.read_csv(os.path.join(TABLES_DIR, "tabela_12_did_event_study.csv"))

    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharex=True)
    plt.subplots_adjust(wspace=0.25)

    outcomes = [
        ("cartoes_totais", "Cartões Totais por Equipe", axes[0], "#1f77b4", "F = 2.430 (p = 0.1037)"),
        ("taxa_conversao", "Taxa de Conversão (Cartão / Falta)", axes[1], "#d62728", "F = 0.366 (p = 0.6961)"),
    ]

    for dep_code, title, ax, color, f_label in outcomes:
        sub = df_es[df_es["dep_var_code"] == dep_code].sort_values("event_time")

        # Inserir o ponto de referência omitido (e = -1, coef = 0, SE = 0)
        ref_row = pd.DataFrame([{
            "event_time": -1,
            "coeficiente": 0.0,
            "std_err": 0.0,
            "ci_95_inferior": 0.0,
            "ci_95_superior": 0.0,
            "p_valor": 1.0,
        }])
        plot_data = pd.concat([sub, ref_row], ignore_index=True).sort_values("event_time")

        # Plotar linha e pontos
        ax.axhline(0, color="gray", linestyle="--", linewidth=1.2, alpha=0.8)
        ax.axvline(-1, color="black", linestyle=":", linewidth=1.5, label="Ano Ref. (e = -1, Pré-Adoção)")

        ax.fill_between(
            plot_data["event_time"],
            plot_data["ci_95_inferior"],
            plot_data["ci_95_superior"],
            color=color,
            alpha=0.18,
            label="Intervalo de Confiança 95%"
        )
        ax.plot(plot_data["event_time"], plot_data["coeficiente"], color=color, marker="o", markersize=7, linewidth=2.2, label="Coeficiente Estimado")

        # Anotações dos pontos
        for _, r in plot_data.iterrows():
            if r["event_time"] != -1:
                sig = "***" if r["p_valor"] < 0.001 else ("**" if r["p_valor"] < 0.01 else ("*" if r["p_valor"] < 0.05 else ("+" if r["p_valor"] < 0.10 else "")))
                offset = 0.03 if r["coeficiente"] >= 0 else -0.04
                ax.annotate(
                    f"{r['coeficiente']:+.2f}{sig}",
                    (r["event_time"], r["coeficiente"]),
                    textcoords="offset points",
                    xytext=(0, 8 if r["coeficiente"] >= 0 else -14),
                    ha="center",
                    fontsize=9,
                    weight="bold" if sig else "normal",
                    color=color
                )

        ax.set_title(f"Adoção Escalonada: {title}\nTeste Tendências Paralelas: {f_label}", fontsize=12, fontweight="bold", pad=12)
        ax.set_xlabel("Anos Relativos à Adoção de Bet (e = 0: Ano de Estreia)", fontsize=11)
        ax.set_ylabel("Impacto Marginal no Outcome", fontsize=11)
        ax.set_xticks([-3, -2, -1, 0, 1, 2, 3, 4])
        ax.set_xticklabels(["≤ -3", "-2", "-1\n(Base)", "0\n(Adotou)", "+1", "+2", "+3", "≥ +4"], fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="upper left", fontsize=9)

    plt.suptitle("Estudo de Eventos Dinâmico (Event Study) — Efeito Causal da Adoção de Bets", fontsize=14, fontweight="bold", y=1.02)
    output_path = os.path.join(FIGURES_DIR, "01_event_study_cartoes_e_taxa.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Figura salva: {output_path}")


def plot_forest_twfe():
    """Gera Forest Plot comparativo dos coeficientes de exposição em TWFE."""
    os.makedirs(FIGURES_DIR, exist_ok=True)
    df_twfe = pd.read_csv(os.path.join(TABLES_DIR, "tabela_11_regressoes_twfe.csv"))

    # Ordenar por relevância
    plot_df = df_twfe.iloc[::-1].copy().reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    y_pos = np.arange(len(plot_df))
    coefs = plot_df["coef_bet_exposure"]
    errors = plot_df["std_err_bet_exposure"] * 1.96

    colors = [
        "#2ca02c" if p < 0.05 else ("#ff7f0e" if p < 0.10 else "#7f7f7f")
        for p in plot_df["p_val_bet_exposure"]
    ]

    ax.axvline(0, color="black", linestyle="--", linewidth=1.2, alpha=0.7)

    for i in range(len(plot_df)):
        ax.errorbar(
            coefs[i], y_pos[i], xerr=errors[i], fmt="o", color=colors[i],
            ecolor=colors[i], elinewidth=2, capsize=4, markersize=8
        )
        sig = "***" if plot_df.loc[i, "p_val_bet_exposure"] < 0.01 else ("**" if plot_df.loc[i, "p_val_bet_exposure"] < 0.05 else ("*" if plot_df.loc[i, "p_val_bet_exposure"] < 0.10 else " (n.s.)"))
        ax.text(
            coefs[i] + errors[i] + 0.02, y_pos[i],
            f"β = {coefs[i]:+.4f} (p = {plot_df.loc[i, 'p_val_bet_exposure']:.4f}){sig}",
            va="center", fontsize=9, color="#222222"
        )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(plot_df["variavel_dependente"], fontsize=11)
    ax.set_xlabel("Coeficiente Marginal do BET_EXPOSURE do Clube (IC 95%)", fontsize=11)
    ax.set_title("Efeito Fixo Bidirecional (TWFE) do Patrocínio de Bets por Variável\nControlando por Clube FE, Temporada FE, Mando, Saldo de Gols e Derbies", fontsize=12, fontweight="bold", pad=12)
    ax.grid(True, linestyle="--", alpha=0.5, axis="x")

    # Legenda customizada
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#2ca02c', markersize=8, label='Significativo a 5% (p < 0,05)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff7f0e', markersize=8, label='Marginalmente Significativo (p < 0,10)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#7f7f7f', markersize=8, label='Não Significativo (p ≥ 0,10)'),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

    output_path = os.path.join(FIGURES_DIR, "02_forest_plot_coeficientes_twfe.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Figura salva: {output_path}")


def plot_dose_response():
    """Gera gráfico comparativo de Dose-Resposta nas partidas contemporâneas."""
    os.makedirs(FIGURES_DIR, exist_ok=True)
    df_panel = pd.read_parquet(os.path.join("data", "processed", "panel", "painel_clube_partida.parquet"))
    matches = df_panel[df_panel["is_mandante"] == 1].copy()

    # Partidas por categoria
    cat_order = ["Nenhuma", "Parcial (1 clube)", "Total (2 clubes)"]
    metrics = [
        ("cartoes_totais", "Cartões Médios por Jogo", "#1f77b4"),
        ("taxa_conversao", "Taxa de Conversão (Cartão/Falta)", "#ff7f0e"),
        ("penalti_na_partida", "Taxa de Jogos com Pênalti", "#2ca02c"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    plt.subplots_adjust(wspace=0.28)

    for i, (m_col, m_label, color) in enumerate(metrics):
        ax = axes[i]
        valid_m = matches.dropna(subset=[m_col])
        means = valid_m.groupby("categoria_exposicao_partida")[m_col].mean().reindex(cat_order)
        stds = valid_m.groupby("categoria_exposicao_partida")[m_col].sem().reindex(cat_order)
        counts = valid_m.groupby("categoria_exposicao_partida").size().reindex(cat_order)

        bars = ax.bar(cat_order, means, yerr=stds, capsize=5, color=color, alpha=0.85, edgecolor="black", linewidth=1.1)

        for j, b in enumerate(bars):
            val = means.iloc[j]
            n = counts.iloc[j]
            ax.text(
                b.get_x() + b.get_width() / 2.0,
                val / 2.0,
                f"{val:.3f}\n(N={n})",
                ha="center", va="center", color="white", weight="bold", fontsize=10
            )

        ax.set_title(m_label, fontsize=12, fontweight="bold", pad=10)
        ax.set_ylabel("Média (com Erro-Padrão)", fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.4, axis="y")
        ax.tick_params(axis="x", rotation=10)

    plt.suptitle("Efeito Dose-Resposta por Grau de Exposição da Partida (Série A 2015–2024)", fontsize=14, fontweight="bold", y=1.03)
    output_path = os.path.join(FIGURES_DIR, "03_dose_resposta_marginal.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Figura salva: {output_path}")


def generate_all_econometric_plots():
    print("\n--- Gerando Figuras Econométricas em Alta Resolução ---")
    plot_event_study()
    plot_forest_twfe()
    plot_dose_response()
    print("--- Figuras Econométricas Geradas com Sucesso! ---")


if __name__ == "__main__":
    generate_all_econometric_plots()
