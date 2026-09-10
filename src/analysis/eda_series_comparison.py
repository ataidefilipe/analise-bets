"""
src/analysis/eda_series_comparison.py
--------------------------------------
Análise Comparativa de Integridade e Disciplina: Série A vs. Série B (2022–2023)
e Contraste com os Casos Reais da Operação Penalidade Máxima.

Metodologia (.agent.md e docs/methodology.md):
- Comparação estatística formal (Teste t de Welch, Mann-Whitney U, Cohen's d)
- Análise de minutagem contínua (KDE e blocos de 15 minutos)
- Decomposição das categorias de infração (faltas de jogo vs. infrações disciplinares/cera)
- Contraste empírico da amostra de casos judiciais da Operação Penalidade Máxima contra a linha de base
"""

import json
import logging
from pathlib import Path
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

FIGURES_DIR = Path("reports/figures/series_comparison")
TABLES_DIR = Path("reports/tables")

def load_all_datasets():
    df_sa_p = pd.read_parquet("data/processed/serie_a/partidas.parquet")
    df_sa_c = pd.read_parquet("data/processed/serie_a/cartoes.parquet")
    df_sa_g = pd.read_parquet("data/processed/serie_a/gols.parquet")

    df_sb_p = pd.read_parquet("data/processed/serie_b/partidas.parquet")
    df_sb_c = pd.read_parquet("data/processed/serie_b/cartoes.parquet")
    df_sb_g = pd.read_parquet("data/processed/serie_b/gols.parquet")

    df_cases = pd.read_parquet("data/processed/integrity/casos_penalidade_maxima.parquet")
    return (df_sa_p, df_sa_c, df_sa_g), (df_sb_p, df_sb_c, df_sb_g), df_cases

def compute_series_comparison_metrics(sa_data, sb_data):
    df_sa_p, df_sa_c, df_sa_g = sa_data
    df_sb_p, df_sb_c, df_sb_g = sb_data

    # Filtrar temporadas coincidentes (2022 e 2023)
    c_sa = df_sa_c[df_sa_c["temporada"].isin([2022, 2023])].copy()
    c_sa["serie"] = "Série A"
    c_sb = df_sb_c[df_sb_c["temporada"].isin([2022, 2023])].copy()
    c_sb["serie"] = "Série B"

    p_sa = df_sa_p[df_sa_p["temporada"].isin([2022, 2023])].copy()
    p_sa["serie"] = "Série A"
    p_sb = df_sb_p[df_sb_p["temporada"].isin([2022, 2023])].copy()
    p_sb["serie"] = "Série B"

    # Cartões por partida
    cards_per_match_sa = c_sa.groupby(["temporada", "partida_id"])["cartao"].count().reset_index()
    cards_per_match_sa["serie"] = "Série A"
    cards_per_match_sb = c_sb.groupby(["temporada", "partida_id"])["cartao"].count().reset_index()
    cards_per_match_sb["serie"] = "Série B"

    cards_per_match = pd.concat([cards_per_match_sa, cards_per_match_sb], ignore_index=True)

    summary = cards_per_match.groupby(["serie", "temporada"])["cartao"].agg(
        partidas="count",
        media="mean",
        std="std",
        mediana="median",
        q25=lambda x: x.quantile(0.25),
        q75=lambda x: x.quantile(0.75)
    ).reset_index()

    return cards_per_match, summary, c_sa, c_sb

def run_hypothesis_tests(cards_per_match: pd.DataFrame):
    logger.info("Executando testes de hipótese comparativos Série A vs. Série B...")
    results = []

    for ano in [2022, 2023, "Ambos (2022-2023)"]:
        if ano == "Ambos (2022-2023)":
            sub = cards_per_match
        else:
            sub = cards_per_match[cards_per_match["temporada"] == ano]

        vals_a = sub[sub["serie"] == "Série A"]["cartao"].values
        vals_b = sub[sub["serie"] == "Série B"]["cartao"].values

        t_stat, t_pval = stats.ttest_ind(vals_a, vals_b, equal_var=False)
        u_stat, u_pval = stats.mannwhitneyu(vals_a, vals_b, alternative="two-sided")

        # Cohen's d
        s_pooled = np.sqrt(((len(vals_a)-1)*np.var(vals_a, ddof=1) + (len(vals_b)-1)*np.var(vals_b, ddof=1)) / (len(vals_a) + len(vals_b) - 2))
        cohen_d = (np.mean(vals_a) - np.mean(vals_b)) / s_pooled if s_pooled > 0 else 0

        results.append({
            "periodo": str(ano),
            "media_serie_a": np.mean(vals_a),
            "std_serie_a": np.std(vals_a, ddof=1),
            "media_serie_b": np.mean(vals_b),
            "std_serie_b": np.std(vals_b, ddof=1),
            "diff_absoluta": np.mean(vals_a) - np.mean(vals_b),
            "diff_percentual": (np.mean(vals_a) - np.mean(vals_b)) / np.mean(vals_b) * 100,
            "t_statistic": t_stat,
            "p_value_t": t_pval,
            "mann_whitney_u": u_stat,
            "p_value_u": u_pval,
            "cohens_d": cohen_d
        })

    return pd.DataFrame(results)

