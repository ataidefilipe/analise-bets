"""
src/ingestion/extract_google_trends.py
--------------------------------------
Extrai a série temporal real de interesse de buscas do Google Trends Brasil (2015–2025)
para os termos de apostas esportivas e compara com a base atual do projeto.
"""

import os
import time
import pandas as pd
import numpy as np
from pytrends.request import TrendReq

RAW_BETTING_DIR = os.path.join("data", "raw", "betting")
CURRENT_TRENDS_PATH = os.path.join(RAW_BETTING_DIR, "google_trends_brasil_2015_2025.csv")


def extract_real_google_trends():
    """
    Realiza a extração dos dados reais via pytrends para o Brasil (geo='BR').
    Extrai tanto o lote comparativo (escala comum entre marcas e termos)
    quanto os termos isoladamente.
    """
    print("=" * 70)
    print("1. CONECTANDO AO GOOGLE TRENDS VIA PYTRENDS")
    print("=" * 70)
    
    pytrends = TrendReq(hl="pt-BR", tz=180, timeout=(15, 30))
    
    terms = ["bet", "bet365", "betano", "sportingbet", "apostas esportivas"]
    timeframe = "2015-01-01 2025-12-31"
    geo = "BR"
    
    print(f"-> Termos analisados: {terms}")
    print(f"-> Período: {timeframe} | Região: {geo}")
    
    # 1. Consulta comparativa comum (todos na mesma escala 0-100)
    print("-> Enviando requisição para lote comparativo...")
    pytrends.build_payload(terms, cat=0, timeframe=timeframe, geo=geo)
    df_comp = pytrends.interest_over_time().reset_index()
    
    # Padronizar datas para o primeiro dia do mês (MS)
    df_comp["data"] = pd.to_datetime(df_comp["date"]).dt.strftime("%Y-%m-01")
    df_comp["ano"] = pd.to_datetime(df_comp["data"]).dt.year
    df_comp["mes"] = pd.to_datetime(df_comp["data"]).dt.month
    
    # Calcular soma dos termos e índice composto relativo
    df_comp["soma_termos"] = df_comp[terms].sum(axis=1)
    max_soma = df_comp["soma_termos"].max()
    df_comp["score_composto_real"] = (df_comp["soma_termos"] / max_soma * 100.0).round(2)
    
    # Termo 'bet' isolado na escala comparativa
    df_comp["score_bet_real"] = df_comp["bet"]
    
    # 2. Consulta isolada do termo 'bet' para comparar escala própria individual
    print("-> Enviando requisição para termo 'bet' isolado...")
    time.sleep(2)
    pytrends.build_payload(["bet"], cat=0, timeframe=timeframe, geo=geo)
    df_bet_solo = pytrends.interest_over_time().reset_index()
    df_bet_solo["data"] = pd.to_datetime(df_bet_solo["date"]).dt.strftime("%Y-%m-01")
    df_bet_solo = df_bet_solo.rename(columns={"bet": "score_bet_solo"})[["data", "score_bet_solo"]]
    
    # Merge das extrações
    df_real = df_comp.merge(df_bet_solo, on="data", how="left")
    
    return df_real, terms


