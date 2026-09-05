# -*- coding: utf-8 -*-
"""Script de Análise Exploratória de Dados (EDA) Profunda — Brasileirão Série A.

Gera métricas consolidadas, testes de hipótese, figuras de visualização
e tabelas tabuladas em reports/figures/ e reports/tables/.
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
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8


def load_datasets(processed_dir: Path = Path('data/processed/serie_a')) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_partidas = pd.read_parquet(processed_dir / 'partidas.parquet')
    df_cartoes = pd.read_parquet(processed_dir / 'cartoes.parquet')
    df_stats = pd.read_parquet(processed_dir / 'estatisticas.parquet')
    df_gols = pd.read_parquet(processed_dir / 'gols.parquet')
    return df_partidas, df_cartoes, df_stats, df_gols


def compute_metrics_by_season(
    df_partidas: pd.DataFrame,
    df_cartoes: pd.DataFrame,
    df_stats: pd.DataFrame,
    df_gols: pd.DataFrame,
) -> pd.DataFrame:
    jogos = df_partidas.groupby('temporada')['partida_id'].count().rename('total_jogos')

    cards_per_match = df_cartoes.groupby(['temporada', 'partida_id'])['cartao'].count().reset_index()
    cards_summary = cards_per_match.groupby('temporada')['cartao'].agg(
        cartoes_media='mean',
        cartoes_std='std',
        cartoes_mediana='median',
    )
    cards_total = df_cartoes.groupby('temporada')['cartao'].count().rename('cartoes_total')

    cards_type = df_cartoes.groupby(['temporada', 'cartao'])['partida_id'].count().unstack(fill_value=0)
    amarelos = cards_type['Amarelo'].rename('cartoes_amarelos') if 'Amarelo' in cards_type else pd.Series(dtype=int)
    vermelhos = cards_type['Vermelho'].rename('cartoes_vermelhos') if 'Vermelho' in cards_type else pd.Series(dtype=int)

    cards_period = df_cartoes.groupby(['temporada', 'periodo'])['partida_id'].count().unstack(fill_value=0)
    cards_1t = cards_period['1T'].rename('cartoes_1T') if '1T' in cards_period else pd.Series(dtype=int)
    cards_2t = cards_period['2T'].rename('cartoes_2T') if '2T' in cards_period else pd.Series(dtype=int)

    first_card = df_cartoes.groupby(['temporada', 'partida_id'])['minuto_continuo'].min().reset_index()
    first_card_mean = first_card.groupby('temporada')['minuto_continuo'].mean().rename('minuto_medio_1o_cartao')

    stats_valid = df_stats[df_stats['scouts_validos']]
    fouls_per_match = stats_valid.groupby(['temporada', 'partida_id'])['faltas'].sum().reset_index()
    fouls_summary = fouls_per_match.groupby('temporada')['faltas'].agg(
        faltas_media='mean',
        faltas_std='std',
    )

    merged_cf = pd.merge(fouls_per_match, cards_per_match, on=['temporada', 'partida_id'], how='inner')
    merged_cf['taxa_cartao_falta'] = merged_cf['cartao'] / merged_cf['faltas'].replace(0, np.nan)
    taxa_cf_mean = merged_cf.groupby('temporada')['taxa_cartao_falta'].mean().rename('taxa_cartao_por_falta')

    goals_per_match = df_partidas.groupby('temporada')['total_gols'].mean().rename('gols_media_por_jogo')
    pen_goals = df_gols[df_gols['tipo_de_gol'] == 'Penalty'].groupby('temporada')['tipo_de_gol'].count().rename('gols_penalti')

    df_res = pd.concat([
        jogos,
        cards_total,
        cards_summary,
        amarelos,
        vermelhos,
        cards_1t,
        cards_2t,
        first_card_mean,
        fouls_summary,
        taxa_cf_mean,
        goals_per_match,
        pen_goals,
    ], axis=1).reset_index()

    df_res['taxa_vermelho_pct'] = (df_res['cartoes_vermelhos'] / df_res['cartoes_total']).round(4)
    df_res['pct_cartoes_1T'] = (df_res['cartoes_1T'] / df_res['cartoes_total']).round(4)
    df_res['penaltis_por_jogo'] = (df_res['gols_penalti'] / df_res['total_jogos']).round(4)

    return df_res


def perform_hypothesis_tests(df_cartoes: pd.DataFrame, df_stats: pd.DataFrame) -> pd.DataFrame:
    cards_match = df_cartoes.groupby(['temporada', 'partida_id'])['cartao'].count().reset_index()
    
    pre_cards = cards_match[cards_match['temporada'].between(2014, 2018)]['cartao']
    pos_cards = cards_match[cards_match['temporada'].between(2022, 2024)]['cartao']
    
    t_stat_cards, p_val_cards = stats.ttest_ind(pre_cards, pos_cards)
    u_stat_cards, p_u_cards = stats.mannwhitneyu(pre_cards, pos_cards)
    pooled_std_cards = np.sqrt((pre_cards.var() + pos_cards.var()) / 2)
    cohen_d_cards = (pos_cards.mean() - pre_cards.mean()) / pooled_std_cards

    stats_valid = df_stats[df_stats['scouts_validos']]
    fouls_match = stats_valid.groupby(['temporada', 'partida_id'])['faltas'].sum().reset_index()
    pre_fouls = fouls_match[fouls_match['temporada'].between(2015, 2018)]['faltas']
    pos_fouls = fouls_match[fouls_match['temporada'].between(2022, 2023)]['faltas']

    t_stat_fouls, p_val_fouls = stats.ttest_ind(pre_fouls, pos_fouls)
    u_stat_fouls, p_u_fouls = stats.mannwhitneyu(pre_fouls, pos_fouls)
    pooled_std_fouls = np.sqrt((pre_fouls.var() + pos_fouls.var()) / 2)
    cohen_d_fouls = (pos_fouls.mean() - pre_fouls.mean()) / pooled_std_fouls

    merged_cf = pd.merge(fouls_match, cards_match, on=['temporada', 'partida_id'], how='inner')
    merged_cf['taxa_cf'] = merged_cf['cartao'] / merged_cf['faltas'].replace(0, np.nan)
    pre_taxa = merged_cf[merged_cf['temporada'].between(2015, 2018)]['taxa_cf'].dropna()
    pos_taxa = merged_cf[merged_cf['temporada'].between(2022, 2023)]['taxa_cf'].dropna()

    t_stat_taxa, p_val_taxa = stats.ttest_ind(pre_taxa, pos_taxa)
    u_stat_taxa, p_u_taxa = stats.mannwhitneyu(pre_taxa, pos_taxa)
    pooled_std_taxa = np.sqrt((pre_taxa.var() + pos_taxa.var()) / 2)
    cohen_d_taxa = (pos_taxa.mean() - pre_taxa.mean()) / pooled_std_taxa

    tests_data = [
        {
            'Variavel': 'Cartões por Partida',
            'Periodo_Controle': '2014-2018 (Pré-Bets)',
            'Media_Controle': round(pre_cards.mean(), 3),
            'Desv_Controle': round(pre_cards.std(), 3),
            'Periodo_Tratamento': '2022-2024 (Alta Exposição)',
            'Media_Tratamento': round(pos_cards.mean(), 3),
            'Desv_Tratamento': round(pos_cards.std(), 3),
            'Delta_Absoluto': round(pos_cards.mean() - pre_cards.mean(), 3),
            'Delta_Pct': round((pos_cards.mean() / pre_cards.mean() - 1) * 100, 2),
            'T_Stat': round(t_stat_cards, 4),
            'P_Valor_T': f'{p_val_cards:.4e}',
            'Mann_Whitney_U': round(u_stat_cards, 1),
            'P_Valor_U': f'{p_u_cards:.4e}',
            'Cohen_d': round(cohen_d_cards, 4),
        },
        {
            'Variavel': 'Faltas por Partida',
            'Periodo_Controle': '2015-2018 (Pré-Bets)',
            'Media_Controle': round(pre_fouls.mean(), 3),
            'Desv_Controle': round(pre_fouls.std(), 3),
            'Periodo_Tratamento': '2022-2023 (Alta Exposição)',
            'Media_Tratamento': round(pos_fouls.mean(), 3),
            'Desv_Tratamento': round(pos_fouls.std(), 3),
            'Delta_Absoluto': round(pos_fouls.mean() - pre_fouls.mean(), 3),
            'Delta_Pct': round((pos_fouls.mean() / pre_fouls.mean() - 1) * 100, 2),
            'T_Stat': round(t_stat_fouls, 4),
            'P_Valor_T': f'{p_val_fouls:.4e}',
            'Mann_Whitney_U': round(u_stat_fouls, 1),
            'P_Valor_U': f'{p_u_fouls:.4e}',
            'Cohen_d': round(cohen_d_fouls, 4),
        },
        {
            'Variavel': 'Taxa Cartão / Falta',
            'Periodo_Controle': '2015-2018 (Pré-Bets)',
            'Media_Controle': round(pre_taxa.mean(), 3),
            'Desv_Controle': round(pre_taxa.std(), 3),
            'Periodo_Tratamento': '2022-2023 (Alta Exposição)',
            'Media_Tratamento': round(pos_taxa.mean(), 3),
            'Desv_Tratamento': round(pos_taxa.std(), 3),
            'Delta_Absoluto': round(pos_taxa.mean() - pre_taxa.mean(), 3),
            'Delta_Pct': round((pos_taxa.mean() / pre_taxa.mean() - 1) * 100, 2),
            'T_Stat': round(t_stat_taxa, 4),
            'P_Valor_T': f'{p_val_taxa:.4e}',
            'Mann_Whitney_U': round(u_stat_taxa, 1),
            'P_Valor_U': f'{p_u_taxa:.4e}',
            'Cohen_d': round(cohen_d_taxa, 4),
        },
    ]
    return pd.DataFrame(tests_data)


def compute_top_athletes_cards(df_cartoes: pd.DataFrame) -> pd.DataFrame:
    df_rec = df_cartoes[df_cartoes['temporada'] >= 2019].copy()
    
    ath_summary = df_rec.groupby(['atleta', 'atleta_slug', 'posicao']).agg(
        total_cartoes=('cartao', 'count'),
        cartoes_amarelos=('cartao', lambda x: (x == 'Amarelo').sum()),
        cartoes_vermelhos=('cartao', lambda x: (x == 'Vermelho').sum()),
        cartoes_1T=('periodo', lambda x: (x == '1T').sum()),
        cartoes_ate_30min=('minuto_continuo', lambda x: (x <= 30).sum()),
        minuto_medio=('minuto_continuo', 'mean'),
        temporadas=('temporada', 'nunique'),
    ).reset_index()

    ath_summary['pct_1T'] = (ath_summary['cartoes_1T'] / ath_summary['total_cartoes']).round(3)
    ath_summary['pct_ate_30min'] = (ath_summary['cartoes_ate_30min'] / ath_summary['total_cartoes']).round(3)

    top_1t = ath_summary[ath_summary['total_cartoes'] >= 15].sort_values(
        by=['pct_1T', 'cartoes_1T'], ascending=False
    ).head(20)

    return top_1t


def generate_figures(
    df_metrics: pd.DataFrame,
    df_cartoes: pd.DataFrame,
    df_stats: pd.DataFrame,
    top_athletes: pd.DataFrame,
    fig_dir: Path = Path('reports/figures/eda_serie_a'),
):
    fig_dir.mkdir(parents=True, exist_ok=True)
    metrics_recent = df_metrics[df_metrics['temporada'] >= 2014].copy()

    # FIGURA 1: Evolução Cartões por Jogo
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.plot(
        metrics_recent['temporada'],
        metrics_recent['cartoes_media'],
        marker='o',
        color='#1f77b4',
        linewidth=2.5,
        label='Média de Cartões / Jogo',
    )
    ax.fill_between(
        metrics_recent['temporada'],
        metrics_recent['cartoes_media'] - 0.2,
        metrics_recent['cartoes_media'] + 0.2,
        color='#1f77b4',
        alpha=0.15,
    )
    ax.axvline(2018.95, color='#d62728', linestyle='--', linewidth=1.5, label='Legalização Bets (Dez/2018)')
    ax.axvline(2019.3, color='#2ca02c', linestyle=':', linewidth=1.5, label='Início VAR (Mai/2019)')
    ax.axvline(2022.8, color='#9467bd', linestyle='--', linewidth=1.5, label='Op. Penalidade Máxima (2022-23)')

    ax.set_title('Evolução da Média de Cartões por Partida no Brasileirão Série A (2014–2024)', fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel('Temporada', fontsize=11)
    ax.set_ylabel('Cartões por Partida', fontsize=11)
    ax.set_xticks(metrics_recent['temporada'])
    ax.set_ylim(4.2, 6.0)
    ax.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()
    fig.savefig(fig_dir / '01_evolucao_cartoes_por_jogo.png')
    plt.close(fig)
    logger.info('Figura 1 salva.')

    # FIGURA 2: Faltas vs Taxa de Conversão
    fig, ax1 = plt.subplots(figsize=(10, 5), dpi=300)
    m_fouls = metrics_recent.dropna(subset=['faltas_media'])
    
    color1 = '#ff7f0e'
    ax1.plot(m_fouls['temporada'], m_fouls['faltas_media'], marker='s', color=color1, linewidth=2.5, label='Faltas por Partida (Eixo Esq.)')
    ax1.set_xlabel('Temporada', fontsize=11)
    ax1.set_ylabel('Faltas Médias por Partida', color=color1, fontsize=11, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_xticks(m_fouls['temporada'])
    ax1.set_ylim(24, 34)

    ax2 = ax1.twinx()
    color2 = '#d62728'
    ax2.plot(m_fouls['temporada'], m_fouls['taxa_cartao_por_falta'], marker='^', color=color2, linewidth=2.5, linestyle='--', label='Taxa Cartão/Falta (Eixo Dir.)')
    ax2.set_ylabel('Taxa de Cartão por Falta Cometida', color=color2, fontsize=11, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0.14, 0.22)
    ax2.grid(False)

    plt.title('O Paradoxo Disciplinar: Queda de Faltas e Disparada da Taxa de Conversão em Cartões', fontsize=12, fontweight='bold', pad=12)
    plt.tight_layout()
    fig.savefig(fig_dir / '02_evolucao_faltas_e_taxa_conversao.png')
    plt.close(fig)
    logger.info('Figura 2 salva.')

    # FIGURA 3: Distribuição da Minutagem
    fig, (ax_kde, ax_bar) = plt.subplots(1, 2, figsize=(14, 5), dpi=300)
    
    c_pre = df_cartoes[df_cartoes['temporada'].between(2014, 2018)]['minuto_continuo']
    c_pos = df_cartoes[df_cartoes['temporada'].between(2022, 2024)]['minuto_continuo']

    sns.kdeplot(c_pre, ax=ax_kde, label='Pré-Bets (2014-2018)', color='#1f77b4', linewidth=2.2, bw_adjust=0.8)
    sns.kdeplot(c_pos, ax=ax_kde, label='Alta Expansão (2022-2024)', color='#d62728', linewidth=2.2, bw_adjust=0.8)
    ax_kde.axvline(45, color='gray', linestyle=':', label='Fim do 1º Tempo')
    ax_kde.set_title('Densidade da Minutagem dos Cartões', fontsize=11, fontweight='bold')
    ax_kde.set_xlabel('Minuto Contínuo do Cartão', fontsize=10)
    ax_kde.set_ylabel('Densidade', fontsize=10)
    ax_kde.legend()

    bins = [0, 15, 30, 45, 60, 75, 90, 120]
    labels = ['0-15', '16-30', '31-45', '46-60', '61-75', '76-90', '90+']
    df_cartoes_cut = df_cartoes[df_cartoes['temporada'] >= 2014].copy()
    df_cartoes_cut['bloco_15min'] = pd.cut(df_cartoes_cut['minuto_continuo'], bins=bins, labels=labels, right=True)
    
    bloco_counts = df_cartoes_cut.groupby('bloco_15min', observed=True)['cartao'].count().reset_index()
    sns.barplot(data=bloco_counts, x='bloco_15min', y='cartao', ax=ax_bar, palette='viridis')
    ax_bar.set_title('Distribuição de Cartões por Blocos de 15 Minutos (2014–2024)', fontsize=11, fontweight='bold')
    ax_bar.set_xlabel('Intervalo de Minutos', fontsize=10)
    ax_bar.set_ylabel('Total de Cartões', fontsize=10)

    plt.tight_layout()
    fig.savefig(fig_dir / '03_distribuicao_minutagem_cartoes.png')
    plt.close(fig)
    logger.info('Figura 3 salva.')

    # FIGURA 4: Pênaltis e Cartões Vermelhos
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.bar(
        metrics_recent['temporada'] - 0.2,
        metrics_recent['gols_penalti'],
        width=0.4,
        color='#3b528b',
        label='Gols de Pênalti',
    )
    ax.bar(
        metrics_recent['temporada'] + 0.2,
        metrics_recent['cartoes_vermelhos'],
        width=0.4,
        color='#e41a1c',
        label='Cartões Vermelhos',
    )
    ax.set_title('Frequência Anual de Gols de Pênalti e Cartões Vermelhos (2014–2024)', fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel('Temporada', fontsize=11)
    ax.set_ylabel('Total por Temporada (380 Jogos)', fontsize=11)
    ax.set_xticks(metrics_recent['temporada'])
    ax.legend()
    plt.tight_layout()
    fig.savefig(fig_dir / '04_gols_penalti_e_vermelhos.png')
    plt.close(fig)
    logger.info('Figura 4 salva.')

    # FIGURA 5: Top Atletas 1T
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    top_plot = top_athletes.head(12).sort_values(by='pct_1T', ascending=True)
    bars = ax.barh(top_plot['atleta'], top_plot['pct_1T'] * 100, color='#2b83ba')
    ax.set_title('Top Atletas com Maior Proporção de Cartões no 1º Tempo (2019–2024, Min. 15 Cartões)', fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel('% de Cartões Recebidos no 1º Tempo', fontsize=10)
    ax.axvline(34.5, color='#d7191c', linestyle='--', linewidth=1.5, label='Média Geral da Liga (~34.5%)')
    ax.legend(loc='lower right')
    
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 1, bar.get_y() + bar.get_height() / 2, f'{w:.1f}%', va='center', fontsize=9)

    ax.set_xlim(0, 65)
    plt.tight_layout()
    fig.savefig(fig_dir / '05_top_atletas_cartoes_1T.png')
    plt.close(fig)
    logger.info('Figura 5 salva.')


def run_eda(
    processed_dir: Path = Path('data/processed/serie_a'),
    reports_fig_dir: Path = Path('reports/figures/eda_serie_a'),
    reports_tab_dir: Path = Path('reports/tables'),
):
    logger.info('Carregando dados da Série A...')
    df_partidas, df_cartoes, df_stats, df_gols = load_datasets(processed_dir)

    logger.info('Calculando métricas descritivas por temporada...')
    df_metrics = compute_metrics_by_season(df_partidas, df_cartoes, df_stats, df_gols)

    logger.info('Executando testes de hipótese estatísticos...')
    df_tests = perform_hypothesis_tests(df_cartoes, df_stats)

    logger.info('Identificando atletas com comportamento atípico em cartões no 1T...')
    top_athletes = compute_top_athletes_cards(df_cartoes)

    reports_tab_dir.mkdir(parents=True, exist_ok=True)
    df_metrics.to_csv(reports_tab_dir / 'tabela_01_metricas_por_temporada.csv', index=False, encoding='utf-8')
    df_tests.to_csv(reports_tab_dir / 'tabela_02_testes_estatisticos_quebra.csv', index=False, encoding='utf-8')
    top_athletes.to_csv(reports_tab_dir / 'tabela_03_atletas_outliers_1T.csv', index=False, encoding='utf-8')
    logger.info('Tabelas salvas com sucesso em %s', reports_tab_dir)

    logger.info('Gerando figuras em alta resolução...')
    generate_figures(df_metrics, df_cartoes, df_stats, top_athletes, reports_fig_dir)

    logger.info('EDA concluída com sucesso!')


if __name__ == '__main__':
    run_eda()
