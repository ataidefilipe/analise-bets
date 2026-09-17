"""
src/analysis/precisao_e_carga_alerta.py
---------------------------------------
Precisão, carga de alerta e curva operacional do sistema de triagem (tarefa F1-04).

Motivação
---------
Todo o sistema vinha sendo avaliado por **sensibilidade** — quantos casos reais foram
capturados. Nenhuma métrica dizia quantos alertas isso custa. Para as personas do produto, é a
segunda pergunta que decide a compra: três revisões de vídeo por rodada é acionável, quarenta
não é.

O que este módulo entrega
-------------------------
1. **Tabela 21** — carga de alerta por tier e por nível: absolutos, percentual da base, alertas
   por rodada (partida) ou por temporada (atleta) e alertas por caso conhecido.
2. **Precisão@k** — para k = 1, 3, 5 e 10, restrita às rodadas que contêm ground truth.
3. **Curva de carga operacional** — sensibilidade contra alertas por rodada conforme o limiar
   percentílico varia, com a figura correspondente.
4. **Limiar recomendado por persona**, derivado da curva.

Limitação que atravessa tudo
----------------------------
Não existem falsos positivos rotulados. O ground truth cobre uma operação, uma temporada e 13
partidas: partidas sinalizadas e não investigadas **não são** negativos confirmados. Por isso a
precisão absoluta não é estimável, e o entregável honesto é a carga de alerta mais a
precisão@k sobre o ground truth disponível, com o denominador declarado.
"""

import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.models.anomaly_detection import (
    TIERS_PARTIDA, TIER_PARTIDA_BASAL, TIERS_ATLETA, TIER_ATLETA_BASAL, GROUND_TRUTH_PATH,
    load_unified_data,
)
from src.models.ground_truth_resolver import resolver_partidas, resolver_atletas

INTEGRITY_DIR = os.path.join("data", "processed", "integrity")
TABLES_DIR = os.path.join("reports", "tables")
FIGURES_DIR = os.path.join("reports", "figures", "integrity")

# Limiares candidatos da curva de carga operacional, em percentil do escore.
PERCENTIS_DA_CURVA = [99.9, 99.5, 99.0, 98.0, 97.0, 96.0, 95.0, 92.5, 90.0, 85.0, 80.0, 75.0, 70.0, 60.0, 50.0]

# Carga que cada persona consegue absorver, em revisões por rodada. Derivada das entrevistas
# previstas na F5-01; até lá, são premissas declaradas, não achados.
PERSONAS = {
    "Analista de federação / STJD": {
        "capacidade_por_rodada": 3.0,
        "racional": "Revisão de vídeo de lances de advertência por analista, dentro da janela de uma rodada.",
    },
    "Compliance de clube": {
        "capacidade_por_rodada": 1.0,
        "racional": "Acompanha apenas o próprio elenco; o alerta relevante é o que envolve os seus atletas.",
    },
    "Integrity de operadora": {
        "capacidade_por_rodada": 10.0,
        "racional": "Tratamento documental em escala, com equipe dedicada e tolerância maior a falso alarme.",
    },
}


def _p_hipergeometrico(capturados: int, n_base: int, n_sinalizados: int, n_positivos: int) -> float:
    """
    P(capturar ao menos `capturados` positivos | sorteio de `n_sinalizados` da base).

    E a pergunta que importa com 13 positivos: a triagem encontra mais casos do que sortear a
    mesma quantidade de partidas? Um p-valor alto significa que nao ha ganho demonstravel —
    e nao que o sistema foi provado inutil. Com N tao pequeno, o teste tem pouco poder.
    """
    if n_positivos == 0 or n_sinalizados == 0:
        return float("nan")
    return float(stats.hypergeom.sf(capturados - 1, n_base, n_positivos, n_sinalizados))


def _carregar():
    matches = pd.read_parquet(os.path.join(INTEGRITY_DIR, "partidas_anomaly_scored.parquet"))
    athletes = pd.read_parquet(os.path.join(INTEGRITY_DIR, "atletas_anomaly_scored.parquet"))
    df_pm = pd.read_parquet(GROUND_TRUTH_PATH)
    _, df_cards, _ = load_unified_data()
    return matches, athletes, df_pm, df_cards


