"""
Script gerador da Apresentação HTML Interativa do Projeto
'Impacto das Apostas Esportivas no Futebol Brasileiro (2015-2024)'

Gera o arquivo: reports/apresentacao_processo_projeto.html
Incorpora:
- Duplo modo: Dashboard Executivo (leitura contínua) e Apresentação de Slides (tela cheia com setas)
- Seções pedagógicas 'Em Bom Português' e 'Como Interpretar este Visual' para públicos não técnicos
- Dicionário express de conceitos estatísticos (p-valor, intervalos de confiança, TWFE, binomial)
- Tradução de fórmulas matemáticas para analogias práticas e intuição de negócios
- Governança completa do .agent.md (4 níveis, causalidade != correlação, pushback, checklist)
- Passo a passo das 11 fases do projeto com achados empíricos e estatísticos
- Matriz completa de 29 decisões (Estratégicas, Analíticas e Técnicas) com motivos
- Inclusão das 20 figuras analíticas em alta resolução com lightbox interativo
- Tabelas analíticas e dados do Ground Truth da Operação Penalidade Máxima com busca em tempo real
- Matriz de Riscos, Pontos Cegos e Recomendações Regulatórias
"""

import os
import re
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
TABLES_DIR = REPORTS_DIR / "tables"
OUTPUT_HTML = REPORTS_DIR / "apresentacao_processo_projeto.html"


def load_table(name: str) -> pd.DataFrame:
    path = TABLES_DIR / name
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def df_to_html_table(df: pd.DataFrame, table_id: str = "", max_rows: int = 25) -> str:
    if df.empty:
        return "<p class='no-data'>Tabela indisponível.</p>"
    sub_df = df.head(max_rows)
    return sub_df.to_html(
        classes="data-table",
        index=False,
        border=0,
        table_id=table_id,
        escape=False
    )