def analyze_infraction_types_serie_b(df_sb_c: pd.DataFrame):
    logger.info("Analisando tipologia textual das infrações na Série B...")
    counts = df_sb_c.groupby(["temporada", "categoria_infracao"])["cartao"].count().unstack(fill_value=0)
    pcts = (counts.div(counts.sum(axis=1), axis=0) * 100).round(2)
    return counts, pcts

def analyze_integrity_cases_contrast(c_sa, c_sb, df_cases):
    logger.info("Contrastando casos da Operação Penalidade Máxima com as partidas normais...")
    all_cards = pd.concat([
        c_sa[["partida_id", "temporada", "serie", "atleta", "atleta_slug", "minuto_continuo", "minuto_nominal", "periodo", "cartao"]],
        c_sb[["partida_id", "temporada", "serie", "atleta", "atleta_slug", "minuto_continuo", "minuto_nominal", "periodo", "cartao"]],
    ], ignore_index=True)

    # Identificar se o cartão pertence a um atleta em jogo investigado
    cases_executed = df_cases[df_cases["evento_ocorreu"]].copy()
    
    # Adicionar flag de caso investigado
    all_cards["investigado_operacao"] = False
    for _, r in cases_executed.iterrows():
        mask = (
            (all_cards["temporada"] == r["temporada"]) &
            (all_cards["serie"].str.contains(r["serie"])) &
            (all_cards["atleta_slug"] == r["atleta_slug"])
        )
        all_cards.loc[mask, "investigado_operacao"] = True

    # Métricas dos investigados vs normais
    cards_investigated = all_cards[all_cards["investigado_operacao"]]
    cards_normal = all_cards[~all_cards["investigado_operacao"]]

    pct_1t_investigated = (cards_investigated["periodo"] == "1T").mean() * 100
    pct_1t_normal = (cards_normal["periodo"] == "1T").mean() * 100

    mean_min_investigated = cards_investigated[cards_investigated["periodo"] == "1T"]["minuto_nominal"].mean()
    mean_min_normal = cards_normal[cards_normal["periodo"] == "1T"]["minuto_nominal"].mean()

    contrast_metrics = {
        "cartoes_investigados_total": len(cards_investigated),
        "cartoes_normais_total": len(cards_normal),
        "pct_1t_investigados": pct_1t_investigated,
        "pct_1t_normais": pct_1t_normal,
        "minuto_medio_1t_investigados": mean_min_investigated,
        "minuto_medio_1t_normais": mean_min_normal,
    }

    return all_cards, contrast_metrics