def _chaves_positivas(matches, athletes, df_pm, df_cards):
    """Partidas e atletas do ground truth, pelo resolvedor de identidade da F1-03."""
    rp = resolver_partidas(matches, df_pm)
    chaves_partida = {
        (r["serie"], r["temporada"], r["partida_id"])
        for _, r in rp.iterrows() if pd.notna(r["partida_id"])
    }
    ra = resolver_atletas(df_cards, athletes, df_pm)
    resolvidos = ra[ra["status_atleta"] == "resolvido"]
    chaves_atleta = {
        (r["serie"], r["temporada"], r["atleta_slug_base"]) for _, r in resolvidos.iterrows()
    }
    return chaves_partida, chaves_atleta


def tabela_carga_por_tier(matches, athletes, chaves_partida, chaves_atleta) -> pd.DataFrame:
    """Tabela 21: volume de alerta por tier, nos dois níveis."""
    n_rodadas = matches.groupby(["serie", "temporada", "rodada"]).ngroups
    n_temporadas = athletes.groupby(["serie", "temporada"]).ngroups

    matches = matches.copy()
    matches["_positivo"] = [
        (s, t, p) in chaves_partida
        for s, t, p in zip(matches["serie"], matches["temporada"], matches["partida_id"])
    ]
    athletes = athletes.copy()
    athletes["_positivo"] = [
        (s, t, a) in chaves_atleta
        for s, t, a in zip(athletes["serie"], athletes["temporada"], athletes["atleta_slug"])
    ]

    linhas = []
    configs = [
        ("partida", matches, "prioridade_triagem", TIERS_PARTIDA, TIER_PARTIDA_BASAL,
         "alertas_por_rodada", n_rodadas),
        ("atleta", athletes, "classificacao_atleta", TIERS_ATLETA, TIER_ATLETA_BASAL,
         "alertas_por_temporada_serie", n_temporadas),
    ]

    for nivel, df, coluna_tier, tiers, basal, rotulo_unidade, divisor in configs:
        total_positivos = int(df["_positivo"].sum())
        for corte, rotulo in list(tiers) + [(None, basal)]:
            sel = df[df[coluna_tier] == rotulo]
            n = len(sel)
            capturados = int(sel["_positivo"].sum())
            linhas.append({
                "nivel": nivel,
                "tier": rotulo,
                "corte_percentil": corte,
                "sinalizados": n,
                "pct_da_base": round(n / len(df) * 100, 2),
                rotulo_unidade: round(n / divisor, 2),
                "casos_conhecidos_no_tier": capturados,
                "casos_conhecidos_totais": total_positivos,
                "alertas_por_caso_conhecido": round(n / capturados, 1) if capturados else np.nan,
            })

    # Linha acumulada: tudo acima do corte mais baixo é, na prática, a fila de trabalho.
    for nivel, df, coluna_tier, tiers, basal, rotulo_unidade, divisor in configs:
        sel = df[df[coluna_tier] != basal]
        capturados = int(sel["_positivo"].sum())
        linhas.append({
            "nivel": nivel,
            "tier": "TOTAL SINALIZADO (todos os tiers)",
            "corte_percentil": min(c for c, _ in tiers),
            "sinalizados": len(sel),
            "pct_da_base": round(len(sel) / len(df) * 100, 2),
            rotulo_unidade: round(len(sel) / divisor, 2),
            "casos_conhecidos_no_tier": capturados,
            "casos_conhecidos_totais": int(df["_positivo"].sum()),
            "alertas_por_caso_conhecido": round(len(sel) / capturados, 1) if capturados else np.nan,
        })

    return pd.DataFrame(linhas)


