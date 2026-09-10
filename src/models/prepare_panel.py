"""
src/models/prepare_panel.py
---------------------------
Estrutura o painel econométrico no nível Clube x Partida para as temporadas 2015–2024 da Série A.
Cada partida gera 2 observações (mandante e visitante).
Integra:
- Variáveis dependentes disciplinares: faltas, cartões amarelos, cartões vermelhos,
  cartões totais, cartões no 1T, taxa de conversão faltas -> cartões e gols de pênalti.
- Variáveis explicativas de exposição a bets: bet_exposure_clube, bet_exposure_total,
  tem_patrocinio_bet, categoria_exposicao_partida e exposição do adversário.
- Covariáveis e controles exógenos: mando de campo (is_mandante), era_var,
  rodada, rodada_final (>=31), clássico estadual (mesma_uf), saldo de gols e resultado.
"""

import os
import hashlib
import json
import pandas as pd
import numpy as np

PROCESSED_SERIE_A_DIR = os.path.join("data", "processed", "serie_a")
PROCESSED_PANEL_DIR = os.path.join("data", "processed", "panel")


def build_panel_dataset() -> pd.DataFrame:
    """Constrói o painel Clube x Partida consolidado para 2015–2024."""
    os.makedirs(PROCESSED_PANEL_DIR, exist_ok=True)

    # 1. Carregar Partidas com Exposição
    partidas_path = os.path.join(PROCESSED_SERIE_A_DIR, "partidas_com_exposure.parquet")
    df_partidas = pd.read_parquet(partidas_path)
    # Filtrar temporadas do estudo econométrico (2015 a 2024)
    df_p = df_partidas[df_partidas["temporada"] >= 2015].copy()

    # Identificar clubes que adotaram patrocínio de aposta em algum momento pós-2018
    clubes_tratados = set(
        df_p[(df_p["temporada"] >= 2019) & (df_p["tem_bet_mandante"] | df_p["tem_bet_visitante"])][
            "clube_mandante_slug"
        ].unique()
    ) | set(
        df_p[(df_p["temporada"] >= 2019) & (df_p["tem_bet_mandante"] | df_p["tem_bet_visitante"])][
            "clube_visitante_slug"
        ].unique()
    )

    # 2. Decompor em Mandante e Visitante
    mandante_df = pd.DataFrame({
        "partida_id": df_p["partida_id"],
        "temporada": df_p["temporada"],
        "rodada": df_p["rodada"],
        "data": df_p["data"],
        "clube": df_p["clube_mandante"],
        "clube_slug": df_p["clube_mandante_slug"],
        "clube_uf": df_p["mandante_uf"],
        "adversario": df_p["clube_visitante"],
        "adversario_slug": df_p["clube_visitante_slug"],
        "adversario_uf": df_p["visitante_uf"],
        "is_mandante": 1,
        "gols_pro": df_p["gols_mandante"],
        "gols_contra": df_p["gols_visitante"],
        "saldo_gols": df_p["saldo_mandante"],
        "tem_patrocinio_bet": df_p["tem_bet_mandante"],
        "tipo_patrocinio_bet": df_p["tipo_bet_mandante"],
        "marca_bet": df_p["marca_bet_mandante"],
        "bet_exposure_clube": df_p["exposure_clube_mandante"],
        "bet_exposure_total": df_p["exposure_total_mandante"],
        "exposure_adversario": df_p["exposure_total_visitante"],
        "exposure_partida": df_p["exposure_total_partida"],
        "categoria_exposicao_partida": df_p["categoria_exposicao_partida"],
    })

    visitante_df = pd.DataFrame({
        "partida_id": df_p["partida_id"],
        "temporada": df_p["temporada"],
        "rodada": df_p["rodada"],
        "data": df_p["data"],
        "clube": df_p["clube_visitante"],
        "clube_slug": df_p["clube_visitante_slug"],
        "clube_uf": df_p["visitante_uf"],
        "adversario": df_p["clube_mandante"],
        "adversario_slug": df_p["clube_mandante_slug"],
        "adversario_uf": df_p["mandante_uf"],
        "is_mandante": 0,
        "gols_pro": df_p["gols_visitante"],
        "gols_contra": df_p["gols_mandante"],
        "saldo_gols": -df_p["saldo_mandante"],
        "tem_patrocinio_bet": df_p["tem_bet_visitante"],
        "tipo_patrocinio_bet": df_p["tipo_bet_visitante"],
        "marca_bet": df_p["marca_bet_visitante"],
        "bet_exposure_clube": df_p["exposure_clube_visitante"],
        "bet_exposure_total": df_p["exposure_total_visitante"],
        "exposure_adversario": df_p["exposure_total_mandante"],
        "exposure_partida": df_p["exposure_total_partida"],
        "categoria_exposicao_partida": df_p["categoria_exposicao_partida"],
    })

    panel = pd.concat([mandante_df, visitante_df], ignore_index=True)
    panel = panel.sort_values(["partida_id", "is_mandante"], ascending=[True, False]).reset_index(drop=True)

    # 3. Covariáveis derivadas
    panel["mesma_uf"] = (panel["clube_uf"] == panel["adversario_uf"]).astype(int)
    panel["vitoria"] = (panel["saldo_gols"] > 0).astype(int)
    panel["derrota"] = (panel["saldo_gols"] < 0).astype(int)
    panel["empate"] = (panel["saldo_gols"] == 0).astype(int)
    panel["resultado"] = np.where(
        panel["vitoria"] == 1, "Vitoria", np.where(panel["derrota"] == 1, "Derrota", "Empate")
    )
    panel["era_var"] = (panel["temporada"] >= 2019).astype(int)
    panel["pos_2018"] = (panel["temporada"] >= 2019).astype(int)
    panel["rodada_final"] = (panel["rodada"] >= 31).astype(int)
    panel["did_tratado"] = panel["clube_slug"].apply(lambda s: 1 if s in clubes_tratados else 0)
    panel["did_interacao"] = panel["did_tratado"] * panel["pos_2018"]

    # 4. Integrar Scouts de Estatísticas
    estat_path = os.path.join(PROCESSED_SERIE_A_DIR, "estatisticas.parquet")
    df_estat = pd.read_parquet(estat_path)
    df_estat = df_estat[df_estat["temporada"] >= 2015]

    panel = pd.merge(
        panel,
        df_estat[[
            "partida_id", "clube_slug", "faltas", "cartao_amarelo", "cartao_vermelho",
            "escanteios", "chutes", "posse_de_bola_pct", "scouts_validos"
        ]],
        on=["partida_id", "clube_slug"],
        how="left"
    )

    panel["faltas"] = panel["faltas"].fillna(0).astype(int)
    panel["cartao_amarelo"] = panel["cartao_amarelo"].fillna(0).astype(int)
    panel["cartao_vermelho"] = panel["cartao_vermelho"].fillna(0).astype(int)
    panel["cartoes_totais"] = panel["cartao_amarelo"] + panel["cartao_vermelho"]
    panel["escanteios"] = panel["escanteios"].fillna(0).astype(int)
    panel["chutes"] = panel["chutes"].fillna(0).astype(int)
    panel["posse_de_bola_pct"] = panel["posse_de_bola_pct"].fillna(0.50)
    panel["scouts_validos"] = panel["scouts_validos"].fillna(True).astype(bool)

    # Taxa de conversão faltas -> cartões
    panel["taxa_conversao"] = np.where(
        panel["faltas"] > 0,
        panel["cartoes_totais"] / panel["faltas"],
        np.nan
    )

    # 5. Integrar Cartões no 1º e 2º Tempo
    cartoes_path = os.path.join(PROCESSED_SERIE_A_DIR, "cartoes.parquet")
    df_cartoes = pd.read_parquet(cartoes_path)
    df_cartoes = df_cartoes[df_cartoes["temporada"] >= 2015]

    c_1t = (
        df_cartoes[df_cartoes["periodo"] == "1T"]
        .groupby(["partida_id", "clube_slug"])
        .size()
        .rename("cartoes_1t")
    )
    c_2t = (
        df_cartoes[df_cartoes["periodo"] == "2T"]
        .groupby(["partida_id", "clube_slug"])
        .size()
        .rename("cartoes_2t")
    )

    panel = panel.set_index(["partida_id", "clube_slug"])
    panel = panel.join(c_1t).join(c_2t).reset_index()

    panel["cartoes_1t"] = panel["cartoes_1t"].fillna(0).astype(int)
    panel["cartoes_2t"] = panel["cartoes_2t"].fillna(0).astype(int)
    panel["prop_cartoes_1t"] = np.where(
        panel["cartoes_totais"] > 0,
        panel["cartoes_1t"] / panel["cartoes_totais"],
        0.0
    )

    # 6. Integrar Pênaltis Marcados e Sofridos
    gols_path = os.path.join(PROCESSED_SERIE_A_DIR, "gols.parquet")
    df_gols = pd.read_parquet(gols_path)
    df_gols = df_gols[df_gols["temporada"] >= 2015]

    penaltis = (
        df_gols[df_gols["tipo_de_gol"] == "Penalty"]
        .groupby(["partida_id", "clube_slug"])
        .size()
        .rename("gols_penalty_marcados")
    )

    panel = panel.set_index(["partida_id", "clube_slug"])
    panel = panel.join(penaltis).reset_index()
    panel["gols_penalty_marcados"] = panel["gols_penalty_marcados"].fillna(0).astype(int)

    # Para pênaltis sofridos, cruzar com o adversário na mesma partida
    penaltis_sofridos = panel[["partida_id", "clube_slug", "gols_penalty_marcados"]].rename(
        columns={"clube_slug": "adversario_slug", "gols_penalty_marcados": "gols_penalty_sofridos"}
    )
    panel = pd.merge(panel, penaltis_sofridos, on=["partida_id", "adversario_slug"], how="left")
    panel["gols_penalty_sofridos"] = panel["gols_penalty_sofridos"].fillna(0).astype(int)
    panel["penalti_na_partida"] = (
        (panel["gols_penalty_marcados"] > 0) | (panel["gols_penalty_sofridos"] > 0)
    ).astype(int)

    # 7. Exportar
    parquet_path = os.path.join(PROCESSED_PANEL_DIR, "painel_clube_partida.parquet")
    csv_path = os.path.join(PROCESSED_PANEL_DIR, "painel_clube_partida.csv")

    panel.to_parquet(parquet_path, index=False)
    panel.to_csv(csv_path, index=False, encoding="utf-8")

    # Manifesto de Integridade
    def get_hash(path):
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    manifest = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "total_rows": len(panel),
        "total_columns": len(panel.columns),
        "columns": list(panel.columns),
        "temporadas": sorted(panel["temporada"].unique().tolist()),
        "total_clubes": int(panel["clube_slug"].nunique()),
        "files": {
            "painel_clube_partida.parquet": {
                "sha256": get_hash(parquet_path),
                "size_bytes": os.path.getsize(parquet_path),
            },
            "painel_clube_partida.csv": {
                "sha256": get_hash(csv_path),
                "size_bytes": os.path.getsize(csv_path),
            },
        },
    }

    with open(os.path.join(PROCESSED_PANEL_DIR, "manifest_panel.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[OK] Painel Clube x Partida construído com sucesso!")
    print(f"     Linhas: {len(panel)} | Colunas: {len(panel.columns)} | Clubes únicos: {panel['clube_slug'].nunique()}")
    print(f"     Temporadas: {panel['temporada'].min()} a {panel['temporada'].max()}")
    print(f"     Média de cartões por clube-jogo: {panel['cartoes_totais'].mean():.3f}")
    print(f"     Média de faltas por clube-jogo: {panel['faltas'].mean():.2f}")
    print(f"     Taxa de conversão média: {panel['taxa_conversao'].mean():.4f}")

    return panel


if __name__ == "__main__":
    build_panel_dataset()