def compare_with_current(df_real: pd.DataFrame, terms: list):
    """
    Carrega a base atual do projeto e confronta estatisticamente com a série real.
    """
    print("\n" + "=" * 70)
    print("2. COMPARANDO SÉRIE REAL COM A BASE ATUAL")
    print("=" * 70)
    
    if not os.path.exists(CURRENT_TRENDS_PATH):
        raise FileNotFoundError(f"Base atual não encontrada em: {CURRENT_TRENDS_PATH}")
    
    df_current = pd.read_csv(CURRENT_TRENDS_PATH)
    df_current["data"] = pd.to_datetime(df_current["data"]).dt.strftime("%Y-%m-01")
    df_current = df_current.rename(columns={"google_trends_score": "score_atual_sintetico"})
    
    merged = df_real.merge(
        df_current[["data", "score_atual_sintetico"]],
        on="data",
        how="inner"
    )
    
    # Correlações
    corr_composto = merged["score_atual_sintetico"].corr(merged["score_composto_real"])
    corr_bet_solo = merged["score_atual_sintetico"].corr(merged["score_bet_solo"])
    corr_bet_comp = merged["score_atual_sintetico"].corr(merged["score_bet_real"])
    
    print("\n--- MATRIZ DE CORRELAÇÃO LINEAR (PEARSON) COM A BASE ATUAL ---")
    print(f"• Atual (Sintético) vs. Real Composto (Soma Ponderada): r = {corr_composto:.4f}")
    print(f"• Atual (Sintético) vs. Real 'bet' (Escala Própria):    r = {corr_bet_solo:.4f}")
    print(f"• Atual (Sintético) vs. Real 'bet' (Escala Comparada):  r = {corr_bet_comp:.4f}")
    
    # Comparativo Anual Médio
    yearly_comp = merged.groupby("ano").agg(
        atual_sintetico=("score_atual_sintetico", "mean"),
        real_composto=("score_composto_real", "mean"),
        real_bet_solo=("score_bet_solo", "mean"),
        bet365=("bet365", "mean"),
        betano=("betano", "mean"),
        sportingbet=("sportingbet", "mean"),
        bet=("bet", "mean"),
        apostas_esp=("apostas esportivas", "mean")
    ).round(2)
    
    yearly_comp["dif_composto_menos_atual"] = (yearly_comp["real_composto"] - yearly_comp["atual_sintetico"]).round(2)
    yearly_comp["dif_bet_menos_atual"] = (yearly_comp["real_bet_solo"] - yearly_comp["atual_sintetico"]).round(2)
    
    print("\n--- EVOLUÇÃO MÉDIA ANUAL (2015–2025) ---")
    print(yearly_comp[["atual_sintetico", "real_composto", "real_bet_solo", "dif_composto_menos_atual", "dif_bet_menos_atual"]])
    
    print("\n--- DECOMPOSIÇÃO DOS TERMOS REAIS POR ANO (ESCALA COMPARATIVA) ---")
    print(yearly_comp[["bet", "bet365", "betano", "sportingbet", "apostas_esp"]])
    
    # Meses de Pico Histórico
    idx_pico_atual = merged["score_atual_sintetico"].idxmax()
    idx_pico_comp = merged["score_composto_real"].idxmax()
    idx_pico_bet = merged["score_bet_solo"].idxmax()
    
    print("\n--- PONTOS DE MÁXIMO HISTÓRICO (PICO 100) ---")
    print(f"• Base Atual: {merged.loc[idx_pico_atual, 'data']} (Score: {merged.loc[idx_pico_atual, 'score_atual_sintetico']:.1f})")
    print(f"• Real Composto: {merged.loc[idx_pico_comp, 'data']} (Score: {merged.loc[idx_pico_comp, 'score_composto_real']:.1f})")
    print(f"• Real 'bet' Solo: {merged.loc[idx_pico_bet, 'data']} (Score: {merged.loc[idx_pico_bet, 'score_bet_solo']:.1f})")
    
    return merged, yearly_comp


if __name__ == "__main__":
    df_real, terms = extract_real_google_trends()
    merged, yearly_comp = compare_with_current(df_real, terms)
    
    # Salvar extração para inspeção sem sobrescrever a base oficial de produção
    out_inspect_dir = os.path.join("data", "interim")
    os.makedirs(out_inspect_dir, exist_ok=True)
    out_file = os.path.join(out_inspect_dir, "comparativo_google_trends_real_vs_atual.csv")
    merged.to_csv(out_file, index=False, encoding="utf-8")
    print(f"\n-> Arquivo comparativo salvo para auditoria em: {out_file}")