def precisao_at_k(matches, chaves_partida, ks=(1, 3, 5, 10)) -> pd.DataFrame:
    """
    Precisão@k por rodada, restrita às rodadas que contêm ao menos um caso do ground truth.

    Com no máximo 3 positivos conhecidos em uma rodada de 10 partidas, a precisão@k tem um teto
    aritmético: `positivos_na_rodada / k`. O teto é reportado junto, para que a métrica não seja
    lida como se o modelo pudesse atingir 100%.
    """
    matches = matches.copy()
    matches["_positivo"] = [
        (s, t, p) in chaves_partida
        for s, t, p in zip(matches["serie"], matches["temporada"], matches["partida_id"])
    ]
    rodadas_com_gt = (
        matches[matches["_positivo"]].groupby(["serie", "temporada", "rodada"]).size().index
    )

    linhas = []
    for k in ks:
        acertos = positivos = teto = avaliadas = 0
        for chave in rodadas_com_gt:
            serie, temporada, rodada = chave
            rodada_df = matches[(matches["serie"] == serie) &
                                (matches["temporada"] == temporada) &
                                (matches["rodada"] == rodada)]
            topo = rodada_df.nlargest(k, "match_anomaly_score")
            acertos += int(topo["_positivo"].sum())
            n_pos = int(rodada_df["_positivo"].sum())
            positivos += n_pos
            teto += min(k, n_pos)
            avaliadas += 1

        linhas.append({
            "k": k,
            "rodadas_avaliadas": avaliadas,
            "partidas_inspecionadas": avaliadas * k,
            "positivos_na_amostra": positivos,
            "positivos_capturados": acertos,
            "precisao_at_k": round(acertos / (avaliadas * k), 4) if avaliadas else np.nan,
            "precisao_maxima_possivel": round(teto / (avaliadas * k), 4) if avaliadas else np.nan,
            "recall_at_k": round(acertos / positivos, 4) if positivos else np.nan,
            # Uma rodada tem 10 partidas: em k = 10 inspeciona-se a rodada inteira, e o recall
            # de 100% nao diz nada. O ganho sobre o acaso e sortear k das 10.
            "ganho_sobre_aleatorio": round((acertos / positivos) / (k / 10.0), 2)
            if positivos else np.nan,
        })
    return pd.DataFrame(linhas)


def curva_carga_operacional(matches, chaves_partida) -> pd.DataFrame:
    """Sensibilidade contra volume de alerta, conforme o limiar percentílico varia."""
    n_rodadas = matches.groupby(["serie", "temporada", "rodada"]).ngroups
    positivo = np.array([
        (s, t, p) in chaves_partida
        for s, t, p in zip(matches["serie"], matches["temporada"], matches["partida_id"])
    ])
    total_positivos = int(positivo.sum())

    linhas = []
    for corte in PERCENTIS_DA_CURVA:
        sinalizada = (matches["percentil_anomalia"] >= corte).values
        capturados = int((sinalizada & positivo).sum())
        linhas.append({
            "corte_percentil": corte,
            "score_minimo": round(float(matches["match_anomaly_score"].quantile(corte / 100)), 2),
            "sinalizados": int(sinalizada.sum()),
            "pct_da_base": round(sinalizada.mean() * 100, 2),
            "alertas_por_rodada": round(sinalizada.sum() / n_rodadas, 2),
            "casos_capturados": capturados,
            "casos_conhecidos": total_positivos,
            "sensibilidade": round(capturados / total_positivos, 4) if total_positivos else np.nan,
            "alertas_por_caso_capturado": round(sinalizada.sum() / capturados, 1) if capturados else np.nan,
            # Ganho sobre sortear a mesma quantidade de partidas ao acaso. 1,0 = indistinguivel
            # do acaso; abaixo de 1,0, a triagem e pior do que sortear.
            "ganho_sobre_aleatorio": round(
                (capturados / total_positivos) / sinalizada.mean(), 2
            ) if total_positivos and sinalizada.mean() > 0 else np.nan,
            "p_valor_vs_acaso": round(_p_hipergeometrico(
                capturados, len(matches), int(sinalizada.sum()), total_positivos), 4),
        })
    return pd.DataFrame(linhas)


