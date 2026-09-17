"""
src/models/validacao_out_of_sample.py
-------------------------------------
Validação fora da amostra do classificador de integridade (tarefa F1-03).

Problema
--------
O classificador híbrido é treinado e avaliado sobre os mesmos 14 casos da Operação Penalidade
Máxima: `df_pm` constrói o rótulo positivo do treino PU **e** serve de gabarito da avaliação.
Com 14 positivos, qualquer classificador semi-supervisionado atinge 100% de sensibilidade
in-sample — o número não carrega informação sobre generalização.

Protocolos implementados
------------------------
1. **Leave-one-out agrupado por atleta.** Retreina sem o grupo do atleta e verifica se ele
   ainda seria capturado. O agrupamento é obrigatório: PM-006 e PM-007 são o mesmo atleta, e
   deixar um dentro do treino enquanto se avalia o outro é vazamento.
2. **Leave-one-out por partida.** Mesmo procedimento no nível da partida.
3. **Separação por série.** Treina com os positivos de uma divisão e avalia na outra — o caso
   de uso real: detectar um esquema novo com um modelo calibrado em esquemas anteriores.

Distinção essencial (item B.4 da tarefa)
---------------------------------------
Os escores estatísticos `MATCH_ANOMALY_SCORE` e `ATHLETE_ANOMALY_SCORE` são **fórmulas
fechadas** calibradas em distribuição basal: não veem o ground truth em momento algum. A
sensibilidade deles é a mesma dentro e fora da amostra, e não é objeto deste módulo. O
`IsolationForest` também é não supervisionado. Só o `BaggingPUClassifier` é treinado nos
rótulos — e só ele sofre do problema de avaliação in-sample.
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from src.models.integrity_classifier import BaggingPUClassifier
from src.models.anomaly_detection import load_unified_data, GROUND_TRUTH_PATH
from src.models.ground_truth_resolver import resolver_partidas, resolver_atletas

TABLES_DIR = os.path.join("reports", "tables")
INTEGRITY_DIR = os.path.join("data", "processed", "integrity")

FEATURES_PARTIDA = [
    "prop_cartoes_1t", "prop_cartoes_30m", "total_cartoes", "z_cartoes",
    "cartoes_reclamacao_cera", "penaltis_1t", "score_tempo", "score_precoce",
]
FEATURES_ATLETA = [
    "prop_cartoes_1t", "cartoes_30m", "minuto_medio_partida",
    "total_cartoes", "score_atleta_tempo", "score_atleta_taxa", "score_atleta_minuto",
]

# Mesmos limiares operacionais do pipeline de produção.
LIMIAR_CLASSE_2 = 0.60
LIMIAR_CLASSE_2_COM_OUTLIER = 0.45
LIMIAR_CLASSE_1 = 0.35


def intervalo_wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """
    Intervalo de confiança de Wilson para uma proporção. Com N = 14, o intervalo normal
    aproximado é inadequado (chega a ultrapassar [0, 1]); o de Wilson, não.
    """
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z**2 / n
    centro = (p + z**2 / (2 * n)) / denom
    margem = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, centro - margem), min(1.0, centro + margem))


def _classificar(prob: float, outlier: int) -> str:
    if prob >= LIMIAR_CLASSE_2 or (outlier == 1 and prob >= LIMIAR_CLASSE_2_COM_OUTLIER):
        return "Classe 2"
    if prob >= LIMIAR_CLASSE_1 or outlier == 1:
        return "Classe 1"
    return "Classe 0"


def _ajustar_iforest(X: np.ndarray) -> np.ndarray:
    """O Isolation Forest é não supervisionado: o mesmo ajuste vale para todas as dobras."""
    iforest = IsolationForest(n_estimators=300, contamination=0.03, max_samples=0.8, random_state=42)
    iforest.fit(X)
    return (iforest.predict(X) == -1).astype(int)


def _probabilidades(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    clf = BaggingPUClassifier(n_estimators=50, random_state=42)
    clf.fit(X, y)
    return clf.predict_proba(X)[:, 1]


def _executar_protocolo(X: np.ndarray, outliers: np.ndarray, positivos: dict[str, list[int]],
                        nivel: str, protocolo: str,
                        grupos_treino: dict[str, list[str]] | None = None) -> list[dict]:
    """
    Executa um protocolo de avaliação.

    `positivos` mapeia rótulo do grupo -> índices na matriz. Em leave-one-out, cada grupo é
    retirado do treino e avaliado. Em `grupos_treino`, cada chave é um cenário de treino cujo
    valor lista os grupos que permanecem rotulados; os demais são avaliados.
    """
    linhas = []
    cenarios = grupos_treino or {g: [o for o in positivos if o != g] for g in positivos}

    for cenario, grupos_rotulados in cenarios.items():
        y = np.zeros(len(X), dtype=int)
        for g in grupos_rotulados:
            y[positivos[g]] = 1
        if y.sum() == 0:
            continue

        prob = _probabilidades(X, y)
        avaliados = [g for g in positivos if g not in grupos_rotulados]
        for grupo in avaliados:
            for idx in positivos[grupo]:
                p = float(prob[idx])
                linhas.append({
                    "protocolo": protocolo,
                    "nivel": nivel,
                    "cenario": cenario,
                    "grupo_avaliado": grupo,
                    "indice": idx,
                    "positivos_no_treino": int(y.sum()),
                    "prob_suspeicao": round(p, 4),
                    "percentil_prob": round(float((prob <= p).mean() * 100), 2),
                    "iforest_outlier": int(outliers[idx]),
                    "classe": _classificar(p, outliers[idx]),
                })
    return linhas


def executar_validacao() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Executa os três protocolos nos dois níveis e consolida a tabela de sensibilidade."""
    df_matches = pd.read_parquet(os.path.join(INTEGRITY_DIR, "partidas_anomaly_scored.parquet"))
    df_athletes = pd.read_parquet(os.path.join(INTEGRITY_DIR, "atletas_anomaly_scored.parquet"))
    df_pm = pd.read_parquet(GROUND_TRUTH_PATH)
    _, df_cards, _ = load_unified_data()

    res_partidas = resolver_partidas(df_matches, df_pm)
    res_atletas = resolver_atletas(df_cards, df_athletes, df_pm)

    # ---------------------------------------------------------------- nível partida
    Xm = df_matches[FEATURES_PARTIDA].fillna(0).values
    out_m = _ajustar_iforest(Xm)
    chave_m = df_matches.set_index(["serie", "temporada", "partida_id"]).index

    positivos_partida: dict[str, list[int]] = {}
    serie_do_grupo_m: dict[str, str] = {}
    for _, r in res_partidas.iterrows():
        if pd.isna(r["partida_id"]):
            continue
        chave = (r["serie"], r["temporada"], r["partida_id"])
        idx = [i for i, k in enumerate(chave_m) if k == chave]
        if not idx:
            continue
        positivos_partida.setdefault(r["caso_id"], []).extend(idx)
        serie_do_grupo_m[r["caso_id"]] = r["serie"]

    # ---------------------------------------------------------------- nível atleta
    Xa = df_athletes[FEATURES_ATLETA].fillna(0).values
    out_a = _ajustar_iforest(Xa)

    positivos_atleta: dict[str, list[int]] = {}
    serie_do_grupo_a: dict[str, str] = {}
    resolvidos = res_atletas[res_atletas["status_atleta"] == "resolvido"]
    for _, r in resolvidos.iterrows():
        mask = ((df_athletes["serie"] == r["serie"]) &
                (df_athletes["temporada"] == r["temporada"]) &
                (df_athletes["atleta_slug"] == r["atleta_slug_base"]))
        idx = list(np.where(mask.values)[0])
        if idx:
            positivos_atleta[r["atleta_ground_truth"]] = idx
            serie_do_grupo_a[r["atleta_ground_truth"]] = r["serie"]

    linhas: list[dict] = []

    # 1. In-sample (referência): treina com todos os positivos e avalia sobre eles mesmos.
    for nivel, X, out, positivos in (("partida", Xm, out_m, positivos_partida),
                                     ("atleta", Xa, out_a, positivos_atleta)):
        y = np.zeros(len(X), dtype=int)
        for idx in positivos.values():
            y[idx] = 1
        prob = _probabilidades(X, y)
        for grupo, idxs in positivos.items():
            for idx in idxs:
                p = float(prob[idx])
                linhas.append({
                    "protocolo": "in_sample", "nivel": nivel, "cenario": "todos_os_positivos",
                    "grupo_avaliado": grupo, "indice": idx, "positivos_no_treino": int(y.sum()),
                    "prob_suspeicao": round(p, 4),
                    "percentil_prob": round(float((prob <= p).mean() * 100), 2),
                    "iforest_outlier": int(out[idx]), "classe": _classificar(p, out[idx]),
                })

    # 2. Leave-one-out agrupado
    linhas += _executar_protocolo(Xm, out_m, positivos_partida, "partida", "leave_one_out")
    linhas += _executar_protocolo(Xa, out_a, positivos_atleta, "atleta", "leave_one_out")

    # 3. Separação por série
    for nivel, X, out, positivos, series in (("partida", Xm, out_m, positivos_partida, serie_do_grupo_m),
                                             ("atleta", Xa, out_a, positivos_atleta, serie_do_grupo_a)):
        cenarios = {
            "treina_em_B_avalia_em_A": [g for g, s in series.items() if s == "B"],
            "treina_em_A_avalia_em_B": [g for g, s in series.items() if s == "A"],
        }
        cenarios = {k: v for k, v in cenarios.items() if v and len(v) < len(positivos)}
        linhas += _executar_protocolo(X, out, positivos, nivel, "separacao_por_serie",
                                      grupos_treino=cenarios)

    detalhe = pd.DataFrame(linhas)

    # ---------------------------------------------------------------- consolidação
    # No leave-one-out cada dobra avalia um único grupo; a sensibilidade só faz sentido
    # agregada sobre todas as dobras.
    detalhe["cenario_agregado"] = np.where(
        detalhe["protocolo"] == "leave_one_out", "todas_as_dobras", detalhe["cenario"]
    )

    resumo = []
    for (protocolo, nivel, cenario), g in detalhe.groupby(
            ["protocolo", "nivel", "cenario_agregado"], sort=False):
        n = len(g)
        for rotulo, mascara in (("Classe 2 (Alto Risco)", g["classe"] == "Classe 2"),
                                ("Classe 1 ou 2 (sinalizado)", g["classe"].isin(["Classe 1", "Classe 2"]))):
            k = int(mascara.sum())
            lo, hi = intervalo_wilson(k, n)
            resumo.append({
                "protocolo": protocolo, "nivel": nivel, "cenario": cenario, "criterio": rotulo,
                "capturados": k, "avaliados": n,
                "sensibilidade": round(k / n, 4) if n else np.nan,
                "ic95_inferior": round(lo, 4), "ic95_superior": round(hi, 4),
                "percentil_mediano_da_prob": round(float(g["percentil_prob"].median()), 2),
            })
    resumo = pd.DataFrame(resumo)

    os.makedirs(TABLES_DIR, exist_ok=True)
    resumo.to_csv(os.path.join(TABLES_DIR, "tabela_22_validacao_out_of_sample.csv"), index=False, encoding="utf-8")
    detalhe.to_csv(os.path.join(TABLES_DIR, "tabela_22b_validacao_out_of_sample_detalhe.csv"), index=False, encoding="utf-8")
    return resumo, detalhe


if __name__ == "__main__":
    resumo, detalhe = executar_validacao()
    print("\n=== SENSIBILIDADE POR PROTOCOLO (Tabela 22) ===")
    print(resumo.to_string(index=False))
    print("\nDetalhe salvo em reports/tables/tabela_22b_validacao_out_of_sample_detalhe.csv")
