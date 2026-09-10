"""
src/analysis/eda_bets.py
------------------------
Análise Exploratória e Estatística da Camada de Exposição às Bets (MVP 2):
1. Evolução do interesse público (Google Trends 2015-2025) e marcos regulatórios.
2. Dinâmica de penetração e saturação dos patrocínios na Série A (2015-2024).
3. Distribuição dos índices BET_EXPOSURE (clube e partida).
4. Cruzamento empírico: associação entre nível de exposição a bets e métricas de integridade
   (volume de cartões, proporção no 1T, faltas e taxa de conversão).
5. Geração de figuras em alta resolução em reports/figures/eda_bets/
   e tabelas estatísticas em reports/tables/.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

FIGURES_DIR = os.path.join("reports", "figures", "eda_bets")
TABLES_DIR = os.path.join("reports", "tables")
PROCESSED_BETTING_DIR = os.path.join("data", "processed", "betting")
PROCESSED_SERIE_A_DIR = os.path.join("data", "processed", "serie_a")

# Configurações visuais de alta qualidade
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 11
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["figure.dpi"] = 300


def load_data():
    trends_m = pd.read_parquet(os.path.join(PROCESSED_BETTING_DIR, "trends_mensal.parquet"))
    trends_a = pd.read_parquet(os.path.join(PROCESSED_BETTING_DIR, "trends_anual.parquet"))
    exp_clubes = pd.read_parquet(os.path.join(PROCESSED_BETTING_DIR, "exposicao_clubes_temporada.parquet"))
    partidas = pd.read_parquet(os.path.join(PROCESSED_SERIE_A_DIR, "partidas_com_exposure.parquet"))
    cartoes = pd.read_parquet(os.path.join(PROCESSED_SERIE_A_DIR, "cartoes.parquet"))
    estatisticas = pd.read_parquet(os.path.join(PROCESSED_SERIE_A_DIR, "estatisticas.parquet"))
    return trends_m, trends_a, exp_clubes, partidas, cartoes, estatisticas


def build_match_level_dataset(partidas, cartoes, estatisticas):
    """
    Consolida métricas disciplinares e scouts por partida_id
    e cruza com a exposição a bets.
    """
    # 1. Agregação de Cartões por partida
    cards_partida = cartoes.groupby("partida_id").agg(
        cartoes_total=("cartao", "count"),
        cartoes_amarelos=("cartao", lambda s: (s == "Amarelo").sum()),
        cartoes_vermelhos=("cartao", lambda s: (s == "Vermelho").sum()),
        cartoes_1T=("periodo", lambda s: (s == "1T").sum()),
        minuto_primeiro_cartao=("minuto_continuo", "min")
    ).reset_index()

    # 2. Agregação de Scouts por partida (faltas)
    stats_partida = estatisticas.groupby("partida_id").agg(
        faltas_total=("faltas", "sum"),
        chutes_total=("chutes", "sum"),
        scouts_validos=("scouts_validos", "all")
    ).reset_index()

    # 3. Merge com partidas
    df = partidas.merge(cards_partida, on="partida_id", how="left")
    df = df.merge(stats_partida, on="partida_id", how="left")

    df["cartoes_total"] = df["cartoes_total"].fillna(0)
    df["cartoes_amarelos"] = df["cartoes_amarelos"].fillna(0)
    df["cartoes_vermelhos"] = df["cartoes_vermelhos"].fillna(0)
    df["cartoes_1T"] = df["cartoes_1T"].fillna(0)
    df["pct_cartoes_1T"] = np.where(
        df["cartoes_total"] > 0,
        df["cartoes_1T"] / df["cartoes_total"],
        np.nan
    )

    # Taxa cartões por falta (quando scouts forem válidos)
    df["taxa_cartao_falta"] = np.where(
        (df["scouts_validos"] == True) & (df["faltas_total"] > 0),
        df["cartoes_total"] / df["faltas_total"],
        np.nan
    )

    return df


def plot_01_trends_and_milestones(trends_m, trends_a):
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(trends_m["data"], trends_m["google_trends_score"],
            color="#1f77b4", alpha=0.5, linewidth=1.2, label="Índice Mensal")
    
    # Média móvel 12 meses
    trends_m["ma_12"] = trends_m["google_trends_score"].rolling(12, min_periods=1).mean()
    ax.plot(trends_m["data"], trends_m["ma_12"],
            color="#0d3b66", linewidth=2.5, label="Tendência (Média Móvel 12M)")

    # Marcos temporais
    marcos = [
        ("2018-12-12", "Lei 13.756/2018\n(Legalização Quota Fixa)", "#d90429"),
        ("2022-11-20", "Copa Catar 2022 &\nOperação Penalidade Máxima", "#f77f00"),
        ("2023-07-25", "MP 1.182 / Lei 14.790\n(Regulamentação Federal)", "#38b000"),
        ("2025-01-01", "Vigência Mercado Regulado\n(Apenas Bets Autorizadas)", "#7209b7")
    ]

    for data_str, rotulo, cor in marcos:
        dt = pd.to_datetime(data_str)
        ax.axvline(dt, color=cor, linestyle="--", linewidth=1.6, alpha=0.85)
        ax.text(dt + pd.Timedelta(days=40), 80, rotulo, color=cor,
                fontsize=9, weight="bold", bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85, edgecolor=cor))

    ax.set_title("Evolução do Interesse por Apostas Esportivas no Brasil (Google Trends 2015–2025)", weight="bold", pad=15)
    ax.set_ylabel("Índice de Interesse de Busca (Escala 0–100)")
    ax.set_xlabel("Ano")
    ax.set_ylim(0, 105)
    ax.legend(loc="upper left", frameon=True)
    plt.tight_layout()

    out_path = os.path.join(FIGURES_DIR, "01_evolucao_google_trends_e_marcos.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"-> Figura 01 salva: {out_path}")


def plot_02_sponsorship_penetration(exp_clubes):
    df_yearly = exp_clubes.groupby("temporada").agg(
        total_clubes=("clube_slug", "count"),
        clubes_com_bet=("tem_patrocinio_bet", "sum"),
        clubes_com_master=("tipo_patrocinio_bet", lambda s: (s == "master").sum()),
        clubes_secundario=("tipo_patrocinio_bet", lambda s: (s.isin(["mangas", "secundario"])).sum())
    ).reset_index()

    df_yearly["pct_qualquer_bet"] = df_yearly["clubes_com_bet"] / df_yearly["total_clubes"] * 100
    df_yearly["pct_master"] = df_yearly["clubes_com_master"] / df_yearly["total_clubes"] * 100
    df_yearly["pct_secundario"] = df_yearly["clubes_secundario"] / df_yearly["total_clubes"] * 100

    fig, ax = plt.subplots(figsize=(11, 6))
    anos = df_yearly["temporada"]

    ax.plot(anos, df_yearly["pct_qualquer_bet"], marker="o", color="#e63946", linewidth=2.8, label="% Clubes com Qualquer Bet")
    ax.plot(anos, df_yearly["pct_master"], marker="s", color="#1d3557", linewidth=2.5, linestyle="--", label="% Clubes com Bet Master")
    ax.bar(anos, df_yearly["pct_secundario"], color="#a8dadc", alpha=0.5, width=0.5, label="% Clubes com Bet Secundária (Mangas/Costas)")

    # Rótulos de dados
    for i, row in df_yearly.iterrows():
        if row["pct_qualquer_bet"] > 0:
            ax.annotate(f"{row['pct_qualquer_bet']:.0f}%", (row["temporada"], row["pct_qualquer_bet"] + 2.5),
                        ha="center", fontsize=9, weight="bold", color="#e63946")
        if row["pct_master"] > 0:
            ax.annotate(f"{row['pct_master']:.0f}%", (row["temporada"], row["pct_master"] - 5),
                        ha="center", fontsize=8, weight="bold", color="#1d3557")

    ax.set_title("Penetração de Patrocínios de Casas de Apostas no Brasileirão Série A (2015–2024)", weight="bold", pad=15)
    ax.set_ylabel("Participação dos Clubes da Elite (%)")
    ax.set_xlabel("Temporada")
    ax.set_ylim(-2, 105)
    ax.set_xticks(anos)
    ax.legend(loc="upper left", frameon=True)
    plt.tight_layout()

    out_path = os.path.join(FIGURES_DIR, "02_penetracao_patrocinios_serie_a.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"-> Figura 02 salva: {out_path}")


def plot_03_bet_exposure_distribution(exp_clubes):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    # Gráfico A: Exposição Contratual Estrita
    sns.boxplot(data=exp_clubes, x="temporada", y="bet_exposure_clube", ax=axes[0], color="#457b9d", width=0.6)
    sns.stripplot(data=exp_clubes, x="temporada", y="bet_exposure_clube", ax=axes[0], color="#1d3557", alpha=0.6, jitter=0.2, size=5)
    axes[0].set_title("A: Índice de Exposição Contratual Estrita (bet_exposure_clube)", weight="bold")
    axes[0].set_ylabel("Índice de Exposição [0.0, 1.0]")
    axes[0].set_xlabel("Temporada")
    axes[0].set_ylim(-0.05, 1.05)

    # Gráfico B: Exposição Total (Contratual + Macro Trends)
    sns.boxplot(data=exp_clubes, x="temporada", y="bet_exposure_total", ax=axes[1], color="#e76f51", width=0.6)
    sns.stripplot(data=exp_clubes, x="temporada", y="bet_exposure_total", ax=axes[1], color="#9d0208", alpha=0.6, jitter=0.2, size=5)
    axes[1].set_title("B: Índice de Exposição Total com Efeito Macro (bet_exposure_total)", weight="bold")
    axes[1].set_ylabel("")
    axes[1].set_xlabel("Temporada")

    plt.suptitle("Distribuição dos Índices de Exposição às Bets nos Clubes da Série A (2015–2024)", weight="bold", y=1.02, fontsize=14)
    plt.tight_layout()

    out_path = os.path.join(FIGURES_DIR, "03_distribuicao_bet_exposure_clubes.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"-> Figura 03 salva: {out_path}")


def plot_04_association_matches(df_matches):
    """
    Contrasta partidas por categoria de exposição (2019–2024):
    Nenhuma vs Parcial (1 clube) vs Total (2 clubes)
    """
    df_recent = df_matches[df_matches["temporada"] >= 2019].copy()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    cat_order = ["Nenhuma", "Parcial (1 clube)", "Total (2 clubes)"]
    palette = ["#2b2d42", "#8d99ae", "#ef233c"]

    # 1. Cartões por Partida
    sns.barplot(data=df_recent, x="categoria_exposicao_partida", y="cartoes_total",
                order=cat_order, palette=palette, ax=axes[0, 0], capsize=0.1, err_kws={'linewidth': 1.5})
    axes[0, 0].set_title("1. Cartões Totais por Partida", weight="bold")
    axes[0, 0].set_ylabel("Média de Cartões")
    axes[0, 0].set_xlabel("")

    # 2. Proporção de Cartões no 1º Tempo (%)
    df_recent["pct_1t_100"] = df_recent["pct_cartoes_1T"] * 100
    sns.barplot(data=df_recent, x="categoria_exposicao_partida", y="pct_1t_100",
                order=cat_order, palette=palette, ax=axes[0, 1], capsize=0.1, err_kws={'linewidth': 1.5})
    axes[0, 1].set_title("2. Cartões Ocorridos no 1º Tempo (%)", weight="bold")
    axes[0, 1].set_ylabel("Proporção 1T (%)")
    axes[0, 1].set_xlabel("")

    # 3. Faltas por Partida (anos com scouts válidos: 2019-2023)
    df_scouts = df_recent[df_recent["scouts_validos"] == True]
    sns.barplot(data=df_scouts, x="categoria_exposicao_partida", y="faltas_total",
                order=cat_order, palette=palette, ax=axes[1, 0], capsize=0.1, err_kws={'linewidth': 1.5})
    axes[1, 0].set_title("3. Faltas Cometidas por Partida (2019–2023)", weight="bold")
    axes[1, 0].set_ylabel("Média de Faltas")
    axes[1, 0].set_xlabel("Categoria de Exposição da Partida")

    # 4. Taxa de Conversão Faltas -> Cartões
    sns.barplot(data=df_scouts, x="categoria_exposicao_partida", y="taxa_cartao_falta",
                order=cat_order, palette=palette, ax=axes[1, 1], capsize=0.1, err_kws={'linewidth': 1.5})
    axes[1, 1].set_title("4. Taxa de Conversão (Cartões / Faltas)", weight="bold")
    axes[1, 1].set_ylabel("Cartões por Falta")
    axes[1, 1].set_xlabel("Categoria de Exposição da Partida")

    plt.suptitle("Associação Empírica entre Exposição às Bets e Métricas de Jogo na Série A (2019–2024)", weight="bold", fontsize=14, y=1.00)
    plt.tight_layout()

    out_path = os.path.join(FIGURES_DIR, "04_associacao_exposicao_vs_cartoes_faltas.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"-> Figura 04 salva: {out_path}")


def plot_05_brands_presence(exp_clubes):
    """
    Mostra o ranking das marcas de apostas com mais temporadas na Série A.
    """
    bets_active = exp_clubes[exp_clubes["tem_patrocinio_bet"]].copy()
    brand_counts = bets_active.groupby("marca_principal_bet")["temporada"].count().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(brand_counts.index, brand_counts.values, color="#3a86ff", height=0.65)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.3, bar.get_y() + bar.get_height() / 2, f"{int(w)} contratos-ano",
                va="center", ha="left", fontsize=9, weight="bold", color="#1d3557")

    ax.set_title("Marcas de Apostas mais Presentes na Série A do Brasileirão (2019–2024)", weight="bold", pad=15)
    ax.set_xlabel("Volume Acumulado de Contratos de Clube × Temporada")
    ax.set_xlim(0, brand_counts.max() + 4)
    plt.tight_layout()

    out_path = os.path.join(FIGURES_DIR, "05_heatmap_marcas_bets_clubes.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"-> Figura 05 salva: {out_path}")


def generate_tables(trends_a, exp_clubes, df_matches):
    os.makedirs(TABLES_DIR, exist_ok=True)

    # --- Tabela 04: Métricas do Mercado de Bets Anual ---
    club_stats = exp_clubes.groupby("temporada").agg(
        total_clubes=("clube_slug", "count"),
        clubes_com_bet=("tem_patrocinio_bet", "sum"),
        clubes_master=("tipo_patrocinio_bet", lambda s: (s == "master").sum()),
        exp_clube_medio=("bet_exposure_clube", "mean"),
        exp_total_medio=("bet_exposure_total", "mean")
    ).reset_index()

    matches_stats = df_matches[df_matches["temporada"] >= 2015].groupby("temporada").agg(
        total_partidas=("partida_id", "count"),
        jogos_ambos_bet=("ambos_patrocinados_bet", "sum"),
        pct_jogos_ambos=("ambos_patrocinados_bet", "mean")
    ).reset_index()

    tab4 = trends_a.merge(club_stats, left_on="ano", right_on="temporada", how="left")
    tab4 = tab4.merge(matches_stats, left_on="ano", right_on="temporada", how="left")

    tab4["pct_clubes_com_bet"] = (tab4["clubes_com_bet"] / tab4["total_clubes"] * 100).round(1)
    tab4["pct_clubes_master"] = (tab4["clubes_master"] / tab4["total_clubes"] * 100).round(1)
    tab4["pct_jogos_ambos"] = (tab4["pct_jogos_ambos"] * 100).round(1)

    cols_tab4 = [
        "ano", "fase_regulatoria", "trends_score_medio", "trends_score_max",
        "pct_clubes_com_bet", "pct_clubes_master", "pct_jogos_ambos",
        "exp_clube_medio", "exp_total_medio"
    ]
    tab4_out = tab4[cols_tab4].copy()
    tab4_path = os.path.join(TABLES_DIR, "tabela_04_metricas_mercado_bets_anual.csv")
    tab4_out.to_csv(tab4_path, index=False, encoding="utf-8")
    print(f"-> Tabela 04 salva: {tab4_path}")

    # --- Tabela 05: Comparação das Partidas por Exposição (2019-2024) ---
    df_rec = df_matches[df_matches["temporada"] >= 2019].copy()
    tab5 = df_rec.groupby("categoria_exposicao_partida").agg(
        total_partidas=("partida_id", "count"),
        cartoes_medio=("cartoes_total", "mean"),
        cartoes_desvio=("cartoes_total", "std"),
        cartoes_1t_pct=("pct_cartoes_1T", lambda s: s.mean() * 100),
        faltas_medio=("faltas_total", lambda s: s[df_rec.loc[s.index, "scouts_validos"] == True].mean()),
        taxa_cartao_falta=("taxa_cartao_falta", "mean")
    ).reset_index()

    tab5_path = os.path.join(TABLES_DIR, "tabela_05_comparacao_partidas_por_exposicao.csv")
    tab5.round(3).to_csv(tab5_path, index=False, encoding="utf-8")
    print(f"-> Tabela 05 salva: {tab5_path}")

    # --- Tabela 06: Top Clubes em Exposição Acumulada (2019-2024) ---
    exp_rec = exp_clubes[exp_clubes["temporada"] >= 2019].copy()
    tab6 = exp_rec.groupby("clube_slug").agg(
        temporadas_serie_a=("temporada", "count"),
        temporadas_com_bet=("tem_patrocinio_bet", "sum"),
        temporadas_bet_master=("tipo_patrocinio_bet", lambda s: (s == "master").sum()),
        marcas_distintas=("marca_principal_bet", lambda s: set(s[s != "Nenhum"])),
        exp_clube_medio=("bet_exposure_clube", "mean"),
        exp_total_medio=("bet_exposure_total", "mean")
    ).reset_index()

    tab6["marcas_distintas"] = tab6["marcas_distintas"].apply(lambda s: ", ".join(sorted(s)) if len(s) > 0 else "Nenhuma")
    tab6 = tab6.sort_values(by="exp_clube_medio", ascending=False)

    tab6_path = os.path.join(TABLES_DIR, "tabela_06_top_clubes_exposicao_acumulada.csv")
    tab6.round(3).to_csv(tab6_path, index=False, encoding="utf-8")
    print(f"-> Tabela 06 salva: {tab6_path}")

    return tab4_out, tab5, tab6


def run_statistical_tests(df_matches):
    """
    Executa testes t de Student e Mann-Whitney comparando partidas de
    Exposição Total (ambas as equipes com bets) vs. Sem Exposição (nenhuma equipe)
    no período contemporâneo (2019-2024).
    """
    df_rec = df_matches[df_matches["temporada"] >= 2019].copy()
    g_total = df_rec[df_rec["categoria_exposicao_partida"] == "Total (2 clubes)"]
    g_nenhuma = df_rec[df_rec["categoria_exposicao_partida"] == "Nenhuma"]

    print("\n" + "=" * 70)
    print("TESTES ESTATÍSTICOS DE HIPÓTESE: TOTAL EXPOSIÇÃO VS. NENHUMA (2019–2024)")
    print("=" * 70)

    # 1. Cartões Totais
    t_stat_c, p_val_c = stats.ttest_ind(g_total["cartoes_total"], g_nenhuma["cartoes_total"], equal_var=False)
    u_stat_c, p_val_u_c = stats.mannwhitneyu(g_total["cartoes_total"], g_nenhuma["cartoes_total"])
    print(f"Cartões Totais por Jogo:")
    print(f"  -> Total Exp (N={len(g_total)}): {g_total['cartoes_total'].mean():.3f} +/- {g_total['cartoes_total'].std():.3f}")
    print(f"  -> Nenhuma (N={len(g_nenhuma)}): {g_nenhuma['cartoes_total'].mean():.3f} +/- {g_nenhuma['cartoes_total'].std():.3f}")
    print(f"  -> Teste t: t = {t_stat_c:.4f}, p = {p_val_c:.4e}")
    print(f"  -> Mann-Whitney U: U = {u_stat_c}, p = {p_val_u_c:.4e}")

    # 2. Cartões no 1º Tempo (%)
    g_tot_1t = g_total["pct_cartoes_1T"].dropna()
    g_nen_1t = g_nenhuma["pct_cartoes_1T"].dropna()
    t_stat_1t, p_val_1t = stats.ttest_ind(g_tot_1t, g_nen_1t, equal_var=False)
    print(f"\nProporção de Cartões no 1T:")
    print(f"  -> Total Exp: {g_tot_1t.mean()*100:.2f}% | Nenhuma: {g_nen_1t.mean()*100:.2f}%")
    print(f"  -> Teste t: t = {t_stat_1t:.4f}, p = {p_val_1t:.4e}")

    # 3. Taxa de Conversão Cartões/Faltas (onde válido)
    g_tot_tx = g_total["taxa_cartao_falta"].dropna()
    g_nen_tx = g_nenhuma["taxa_cartao_falta"].dropna()
    t_stat_tx, p_val_tx = stats.ttest_ind(g_tot_tx, g_nen_tx, equal_var=False)
    print(f"\nTaxa de Conversão (Cartões / Falta):")
    print(f"  -> Total Exp: {g_tot_tx.mean():.4f} | Nenhuma: {g_nen_tx.mean():.4f}")
    print(f"  -> Teste t: t = {t_stat_tx:.4f}, p = {p_val_tx:.4e}")
    print("=" * 70)


def main():
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(TABLES_DIR, exist_ok=True)
    print("=" * 70)
    print("INICIANDO ANÁLISE EXPLORATÓRIA E ESTATÍSTICA DO MERCADO DE BETS (MVP 2)")
    print("=" * 70)

    trends_m, trends_a, exp_clubes, partidas, cartoes, estatisticas = load_data()
    df_matches = build_match_level_dataset(partidas, cartoes, estatisticas)

    # 1. Gerar Figuras
    plot_01_trends_and_milestones(trends_m, trends_a)
    plot_02_sponsorship_penetration(exp_clubes)
    plot_03_bet_exposure_distribution(exp_clubes)
    plot_04_association_matches(df_matches)
    plot_05_brands_presence(exp_clubes)

    # 2. Gerar Tabelas
    generate_tables(trends_a, exp_clubes, df_matches)

    # 3. Executar Testes Estatísticos
    run_statistical_tests(df_matches)

    print("=" * 70)
    print("EDA DO MVP 2 CONCLUÍDA COM SUCESSO!")
    print("=" * 70)


if __name__ == "__main__":
    main()