def curva_carga_operacional_atleta(athletes, chaves_atleta) -> pd.DataFrame:
    """
    Mesma curva no nivel do atleta-temporada. A unidade operacional aqui nao e a rodada, e sim
    a temporada de uma divisao: o escore de atleta so existe ao fim do acumulo de cartoes.
    """
    n_temporadas = athletes.groupby(["serie", "temporada"]).ngroups
    positivo = np.array([
        (s, t, a) in chaves_atleta
        for s, t, a in zip(athletes["serie"], athletes["temporada"], athletes["atleta_slug"])
    ])
    total_positivos = int(positivo.sum())

    linhas = []
    for corte in PERCENTIS_DA_CURVA:
        sinalizado = (athletes["percentil_atleta"] >= corte).values
        capturados = int((sinalizado & positivo).sum())
        linhas.append({
            "corte_percentil": corte,
            "score_minimo": round(float(athletes["athlete_anomaly_score"].quantile(corte / 100)), 2),
            "sinalizados": int(sinalizado.sum()),
            "pct_da_base": round(sinalizado.mean() * 100, 2),
            "alertas_por_temporada_serie": round(sinalizado.sum() / n_temporadas, 1),
            "casos_capturados": capturados,
            "casos_conhecidos": total_positivos,
            "sensibilidade": round(capturados / total_positivos, 4) if total_positivos else np.nan,
            "ganho_sobre_aleatorio": round(
                (capturados / total_positivos) / sinalizado.mean(), 2
            ) if total_positivos and sinalizado.mean() > 0 else np.nan,
            "p_valor_vs_acaso": round(_p_hipergeometrico(
                capturados, len(athletes), int(sinalizado.sum()), total_positivos), 4),
        })
    return pd.DataFrame(linhas)


def limiares_por_persona(curva: pd.DataFrame) -> pd.DataFrame:
    """
    Para cada persona, o corte mais permissivo que ainda cabe na sua capacidade declarada —
    isto é, a maior sensibilidade alcançável dentro do orçamento de revisão.
    """
    linhas = []
    for persona, cfg in PERSONAS.items():
        cabem = curva[curva["alertas_por_rodada"] <= cfg["capacidade_por_rodada"]]
        if cabem.empty:
            linhas.append({
                "persona": persona, "capacidade_por_rodada": cfg["capacidade_por_rodada"],
                "corte_percentil_recomendado": np.nan, "alertas_por_rodada": np.nan,
                "sensibilidade_esperada": np.nan, "casos_capturados": np.nan,
                "racional": cfg["racional"],
            })
            continue
        escolhido = cabem.loc[cabem["corte_percentil"].idxmin()]
        linhas.append({
            "persona": persona,
            "capacidade_por_rodada": cfg["capacidade_por_rodada"],
            "corte_percentil_recomendado": escolhido["corte_percentil"],
            "score_minimo": escolhido["score_minimo"],
            "alertas_por_rodada": escolhido["alertas_por_rodada"],
            "sensibilidade_esperada": escolhido["sensibilidade"],
            "casos_capturados": f"{int(escolhido['casos_capturados'])}/{int(escolhido['casos_conhecidos'])}",
            "racional": cfg["racional"],
        })
    return pd.DataFrame(linhas)