def generate_visualizations(cards_per_match, df_tests, c_sa, c_sb, all_cards, df_cases):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Gerando figuras comparativas em alta resolução...")

    # 1. Boxplot e Barplot Comparativo Série A vs. Série B
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    sns.barplot(
        data=cards_per_match,
        x="temporada",
        y="cartao",
        hue="serie",
        palette=["#1f77b4", "#ff7f0e"],
        ax=axes[0],
        errorbar=("ci", 95),
        capsize=0.1
    )
    axes[0].set_title("Média de Cartões por Jogo com IC 95% (Série A vs. Série B)", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Temporada")
    axes[0].set_ylabel("Média de Cartões / Partida")
    axes[0].legend(title="Divisão")

    sns.boxplot(
        data=cards_per_match,
        x="temporada",
        y="cartao",
        hue="serie",
        palette=["#1f77b4", "#ff7f0e"],
        ax=axes[1],
        showmeans=True,
        meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"}
    )
    axes[1].set_title("Distribuição e Dispersão de Cartões por Jogo", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Temporada")
    axes[1].set_ylabel("Cartões por Jogo")
    axes[1].legend(title="Divisão")

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "01_comparacao_cartoes_serie_a_vs_b.png", dpi=300)
    plt.close()

    # 2. Curva KDE de Minutagem Série A vs. Série B
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.kdeplot(c_sa["minuto_continuo"], label="Série A (2022–2023)", color="#1f77b4", fill=True, alpha=0.3, ax=ax)
    sns.kdeplot(c_sb["minuto_continuo"], label="Série B (2022–2023)", color="#ff7f0e", fill=True, alpha=0.3, ax=ax)
    ax.axvline(45, color="red", linestyle="--", linewidth=1.2, label="Intervalo (45')")
    ax.set_title("Densidade Temporal dos Cartões: Série A vs. Série B", fontsize=13, fontweight="bold")
    ax.set_xlabel("Minuto Contínuo da Partida")
    ax.set_ylabel("Densidade")
    ax.set_xlim(0, 105)
    ax.legend(loc="upper left")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "02_distribuicao_minutagem_a_vs_b.png", dpi=300)
    plt.close()

    # 3. Tipologia das Infrações na Série B
    fig, ax = plt.subplots(figsize=(11, 5))
    counts_infr = c_sb["categoria_infracao"].value_counts(ascending=True)
    colors = ["#7f7f7f", "#9467bd", "#e377c2", "#2ca02c", "#d62728", "#1f77b4"]
    bars = ax.barh(counts_infr.index, counts_infr.values, color=colors[:len(counts_infr)])
    ax.set_title("Tipologia das Advertências Disciplinares na Série B (2022–2023)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Quantidade de Cartões Aplicados")
    for bar in bars:
        w = bar.get_width()
        pct = w / counts_infr.sum() * 100
        ax.text(w + 20, bar.get_y() + bar.get_height()/2, f"{w} ({pct:.1f}%)", va="center", fontsize=10, fontweight="bold")
    ax.set_xlim(0, max(counts_infr.values) * 1.15)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "03_tipologia_infracoes_serie_b.png", dpi=300)
    plt.close()

    # 4. Contraste dos Casos da Operação Penalidade Máxima
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Histograma de fundo da população normal
    normal_min = all_cards[~all_cards["investigado_operacao"]]["minuto_continuo"]
    ax.hist(normal_min, bins=35, range=(0, 105), density=True, color="#bcbddc", alpha=0.6, label="População Normal (Partidas 2022-2023)")
    
    # Pontos dos eventos investigados
    cases_executed = df_cases[df_cases["evento_ocorreu"] & df_cases["minuto_real"].notna()].copy()
    y_jitter = np.linspace(0.005, 0.025, len(cases_executed))
    
    for idx, (_, r) in enumerate(cases_executed.iterrows()):
        min_c = r["minuto_real"] if r["minuto_alvo"] == "1T" or r["minuto_real"] <= 45 else r["minuto_real"] + 45
        cor = "red" if r["evento_alvo"] == "cometer_penalti_1t" else "darkorange"
        label_pt = f"{r['atleta']} ({r['confronto']}, {r['minuto_real']}')"
        ax.scatter(min_c, y_jitter[idx], color=cor, s=120, zorder=5, edgecolor="black", linewidth=1.2)
        ax.annotate(label_pt, (min_c, y_jitter[idx]), xytext=(min_c + 1.5, y_jitter[idx]), fontsize=8, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color="black", lw=0.6))

    ax.axvline(45, color="red", linestyle="--", linewidth=1.5, label="Fim do 1º Tempo (45')")
    ax.set_title("Contraste de Integridade: Minutagem dos Casos da Operação Penalidade Máxima vs. População Geral", fontsize=13, fontweight="bold")
    ax.set_xlabel("Minuto Contínuo do Evento")
    ax.set_ylabel("Densidade de Ocorrência")
    ax.set_xlim(0, 105)
    
    # Legenda customizada
    from matplotlib.lines import Line2D
    custom_legend = [
        Line2D([0], [0], color="#bcbddc", lw=6, label="Distribuição Normal (Partidas)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="darkorange", markeredgecolor="black", markersize=10, label="Cartão Amarelo Investigado"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="red", markeredgecolor="black", markersize=10, label="Pênalti Investigado"),
        Line2D([0], [0], color="red", linestyle="--", label="Intervalo (45')")
    ]
    ax.legend(handles=custom_legend, loc="upper right")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "04_contraste_casos_penalidade_maxima.png", dpi=300)
    plt.close()

    logger.info("Todas as figuras salvas com sucesso em %s", FIGURES_DIR)

def run_series_comparison_pipeline():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    sa_data, sb_data, df_cases = load_all_datasets()

    cards_per_match, summary, c_sa, c_sb = compute_series_comparison_metrics(sa_data, sb_data)
    df_tests = run_hypothesis_tests(cards_per_match)
    counts_infr, pcts_infr = analyze_infraction_types_serie_b(c_sb)
    all_cards, contrast_metrics = analyze_integrity_cases_contrast(c_sa, c_sb, df_cases)

    generate_visualizations(cards_per_match, df_tests, c_sa, c_sb, all_cards, df_cases)

    # Salvar Tabelas
    summary.to_csv(TABLES_DIR / "tabela_07_comparacao_metricas_series_a_b.csv", index=False)
    df_tests.to_csv(TABLES_DIR / "tabela_08_testes_estatisticos_serie_a_vs_b.csv", index=False)
    counts_infr.to_csv(TABLES_DIR / "tabela_09_tipologia_cartoes_serie_b.csv")
    df_cases.to_csv(TABLES_DIR / "tabela_10_casos_penalidade_maxima_analise.csv", index=False)

    logger.info("Pipeline comparativo Série A vs. B concluído com sucesso!")
    return summary, df_tests, contrast_metrics

if __name__ == "__main__":
    run_series_comparison_pipeline()