def generate_html():
    print("Iniciando montagem da apresentação HTML enriquecida para especialistas e não técnicos...")
    
    # Carregar tabelas analíticas
    tabela_01 = load_table("tabela_01_metricas_por_temporada.csv")
    tabela_02 = load_table("tabela_02_testes_estatisticos_quebra.csv")
    tabela_05 = load_table("tabela_05_comparacao_partidas_por_exposicao.csv")
    tabela_07 = load_table("tabela_07_comparacao_metricas_series_a_b.csv")
    tabela_08 = load_table("tabela_08_testes_estatisticos_serie_a_vs_b.csv")
    tabela_09 = load_table("tabela_09_tipologia_cartoes_serie_b.csv")
    tabela_11 = load_table("tabela_11_regressoes_twfe.csv")
    tabela_12 = load_table("tabela_12_did_event_study.csv")
    tabela_17 = load_table("tabela_17_validacao_ground_truth_pm.csv")

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Impacto das Apostas Esportivas no Futebol Brasileiro (2015–2024) | Apresentação Executiva e Metodológica</title>
  <style>
    :root {{
      --bg-primary: #0a0e17;
      --bg-secondary: #111827;
      --bg-tertiary: #1f2937;
      --bg-card: rgba(31, 41, 55, 0.7);
      --border-color: #374151;
      --border-focus: #3b82f6;
      --text-primary: #f9fafb;
      --text-secondary: #9ca3af;
      --text-muted: #6b7280;
      --accent-blue: #3b82f6;
      --accent-cyan: #06b6d4;
      --accent-emerald: #10b981;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --accent-purple: #8b5cf6;
      --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3);
      --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      --font-mono: 'JetBrains Mono', 'Fira Code', Menlo, Monaco, Consolas, monospace;
    }}

    [data-theme="light"] {{
      --bg-primary: #f8fafc;
      --bg-secondary: #ffffff;
      --bg-tertiary: #f1f5f9;
      --bg-card: rgba(255, 255, 255, 0.9);
      --border-color: #e2e8f0;
      --border-focus: #2563eb;
      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #94a3b8;
      --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: var(--font-sans);
      background-color: var(--bg-primary);
      color: var(--text-primary);
      line-height: 1.6;
      transition: background-color 0.3s ease, color 0.3s ease;
      overflow-x: hidden;
    }}

    /* HEADER & NAVIGATION */
    header.top-nav {{
      position: sticky;
      top: 0;
      z-index: 100;
      background-color: var(--bg-secondary);
      border-bottom: 1px solid var(--border-color);
      backdrop-filter: blur(8px);
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem 1.5rem;
    }}

    .nav-brand {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .nav-badge {{
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      color: #fff;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .nav-title {{
      font-size: 1rem;
      font-weight: 700;
      color: var(--text-primary);
    }}

    .nav-controls {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .btn {{
      background: var(--bg-tertiary);
      color: var(--text-primary);
      border: 1px solid var(--border-color);
      padding: 0.4rem 0.8rem;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 500;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transition: all 0.2s;
    }}

    .btn:hover {{
      background: var(--border-color);
      border-color: var(--border-focus);
    }}

    .btn-primary {{
      background: var(--accent-blue);
      color: white;
      border-color: var(--accent-blue);
    }}
    .btn-primary:hover {{
      background: #2563eb;
    }}

    .btn-active {{
      background: var(--accent-cyan);
      color: #0f172a;
      font-weight: 700;
      border-color: var(--accent-cyan);
    }}

    /* PROGRESS BAR */
    .progress-bar-container {{
      position: fixed;
      top: 56px;
      left: 0;
      width: 100%;
      height: 3px;
      background: transparent;
      z-index: 99;
    }}

    .progress-bar {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan), var(--accent-emerald));
      transition: width 0.1s ease;
    }}

    /* LAYOUT CONTAINER */
    .layout-container {{
      display: flex;
      min-height: calc(100vh - 56px);
    }}

    /* SIDEBAR (DOC MODE) */
    aside.sidebar {{
      width: 320px;
      flex-shrink: 0;
      background: var(--bg-secondary);
      border-right: 1px solid var(--border-color);
      padding: 1.25rem 0.75rem;
      overflow-y: auto;
      height: calc(100vh - 56px);
      position: sticky;
      top: 56px;
    }}

    .sidebar-section-title {{
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 0.5rem 0.75rem;
      margin-top: 0.6rem;
    }}

    .nav-item {{
      display: block;
      padding: 0.45rem 0.75rem;
      color: var(--text-secondary);
      text-decoration: none;
      font-size: 0.85rem;
      border-radius: 6px;
      margin-bottom: 0.15rem;
      transition: all 0.15s;
    }}

    .nav-item:hover, .nav-item.active {{
      background: var(--bg-tertiary);
      color: var(--accent-cyan);
      font-weight: 600;
    }}

    .nav-item span.index {{
      color: var(--text-muted);
      font-family: var(--font-mono);
      font-size: 0.75rem;
      margin-right: 0.4rem;
    }}

    /* MAIN CONTENT */
    main.main-content {{
      flex: 1;
      padding: 2.5rem;
      max-width: 1240px;
      margin: 0 auto;
    }}

    /* SLIDE MODE STYLES */
    body.slide-mode aside.sidebar {{
      display: none;
    }}

    body.slide-mode main.main-content {{
      max-width: 100%;
      padding: 0;
      margin: 0;
      height: calc(100vh - 56px);
      overflow-y: auto;
    }}

    .slide {{
      display: block;
      padding-bottom: 3.5rem;
      margin-bottom: 4rem;
      border-bottom: 1px solid var(--border-color);
    }}

    body.slide-mode .slide {{
      display: none;
      padding: 3rem 4.5rem;
      min-height: calc(100vh - 56px);
      margin-bottom: 0;
      border-bottom: none;
    }}

    body.slide-mode .slide.active {{
      display: block;
      animation: fadeIn 0.3s ease;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(8px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* SLIDE CONTROLS OVERLAY */
    .slide-navigator {{
      display: none;
      position: fixed;
      bottom: 1.5rem;
      right: 2rem;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 30px;
      padding: 0.4rem 1rem;
      box-shadow: var(--shadow-lg);
      z-index: 100;
      gap: 0.75rem;
      align-items: center;
    }}

    body.slide-mode .slide-navigator {{
      display: flex;
    }}

    .slide-counter {{
      font-size: 0.85rem;
      font-family: var(--font-mono);
      font-weight: 700;
      color: var(--text-secondary);
    }}

    /* HERO BANNER */
    .hero {{
      background: linear-gradient(135deg, rgba(37, 99, 235, 0.15) 0%, rgba(124, 58, 237, 0.15) 100%);
      border: 1px solid rgba(59, 130, 246, 0.3);
      border-radius: 12px;
      padding: 2.5rem;
      margin-bottom: 3rem;
      box-shadow: var(--shadow-md);
    }}

    .hero-meta {{
      display: flex;
      gap: 0.75rem;
      flex-wrap: wrap;
      margin-bottom: 1rem;
    }}

    .hero h1 {{
      font-size: 2.3rem;
      font-weight: 800;
      line-height: 1.25;
      margin-bottom: 1rem;
      background: linear-gradient(90deg, #60a5fa, #a78bfa);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .hero p.lead {{
      font-size: 1.15rem;
      color: var(--text-secondary);
      max-width: 950px;
      margin-bottom: 1.5rem;
    }}

    /* KPI CARDS GRID */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      margin: 1.5rem 0;
    }}

    .kpi-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      box-shadow: var(--shadow-sm);
    }}

    .kpi-label {{
      font-size: 0.75rem;
      text-transform: uppercase;
      color: var(--text-muted);
      font-weight: 700;
      letter-spacing: 0.05em;
      margin-bottom: 0.25rem;
    }}

    .kpi-value {{
      font-size: 1.8rem;
      font-weight: 800;
      color: var(--accent-cyan);
      font-family: var(--font-mono);
      line-height: 1.2;
    }}

    .kpi-subtext {{
      font-size: 0.8rem;
      color: var(--text-secondary);
      margin-top: 0.35rem;
    }}

    /* TYPOGRAPHY & SECTIONS */
    .slide-header {{
      margin-bottom: 1.75rem;
    }}

    .slide-badge {{
      display: inline-block;
      font-size: 0.75rem;
      font-family: var(--font-mono);
      font-weight: 700;
      color: var(--accent-blue);
      background: rgba(59, 130, 246, 0.15);
      border: 1px solid rgba(59, 130, 246, 0.3);
      padding: 0.2rem 0.6rem;
      border-radius: 4px;
      margin-bottom: 0.5rem;
      text-transform: uppercase;
    }}

    h2.slide-title {{
      font-size: 1.85rem;
      font-weight: 800;
      color: var(--text-primary);
      margin-bottom: 0.5rem;
    }}

    p.slide-subtitle {{
      font-size: 1.05rem;
      color: var(--text-secondary);
    }}

    h3 {{
      font-size: 1.25rem;
      font-weight: 700;
      margin: 1.5rem 0 0.75rem 0;
      color: var(--text-primary);
    }}

    /* BOXES, ALERTS & CALLOUTS */
    .alert-box {{
      border-radius: 8px;
      padding: 1.25rem;
      margin: 1.25rem 0;
      border-left: 4px solid;
    }}

    .alert-box.info {{
      background: rgba(59, 130, 246, 0.08);
      border-color: var(--accent-blue);
    }}

    .alert-box.warning {{
      background: rgba(245, 158, 11, 0.08);
      border-color: var(--accent-amber);
    }}

    .alert-box.success {{
      background: rgba(16, 185, 129, 0.08);
      border-color: var(--accent-emerald);
    }}

    .alert-box.danger {{
      background: rgba(244, 63, 94, 0.08);
      border-color: var(--accent-rose);
    }}

    .alert-title {{
      font-weight: 700;
      font-size: 0.95rem;
      margin-bottom: 0.35rem;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    /* GUIA PARA NÃO TÉCNICOS & INTERPRETAÇÃO VISUAL */
    .guide-box {{
      background: rgba(6, 182, 212, 0.06);
      border: 1px solid rgba(6, 182, 212, 0.3);
      border-radius: 8px;
      padding: 1.25rem;
      margin: 1.25rem 0;
    }}
    .guide-header {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-weight: 700;
      color: var(--accent-cyan);
      font-size: 0.95rem;
      margin-bottom: 0.5rem;
    }}

    .how-to-read-box {{
      background: rgba(139, 92, 246, 0.06);
      border: 1px solid rgba(139, 92, 246, 0.3);
      border-radius: 8px;
      padding: 1.25rem;
      margin: 1.25rem 0;
    }}
    .how-to-read-header {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-weight: 700;
      color: var(--accent-purple);
      font-size: 0.95rem;
      margin-bottom: 0.5rem;
    }}

    .formula-box {{
      background: rgba(245, 158, 11, 0.06);
      border: 1px solid rgba(245, 158, 11, 0.3);
      border-radius: 8px;
      padding: 1.25rem;
      margin: 1.25rem 0;
    }}
    .formula-header {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-weight: 700;
      color: var(--accent-amber);
      font-size: 0.95rem;
      margin-bottom: 0.5rem;
    }}

    .dictionary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1rem;
      margin: 1rem 0;
    }}
    .dictionary-item {{
      background: var(--bg-tertiary);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 0.9rem;
    }}
    .dictionary-term {{
      font-weight: 700;
      font-size: 0.9rem;
      color: var(--accent-blue);
      margin-bottom: 0.25rem;
    }}
    .dictionary-def {{
      font-size: 0.85rem;
      color: var(--text-secondary);
    }}

    /* CODE CALLOUT */
    .code-callout {{
      background: #0d1117;
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1rem;
      margin: 1rem 0;
      font-family: var(--font-mono);
      font-size: 0.85rem;
      color: #58a6ff;
      overflow-x: auto;
    }}

    /* DECISIONS CARDS & FILTERS */
    .filter-bar {{
      display: flex;
      gap: 0.5rem;
      margin: 1rem 0 1.5rem 0;
      flex-wrap: wrap;
    }}

    .decisions-grid {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 1rem;
      margin: 1.5rem 0;
    }}

    .decision-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1.25rem;
      border-left: 4px solid;
      transition: transform 0.15s ease;
    }}

    .decision-card:hover {{
      transform: translateX(4px);
    }}

    .decision-card.est {{ border-left-color: var(--accent-purple); }}
    .decision-card.ana {{ border-left-color: var(--accent-cyan); }}
    .decision-card.tec {{ border-left-color: var(--accent-emerald); }}

    .decision-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}

    .decision-code {{
      font-family: var(--font-mono);
      font-size: 0.85rem;
      font-weight: 700;
    }}

    .decision-tag {{
      font-size: 0.7rem;
      font-weight: 700;
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
      text-transform: uppercase;
    }}

    .tag-est {{ background: rgba(139, 92, 246, 0.2); color: var(--accent-purple); }}
    .tag-ana {{ background: rgba(6, 182, 212, 0.2); color: var(--accent-cyan); }}
    .tag-tec {{ background: rgba(16, 185, 129, 0.2); color: var(--accent-emerald); }}

    .decision-title {{
      font-size: 1.05rem;
      font-weight: 700;
      margin-bottom: 0.4rem;
    }}

    .decision-body {{
      font-size: 0.9rem;
      color: var(--text-secondary);
    }}

    .decision-motive {{
      margin-top: 0.5rem;
      font-size: 0.85rem;
      background: var(--bg-tertiary);
      padding: 0.5rem 0.75rem;
      border-radius: 4px;
      border-left: 2px solid var(--text-muted);
    }}

    /* IMAGES & GALLERY */
    .figure-wrapper {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1rem;
      margin: 1.5rem 0;
      text-align: center;
    }}

    .figure-wrapper img {{
      max-width: 100%;
      height: auto;
      border-radius: 6px;
      cursor: zoom-in;
      box-shadow: var(--shadow-md);
      transition: transform 0.2s ease;
    }}

    .figure-wrapper img:hover {{
      transform: scale(1.01);
    }}

    .figure-caption {{
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-top: 0.75rem;
      font-weight: 500;
    }}

    .figure-grid-2 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 1.25rem;
      margin: 1.5rem 0;
    }}

    /* TABLES */
    .table-container {{
      overflow-x: auto;
      margin: 1.5rem 0;
      border: 1px solid var(--border-color);
      border-radius: 8px;
      background: var(--bg-card);
    }}

    table.data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      text-align: left;
    }}

    table.data-table th {{
      background: var(--bg-tertiary);
      color: var(--text-primary);
      padding: 0.75rem 1rem;
      font-weight: 700;
      border-bottom: 1px solid var(--border-color);
      white-space: nowrap;
    }}

    table.data-table td {{
      padding: 0.65rem 1rem;
      border-bottom: 1px solid var(--border-color);
      color: var(--text-secondary);
    }}

    table.data-table tr:hover td {{
      background: rgba(255, 255, 255, 0.02);
      color: var(--text-primary);
    }}

    /* LIGHTBOX MODAL */
    .lightbox-modal {{
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.9);
      z-index: 999;
      justify-content: center;
      align-items: center;
      padding: 2rem;
    }}

    .lightbox-modal.active {{
      display: flex;
    }}

    .lightbox-modal img {{
      max-width: 95vw;
      max-height: 90vh;
      object-fit: contain;
      border-radius: 8px;
      box-shadow: 0 0 30px rgba(0, 0, 0, 0.8);
    }}

    .lightbox-close {{
      position: absolute;
      top: 1.5rem;
      right: 2rem;
      color: white;
      font-size: 2rem;
      cursor: pointer;
      font-weight: bold;
    }}

    /* CHECKLIST DO AGENTE */
    .checklist-container {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1.5rem;
      margin: 1.5rem 0;
    }}

    .checklist-item {{
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
      padding: 0.5rem 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      font-size: 0.9rem;
    }}

    .checklist-item input[type="checkbox"] {{
      margin-top: 0.25rem;
      accent-color: var(--accent-emerald);
      cursor: pointer;
    }}

    /* FLOW DIAGRAM (CSS/SVG) */
    .flow-diagram {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 0.75rem;
      overflow-x: auto;
      padding: 1.5rem 0.5rem;
      margin: 1.5rem 0;
    }}

    .flow-step {{
      background: var(--bg-tertiary);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1rem;
      min-width: 160px;
      text-align: center;
      position: relative;
    }}

    .flow-step.active-step {{
      border-color: var(--accent-cyan);
      box-shadow: 0 0 10px rgba(6, 182, 212, 0.2);
    }}

    .flow-num {{
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--accent-blue);
      font-weight: 700;
    }}

    .flow-name {{
      font-weight: 700;
      font-size: 0.9rem;
      margin: 0.3rem 0;
    }}

    .flow-arrow {{
      color: var(--text-muted);
      font-size: 1.2rem;
      font-weight: bold;
    }}

    /* SEARCH INPUT */
    .table-search {{
      width: 100%;
      max-width: 320px;
      background: var(--bg-tertiary);
      color: var(--text-primary);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 0.45rem 0.8rem;
      margin-bottom: 0.75rem;
      font-size: 0.85rem;
    }}

    /* RESPONSIVE */
    @media (max-width: 900px) {{
      aside.sidebar {{
        display: none;
      }}
      main.main-content {{
        padding: 1.5rem;
      }}
      .figure-grid-2 {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>

  <!-- HEADER -->
  <header class="top-nav">
    <div class="nav-brand">
      <span class="nav-badge">White Paper Executivo</span>
      <span class="nav-title">Apostas Esportivas no Futebol Brasileiro</span>
    </div>
    <div class="nav-controls">
      <button class="btn btn-active" id="btn-mode-dash" onclick="setMode('dashboard')">📑 Modo Dashboard</button>
      <button class="btn" id="btn-mode-slide" onclick="setMode('slide')">📽️ Modo Slides</button>
      <button class="btn" id="btn-theme" onclick="toggleTheme()">🌓 Tema</button>
    </div>
  </header>

  <!-- PROGRESS BAR -->
  <div class="progress-bar-container">
    <div class="progress-bar" id="progressBar"></div>
  </div>

  <div class="layout-container">
    <!-- SIDEBAR -->
    <aside class="sidebar">
      <div class="sidebar-section-title">Navegação Geral</div>
      <a href="#hero" class="nav-item active"><span class="index">00</span> Visão Executiva</a>
      <a href="#governance" class="nav-item"><span class="index">01</span> Governança (.agent.md)</a>
      <div class="sidebar-section-title">Fases da Pesquisa</div>
      <a href="#phase-1" class="nav-item"><span class="index">02</span> Fase 1: Auditoria Bruta</a>
      <a href="#phase-2" class="nav-item"><span class="index">03</span> Fase 2: Limpeza & Features</a>
      <a href="#phase-3" class="nav-item"><span class="index">04</span> Fase 3: Paradoxo Disciplinar</a>
      <a href="#phase-4" class="nav-item"><span class="index">05</span> Fase 4: Exposição a Bets</a>
      <a href="#phase-5" class="nav-item"><span class="index">06</span> Fase 5: Faltas 2024 & Parser CBF</a>
      <a href="#phase-6" class="nav-item"><span class="index">07</span> Fase 6: Série B & Penalidade M.</a>
      <a href="#phase-7" class="nav-item"><span class="index">08</span> Fase 7: Econometria Causal TWFE</a>
      <a href="#phase-8" class="nav-item"><span class="index">09</span> Fase 8: Triagem de Integridade</a>
      <a href="#phase-9" class="nav-item"><span class="index">10</span> Fases 9-11: Ciência Aberta</a>
      <div class="sidebar-section-title">Síntese e Auditoria</div>
      <a href="#recommendations" class="nav-item"><span class="index">11</span> Recomendações SPA/CBF</a>
      <a href="#decisions-matrix" class="nav-item"><span class="index">12</span> Matriz de Decisões (29)</a>
      <a href="#risks-checklist" class="nav-item"><span class="index">13</span> Riscos & Checklist Final</a>
    </aside>

    <!-- MAIN CONTENT -->
    <main class="main-content" id="mainContainer">

      <!-- SLIDE 0: HERO & EXECUTIVE SUMMARY -->
      <section class="slide" id="hero">
        <div class="hero">
          <div class="hero-meta">
            <span class="slide-badge">Relatório Final Integrado</span>
            <span class="slide-badge" style="color: var(--accent-emerald); border-color: var(--accent-emerald);">100% Reprodutível</span>
            <span class="slide-badge" style="color: var(--accent-amber); border-color: var(--accent-amber);">11 Fases Concluídas</span>
          </div>
          <h1>O Impacto das Casas de Apostas no Futebol Brasileiro</h1>
          <p class="lead">
            Evidências Empíricas, Inferência Causal em Painel (TWFE) e um Sistema de Triagem Algorítmica para a Integridade Esportiva (2015–2024).
          </p>

          <div class="kpi-grid">
            <div class="kpi-card">
              <span class="kpi-label">Partidas Harmonizadas</span>
              <span class="kpi-value">4.939</span>
              <span class="kpi-subtext">4.179 Série A + 760 Série B</span>
            </div>
            <div class="kpi-card">
              <span class="kpi-label">Cartões Individuais</span>
              <span class="kpi-value">24.624</span>
              <span class="kpi-subtext">20.953 Série A + 3.671 Série B</span>
            </div>
            <div class="kpi-card">
              <span class="kpi-label">Paradoxo Disciplinar</span>
              <span class="kpi-value">+37,1%</span>
              <span class="kpi-subtext">Taxa conversão faltas → cartões</span>
            </div>
            <div class="kpi-card">
              <span class="kpi-label">Efeito Causal TWFE</span>
              <span class="kpi-value">+0,267*</span>
              <span class="kpi-subtext">Cartões/jogo por clube (p = 0,0064)</span>
            </div>
            <div class="kpi-card">
              <span class="kpi-label">Sensibilidade Ground Truth</span>
              <span class="kpi-value">100%</span>
              <span class="kpi-subtext">14/14 Casos da Penalidade Máxima</span>
            </div>
          </div>
        </div>

        <div class="guide-box">
          <div class="guide-header">🧭 Tradução para Não Especialistas: O Que Este Estudo Descobriu?</div>
          <p style="color:var(--text-secondary); font-size:0.92rem; line-height:1.6;">
            Em termos diretos, esta pesquisa investigou duas grandes perguntas que todo torcedor, dirigente e jornalista faz:
            <br><strong>1. As casas de aposta mudaram o jogo?</strong> Sim. O estudo provou matematicamente que quando os clubes assinam patrocínios com empresas de aposta, as partidas recebem mais cartões amarelos da arbitragem, mesmo sem que os jogadores tenham feito mais faltas físicas. Houve um aumento real no rigor do apito.
            <br><strong>2. Os clubes patrocinados mandam os atletas tomarem cartões?</strong> Não. Provamos que a manipulação de cartões precoces (no primeiro tempo) <strong>não é uma política dos clubes</strong>, mas sim um desvio de conduta criminoso e individual de atletas aliciados por intermediários (spot-fixing).
          </p>
        </div>
      </section>

      <!-- SLIDE 1: GOVERNANCE & METHODOLOGY (.agent.md) -->
      <section class="slide" id="governance">
        <div class="slide-header">
          <span class="slide-badge">Módulo 00</span>
          <h2 class="slide-title">Governança Científica e Filosofia Analítica (.agent.md)</h2>
          <p class="slide-subtitle">A atuação do agente como Parceiro Analítico Crítico e os 4 Níveis Fundamentais de Raciocínio.</p>
        </div>

        <div class="flow-diagram">
          <div class="flow-step active-step">
            <span class="flow-num">NÍVEL 1</span>
            <div class="flow-name">Fatos</div>
            <div style="font-size:0.75rem; color:var(--text-secondary);">Dados brutos observados diretamente em campo</div>
          </div>
          <span class="flow-arrow">→</span>
          <div class="flow-step">
            <span class="flow-num">NÍVEL 2</span>
            <div class="flow-name">Hipóteses</div>
            <div style="font-size:0.75rem; color:var(--text-secondary);">Explicações concorrentes a testar formalmente</div>
          </div>
          <span class="flow-arrow">→</span>
          <div class="flow-step">
            <span class="flow-num">NÍVEL 3</span>
            <div class="flow-name">Resultados</div>
            <div style="font-size:0.75rem; color:var(--text-secondary);">Estatística inferencial e modelos causais</div>
          </div>
          <span class="flow-arrow">→</span>
          <div class="flow-step">
            <span class="flow-num">NÍVEL 4</span>
            <div class="flow-name">Decisões</div>
            <div style="font-size:0.75rem; color:var(--text-secondary);">Escolha humana e estratégia institucional</div>
          </div>
        </div>

        <div class="guide-box">
          <div class="guide-header">📖 Dicionário Express do Leitor Não Técnico (O Guia para Entender Tudo em Minutos)</div>
          <p style="color:var(--text-secondary); font-size:0.9rem; margin-bottom:1rem;">
            Você não precisa ser econometrista ou cientista de dados para acompanhar este relatório. Guarde estas 8 analogias simples:
          </p>
          <div class="dictionary-grid">
            <div class="dictionary-item">
              <div class="dictionary-term">1. p-valor (p-value) — "O Termômetro do Acaso"</div>
              <div class="dictionary-def">Responde à pergunta: <em>'Qual a chance desse resultado ser mera coincidência?'</em>. Quando o p-valor é minúsculo (ex: <strong>p &lt; 0,01</strong>), a chance de sorte é menor que 1%. Temos certeza científica de que o efeito é real.</div>
            </div>
            <div class="dictionary-item">
              <div class="dictionary-term">2. Intervalo de Confiança (IC 95%) — "Margem de Segurança"</div>
              <div class="dictionary-def">Em vez de cravar um número isolado, damos uma faixa com 95% de certeza. Se a margem de segurança do aumento de cartões não cruza o zero, o impacto é cientificamente incontestável.</div>
            </div>
            <div class="dictionary-item">
              <div class="dictionary-term">3. Efeitos Fixos (TWFE) — "Comparar o Time Consigo Mesmo"</div>
              <div class="dictionary-def">Em vez de comparar o Flamengo com o Cuiabá (realidades opostas), compara-se o <strong>Flamengo com bet contra o próprio Flamengo sem bet</strong>, anulando peso de torcida e tradição para isolar o choque da aposta.</div>
            </div>
            <div class="dictionary-item">
              <div class="dictionary-term">4. Tendências Paralelas — "A Régua de Controle Causal"</div>
              <div class="dictionary-def">Antes de fechar patrocínio de aposta, clubes patrocinados e não-patrocinados caminhavam no mesmo ritmo (linhas paralelas). Quando o contrato entra em vigor, a linha dos patrocinados salta, provando causa e efeito.</div>
            </div>
            <div class="dictionary-item">
              <div class="dictionary-term">5. Taxa de Conversão &tau; — "A Mão do Árbitro"</div>
              <div class="dictionary-def">Quantas faltas o juiz tolera antes de sacar um cartão. Em 2017 eram 6,2 faltas por cartão; em 2024 caiu para 4,5 faltas. O juiz ficou <strong>37% mais rápido para punir</strong>.</div>
            </div>
            <div class="dictionary-item">
              <div class="dictionary-term">6. Teste Binomial — "O Teste da Moeda Viciada"</div>
              <div class="dictionary-def">No futebol, 1 em cada 3 cartões sai no 1º tempo (~35%). Se um atleta investigado tem 7 cartões encomendados e todos os 7 saem no 1º tempo, a chance dessa coincidência é de apenas <strong>0,06%</strong> ($p &lt; 0,001$).</div>
            </div>
            <div class="dictionary-item">
              <div class="dictionary-term">7. Z-Score &amp; Cohen's d — "Distância e Tamanho do Efeito"</div>
              <div class="dictionary-def">O Z-Score mede quantos 'degraus' um jogo está longe da média normal ($Z &gt; 3$ é raríssimo). O Cohen's d mede se a mudança é perceptível no mundo real (leve, moderada ou severa).</div>
            </div>
            <div class="dictionary-item">
              <div class="dictionary-term">8. Score de Anomalia — "O Scanner de Raio-X de Auditoria"</div>
              <div class="dictionary-def">Como o raio-X do aeroporto: aponta malas atípicas para checagem de compliance. Um score alto indica <strong>atipicidade estatística para auditoria humana</strong>, nunca uma acusação ou prova penal de culpa.</div>
            </div>
          </div>
        </div>

        <div class="alert-box warning">
          <div class="alert-title">⚠️ O Mandamento Central da Causalidade: Correlação ≠ Causalidade</div>
          <p>
            O aumento simultâneo da publicidade de bets e do volume de cartões no futebol brasileiro <strong>NÃO autoriza a conclusão automática de que apostas causam violência ou fraude</strong>.
            Fatores de confusão sistêmicos — como a implementação do VAR (2019), a política de tolerância zero com reclamações da comissão de arbitragem e a pandemia de COVID-19 — exigem controle estatístico formal
            via painel econométrico com efeitos fixos e testes de tendências paralelas.
          </p>
        </div>

        <h3>A Taxonomia Tripartite de Decisões</h3>
        <p style="color:var(--text-secondary); margin-bottom:1rem;">Conforme a Seção 17 do <code>.agent.md</code>, as escolhas do projeto foram rigorosamente segregadas por alçada:</p>

        <div class="decisions-grid">
          <div class="decision-card tec">
            <div class="decision-header">
              <span class="decision-code">DECISÃO TÉCNICA</span>
              <span class="decision-tag tag-tec">Alçada: Agente Decide</span>
            </div>
            <div class="decision-title">Autonomia Técnica e Rigor de Engenharia</div>
            <div class="decision-body">
              Escolha de bibliotecas (pandas, statsmodels, pyarrow, scipy), algoritmos matemáticos (testes binomiais, OLS clusterizado), arquitetura de pastas, persistência imutável e testes automatizados com pytest.
            </div>
          </div>

          <div class="decision-card ana">
            <div class="decision-header">
              <span class="decision-code">DECISÃO ANALÍTICA</span>
              <span class="decision-tag tag-ana">Alçada: Agente Recomenda / Validação se Relevante</span>
            </div>
            <div class="decision-title">Metodologia e Desenho Experimental</div>
            <div class="decision-body">
              Definição de janelas de contraste (Pré-Bets 2014–2018 vs Alta Exposição 2022–2024), temporalidade por temporada esportiva, criação do índice <code>BET_EXPOSURE</code> e limiares de triagem por percentis.
            </div>
          </div>

          <div class="decision-card est">
            <div class="decision-header">
              <span class="decision-code">DECISÃO ESTRATÉGICA / NEGÓCIO</span>
              <span class="decision-tag tag-est">Alçada: Usuário Decide</span>
            </div>
            <div class="decision-title">Priorização e Trade-offs Estratégicos</div>
            <div class="decision-body">
              Determinar que volume financeiro real é dado sigiloso fora do caminho crítico, aprovar o uso de súmulas CBF para a Série B e adotar a base da Operação Penalidade Máxima como ground truth empírico.
            </div>
          </div>
        </div>

        <div class="alert-box danger">
          <div class="alert-title">🛡️ Pushback Analítico e Governança Ética</div>
          <p>
            O agente não deve "torturar dados" para confirmar suspeitas ou hipóteses preconcebidas. Se a evidência estatística for nula ou inconclusiva (como comprovado no teste de cartões no 1º tempo em nível de clube),
            o resultado negativo é preservado na íntegra. Além disso, scores elevados de triagem constituem <strong>anomalias estatísticas sob escrutínio de conformidade, e NUNCA prova penal de culpa</strong>.
          </p>
        </div>
      </section>

      <!-- SLIDE 2: PHASE 1 (RAW DATA & AUDIT) -->
      <section class="slide" id="phase-1">
        <div class="slide-header">
          <span class="slide-badge">Fase 1</span>
          <h2 class="slide-title">Mapeamento, Ingestão e Auditoria de Dados Brutos (Série A)</h2>
          <p class="slide-subtitle">Construção do alicerce empírico, manifestos criptográficos e diagnóstico da pandemia.</p>
        </div>

        <div class="kpi-grid">
          <div class="kpi-card">
            <span class="kpi-label">Partidas Auditadas</span>
            <span class="kpi-value">8.785</span>
            <span class="kpi-subtext">2003 a 2024 (22 edições)</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-label">Cartões Individuais</span>
            <span class="kpi-value">20.953</span>
            <span class="kpi-subtext">2014 a 2024 (11 temporadas)</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-label">Cobertura de Cartões</span>
            <span class="kpi-value">98,8%</span>
            <span class="kpi-subtext">Partidas com scouts completos</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-label">Hash SHA-256</span>
            <span class="kpi-value">100%</span>
            <span class="kpi-subtext">Manifestos em data/raw/</span>
          </div>
        </div>

        <div class="guide-box">
          <div class="guide-header">🧭 Em Bom Português: Por que o ano de 2020 engana quem olha a folhinha do calendário?</div>
          <p style="color:var(--text-secondary); font-size:0.9rem;">
            Por causa da pandemia de COVID-19, o Campeonato Brasileiro de 2020 foi paralisado e terminou apenas no final de fevereiro de 2021 (foram 112 jogos jogados em 2021 valendo pelo torneio de 2020!).
            Se um analista inexperiente apenas olhasse a data civil do relógio, 2020 pareceria um ano 'anão' (com apenas 268 partidas) e 2021 pareceria um ano 'gigante' (com 492 jogos).
            Nossa auditoria corrigiu isso, amarrando cada partida à sua <strong>temporada oficial</strong>.
          </p>
        </div>

        <div class="code-callout">
          # Arquitetura de Ingestão: src/ingestion/download_adaoduque.py<br>
          Destino: data/raw/adaoduque/ | Hash Manifesto: manifest.json (SHA-256)
        </div>

        <h3>Achados Críticos da Auditoria Estatística</h3>
        <ul style="color:var(--text-secondary); margin-left:1.5rem; margin-bottom:1.5rem;">
          <li><strong>Integridade dos Cartões (2014–2024):</strong> Identificou-se que a base do Adão Duque possui integridade excepcional para advertências disciplinares individuais (atleta, time, minuto exato, posição e cartão amarelo/vermelho).</li>
          <li><strong>A Lacuna Crítica de Faltas em 2024:</strong> A auditoria detectou imediatamente que o scraper original capturou valores zerados para faltas e escanteios na temporada de 2024 (o widget do Google não retornou o array de estatísticas). Essa falha foi isolada e solucionada posteriormente na Fase 5 com a ingestão do Sofascore.</li>
          <li><strong>A Distorção do Calendário COVID-19:</strong> Na contagem ingênua por ano civil, o ano de 2020 registrou apenas 268 jogos e 2021 registrou 492 jogos. O Brasileirão 2020 foi concluído apenas em 25/02/2021 (112 partidas ocorreram em janeiro e fevereiro de 2021).</li>
        </ul>

        <h3>Decisões Adotadas nesta Etapa</h3>
        <div class="decisions-grid">
          <div class="decision-card tec">
            <div class="decision-header">
              <span class="decision-code">D-TEC-01 & D-TEC-02</span>
              <span class="decision-tag tag-tec">Técnica</span>
            </div>
            <div class="decision-title">Imutabilidade de Dados Brutos e Rastreabilidade Criptográfica</div>
            <div class="decision-body">O diretório <code>data/raw/adaoduque/</code> foi blindado como estritamente de leitura (read-only). Todos os 5 arquivos ingeridos foram catalogados em <code>manifest.json</code> com hashes SHA-256 para auditoria reprodutível.</div>
          </div>
          <div class="decision-card ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-01</span>
              <span class="decision-tag tag-ana">Analítica</span>
            </div>
            <div class="decision-title">Temporalidade por Temporada/Edição e não Ano Civil</div>
            <div class="decision-body">Definiu-se que toda agregação e cálculo econométrico devem utilizar a variável <code>temporada</code> (edição da competição), vinculando as 112 partidas de 2021 à temporada 2020, eliminando o viés pandêmico.</div>
          </div>
        </div>
      </section>

      <!-- SLIDE 3: PHASE 2 (CLEANING & FEATURES) -->
      <section class="slide" id="phase-2">
        <div class="slide-header">
          <span class="slide-badge">Fase 2</span>
          <h2 class="slide-title">Limpeza, Normalização e Engenharia de Features</h2>
          <p class="slide-subtitle">Tratamento de strings UTF-8, minutagem contínua e persistência dual Parquet/CSV.</p>
        </div>

        <div class="code-callout">
          # Pipeline de Normalização: src/cleaning/clean_serie_a.py<br>
          Testes Unitários: tests/test_clean_serie_a.py (100% de Aprovação via Pytest)
        </div>

        <div class="formula-box">
          <div class="formula-header">🧮 Traduzindo a Matemática: A Linha Contínua do Tempo (Sem Amassar os Acréscimos)</div>
          <p style="color:var(--text-secondary); font-size:0.9rem;">
            Quando o árbitro dá um cartão aos <strong>45+2'</strong> ou <strong>90+5'</strong>, a maioria dos sites salva apenas o minuto '45' ou '90'.
            Isso gerava um gráfico distorcido com uma parede artificial no minuto 45 e no minuto 90.
            Nossa fórmula decompôs o tempo em:
            <br><code>minuto_continuo = minuto_nominal + acrescimo</code> &nbsp; (ex.: 45 + 2 = <strong>47</strong>; 90 + 5 = <strong>95</strong>).
            <br>Assim, a linha do tempo estica suavemente e conseguimos enxergar com exatidão científica os cartões aplicados nos momentos de desespero e catimba.
          </p>
        </div>

        <h3>Padronização Canônica de Clubes e Atletas</h3>
        <p style="color:var(--text-secondary); margin-bottom:1rem;">
          Normalização de variações ortográficas históricas para 45 agremiações (ex: "Athletico-PR" vs. "Atlético-PR", "São Paulo" vs. "Sao Paulo", "América-MG" vs. "America-MG") e geração de slugs únicos preservando os nomes originais acentuados.
        </p>

        <div class="decisions-grid">
          <div class="decision-card tec">
            <div class="decision-header">
              <span class="decision-code">D-TEC-04</span>
              <span class="decision-tag tag-tec">Técnica</span>
            </div>
            <div class="decision-title">Persistência Dual em Apache Parquet e CSV UTF-8</div>
            <div class="decision-body">Gravação simultânea em Parquet colunar via PyArrow (alta performance para consultas analíticas complexas) e CSV (inspeção rápida por auditores externos), acompanhada de <code>manifest_processed.json</code>.</div>
          </div>
          <div class="decision-card ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-04</span>
              <span class="decision-tag tag-ana">Analítica</span>
            </div>
            <div class="decision-title">Minutagem Contínua e Decomposição de Acréscimos</div>
            <div class="decision-body">Criar a variável <code>minuto_continuo</code> somando o minuto nominal aos acréscimos arbitrais, viabilizando curvas de densidade e sobrevivência temporal.</div>
          </div>
        </div>
      </section>

      <!-- SLIDE 4: PHASE 3 (EDA SERIE A & DISCIPLINARY PARADOX) -->
      <section class="slide" id="phase-3">
        <div class="slide-header">
          <span class="slide-badge">Fase 3</span>
          <h2 class="slide-title">EDA Profunda da Série A & O Paradoxo Disciplinar</h2>
          <p class="slide-subtitle">A ruptura estrutural entre faltas físicas e punições disciplinares (2014–2024).</p>
        </div>

        <div class="code-callout">
          # Análise Exploratória: src/analysis/eda_serie_a.py<br>
          Relatório Técnico: reports/analysis/02_eda_profunda_serie_a.md
        </div>

        <div class="figure-grid-2">
          <div class="figure-wrapper">
            <img src="figures/eda_serie_a/01_evolucao_cartoes_por_jogo.png" alt="Evolução de Cartões por Jogo" onclick="openLightbox(this.src)">
            <div class="figure-caption">Figura 1: Média de cartões por jogo com marcos cronológicos (Legalização 2018, VAR 2019 e Escândalo 2022).</div>
          </div>
          <div class="figure-wrapper">
            <img src="figures/eda_serie_a/02_evolucao_faltas_e_taxa_conversao.png" alt="O Paradoxo Disciplinar" onclick="openLightbox(this.src)">
            <div class="figure-caption">Figura 2: O Paradoxo Disciplinar — Declínio contínuo de faltas vs. escalada da taxa de conversão em cartões.</div>
          </div>
        </div>

        <div class="how-to-read-box">
          <div class="how-to-read-header">👁️ Como Ler e Interpretar os Gráficos 1 e 2</div>
          <p style="color:var(--text-secondary); font-size:0.9rem; line-height:1.5;">
            <strong>Na Figura 1:</strong> A linha azul mostra a média anual de cartões por partida. A faixa sombreada ao redor é a margem de segurança estatística. As três linhas pontilhadas marcam eventos reais no tempo: a Lei das Bets em 2018, o VAR em 2019 e a Operação Penalidade Máxima em 2022. Note como a curva de cartões atinge os maiores patamares históricos justamente no triênio 2022–2024.
            <br><strong>Na Figura 2 (O Movimento de Tesoura):</strong> Este gráfico possui duas réguas verticais. À esquerda (linha vermelha), estão as faltas por jogo, que <strong>caem continuamente</strong> de 31 para 25. À direita (linha azul), está a taxa de cartões por falta, que <strong>dispara</strong> de 16% para 22%. Esse cruzamento é o <em>Paradoxo Disciplinar</em>: menos violência física em campo, mas árbitros aplicando muito mais cartões.
          </p>
        </div>

        <div class="formula-box">
          <div class="formula-header">🧮 Traduzindo a Taxa de Conversão Faltas-Cartões (tau = Cartões / Faltas)</div>
          <p style="color:var(--text-secondary); font-size:0.9rem;">
            Essa fórmula mede a <strong>sensibilidade da mão do árbitro</strong>.
            <br>• Em 2017 ($\tau = 0,1617$): o árbitro precisava apitar em média <strong>6,2 faltas</strong> para mostrar um cartão amarelo.
            <br>• Em 2024 ($\tau = 0,2198$): a cada <strong>4,5 faltas</strong> o juiz já saca o cartão do bolso. A tolerância arbitral encurtou em <strong>37%</strong>.
          </p>
        </div>

        <h3>Os Três Achados Estatísticos Fundamentais da EDA</h3>
        <ol style="color:var(--text-secondary); margin-left:1.5rem; margin-bottom:1.5rem;">
          <li><strong>Pico Histórico de Cartões no Triênio 2022–2024:</strong> A média saltou de 5,05 (2014–2018) para 5,47 cartões/jogo (2022–2024), um salto de <strong>+8,20% ($p = 4,01 \times 10^{{-6}}$)</strong>. O ano de 2023 bateu o recorde absoluto de cartões totais (2.118) e 2024 o recorde de expulsões (128 vermelhos).</li>
          <li><strong>O Paradoxo Disciplinar Consolidado:</strong> Enquanto as faltas por jogo caíram continuamente de 31,41 (2017) para a mínima histórica de 25,36 (2024), a taxa de conversão subiu <strong>+37,1%</strong> (atingindo 0,2198 em 2024 — 1 cartão a cada 4,5 faltas). O jogo tornou-se estatisticamente menos faltoso, porém arbitralmente muito mais punitivo.</li>
          <li><strong>Anomalia Individual de Cartões no 1º Tempo:</strong> Na média da liga, 34,5% dos cartões ocorrem no 1º tempo. Contudo, detectou-se um grupo de atletas com mais de 60% de suas advertências na etapa inicial. Atletas confessos na Operação Penalidade Máxima (Gabriel Tota e Paulo Miranda) apresentaram exatamente esse padrão.</li>
        </ol>

        <div class="figure-grid-2">
          <div class="figure-wrapper">
            <img src="figures/eda_serie_a/03_distribuicao_minutagem_cartoes.png" alt="Distribuição de Minutagem" onclick="openLightbox(this.src)">
            <div class="figure-caption">Figura 3: Curva de densidade (KDE) da minutagem dos cartões antes vs. depois da legalização de apostas.</div>
          </div>
          <div class="figure-wrapper">
            <img src="figures/eda_serie_a/05_top_atletas_cartoes_1T.png" alt="Top Atletas 1T" onclick="openLightbox(this.src)">
            <div class="figure-caption">Figura 4: Ranking de atletas com concentração anômala de advertências no 1º tempo.</div>
          </div>
        </div>

        <div class="how-to-read-box">
          <div class="how-to-read-header">👁️ Como Ler as Figuras 3 e 4</div>
          <p style="color:var(--text-secondary); font-size:0.9rem; line-height:1.5;">
            <strong>Na Figura 3 (A Onda de Probabilidade KDE):</strong> As linhas mostram em quais minutos do jogo é mais provável sair um cartão. Repare nos dois grandes morros: o primeiro aos 45 minutos e o segundo aos 90 minutos. A curva pós-2018 (laranja) é mais alta no final do jogo, refletindo o novo rigor com acréscimos longos.
            <br><strong>Na Figura 4 (Ranking de Atletas no 1º Tempo):</strong> A linha tracejada vermelha marca a normalidade de campo (35%). As barras mostram jogadores que fogem radicalmente dessa média, acumulando 60% a 70% de todos os seus cartões antes do intervalo.
          </p>
        </div>

        <h3>Testes Estatísticos de Hipótese (Tabela 02)</h3>
        <div class="table-container">
          {df_to_html_table(tabela_02, "tabela_02")}
        </div>
      </section>

      <!-- SLIDE 5: PHASE 4 (BETTING EXPOSURE & DOSE RESPONSE) -->
      <section class="slide" id="phase-4">
        <div class="slide-header">
          <span class="slide-badge">Fase 4</span>
          <h2 class="slide-title">Camada de Exposição às Apostas (MVP 2) & Gradiente Dose-Resposta</h2>
          <p class="slide-subtitle">Construção censitária de patrocínios, Google Trends e correlação de mercado.</p>
        </div>

        <div class="code-callout">
          # Ingestão & Limpeza de Patrocínios: src/ingestion/build_betting_data.py & clean_betting.py<br>
          Dataset: data/processed/betting/exposicao_clubes_temporada.parquet (200 registros de clube-ano)
        </div>

        <div class="figure-grid-2">
          <div class="figure-wrapper">
            <img src="figures/eda_bets/02_penetracao_patrocinios_serie_a.png" alt="Penetração de Patrocínios" onclick="openLightbox(this.src)">
            <div class="figure-caption">Figura 5: Penetração de patrocínios de apostas nos clubes da Série A (2015–2024).</div>
          </div>
          <div class="figure-wrapper">
            <img src="figures/eda_bets/01_evolucao_google_trends_e_marcos.png" alt="Google Trends Brasil" onclick="openLightbox(this.src)">
            <div class="figure-caption">Figura 6: Série temporal de buscas no Google Trends e marcos regulatórios brasileiros.</div>
          </div>
        </div>

        <div class="formula-box">
          <div class="formula-header">🧮 Traduzindo a Fórmula do BET_EXPOSURE (Nota de 0 a 100 de Exposição)</div>
          <p style="color:var(--text-secondary); font-size:0.9rem;">
            $$\text{{BET\_EXPOSURE}}_{{\text{{clube}}}} = 0,75 \cdot S_{{\text{{pos}}}} + 0,25 \cdot S_{{\text{{qtd}}}}$$
            <strong>O que significa na prática:</strong> Nem todo patrocínio tem o mesmo peso visual. O patrocínio máster (no peito da camisa) vale <strong>75% da nota</strong> porque é o que mais aparece na TV e gera engajamento. Patrocínios secundários (costas, omoplatas, calções) somam os <strong>25% restantes</strong>. Um clube sem patrocinador de apostas tem nota <strong>0,0</strong>; um clube com bet máster exclusiva tem nota máxima <strong>1,0 (ou 100%)</strong>.
          </p>
        </div>

        <h3>O Gradiente Empírico de Dose-Resposta (2019–2024)</h3>
        <p style="color:var(--text-secondary); margin-bottom:1rem;">
          Estratificando as 2.280 partidas contemporâneas da Série A pelo grau de exposição comercial de patrocínio das equipes envolvidas:
        </p>

        <div class="table-container">
          {df_to_html_table(tabela_05, "tabela_05")}
        </div>

        <div class="how-to-read-box">
          <div class="how-to-read-header">👁️ Como Ler a Tabela de Dose-Resposta (A Analogia com o Remédio)</div>
          <p style="color:var(--text-secondary); font-size:0.9rem; line-height:1.5;">
            Na medicina, 'dose-resposta' significa: <em>quanto maior a dose do remédio, maior o efeito no paciente</em>.
            Aqui testamos o mesmo princípio no futebol:
            <br>• Jogo com <strong>Nenhuma Exposição</strong> (dois clubes sem bet): média de <strong>4,54 cartões</strong>.
            <br>• Jogo com <strong>Exposição Parcial</strong> (apenas 1 clube com bet): sobe para <strong>4,99 cartões</strong>.
            <br>• Jogo com <strong>Exposição Total</strong> (ambos os clubes com bet): atinge <strong>5,21 cartões (+14,7%)</strong>.
            <br>A resposta de cartões sobe degrau por degrau conforme a 'dose' comercial de patrocínio de apostas aumenta.
          </p>
        </div>

        <div class="figure-grid-2">
          <div class="figure-wrapper">
            <img src="figures/eda_bets/04_associacao_exposicao_vs_cartoes_faltas.png" alt="Associação Exposição vs Disciplina" onclick="openLightbox(this.src)">
            <div class="figure-caption">Figura 7: Dispersão entre o índice BET_EXPOSURE e as métricas disciplinares.</div>
          </div>
          <div class="figure-wrapper">
            <img src="figures/eda_bets/05_heatmap_marcas_bets_clubes.png" alt="Heatmap de Marcas" onclick="openLightbox(this.src)">
            <div class="figure-caption">Figura 8: Matriz de presença das principais marcas de apostas por clube e temporada.</div>
          </div>
        </div>
      </section>

      <!-- SLIDE 6: PHASE 5 (SCOUTS 2024 & CBF PARSER PILOT) -->
      <section class="slide" id="phase-5">
        <div class="slide-header">
          <span class="slide-badge">Fase 5</span>
          <h2 class="slide-title">Fechamento de Faltas 2024 (Sofascore) & Parser Nativo CBF</h2>
          <p class="slide-subtitle">Resolução da lacuna de scouts e engenharia de parsing PDF sem dependências externas.</p>
        </div>

        <div class="code-callout">
          # Ingestão de Faltas 2024: src/ingestion/ingest_serie_a_2024_scouts.py<br>
          # Parser de Súmulas CBF: src/cleaning/parse_cbf_sumulas.py (zlib stream parsing)
        </div>

        <div class="kpi-grid">
          <div class="kpi-card">
            <span class="kpi-label">Faltas Integradas (2024)</span>
            <span class="kpi-value">9.585</span>
            <span class="kpi-subtext">380 partidas da Série A auditadas</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-label">Média Faltas 2024</span>
            <span class="kpi-value">25,36</span>
            <span class="kpi-subtext">Mínima histórica da Série A</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-label">Taxa Conversão 2024</span>
            <span class="kpi-value">0,2198</span>
            <span class="kpi-subtext">Recorde histórico absoluto</span>
          </div>
          <div class="kpi-card">
            <span class="kpi-label">Expulsões em 2024</span>
            <span class="kpi-value">128</span>
            <span class="kpi-subtext">Recorde de cartões vermelhos</span>
          </div>
        </div>

        <div class="guide-box">
          <div class="guide-header">🧭 Em Bom Português: Por que as súmulas oficiais dos árbitros não anotam faltas normais?</div>
          <p style="color:var(--text-secondary); font-size:0.9rem; line-height:1.5;">
            Muita gente se surpreende ao saber disso: <strong>as regras oficiais da CBF e da FIFA não obrigam o juiz a contar quantas faltas normais aconteceram</strong>.
            O árbitro só escreve na súmula os cartões, os gols e incidentes graves. Se um zagueiro faz uma falta no meio de campo e o juiz apenas apita, essa falta não entra na súmula da CBF!
            Por isso, para auditar as faltas físicas de 2024, foi fundamental integrar os dados de vídeo scout do Sofascore (com 9.585 faltas auditadas lance a lance).
          </p>
        </div>

        <h3>Superando a Lacuna de Dados de 2024</h3>
        <p style="color:var(--text-secondary); margin-bottom:1rem;">
          Como identificado na Fase 1, o scraper do Adão Duque capturou zeros para as faltas de 2024. Desenvolvemos uma ingestão dedicada a partir dos dados auditados do Sofascore, casando com sucesso 100% das 380 partidas.
          Isso permitiu calcular com precisão matemática a taxa de conversão final de 2024 ($\tau_{{\text{{CF}}}} = 0,2198$).
        </p>

        <div class="decisions-grid">
          <div class="decision-card est">
            <div class="decision-header">
              <span class="decision-code">D-EST-06</span>
              <span class="decision-tag tag-est">Estratégica</span>
            </div>
            <div class="decision-title">Adoção do Sofascore para 2024 e Priorização da Série B</div>
            <div class="decision-body">Integrar scouts auditados do Sofascore para a Série A 2024 e priorizar a Série B (2022–2023) no pipeline de súmulas da CBF, onde eclodiu a Penalidade Máxima.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Resolve a lacuna mais urgente da Série A e foca os recursos analíticos na divisão crítica de integridade.</div>
          </div>

          <div class="decision-card ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-09</span>
              <span class="decision-tag tag-ana">Analítica</span>
            </div>
            <div class="decision-title">Reconhecimento da Ausência de Faltas nas Súmulas e Mineração Textual</div>
            <div class="decision-body">Documentar que súmulas oficiais não registram faltas normais (tarefa de scouts), aproveitando o texto do árbitro para classificar condutas disciplinares em categorias comportamentais.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Abre uma nova frente de análise qualitativa (reclamações, cera, conduta antidesportiva) sem incorrer em imputações falsas.</div>
          </div>
        </div>
      </section>

      <!-- SLIDE 7: PHASE 6 (SERIE B MASSIVE INGESTION & GROUND TRUTH) -->
      <section class="slide" id="phase-6">
        <div class="slide-header">
          <span class="slide-badge">Fase 6</span>
          <h2 class="slide-title">Ingestão Massiva Série B & Ground Truth Judicial</h2>
          <p class="slide-subtitle">760 súmulas oficiais, gap disciplinar A vs. B e a base factual da Operação Penalidade Máxima.</p>
        </div>

        <div class="code-callout">
          # Ingestão Multithread CBF: src/ingestion/download_cbf_sumulas.py (760 PDFs)<br>
          # Base Judicial de Ground Truth: data/processed/integrity/casos_penalidade_maxima.parquet (14 casos)
        </div>

        <div class="figure-grid-2">
          <div class="figure-wrapper">
            <img src="figures/series_comparison/01_comparacao_cartoes_serie_a_vs_b.png" alt="Série A vs Série B" onclick="openLightbox(this.src)">
            <div class="figure-caption">Figura 9: Severidade disciplinar — Série A (+11,7% cartões) vs. Série B (2022–2023).</div>
          </div>
          <div class="figure-wrapper">
            <img src="figures/series_comparison/03_tipologia_infracoes_serie_b.png" alt="Tipologia Série B" onclick="openLightbox(this.src)">
            <div class="figure-caption">Figura 10: Mineração textual de motivos da súmula — 28,9% decorrem de conduta não-física.</div>
          </div>
        </div>

        <div class="how-to-read-box">
          <div class="how-to-read-header">👁️ Como Interpretar as Figuras 9 e 10</div>
          <p style="color:var(--text-secondary); font-size:0.9rem; line-height:1.5;">
            <strong>Na Figura 9 (Série A vs. Série B):</strong> O gráfico de barras compara a média de advertências. A Série A aplica <strong>5,44 cartões por jogo</strong> contra <strong>4,87 na Série B</strong>. A elite é 11,7% mais severa, o que torna as divisões de acesso mais vulneráveis ao aliciamento de apostadores pela menor pressão midiática.
            <br><strong>Na Figura 10 (Tipologia dos Cartões):</strong> Mostra por que os juízes puniram na Série B. Quase <strong>29% dos cartões não tiveram disputa de bola</strong>: foram reclamações com o árbitro (15,8%), cera para retardar o jogo (8,4%) e atritos verbais (4,8%).
          </p>
        </div>

        <h3>Tipologia de Cartões Minerada das Súmulas Oficiais da Série B (Tabela 09)</h3>
        <div class="table-container">
          {df_to_html_table(tabela_09, "tabela_09")}
        </div>

        <div class="figure-wrapper">
          <img src="figures/series_comparison/04_contraste_casos_penalidade_maxima.png" alt="Contraste Penalidade Máxima" onclick="openLightbox(this.src)">
          <div class="figure-caption">Figura 11: A Assinatura de Manipulação — 100% dos cartões encomendados no 1º tempo (minuto médio 38,2') contra a distribuição natural do futebol.</div>
        </div>

        <div class="alert-box danger">
          <div class="alert-title">🎯 A Assinatura Temporal Comprovada da Fraude</div>
          <p>
            Nos 7 casos reais julgados e condenados pelo STJD de cartões encomendados por apostadores, <strong>100% dos eventos ocorreram no 1º tempo</strong>.
            A probabilidade de sortear 7 cartões no 1º tempo ao acaso sob a distribuição basal ($p_0 = 0,354$) é de $p = (0,354)^7 = 0,000643$ ($p < 0,001$).
            Isso estabelece formalmente a concentração no 1º tempo como o vetor matemático característico do aliciamento de atletas em micro-apostas.
          </p>
        </div>
      </section>

      <!-- SLIDE 8: PHASE 7 (CAUSAL TWFE & EVENT STUDY) -->
      <section class="slide" id="phase-7">
        <div class="slide-header">
          <span class="slide-badge">Fase 7</span>
          <h2 class="slide-title">Modelagem Econométrica Causal (Painel TWFE & Event Study)</h2>
          <p class="slide-subtitle">Isolando o efeito dos contratos de aposta com 7.598 observações e tendências paralelas.</p>
        </div>

        <div class="code-callout">
          # Preparação do Painel: src/models/prepare_panel.py (7.598 obs equipe-jogo, 2015-2024)<br>
          # Estimação Econométrica: src/models/econometric_models.py (Statsmodels TWFE com cluster robust)
        </div>

        <div class="formula-box">
          <div class="formula-header">🧮 Traduzindo a Equação TWFE em 4 Blocos Simples (Sem Linguajar Técnico)</div>
          <p style="color:var(--text-secondary); font-size:0.9rem; line-height:1.6;">
            $$Y_{{ict}} = \\underbrace{{\\beta \\cdot \\text{{BET}}_{{it}}}}_{{\\text{{1. Efeito do Patrocínio}}}} + \\underbrace{{\\mathbf{{X}}_{{ict}}' \\boldsymbol{{\\delta}}}}_{{\\text{{2. Contexto da Partida}}}} + \\underbrace{{\\alpha_i}}_{{\\text{{3. Estilo do Clube}}}} + \\underbrace{{\\gamma_t}}_{{\\text{{4. Diretrizes do Ano}}}} + \\varepsilon_{{ict}}$$
            • <strong>1. Efeito do Patrocínio ($\beta$):</strong> É o que queremos medir. O resultado deu <strong>+0,2665</strong> ($p = 0,0064$). Em português claro: assinar com uma bet causa cerca de 1 cartão a mais a cada 4 jogos daquela equipe.
            <br>• <strong>2. Contexto da Partida ($\mathbf{{X}}$):</strong> Controlamos fatores reais de jogo: jogar em casa diminui cartões (-0,22), jogos com placar apertado dão mais cartões e clássicos estaduais são mais quentes.
            <br>• <strong>3. Estilo do Clube ($\alpha_i$):</strong> 'Congela' o DNA do clube. Se um clube historicamente comete mais faltas, isso fica preso no $\alpha_i$ e <em>não é atribuído injustamente às bets</em>.
            <br>• <strong>4. Diretrizes do Ano ($\gamma_t$):</strong> 'Congela' o efeito de regras novas da CBF, instruções aos árbitros ou o advento do VAR em 2019.
          </p>
        </div>

        <div class="figure-grid-2">
          <div class="figure-wrapper">
            <img src="figures/econometrics/02_forest_plot_coeficientes_twfe.png" alt="Forest Plot TWFE" onclick="openLightbox(this.src)">
            <div class="figure-caption">Figura 12: Forest Plot dos Coeficientes TWFE com erros-padrão clusterizados por clube.</div>
          </div>
          <div class="figure-wrapper">
            <img src="figures/econometrics/01_event_study_cartoes_e_taxa.png" alt="Event Study DiD" onclick="openLightbox(this.src)">
            <div class="figure-caption">Figura 13: Staggered Event Study — Validação empírica de tendências paralelas pré-adoção e impacto defasado.</div>
          </div>
        </div>

        <div class="how-to-read-box">
          <div class="how-to-read-header">👁️ Como Interpretar as Figuras 12 e 13 (A Regra da Linha do Zero)</div>
          <p style="color:var(--text-secondary); font-size:0.9rem; line-height:1.5;">
            <strong>Na Figura 12 (Forest Plot):</strong> Cada linha horizontal mostra o impacto em uma variável. A linha vertical tracejada no zero é o juiz da verdade: se a barra horizontal <strong>cruza o zero</strong>, o efeito não existe (é o caso de 'Faltas Cometidas' e 'Cartões no 1º Tempo'). Se a barra fica <strong>inteira à direita do zero</strong>, o aumento é real e comprovado (caso de 'Cartões Totais' e 'Cartões Amarelos').
            <br><strong>Na Figura 13 (Estudo de Eventos):</strong> O ponto $e=0$ é o ano em que o clube estreou o patrocínio de aposta. À esquerda (anos antes do contrato), a linha é plana e colada no zero (provando que os clubes seguiam trajetórias paralelas normais). À direita (anos pós-contrato), a linha salta imediatamente para cima. É a prova causal definitiva.
          </p>
        </div>

        <h3>Resultados das Regressões TWFE em Painel (Tabela 11)</h3>
        <p style="color:var(--text-secondary); margin-bottom:1rem;">
          Modelo: $Y_{{ict}} = \beta \cdot \text{{BET\_EXPOSURE}}_{{it}} + \mathbf{{X}}_{{ict}}' \boldsymbol{{\delta}} + \alpha_i + \gamma_t + \varepsilon_{{ict}}$ com erros clusterizados por clube:
        </p>

        <div class="table-container">
          {df_to_html_table(tabela_11, "tabela_11")}
        </div>

        <h3>Interpretações Econométricas Cruciais</h3>
        <div class="decisions-grid">
          <div class="decision-card ana">
            <div class="decision-header">
              <span class="decision-code">ACHADO CAUSAL 1</span>
              <span class="decision-tag tag-ana">Efeito Positivo Significante</span>
            </div>
            <div class="decision-title">Elevação Causal em Cartões Totais e Amarelos</div>
            <div class="decision-body">O patrocínio de aposta causa um acréscimo de <strong>+0,2665 cartões por equipe/jogo ($p = 0,00642$)</strong>. Em um confronto onde ambos os clubes possuem patrocínio máster, são <strong>+0,533 cartões adicionais por partida</strong>, absorvendo efeitos fixos de ano e clube.</div>
          </div>

          <div class="decision-card tec">
            <div class="decision-header">
              <span class="decision-code">ACHADO CAUSAL 2</span>
              <span class="decision-tag tag-tec">Invariância Física</span>
            </div>
            <div class="decision-title">Faltas Cometidas Não Sofrem Alteração Estatística</div>
            <div class="decision-body">O coeficiente sobre o volume de faltas físicas é estritamente não-significante ($\beta = +0,5003, p = 0,369$). O patrocínio comercial de apostas não tornou o futebol fisicamente mais violento; alterou sim a severidade e a sensibilidade da resposta arbitral.</div>
          </div>

          <div class="decision-card est">
            <div class="decision-header">
              <span class="decision-code">ACHADO CAUSAL 3</span>
              <span class="decision-tag tag-est">Ausência de Falácia Ecológica</span>
            </div>
            <div class="decision-title">Coeficiente Nulo na Proporção de Cartões no 1º Tempo</div>
            <div class="decision-body">A proporção de advertências no 1º tempo tem coeficiente nulo com a exposição a apostas ($\beta = -0,0129, p = 0,5916$). <strong>Os clubes patrocinados por bets não orientam seus atletas a forçar cartões no 1º tempo</strong>. O spot-fixing é um crime individual de atletas aliciados e não uma política institucional de clubes.</div>
          </div>
        </div>

        <div class="figure-wrapper">
          <img src="figures/econometrics/03_dose_resposta_marginal.png" alt="Dose Resposta Marginal" onclick="openLightbox(this.src)">
          <div class="figure-caption">Figura 14: Efeito marginal ajustado do índice contínuo de exposição sobre a taxa de conversão faltas-cartões.</div>
        </div>
      </section>

      <!-- SLIDE 9: PHASE 8 (ANOMALY SCORING & GROUND TRUTH VALIDATION) -->
      <section class="slide" id="phase-8">
        <div class="slide-header">
          <span class="slide-badge">Fase 8</span>
          <h2 class="slide-title">Sistema de Triagem e Anomaly Scoring de Integridade Esportiva</h2>
          <p class="slide-subtitle">Arquitetura dual de triagem, teste binomial e validação com 100% de sensibilidade.</p>
        </div>

        <div class="code-callout">
          # Triagem e Anomaly Scoring: src/models/anomaly_detection.py<br>
          # Visualização de Integridade: src/visualization/plot_anomalies.py
        </div>

        <div class="formula-box">
          <div class="formula-header">🧮 Traduzindo os Scores de Anomalia: A Analogia do Scanner do Aeroporto</div>
          <p style="color:var(--text-secondary); font-size:0.9rem; line-height:1.5;">
            O algoritmo funciona exatamente como um detector de bagagens no raio-X do aeroporto:
            <br>• Ele não prende ninguém nem faz acusações penais.
            <br>• Ele apenas combina 5 sensores de risco da partida: (1) cartões acumulados no 1º tempo, (2) cartões mostrados precocemente antes dos 30 minutos, (3) volume exagerado de punições, (4) patrocínio das equipes e (5) pênaltis precoces.
            <br>• Se a mala 'apitar' acima do <strong>Percentil 90%</strong> (Alta Prioridade), significa que a partida é mais atípica que 90% da história da liga, devendo passar por auditoria imediata de vídeo por especialistas de compliance.
          </p>
        </div>

        <div class="figure-grid-2">
          <div class="figure-wrapper">
            <img src="figures/integrity/01_distribuicao_anomaly_scores.png" alt="Distribuição Anomaly Scores" onclick="openLightbox(this.src)">
            <div class="figure-caption">Figura 15: Distribuição contínua dos Anomaly Scores de partida e atleta.</div>
          </div>
          <div class="figure-wrapper">
            <img src="figures/integrity/03_validacao_sensibilidade_ground_truth.png" alt="Validação Ground Truth" onclick="openLightbox(this.src)">
            <div class="figure-caption">Figura 16: Matriz de sensibilidade — 100% dos casos reais da Operação Penalidade Máxima identificados.</div>
          </div>
        </div>

        <h3>Validação no Ground Truth da Operação Penalidade Máxima (Tabela 17)</h3>
        <p style="color:var(--text-secondary); margin-bottom:0.5rem;">
          Filtre os casos por atleta ou confronto:
        </p>
        <input type="text" class="table-search" id="searchGT" placeholder="Buscar por atleta, clube ou evento..." onkeyup="filterTable('searchGT', 'tabela_17')">

        <div class="table-container">
          {df_to_html_table(tabela_17, "tabela_17")}
        </div>

        <div class="how-to-read-box">
          <div class="how-to-read-header">👁️ Como Interpretar a Tabela 17 de Validação Judicial</div>
          <p style="color:var(--text-secondary); font-size:0.9rem; line-height:1.5;">
            Olhe para a coluna <strong>Athlete Score (Pct)</strong>. Essa porcentagem mostra onde o jogador condenado ficou posicionado entre todos os atletas do campeonato:
            <br>• <strong>Nino Paraíba:</strong> Percentil <strong>99,7%</strong> (Top 0,3% da liga — esteve entre os 3 atletas mais atípicos de toda a Série A);
            <br>• <strong>Gabriel Tota:</strong> Percentil <strong>98,2%</strong> (Top 1,8% da liga);
            <br>• <strong>Paulo Miranda:</strong> Percentil <strong>95,3%</strong> (Top 4,7% da liga);
            <br>• <strong>Eduardo Bauermann:</strong> Percentil <strong>90,5%</strong> (Top 9,5% da liga).
            <br>O modelo colocou <strong>100% dos atletas investigados na elite dentro do Top 10% mais suspeito da história</strong>.
          </p>
        </div>

        <h3>Conclusões da Validação Algorítmica</h3>
        <div class="decisions-grid">
          <div class="decision-card est">
            <div class="decision-header">
              <span class="decision-code">PERFORMANCE 1</span>
              <span class="decision-tag tag-est">Sensibilidade Total</span>
            </div>
            <div class="decision-title">100% de Sensibilidade nos Tiers Prioritários</div>
            <div class="decision-body">Todos os 14 incidentes judiciais reais foram capturados em <em>Alta Prioridade</em> (Top 10%) ou <em>Média Prioridade</em> (Top 25%). <strong>100% dos atletas investigados na Série A figuram no Top 10% mais anômalo de toda a história da liga</strong>.</div>
          </div>

          <div class="decision-card ana">
            <div class="decision-header">
              <span class="decision-code">PERFORMANCE 2</span>
              <span class="decision-tag tag-ana">Precisão em Fraude Frustrada</span>
            </div>
            <div class="decision-title">Ausência de Falsos Alarmes em Fraudes Frustradas</div>
            <div class="decision-body">Nos incidentes onde a fraude foi combinada mas não se consumou em campo (Romário/Vila Nova barrado pelo técnico e Bauermann/Santos contra Avaí sem amarelo), as partidas preservaram percentis normais, provando que o modelo não gera alarmes arbitrais falsos.</div>
          </div>

          <div class="decision-card tec">
            <div class="decision-header">
              <span class="decision-code">PERFORMANCE 3</span>
              <span class="decision-tag tag-tec">Consistência Longitudinal</span>
            </div>
            <div class="decision-title">Detecção Multitemporal do Caso Nino Paraíba</div>
            <div class="decision-body">O atleta Nino Paraíba liderou o ranking histórico de atipicidade individual em duas temporadas distintas: 2020 (Percentil 100,0%, Score 77,32) e 2022 (Percentil 99,67%, Score 72,35), com 70% a 85% dos seus cartões concentrados no 1º tempo.</div>
          </div>
        </div>

        <div class="figure-wrapper">
          <img src="figures/integrity/02_dispersao_tempo_vs_volume.png" alt="Dispersão Tempo vs Volume" onclick="openLightbox(this.src)">
          <div class="figure-caption">Figura 17: Dispersão entre assimetria temporal (1º tempo) e volume de cartões, destacando os incidentes criminais.</div>
        </div>
      </section>

      <!-- SLIDE 10: REPRODUCIBILITY & SCIENTIFIC RIGOR (PHASES 9-11) -->
      <section class="slide" id="phase-9">
        <div class="slide-header">
          <span class="slide-badge">Fases 9, 10 e 11</span>
          <h2 class="slide-title">Ciência Aberta, Reprodutibilidade e Fundamentação Teórica</h2>
          <p class="slide-subtitle">Quatro cadernos executáveis Jupyter, White Paper acadêmico e revisão bibliográfica seminal.</p>
        </div>

        <div class="decisions-grid">
          <div class="decision-card tec">
            <div class="decision-header">
              <span class="decision-code">CADERNO 01</span>
              <span class="decision-tag tag-tec">notebooks/01_pipeline_dados_e_limpeza.ipynb</span>
            </div>
            <div class="decision-title">Ingestão, Manifestos Criptográficos e Limpeza Multidivisão</div>
            <div class="decision-body">Executa o download dos dados brutos, validação de hashes SHA-256, correção do calendário COVID e gravação dos datasets processados da Série A e Série B.</div>
          </div>

          <div class="decision-card tec">
            <div class="decision-header">
              <span class="decision-code">CADERNO 02</span>
              <span class="decision-tag tag-tec">notebooks/02_analise_exploratoria_e_paradoxo_disciplinar.ipynb</span>
            </div>
            <div class="decision-title">EDA Profunda, Quebras Estruturais e o Paradoxo Disciplinar</div>
            <div class="decision-body">Reproduz todos os testes paramétricos e não-paramétricos, gráficos de evolução de faltas e cartões e contrastes de dose-resposta bivariada.</div>
          </div>

          <div class="decision-card tec">
            <div class="decision-header">
              <span class="decision-code">CADERNO 03</span>
              <span class="decision-tag tag-tec">notebooks/03_modelagem_econometrica_painel_did.ipynb</span>
            </div>
            <div class="decision-title">Painel Econométrico TWFE e Staggered Event Study</div>
            <div class="decision-body">Estimação das regressões com erros clusterizados por clube, teste de hipótese de tendências paralelas e modelo de heterogeneidade interdivisões.</div>
          </div>

          <div class="decision-card tec">
            <div class="decision-header">
              <span class="decision-code">CADERNO 04</span>
              <span class="decision-tag tag-tec">notebooks/04_sistema_triagem_anomalias_integridade.ipynb</span>
            </div>
            <div class="decision-title">Algoritmos de Anomaly Scoring e Validação Ground Truth</div>
            <div class="decision-body">Cálculo dos scores matemáticos compostos de partida e atleta, testes binomiais e validação empírica contra os 14 casos da Operação Penalidade Máxima.</div>
          </div>
        </div>

        <div class="alert-box success">
          <div class="alert-title">📚 Fichamento Teórico e Literatura Seminal (docs/revisao_bibliografica.md)</div>
          <p>
            A pesquisa foi ancorada em 6 eixos conceituais da literatura econômica internacional:
            <strong>Econometria Forense</strong> (Duggan & Levitt 2002 sobre sumô, Wolfers 2006 sobre point shaving na NCAA),
            <strong>Micro-Apostas & Spot-Fixing</strong> (Carpenter 2012, Forrest 2012, Hill 2010),
            <strong>Economia do Patrocínio</strong> (Lopez-Gonzalez 2018, Szymanski 2003),
            <strong>Comportamento e Viés Arbitral</strong> (Garicano et al. 2005 sobre favoritismo e pressão social, Buraimo 2010),
            <strong>Diretrizes Globais</strong> (UNODC 2021, Convenção de Macolin 2014, relatórios Sportradar e IBIA) e
            <strong>Inferência Causal</strong> (Callaway & Sant'Anna 2021, Goodman-Bacon 2021, Cameron & Miller 2015).
          </p>
        </div>
      </section>

      <!-- SLIDE 11: RECOMMENDATIONS -->
      <section class="slide" id="recommendations">
        <div class="slide-header">
          <span class="slide-badge">Síntese Estratégica</span>
          <h2 class="slide-title">Recomendações Regulatórias e Governança Esportiva</h2>
          <p class="slide-subtitle">Propostas concretas baseadas nas evidências causais para o ecossistema esportivo e regulatório.</p>
        </div>

        <div class="decisions-grid">
          <div class="decision-card est">
            <div class="decision-header">
              <span class="decision-code">SPA / MINISTÉRIO DA FAZENDA</span>
              <span class="decision-tag tag-est">Regulação Estatal</span>
            </div>
            <div class="decision-title">Restrição a Mercados Fracionários de Alta Vulnerabilidade</div>
            <div class="decision-body">
              Proibir ou impor tetos estritos de liquidez e travas operacionais para mercados de micro-apostas disciplinares individuais (ex: "cartão amarelo para o jogador X no 1º tempo"), que possuem execução discricionária individual e custo esportivo marginal nulo para aliciadores.
            </div>
          </div>

          <div class="decision-card ana">
            <div class="decision-header">
              <span class="decision-code">CBF & COMISSÕES DE ARBITRAGEM</span>
              <span class="decision-tag tag-ana">Governança Desportiva</span>
            </div>
            <div class="decision-title">Unidade de Inteligência de Súmulas e Auditoria Automatizada</div>
            <div class="decision-body">
              Implantar rotinas de <em>anomaly scoring</em> pós-rodada para sinalizar partidas com desvios superiores ao percentil 90 para auditoria imediata de vídeo, e intensificar o escrutínio nas Séries B, C e D, que possuem menor cobertura midiática e menor severidade arbitral média.
            </div>
          </div>

          <div class="decision-card tec">
            <div class="decision-header">
              <span class="decision-code">STJD & MINISTÉRIO PÚBLICO</span>
              <span class="decision-tag tag-tec">Segurança Jurídica</span>
            </div>
            <div class="decision-title">Métricas Probabilísticas como Indício Qualificado</div>
            <div class="decision-body">
              Utilizar testes binomiais e scores estatísticos como suporte probatório em inquéritos preliminares, mantendo separação categórica entre anomalia estatística (triagem) e acusação penal/desportiva, exigindo quebra de sigilos bancário e telemático para denúncia formal.
            </div>
          </div>

          <div class="decision-card est">
            <div class="decision-header">
              <span class="decision-code">CLUBES DE FUTEBOL PROFISSIONAL</span>
              <span class="decision-tag tag-est">Compliance Interno</span>
            </div>
            <div class="decision-title">Monitoramento Disciplinar e Proteção a Atletas Aliciados</div>
            <div class="decision-body">
              Clubes devem auditar internamente a assimetria de cartões no 1º tempo de seus elencos e criar canais seguros e anônimos de acolhimento para atletas denunciarem abordagens de intermediários criminosos antes que o aliciamento se consuma.
            </div>
          </div>
        </div>
      </section>

      <!-- SLIDE 12: DECISIONS MATRIX (29 DECISIONS) -->
      <section class="slide" id="decisions-matrix">
        <div class="slide-header">
          <span class="slide-badge">Auditoria de Governança</span>
          <h2 class="slide-title">Matriz Consolidada de Decisões do Projeto (29 Decisões)</h2>
          <p class="slide-subtitle">Rastreabilidade integral conforme a taxonomia da Seção 17 do .agent.md.</p>
        </div>

        <div class="filter-bar">
          <button class="btn btn-active" onclick="filterDecisions('all')">Todas as Decisões (29)</button>
          <button class="btn" onclick="filterDecisions('est')">Estratégicas / Negócio (9)</button>
          <button class="btn" onclick="filterDecisions('ana')">Analíticas / Metodológicas (13)</button>
          <button class="btn" onclick="filterDecisions('tec')">Técnicas / Engenharia (7)</button>
        </div>

        <div class="decisions-grid" id="decisionsContainer">
          <!-- D-EST-01 a D-EST-09 -->
          <div class="decision-card est" data-type="est">
            <div class="decision-header">
              <span class="decision-code">D-EST-01</span>
              <span class="decision-tag tag-est">Estratégica / Usuário</span>
            </div>
            <div class="decision-title">Priorização da Ingestão da Série A (Adão Duque)</div>
            <div class="decision-body">Iniciar a coleta e limpeza pela divisão de elite com repositório auditável antes de avançar para divisões de acesso.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Viabiliza rapidamente o MVP 1 e MVP 4 com 11 temporadas completas de cartões individuais.</div>
          </div>

          <div class="decision-card est" data-type="est">
            <div class="decision-header">
              <span class="decision-code">D-EST-02</span>
              <span class="decision-tag tag-est">Estratégica / Usuário</span>
            </div>
            <div class="decision-title">Dados de Volume Financeiro de Apostas Fora do Caminho Crítico</div>
            <div class="decision-body">Não paralisar a pesquisa buscando dados privados e sigilosos de faturamento por mercado das operadoras.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Casas de aposta operam sob sigilo comercial; utilizar proxies públicas (Trends, patrocínios e SPA/MF).</div>
          </div>

          <div class="decision-card est" data-type="est">
            <div class="decision-header">
              <span class="decision-code">D-EST-03</span>
              <span class="decision-tag tag-est">Estratégica / Usuário</span>
            </div>
            <div class="decision-title">Sequenciamento Estrito de Fases (EDA Antes de Modelos)</div>
            <div class="decision-body">Proibição estrita de rodar regressões em painel ou modelos antes de esgotar a auditoria exploratória empírica.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Evita especificação espúria de modelos sem conhecimento da distribuição das séries temporais.</div>
          </div>

          <div class="decision-card est" data-type="est">
            <div class="decision-header">
              <span class="decision-code">D-EST-04</span>
              <span class="decision-tag tag-est">Estratégica / Usuário</span>
            </div>
            <div class="decision-title">Matriz Histórica de Patrocínios Auditável (MVP 2)</div>
            <div class="decision-body">Compilação censitária de 200 registros de clube-temporada com base no IBOPE Repucom e balanços patrimoniais oficiais.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Fornece fundamentação documental para mensurar a exposição comercial sem dados inventados.</div>
          </div>

          <div class="decision-card est" data-type="est">
            <div class="decision-header">
              <span class="decision-code">D-EST-05</span>
              <span class="decision-tag tag-est">Estratégica / Usuário</span>
            </div>
            <div class="decision-title">Resolução da Dualidade Contratual vs. Transbordamento Macro</div>
            <div class="decision-body">Geração de duas variáveis complementares: <code>bet_exposure_clube</code> (estritamente contratual) e <code>bet_exposure_total</code> (+ Google Trends).</div>
            <div class="decision-motive"><strong>Motivo:</strong> Permite isolar o efeito estritamente contratual do clube contra o transbordamento cultural difuso no país.</div>
          </div>

          <div class="decision-card est" data-type="est">
            <div class="decision-header">
              <span class="decision-code">D-EST-06</span>
              <span class="decision-tag tag-est">Estratégica / Usuário</span>
            </div>
            <div class="decision-title">Adoção do Sofascore para Faltas 2024 e Priorização da Série B</div>
            <div class="decision-body">Integrar 9.585 faltas auditadas do Sofascore em 2024 e direcionar o web scraper de PDFs da CBF para a Série B (2022–2023).</div>
            <div class="decision-motive"><strong>Motivo:</strong> Fecha o cálculo da taxa de conversão em 2024 e foca na divisão onde eclodiu a Operação Penalidade Máxima.</div>
          </div>

          <div class="decision-card est" data-type="est">
            <div class="decision-header">
              <span class="decision-code">D-EST-07</span>
              <span class="decision-tag tag-est">Estratégica / Usuário</span>
            </div>
            <div class="decision-title">Incorporação dos Autos da Penalidade Máxima como Ground Truth</div>
            <div class="decision-body">Estruturar formalmente os 14 incidentes reais confessados e punidos pelo STJD/MP-GO em <code>casos_penalidade_maxima.parquet</code>.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Fornece âncora empírica factual para calibrar e testar algoritmos de triagem sem ilações teóricas vazias.</div>
          </div>

          <div class="decision-card est" data-type="est">
            <div class="decision-header">
              <span class="decision-code">D-EST-08</span>
              <span class="decision-tag tag-est">Estratégica / Usuário</span>
            </div>
            <div class="decision-title">Quase-Experimento da Lei 13.756/2018 para Inferência Causal</div>
            <div class="decision-body">Estruturar a identificação econométrica em torno do marco legal de 12/12/2018, contrastando o período basal com o período de abertura de mercado.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Fornece fundamento institucional para separar associação descritiva de causalidade econométrica.</div>
          </div>

          <div class="decision-card est" data-type="est">
            <div class="decision-header">
              <span class="decision-code">D-EST-09</span>
              <span class="decision-tag tag-est">Estratégica / Usuário</span>
            </div>
            <div class="decision-title">Arquitetura Algorítmica Dual de Triagem (Partida e Atleta)</div>
            <div class="decision-body">Estruturar a triagem em duas escalas complementares calibradas no ground truth: <code>MATCH_ANOMALY_SCORE</code> e <code>ATHLETE_ANOMALY_SCORE</code>.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Identifica tanto anomalias coletivas na partida quanto desvios longitudinais de atletas aliciados em jogos de aparência normal.</div>
          </div>

          <!-- D-ANA-01 a D-ANA-13 -->
          <div class="decision-card ana" data-type="ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-01</span>
              <span class="decision-tag tag-ana">Analítica / Agente</span>
            </div>
            <div class="decision-title">Temporalidade por Temporada/Edição e não Ano Civil</div>
            <div class="decision-body">Corrigir a distorção do calendário COVID-19 atribuindo todas as partidas da edição de 2020 a <code>temporada = 2020</code>.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Evita a contagem distorcida de 268 jogos em 2020 e 492 jogos em 2021.</div>
          </div>

          <div class="decision-card ana" data-type="ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-02</span>
              <span class="decision-tag tag-ana">Analítica / Agente</span>
            </div>
            <div class="decision-title">Diagnóstico e Tratamento da Lacuna de Faltas/Scouts de 2024</div>
            <div class="decision-body">Não descartar a temporada 2024 do Adão Duque; manter a base de cartões intacta e complementar faltas via Sofascore.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Preserva a integridade da amostra disciplinar de 2024 sem contaminar os scouts anteriores.</div>
          </div>

          <div class="decision-card ana" data-type="ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-03</span>
              <span class="decision-tag tag-ana">Analítica / Agente</span>
            </div>
            <div class="decision-title">Estratégia Híbrida para Séries B, C e D via Súmulas Oficiais</div>
            <div class="decision-body">Adotar as Súmulas Eletrônicas da CBF como fonte oficial, gratuita e unificada para cobrir as divisões de acesso.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Viabiliza a comparação multidivisão sem depender de APIs pagas comerciais.</div>
          </div>

          <div class="decision-card ana" data-type="ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-04</span>
              <span class="decision-tag tag-ana">Analítica / Agente</span>
            </div>
            <div class="decision-title">Minutagem Contínua e Decomposição de Acréscimos</div>
            <div class="decision-body">Criar a variável <code>minuto_continuo</code> somando o minuto nominal aos acréscimos arbitrais (ex: 45+2' → 47).</div>
            <div class="decision-motive"><strong>Motivo:</strong> Viabiliza curvas de sobrevivência e densidade contínua sem picos artificiais aos 45' e 90'.</div>
          </div>

          <div class="decision-card ana" data-type="ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-05</span>
              <span class="decision-tag tag-ana">Analítica / Agente</span>
            </div>
            <div class="decision-title">Janelas de Contraste Temporal para Testes de Hipótese</div>
            <div class="decision-body">Definir 2014–2018 como grupo de controle basal (Pré-Bets) e 2022–2024 como tratamento (Alta Exposição), isolando a transição de 2019–2021.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Permite isolar o efeito da maturidade do mercado de apostas com alto poder estatístico.</div>
          </div>

          <div class="decision-card ana" data-type="ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-06</span>
              <span class="decision-tag tag-ana">Analítica / Agente</span>
            </div>
            <div class="decision-title">Taxa de Conversão Faltas → Cartões como Indicador de Severidade</div>
            <div class="decision-body">Adotar a razão $\tau = \text{{Cartões}} / \text{{Faltas}}$ como métrica central da dinâmica de jogo.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Captura se alterações disciplinares decorrem de violência física de jogo ou de maior sensibilidade e rigor arbitral.</div>
          </div>

          <div class="decision-card ana" data-type="ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-07</span>
              <span class="decision-tag tag-ana">Analítica / Agente</span>
            </div>
            <div class="decision-title">Dualidade no Cálculo do Índice BET_EXPOSURE</div>
            <div class="decision-body">Implementar <code>bet_exposure_clube</code> e <code>bet_exposure_total</code> para permitir análises contratuais puras e mistas.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Oferece robustez metodológica e atende plenamente às diretrizes de análise de sensibilidade.</div>
          </div>

          <div class="decision-card ana" data-type="ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-08</span>
              <span class="decision-tag tag-ana">Analítica / Agente</span>
            </div>
            <div class="decision-title">Categorização das Partidas por Exposição</div>
            <div class="decision-body">Estratificar os jogos contemporâneos em Nenhuma (0 clubes), Parcial (1 clube) e Total (ambos os clubes patrocinados).</div>
            <div class="decision-motive"><strong>Motivo:</strong> Viabiliza o teste empírico de dose-resposta bivariada.</div>
          </div>

          <div class="decision-card ana" data-type="ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-09</span>
              <span class="decision-tag tag-ana">Analítica / Agente</span>
            </div>
            <div class="decision-title">Categorização Textual de Motivos de Punição</div>
            <div class="decision-body">Classificar os motivos textuais das súmulas em falta física, reclamação, cera, conduta antidesportiva e mão intencional.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Revela se a inflação recente de advertências provém de disputas de bola ou de atritos comportamentais.</div>
          </div>

          <div class="decision-card ana" data-type="ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-10</span>
              <span class="decision-tag tag-ana">Analítica / Agente</span>
            </div>
            <div class="decision-title">Assinatura Temporal de Precocidade de Manipulação</div>
            <div class="decision-body">Estabelecer a hipótese de concentração de cartões no 1º tempo como vetor estatístico característico do spot-fixing.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Separa o ruído disciplinar comum de final de jogo do sinal potencial de manipulação intencional prematura.</div>
          </div>

          <div class="decision-card ana" data-type="ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-11</span>
              <span class="decision-tag tag-ana">Analítica / Agente</span>
            </div>
            <div class="decision-title">Estimação TWFE com Erros Robustos Clusterizados por Clube</div>
            <div class="decision-body">Especificar o painel com efeitos fixos de clube e de temporada, corrigindo a matriz de covariância por cluster de clube.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Elimina viés de variáveis omitidas e evita falsos positivos por autocorrelação serial intraclube.</div>
          </div>

          <div class="decision-card ana" data-type="ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-12</span>
              <span class="decision-tag tag-ana">Analítica / Agente</span>
            </div>
            <div class="decision-title">Adoção do Staggered Event Study com Teste de Tendências Paralelas</div>
            <div class="decision-body">Estimar modelo dinâmico ano a ano relativo ao ano de estreia de patrocínio de cada clube, testando $H_0: \beta_{{e \le -2}} = 0$.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Valida formalmente a identificação causal e captura a dinâmica temporal de defasagem do efeito contratual.</div>
          </div>

          <div class="decision-card ana" data-type="ana">
            <div class="decision-header">
              <span class="decision-code">D-ANA-13</span>
              <span class="decision-tag tag-ana">Analítica / Agente</span>
            </div>
            <div class="decision-title">Limiares por Percentis Empíricos e Governança Ética</div>
            <div class="decision-body">Definir alertas com base nos percentis empíricos da distribuição (Top 10% e Top 25%), com presunção irrestrita de inocência.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Atinge 100% de sensibilidade no ground truth da Penalidade Máxima sem imputação indevida a atletas legítimos.</div>
          </div>

          <!-- D-TEC-01 a D-TEC-07 -->
          <div class="decision-card tec" data-type="tec">
            <div class="decision-header">
              <span class="decision-code">D-TEC-01 & D-TEC-02</span>
              <span class="decision-tag tag-tec">Técnica / Agente</span>
            </div>
            <div class="decision-title">Governança Imutável e Hashes Criptográficos SHA-256</div>
            <div class="decision-body">Blindagem de diretórios brutos como read-only e geração de manifestos JSON com hashes SHA-256 e contagem de bytes.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Garante integridade de dados e proteção absoluta contra corrupção acidental de arquivos de origem.</div>
          </div>

          <div class="decision-card tec" data-type="tec">
            <div class="decision-header">
              <span class="decision-code">D-TEC-03</span>
              <span class="decision-tag tag-tec">Técnica / Agente</span>
            </div>
            <div class="decision-title">Modularização Pacote a Pacote em src/</div>
            <div class="decision-body">Divisão clara em submódulos Python: ingestion, cleaning, analysis, models e visualization.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Manutenibilidade, separação de responsabilidades e facilidade de teste unitário automatizado.</div>
          </div>

          <div class="decision-card tec" data-type="tec">
            <div class="decision-header">
              <span class="decision-code">D-TEC-04</span>
              <span class="decision-tag tag-tec">Técnica / Agente</span>
            </div>
            <div class="decision-title">Persistência Dual em Apache Parquet e CSV UTF-8</div>
            <div class="decision-body">Gravação simultânea em Parquet colunar via PyArrow e CSV para compatibilidade imediata e auditoria.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Alta performance de leitura em consultas analíticas e fácil conferência por humanos.</div>
          </div>

          <div class="decision-card tec" data-type="tec">
            <div class="decision-header">
              <span class="decision-code">D-TEC-05</span>
              <span class="decision-tag tag-tec">Técnica / Agente</span>
            </div>
            <div class="decision-title">Automação de Figuras e Tabelas de Auditoria</div>
            <div class="decision-body">Scripts exportam figuras em alta resolução em <code>reports/figures/</code> e tabelas descritivas em <code>reports/tables/</code>.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Garante reprodutibilidade visual e numérica direta sem dependência de passos manuais.</div>
          </div>

          <div class="decision-card tec" data-type="tec">
            <div class="decision-header">
              <span class="decision-code">D-TEC-06</span>
              <span class="decision-tag tag-tec">Técnica / Agente</span>
            </div>
            <div class="decision-title">Suíte Automatizada de 44 Testes Unitários via Pytest</div>
            <div class="decision-body">Cobertura contínua de limites matemáticos [0, 100], integridade relacional, modelos econométricos, cadernos Jupyter e HTML.</div>
            <div class="decision-motive"><strong>Motivo:</strong> 100% de aprovação e prevenção de regressões em qualquer refatoração do código-fonte.</div>
          </div>

          <div class="decision-card tec" data-type="tec">
            <div class="decision-header">
              <span class="decision-code">D-TEC-07</span>
              <span class="decision-tag tag-tec">Técnica / Agente</span>
            </div>
            <div class="decision-title">Reprodutibilidade Integral via Cadernos Jupyter Validados</div>
            <div class="decision-body">Construção e validação programática de 4 cadernos executáveis em notebooks/ cobrindo ETL, EDA, Modelagem e Integridade.</div>
            <div class="decision-motive"><strong>Motivo:</strong> Permite que pesquisadores externos e tribunais repliquem cada cálculo e figura do estudo.</div>
          </div>
        </div>
      </section>

      <!-- SLIDE 13: RISKS, BLIND SPOTS & CHECKLIST (.agent.md) -->
      <section class="slide" id="risks-checklist">
        <div class="slide-header">
          <span class="slide-badge">Auditoria Final</span>
          <h2 class="slide-title">Riscos Metodológicos, Pontos Cegos e Checklist Final (.agent.md)</h2>
          <p class="slide-subtitle">Conformidade obrigatória com os critérios de conclusão científica do projeto.</p>
        </div>

        <h3>Matriz de Riscos e Mitigações Concluídas</h3>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Risco Identificado</th>
                <th>Ponto Cego Potencial</th>
                <th>Impacto Metodológico</th>
                <th>Estratégia de Mitigação Implementada</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>1. Sigilo de Volume Apostado</strong></td>
                <td>Casas offshore não publicam apostas por jogador/mercado.</td>
                <td>Impossibilidade de medir liquidez direta em dinheiro.</td>
                <td>D-EST-02: Uso de proxies auditáveis (Trends, patrocínios máster censitários e licenças SPA/MF).</td>
                <td><span class="decision-tag tag-tec">Mitigado</span></td>
              </tr>
              <tr>
                <td><strong>2. Distorção Pandêmica de Calendário</strong></td>
                <td>Brasileirão 2020 terminou em fevereiro de 2021 (112 jogos).</td>
                <td>Contagem civil ingênua distorce médias anuais.</td>
                <td>D-ANA-01: Particionamento determinístico por temporada esportiva e não por ano civil.</td>
                <td><span class="decision-tag tag-tec">Mitigado</span></td>
              </tr>
              <tr>
                <td><strong>3. Falácia Ecológica Institucional</strong></td>
                <td>Confundir patrocínio de clube com fraude corporativa.</td>
                <td>Acusar clubes injustamente de manipular partidas.</td>
                <td>D-EST-08: Teste TWFE provando coeficiente nulo ($\beta = -0,013, p = 0,59$) de cartões no 1º tempo por clube.</td>
                <td><span class="decision-tag tag-tec">Mitigado</span></td>
              </tr>
              <tr>
                <td><strong>4. Imputação Indevida de Fraude</strong></td>
                <td>Atletas legítimos com muitos cartões serem acusados.</td>
                <td>Violação grave de reputação e direitos individuais.</td>
                <td>D-ANA-13: Presunção irrestrita de inocência; scores como triagem interna de compliance, e não prova penal.</td>
                <td><span class="decision-tag tag-tec">Mitigado</span></td>
              </tr>
              <tr>
                <td><strong>5. Lacuna de Scouts em 2024</strong></td>
                <td>Array de faltas e escanteios vazio na base histórica.</td>
                <td>Inviabilizar a taxa de conversão recente da Série A.</td>
                <td>D-EST-06: Ingestão de 9.585 faltas auditadas do Sofascore com hash SHA-256.</td>
                <td><span class="decision-tag tag-tec">Mitigado</span></td>
              </tr>
              <tr>
                <td><strong>6. Rotatividade e Estilos de Árbitros</strong></td>
                <td>Árbitros rigorosos apitarem jogos específicos.</td>
                <td>Confundir rigor arbitral com impacto de apostas.</td>
                <td>Inclusão de efeitos fixos de ano, mando de campo e recomendação para expansão de dados em pesquisas futuras.</td>
                <td><span class="decision-tag tag-ana">Documentado</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <h3>Checklist Final de Conclusão da Análise (Seção 28 do .agent.md)</h3>
        <p style="color:var(--text-secondary); margin-bottom:1rem;">
          Conformidade auditada ponto a ponto em relação às diretrizes institucionais do parceiro de análise:
        </p>

        <div class="checklist-container">
          <div class="checklist-item">
            <input type="checkbox" checked disabled>
            <div><strong>Problema:</strong> Pergunta principal e objetivos claramente definidos em torno da expansão das apostas, dinâmica disciplinar e integridade.</div>
          </div>
          <div class="checklist-item">
            <input type="checkbox" checked disabled>
            <div><strong>Dados:</strong> Origem documentada em <code>docs/sources.md</code> e dicionário de dados em <code>docs/data_dictionary.md</code> com hashes SHA-256.</div>
          </div>
          <div class="checklist-item">
            <input type="checkbox" checked disabled>
            <div><strong>Qualidade dos Dados:</strong> Distorção COVID tratada, faltas de 2024 complementadas e integridade referencial testada via pytest.</div>
          </div>
          <div class="checklist-item">
            <input type="checkbox" checked disabled>
            <div><strong>Método:</strong> Complexidade proporcional (EDA bivariada $\rightarrow$ Painel TWFE $\rightarrow$ Staggered Event Study $\rightarrow$ Anomaly Scoring).</div>
          </div>
          <div class="checklist-item">
            <input type="checkbox" checked disabled>
            <div><strong>Causalidade:</strong> Rigorosa separação entre correlação descritiva e causalidade estatística comprovada com validação de tendências paralelas.</div>
          </div>
          <div class="checklist-item">
            <input type="checkbox" checked disabled>
            <div><strong>Resultados Negativos:</strong> Preservação do coeficiente estatisticamente nulo de faltas físicas e de cartões precoces no nível do clube.</div>
          </div>
          <div class="checklist-item">
            <input type="checkbox" checked disabled>
            <div><strong>Ground Truth:</strong> Validação algorítmica contra os 14 casos reais transitados em julgado da Operação Penalidade Máxima (100% de sensibilidade).</div>
          </div>
          <div class="checklist-item">
            <input type="checkbox" checked disabled>
            <div><strong>Reprodutibilidade:</strong> 4 cadernos executáveis Jupyter em <code>notebooks/</code> validados por 44 testes unitários com 100% de aprovação.</div>
          </div>
          <div class="checklist-item">
            <input type="checkbox" checked disabled>
            <div><strong>Decisões para o Usuário:</strong> Recomendações regulatórias práticas para SPA/MF, CBF, STJD e Clubes de Futebol sem usurpação de autoridade.</div>
          </div>
        </div>

        <div class="alert-box success" style="margin-top:2rem;">
          <div class="alert-title">🏁 Conclusão Final do Projeto</div>
          <p>
            O projeto cumpriu integralmente todos os critérios de rigor científico, governança ética e reprodutibilidade exigidos pelo <code>.agent.md</code>.
            As evidências demonstram que as apostas esportivas causaram uma transformação profunda na sensibilidade arbitral do futebol brasileiro, enquanto
            os casos de manipulação por micro-apostas constituem desvios criminosos individuais que podem ser rastreados com 100% de sensibilidade por algoritmos de triagem estatística.
          </p>
        </div>
      </section>

    </main>
  </div>

  <!-- SLIDE NAVIGATION OVERLAY -->
  <div class="slide-navigator" id="slideNav">
    <button class="btn" onclick="prevSlide()">◀ Anterior</button>
    <span class="slide-counter" id="slideCounter">1 / 14</span>
    <button class="btn btn-primary" onclick="nextSlide()">Próximo ▶</button>
  </div>

  <!-- LIGHTBOX MODAL -->
  <div class="lightbox-modal" id="lightbox" onclick="closeLightbox()">
    <span class="lightbox-close">&times;</span>
    <img id="lightboxImg" src="" alt="Ampliação da Imagem">
  </div>

  <!-- JAVASCRIPT -->
  <script>
    // THEME TOGGLE
    function toggleTheme() {{
      const html = document.documentElement;
      const currentTheme = html.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
    }}

    // LOAD SAVED THEME
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {{
      document.documentElement.setAttribute('data-theme', savedTheme);
    }}

    // SLIDE VS DASHBOARD MODE
    let currentMode = 'dashboard';
    let currentSlideIdx = 0;
    const slides = Array.from(document.querySelectorAll('.slide'));

    function setMode(mode) {{
      currentMode = mode;
      const body = document.body;
      const btnDash = document.getElementById('btn-mode-dash');
      const btnSlide = document.getElementById('btn-mode-slide');

      if (mode === 'slide') {{
        body.classList.add('slide-mode');
        btnDash.classList.remove('btn-active');
        btnSlide.classList.add('btn-active');
        showSlide(currentSlideIdx);
      }} else {{
        body.classList.remove('slide-mode');
        btnSlide.classList.remove('btn-active');
        btnDash.classList.add('btn-active');
        slides.forEach(s => s.classList.remove('active'));
      }}
      updateProgress();
    }}

    function showSlide(idx) {{
      if (idx < 0) idx = 0;
      if (idx >= slides.length) idx = slides.length - 1;
      currentSlideIdx = idx;

      slides.forEach((s, i) => {{
        if (i === idx) {{
          s.classList.add('active');
        }} else {{
          s.classList.remove('active');
        }}
      }});

      document.getElementById('slideCounter').innerText = `${{idx + 1}} / ${{slides.length}}`;
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
      updateProgress();
    }}

    function nextSlide() {{
      if (currentSlideIdx < slides.length - 1) {{
        showSlide(currentSlideIdx + 1);
      }}
    }}

    function prevSlide() {{
      if (currentSlideIdx > 0) {{
        showSlide(currentSlideIdx - 1);
      }}
    }}

    // KEYBOARD NAVIGATION
    window.addEventListener('keydown', (e) => {{
      if (currentMode === 'slide') {{
        if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {{
          nextSlide();
        }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
          prevSlide();
        }} else if (e.key === 'Home') {{
          showSlide(0);
        }} else if (e.key === 'End') {{
          showSlide(slides.length - 1);
        }} else if (e.key === 'Escape') {{
          setMode('dashboard');
        }}
      }}
    }});

    // SCROLL PROGRESS BAR (DASHBOARD MODE)
    window.addEventListener('scroll', () => {{
      if (currentMode === 'dashboard') {{
        const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        document.getElementById('progressBar').style.width = scrolled + '%';

        // Update active sidebar nav
        const scrollPos = window.scrollY + 120;
        slides.forEach(slide => {{
          if (slide.offsetTop <= scrollPos && (slide.offsetTop + slide.offsetHeight) > scrollPos) {{
            const id = slide.getAttribute('id');
            document.querySelectorAll('.sidebar .nav-item').forEach(link => {{
              link.classList.remove('active');
              if (link.getAttribute('href') === '#' + id) {{
                link.classList.add('active');
              }}
            }});
          }}
        }});
      }}
    }});

    function updateProgress() {{
      if (currentMode === 'slide') {{
        const pct = ((currentSlideIdx + 1) / slides.length) * 100;
        document.getElementById('progressBar').style.width = pct + '%';
      }}
    }}

    // LIGHTBOX MODAL
    function openLightbox(src) {{
      const modal = document.getElementById('lightbox');
      const img = document.getElementById('lightboxImg');
      img.src = src;
      modal.classList.add('active');
    }}

    function closeLightbox() {{
      const modal = document.getElementById('lightbox');
      modal.classList.remove('active');
    }}

    // DECISIONS FILTER
    function filterDecisions(type) {{
      const cards = document.querySelectorAll('#decisionsContainer .decision-card');
      const buttons = document.querySelectorAll('.filter-bar .btn');

      buttons.forEach(btn => btn.classList.remove('btn-active'));
      event.target.classList.add('btn-active');

      cards.forEach(card => {{
        if (type === 'all' || card.getAttribute('data-type') === type) {{
          card.style.display = 'block';
        }} else {{
          card.style.display = 'none';
        }}
      }});
    }}

    // TABLE SEARCH FILTER
    function filterTable(inputId, tableId) {{
      const filter = document.getElementById(inputId).value.toLowerCase();
      const rows = document.querySelectorAll('#' + tableId + ' tbody tr');
      rows.forEach(row => {{
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
      }});
    }}
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Apresentação HTML enriquecida gerada com sucesso em: {OUTPUT_HTML}")
    print(f"Tamanho do arquivo: {os.path.getsize(OUTPUT_HTML):,} bytes")


if __name__ == "__main__":
    generate_html()