def plotar_curva(curva: pd.DataFrame, curva_atleta: pd.DataFrame, personas: pd.DataFrame) -> str:
    """
    Duas curvas de carga operacional, partida e atleta, contra a mesma referencia: sortear a
    mesma quantidade de registros ao acaso. A distancia entre a curva e a diagonal e o ganho
    real da triagem — e e ela que decide se o sistema tem valor operacional.
    """
    os.makedirs(FIGURES_DIR, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    paineis = [
        (ax1, curva, "Nivel partida", "alertas_por_rodada", "#1f4e79",
         "Alertas por rodada (carga operacional)", (99.0, 95.0, 90.0, 85.0, 80.0, 50.0)),
        (ax2, curva_atleta, "Nivel atleta-temporada", "alertas_por_temporada_serie", "#7b3294",
         "Alertas por temporada e divisao", (99.0, 95.0, 90.0, 75.0, 70.0, 60.0)),
    ]

    for ax, dados, titulo, coluna_carga, cor, rotulo_x, anotar in paineis:
        ax.plot(dados["pct_da_base"], dados["sensibilidade"] * 100,
                marker="o", color=cor, linewidth=2, label="Triagem")
        ax.plot([0, 55], [0, 55], linestyle=":", color="#999999", linewidth=1.8,
                label="Selecao aleatoria (referencia)")
        for _, r in dados.iterrows():
            if r["corte_percentil"] in anotar:
                marca = "*" if r["p_valor_vs_acaso"] < 0.05 else ""
                ax.annotate(f"P{r['corte_percentil']:.0f}{marca}",
                            (r["pct_da_base"], r["sensibilidade"] * 100),
                            textcoords="offset points", xytext=(6, -12),
                            fontsize=9, color="#555555")
        n_pos = int(dados["casos_conhecidos"].iloc[0])
        ax.set_xlabel("Percentual da base sinalizado (%)")
        ax.set_ylabel(f"Sensibilidade no ground truth (%)  —  n = {n_pos}")
        ax.set_title(titulo, fontsize=12, fontweight="bold")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=9, loc="upper left")

        segundo = ax.secondary_xaxis(
            "top",
            functions=(lambda x, d=dados, c=coluna_carga: x * d[c].max() / d["pct_da_base"].max(),
                       lambda x, d=dados, c=coluna_carga: x * d["pct_da_base"].max() / d[c].max()),
        )
        segundo.set_xlabel(rotulo_x, fontsize=9, color="#555555")

    cores = ["#d62728", "#2ca02c", "#ff7f0e"]
    for cor, (_, pers) in zip(cores, personas.iterrows()):
        if pd.notna(pers.get("corte_percentil_recomendado")):
            linha = curva[curva["corte_percentil"] == pers["corte_percentil_recomendado"]]
            if not linha.empty:
                ax1.axvline(float(linha["pct_da_base"].iloc[0]), color=cor, linestyle="--",
                            linewidth=1.2, alpha=0.8,
                            label=f"{pers['persona']} ({pers['capacidade_por_rodada']:.0f}/rodada)")
    ax1.legend(fontsize=8, loc="upper left")

    fig.suptitle(
        "Curva de carga operacional. A curva da triagem so tem valor onde se afasta da diagonal. "
        "* = p < 0,05 contra sorteio (teste hipergeometrico). "
        "Sem falsos positivos rotulados, a precisao absoluta nao e estimavel.",
        fontsize=9, y=0.02, color="#555555",
    )
    plt.tight_layout()
    caminho = os.path.join(FIGURES_DIR, "04_curva_carga_operacional.png")
    plt.savefig(caminho, dpi=300, bbox_inches="tight")
    plt.close()
    return caminho


def executar():
    matches, athletes, df_pm, df_cards = _carregar()
    chaves_partida, chaves_atleta = _chaves_positivas(matches, athletes, df_pm, df_cards)

    t21 = tabela_carga_por_tier(matches, athletes, chaves_partida, chaves_atleta)
    t21b = precisao_at_k(matches, chaves_partida)
    curva = curva_carga_operacional(matches, chaves_partida)
    curva_atleta = curva_carga_operacional_atleta(athletes, chaves_atleta)
    personas = limiares_por_persona(curva)

    os.makedirs(TABLES_DIR, exist_ok=True)
    t21.to_csv(os.path.join(TABLES_DIR, "tabela_21_precisao_e_carga_de_alerta.csv"), index=False, encoding="utf-8")
    t21b.to_csv(os.path.join(TABLES_DIR, "tabela_21b_precisao_at_k.csv"), index=False, encoding="utf-8")
    curva.to_csv(os.path.join(TABLES_DIR, "tabela_21c_curva_carga_operacional.csv"), index=False, encoding="utf-8")
    curva_atleta.to_csv(os.path.join(TABLES_DIR, "tabela_21e_curva_carga_operacional_atleta.csv"), index=False, encoding="utf-8")
    personas.to_csv(os.path.join(TABLES_DIR, "tabela_21d_limiar_por_persona.csv"), index=False, encoding="utf-8")
    caminho_fig = plotar_curva(curva, curva_atleta, personas)

    return t21, t21b, curva, curva_atleta, personas, caminho_fig


if __name__ == "__main__":
    t21, t21b, curva, curva_atleta, personas, fig = executar()
    print("\n=== TABELA 21 — CARGA DE ALERTA POR TIER ===")
    print(t21.to_string(index=False))
    print("\n=== PRECISAO@K (rodadas com ground truth) ===")
    print(t21b.to_string(index=False))
    print("\n=== CURVA DE CARGA OPERACIONAL ===")
    print(curva.to_string(index=False))
    print("\n=== LIMIAR RECOMENDADO POR PERSONA ===")
    print(personas.drop(columns=["racional"]).to_string(index=False))
    print("\nFigura:", fig)
