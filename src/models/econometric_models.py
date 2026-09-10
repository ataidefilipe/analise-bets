"""
src/models/econometric_models.py
--------------------------------
Estimação dos modelos econométricos e de inferência causal da Fase 7:
1. Two-Way Fixed Effects (TWFE) com exposição contínua (bet_exposure_clube e bet_exposure_total).
2. Estudo de Eventos com Adoção Escalonada (Staggered Event Study) e Teste de Tendências Paralelas.
3. Modelos de Dose-Resposta Categórica (Nenhuma, Parcial, Total).
4. Modelagem de Heterogeneidade Interdivisões (Série A vs. Série B em 2022–2023).
5. Exportação de tabelas acadêmicas consolidadas em reports/tables/.
"""

import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

PANEL_PATH = os.path.join("data", "processed", "panel", "painel_clube_partida.parquet")
SERIE_B_PARTIDAS = os.path.join("data", "processed", "serie_b", "partidas.parquet")
SERIE_B_CARTOES = os.path.join("data", "processed", "serie_b", "cartoes.parquet")
TABLES_DIR = os.path.join("reports", "tables")


def load_panel() -> pd.DataFrame:
    if not os.path.exists(PANEL_PATH):
        from src.models.prepare_panel import build_panel_dataset
        return build_panel_dataset()
    return pd.read_parquet(PANEL_PATH)


def run_twfe_models(df: pd.DataFrame) -> pd.DataFrame:
    """Estima regressões TWFE para múltiplas variáveis dependentes com erros clusterizados por clube."""
    os.makedirs(TABLES_DIR, exist_ok=True)
    targets = [
        ("cartoes_totais", "Cartões Totais", df),
        ("cartao_amarelo", "Cartões Amarelos", df),
        ("cartao_vermelho", "Cartões Vermelhos", df),
        ("taxa_conversao", "Taxa Conversão (Cartão/Falta)", df[df["scouts_validos"] & (df["faltas"] > 0)]),
        ("prop_cartoes_1t", "Proporção Cartões 1T", df),
        ("faltas", "Faltas Cometidas", df[df["scouts_validos"] & (df["faltas"] > 0)]),
        ("gols_penalty_marcados", "Gols de Pênalti Marcados", df),
    ]

    results = []

    for dep_var, dep_label, sub_df in targets:
        # 1. Modelo com bet_exposure_clube (estritamente contratual)
        formula_clube = (
            f"{dep_var} ~ bet_exposure_clube + is_mandante + rodada + saldo_gols + mesma_uf "
            f"+ C(clube_slug) + C(temporada)"
        )
        mod_clube = smf.ols(formula_clube, data=sub_df).fit(
            cov_type="cluster", cov_kwds={"groups": sub_df["clube_slug"]}
        )

        # 2. Modelo com exposure_adversario
        formula_opp = (
            f"{dep_var} ~ bet_exposure_clube + exposure_adversario + is_mandante + rodada + saldo_gols + mesma_uf "
            f"+ C(clube_slug) + C(temporada)"
        )
        mod_opp = smf.ols(formula_opp, data=sub_df).fit(
            cov_type="cluster", cov_kwds={"groups": sub_df["clube_slug"]}
        )

        results.append({
            "variavel_dependente": dep_label,
            "dep_var_code": dep_var,
            "n_obs": int(mod_clube.nobs),
            "r2": round(mod_clube.rsquared, 4),
            "r2_adj": round(mod_clube.rsquared_adj, 4),
            "coef_bet_exposure": round(mod_clube.params["bet_exposure_clube"], 4),
            "std_err_bet_exposure": round(mod_clube.bse["bet_exposure_clube"], 4),
            "t_stat_bet_exposure": round(mod_clube.tvalues["bet_exposure_clube"], 4),
            "p_val_bet_exposure": round(mod_clube.pvalues["bet_exposure_clube"], 5),
            "coef_is_mandante": round(mod_clube.params["is_mandante"], 4),
            "p_val_is_mandante": round(mod_clube.pvalues["is_mandante"], 5),
            "coef_saldo_gols": round(mod_clube.params["saldo_gols"], 4),
            "p_val_saldo_gols": round(mod_clube.pvalues["saldo_gols"], 5),
            "coef_exposure_adversario": round(mod_opp.params.get("exposure_adversario", np.nan), 4),
            "p_val_exposure_adversario": round(mod_opp.pvalues.get("exposure_adversario", np.nan), 5),
        })

    df_results = pd.DataFrame(results)
    csv_path = os.path.join(TABLES_DIR, "tabela_11_regressoes_twfe.csv")
    df_results.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[OK] Tabela TWFE exportada: {csv_path}")
    return df_results


def run_staggered_event_study(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Estima o Event Study escalonado relativo ao ano imediatamente anterior à adoção (e = -1)."""
    os.makedirs(TABLES_DIR, exist_ok=True)
    df_es = df.copy()

    # Identificar primeiro ano de patrocínio de aposta para cada clube
    first_bet = df_es[df_es["tem_patrocinio_bet"]].groupby("clube_slug")["temporada"].min().rename("primeiro_ano_bet")
    df_es = df_es.merge(first_bet, on="clube_slug", how="left")

    # Event time: temporada - primeiro_ano_bet (NaN para clubes que nunca adotaram)
    df_es["event_time"] = df_es["temporada"] - df_es["primeiro_ano_bet"]

    # Dummies para event time: de <= -3 a >= +4 (omitindo -1 como referência basal)
    df_es["event_m3"] = (df_es["event_time"] <= -3).astype(int)
    df_es["event_m2"] = (df_es["event_time"] == -2).astype(int)
    df_es["event_p0"] = (df_es["event_time"] == 0).astype(int)
    df_es["event_p1"] = (df_es["event_time"] == 1).astype(int)
    df_es["event_p2"] = (df_es["event_time"] == 2).astype(int)
    df_es["event_p3"] = (df_es["event_time"] == 3).astype(int)
    df_es["event_p4"] = (df_es["event_time"] >= 4).astype(int)

    event_vars = ["event_m3", "event_m2", "event_p0", "event_p1", "event_p2", "event_p3", "event_p4"]
    event_terms = " + ".join(event_vars)

    outcomes = [
        ("cartoes_totais", "Cartões Totais", df_es),
        ("taxa_conversao", "Taxa Conversão (Cartão/Falta)", df_es[df_es["scouts_validos"] & (df_es["faltas"] > 0)]),
        ("faltas", "Faltas Cometidas", df_es[df_es["scouts_validos"] & (df_es["faltas"] > 0)]),
    ]

    all_event_results = []
    tests_summary = {}

    labels_map = {
        "event_m3": "e <= -3 (3+ anos antes)",
        "event_m2": "e = -2 (2 anos antes)",
        "event_p0": "e = 0 (Ano de Adoção)",
        "event_p1": "e = +1 (1 ano após)",
        "event_p2": "e = +2 (2 anos após)",
        "event_p3": "e = +3 (3 anos após)",
        "event_p4": "e >= +4 (4+ anos após)",
    }

    for dep_var, dep_label, sub_data in outcomes:
        formula = f"{dep_var} ~ {event_terms} + is_mandante + rodada + saldo_gols + mesma_uf + C(clube_slug) + C(temporada)"
        mod = smf.ols(formula, data=sub_data).fit(
            cov_type="cluster", cov_kwds={"groups": sub_data["clube_slug"]}
        )

        # Teste F de tendências paralelas (H0: event_m3 = 0, event_m2 = 0)
        f_test = mod.f_test("event_m3 = 0, event_m2 = 0")
        tests_summary[dep_var] = {
            "f_stat": float(f_test.fvalue.item() if hasattr(f_test.fvalue, "item") else f_test.fvalue),
            "p_val": float(f_test.pvalue.item() if hasattr(f_test.pvalue, "item") else f_test.pvalue),
        }

        for ev in event_vars:
            coef = mod.params[ev]
            se = mod.bse[ev]
            pval = mod.pvalues[ev]
            ci_low = coef - 1.96 * se
            ci_high = coef + 1.96 * se
            all_event_results.append({
                "variavel_dependente": dep_label,
                "dep_var_code": dep_var,
                "event_var": ev,
                "event_label": labels_map[ev],
                "event_time": int(ev.replace("event_m", "-").replace("event_p", "")),
                "coeficiente": round(coef, 4),
                "std_err": round(se, 4),
                "ci_95_inferior": round(ci_low, 4),
                "ci_95_superior": round(ci_high, 4),
                "p_valor": round(pval, 5),
            })

    df_event = pd.DataFrame(all_event_results)
    csv_path = os.path.join(TABLES_DIR, "tabela_12_did_event_study.csv")
    df_event.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[OK] Tabela Event Study exportada: {csv_path}")
    return df_event, tests_summary


def run_dose_response_models(df: pd.DataFrame) -> pd.DataFrame:
    """Estima modelos de dose-resposta por categoria de exposição na partida."""
    os.makedirs(TABLES_DIR, exist_ok=True)

    # Agregação no nível da partida (1 linha por jogo)
    match_df = df[df["is_mandante"] == 1].copy()

    # Dummies para dose-resposta (Nenhuma como categoria basal)
    match_df["dose_parcial"] = (match_df["categoria_exposicao_partida"] == "Parcial (1 clube)").astype(int)
    match_df["dose_total"] = (match_df["categoria_exposicao_partida"] == "Total (2 clubes)").astype(int)

    targets = [
        ("cartoes_totais", "Cartões Totais da Partida"),
        ("taxa_conversao", "Taxa de Conversão"),
        ("prop_cartoes_1t", "Proporção Cartões 1T"),
        ("penalti_na_partida", "Probabilidade de Pênalti no Jogo"),
    ]

    results = []
    for dep_var, dep_label in targets:
        sub_data = match_df.dropna(subset=[dep_var]).copy()
        formula = f"{dep_var} ~ dose_parcial + dose_total + rodada + mesma_uf + C(temporada)"
        mod = smf.ols(formula, data=sub_data).fit(cov_type="HC1")

        results.append({
            "variavel_dependente": dep_label,
            "dep_var_code": dep_var,
            "n_partidas": int(mod.nobs),
            "r2": round(mod.rsquared, 4),
            "media_categoria_nenhuma": round(sub_data[sub_data["dose_parcial"] + sub_data["dose_total"] == 0][dep_var].mean(), 4),
            "coef_dose_parcial": round(mod.params["dose_parcial"], 4),
            "std_err_dose_parcial": round(mod.bse["dose_parcial"], 4),
            "p_val_dose_parcial": round(mod.pvalues["dose_parcial"], 5),
            "coef_dose_total": round(mod.params["dose_total"], 4),
            "std_err_dose_total": round(mod.bse["dose_total"], 4),
            "p_val_dose_total": round(mod.pvalues["dose_total"], 5),
            "diferenca_total_vs_parcial": round(mod.params["dose_total"] - mod.params["dose_parcial"], 4),
        })

    df_dose = pd.DataFrame(results)
    csv_path = os.path.join(TABLES_DIR, "tabela_13_dose_resposta_econometrica.csv")
    df_dose.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[OK] Tabela Dose-Resposta exportada: {csv_path}")
    return df_dose


def run_series_heterogeneity_models(df: pd.DataFrame) -> pd.DataFrame:
    """Estima a heterogeneidade interdivisões (Série A vs. Série B) para 2022–2023."""
    os.makedirs(TABLES_DIR, exist_ok=True)

    # 1. Série A 2022–2023
    df_a = df[df["temporada"].isin([2022, 2023])].copy()
    df_a["serie"] = "A"
    df_a["is_serie_b"] = 0

    # 2. Série B 2022–2023
    df_pb = pd.read_parquet(SERIE_B_PARTIDAS)
    df_cb = pd.read_parquet(SERIE_B_CARTOES)

    cards_b = df_cb.groupby(["partida_id", "clube_slug"]).size().rename("cartoes_totais")
    cards_b_1t = df_cb[df_cb["periodo"] == "1T"].groupby(["partida_id", "clube_slug"]).size().rename("cartoes_1t")

    mb = pd.DataFrame({
        "partida_id": df_pb["partida_id"],
        "temporada": df_pb["temporada"],
        "rodada": df_pb["rodada"],
        "clube_slug": df_pb["clube_mandante_slug"],
        "adversario_slug": df_pb["clube_visitante_slug"],
        "is_mandante": 1,
        "gols_pro": df_pb["gols_mandante"],
        "gols_contra": df_pb["gols_visitante"],
        "serie": "B",
        "is_serie_b": 1,
    })
    vb = pd.DataFrame({
        "partida_id": df_pb["partida_id"],
        "temporada": df_pb["temporada"],
        "rodada": df_pb["rodada"],
        "clube_slug": df_pb["clube_visitante_slug"],
        "adversario_slug": df_pb["clube_mandante_slug"],
        "is_mandante": 0,
        "gols_pro": df_pb["gols_visitante"],
        "gols_contra": df_pb["gols_mandante"],
        "serie": "B",
        "is_serie_b": 1,
    })

    b_panel = pd.concat([mb, vb], ignore_index=True)
    b_panel = b_panel.set_index(["partida_id", "clube_slug"]).join(cards_b).join(cards_b_1t).reset_index()
    b_panel["cartoes_totais"] = b_panel["cartoes_totais"].fillna(0).astype(int)
    b_panel["cartoes_1t"] = b_panel["cartoes_1t"].fillna(0).astype(int)
    b_panel["saldo_gols"] = b_panel["gols_pro"] - b_panel["gols_contra"]
    b_panel["prop_cartoes_1t"] = np.where(
        b_panel["cartoes_totais"] > 0, b_panel["cartoes_1t"] / b_panel["cartoes_totais"], 0.0
    )

    common_cols = ["partida_id", "temporada", "rodada", "clube_slug", "is_mandante", "saldo_gols", "cartoes_totais", "cartoes_1t", "prop_cartoes_1t", "serie", "is_serie_b"]
    combined = pd.concat([df_a[common_cols], b_panel[common_cols]], ignore_index=True)

    # Regressão com interação Série B x Temporada 2023
    combined["ano_2023"] = (combined["temporada"] == 2023).astype(int)
    combined["interacao_serie_b_2023"] = combined["is_serie_b"] * combined["ano_2023"]

    formula = "cartoes_totais ~ is_serie_b + ano_2023 + interacao_serie_b_2023 + is_mandante + saldo_gols + rodada"
    mod = smf.ols(formula, data=combined).fit(cov_type="cluster", cov_kwds={"groups": combined["clube_slug"]})

    formula_1t = "prop_cartoes_1t ~ is_serie_b + ano_2023 + interacao_serie_b_2023 + is_mandante + saldo_gols + rodada"
    mod_1t = smf.ols(formula_1t, data=combined).fit(cov_type="cluster", cov_kwds={"groups": combined["clube_slug"]})

    res = pd.DataFrame([
        {
            "modelo": "Cartões Totais (Séries A e B 2022-2023)",
            "n_obs": int(mod.nobs),
            "r2": round(mod.rsquared, 4),
            "coef_is_serie_b": round(mod.params["is_serie_b"], 4),
            "p_val_is_serie_b": round(mod.pvalues["is_serie_b"], 5),
            "coef_ano_2023": round(mod.params["ano_2023"], 4),
            "p_val_ano_2023": round(mod.pvalues["ano_2023"], 5),
            "coef_interacao": round(mod.params["interacao_serie_b_2023"], 4),
            "p_val_interacao": round(mod.pvalues["interacao_serie_b_2023"], 5),
            "coef_is_mandante": round(mod.params["is_mandante"], 4),
            "p_val_is_mandante": round(mod.pvalues["is_mandante"], 5),
        },
        {
            "modelo": "Proporção Cartões 1T (Séries A e B 2022-2023)",
            "n_obs": int(mod_1t.nobs),
            "r2": round(mod_1t.rsquared, 4),
            "coef_is_serie_b": round(mod_1t.params["is_serie_b"], 4),
            "p_val_is_serie_b": round(mod_1t.pvalues["is_serie_b"], 5),
            "coef_ano_2023": round(mod_1t.params["ano_2023"], 4),
            "p_val_ano_2023": round(mod_1t.pvalues["ano_2023"], 5),
            "coef_interacao": round(mod_1t.params["interacao_serie_b_2023"], 4),
            "p_val_interacao": round(mod_1t.pvalues["interacao_serie_b_2023"], 5),
            "coef_is_mandante": round(mod_1t.params["is_mandante"], 4),
            "p_val_is_mandante": round(mod_1t.pvalues["is_mandante"], 5),
        }
    ])

    csv_path = os.path.join(TABLES_DIR, "tabela_14_heterogeneidade_series_regressao.csv")
    res.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[OK] Tabela Heterogeneidade Série A vs B exportada: {csv_path}")
    return res


def run_all_econometric_models():
    """Executa o pipeline completo de modelagem econométrica."""
    print("\n" + "=" * 70)
    print("INICIANDO MODELAGEM ECONOMÉTRICA E CAUSAL (FASE 7)")
    print("=" * 70)

    df = load_panel()

    print("\n--- 1. Estimando Modelos Two-Way Fixed Effects (TWFE) ---")
    df_twfe = run_twfe_models(df)

    print("\n--- 2. Estimando Staggered Event Study e Teste de Tendências Paralelas ---")
    df_event, tests_summary = run_staggered_event_study(df)
    for k, v in tests_summary.items():
        print(f"     Teste Tendências Paralelas [{k}]: F = {v['f_stat']:.3f} | p-valor = {v['p_val']:.4f}")

    print("\n--- 3. Estimando Modelos de Dose-Resposta Categórica ---")
    df_dose = run_dose_response_models(df)

    print("\n--- 4. Estimando Modelos de Heterogeneidade Interdivisões ---")
    df_series = run_series_heterogeneity_models(df)

    print("\n" + "=" * 70)
    print("MODELAGEM ECONOMÉTRICA CONCLUÍDA COM SUCESSO!")
    print("=" * 70)

    return {
        "twfe": df_twfe,
        "event_study": df_event,
        "parallel_trends": tests_summary,
        "dose_response": df_dose,
        "series_heterogeneity": df_series,
    }


if __name__ == "__main__":
    run_all_econometric_models()
