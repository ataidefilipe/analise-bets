"""
src/models/integrity_classifier.py
----------------------------------
Modelos de Machine Learning para Classificação de Integridade e Suspeição:
1. Isolation Forest Multidimensional para Partidas (Detecção de Outliers não-supervisionada).
2. Classificador Semi-Supervisionado (Bagging PU-Learning) para probabilidade calibrada de suspeição em partidas.
3. Isolation Forest e PU-Learning para Atletas individuais.
4. Validação e auditoria comparativa com os 14 casos reais da Operação Penalidade Máxima.
5. Exportação de modelos serializados (.joblib) e tabelas analíticas (Tabelas 18, 19 e 20).
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import RobustScaler

from src.models.ground_truth_resolver import resolver_partidas, resolver_atletas
from src.pipeline.camadas_de_exposicao import (
    CAMADA_ABERTA,
    aplicar_camada,
    salvar_mapa_pseudonimos,
)

DATA_PARTIDAS = os.path.join("data", "processed", "integrity", "partidas_anomaly_scored.parquet")
DATA_ATLETAS = os.path.join("data", "processed", "integrity", "atletas_anomaly_scored.parquet")
DATA_PM = os.path.join("data", "processed", "integrity", "casos_penalidade_maxima.parquet")

MODELS_DIR = os.path.join("data", "processed", "integrity", "models")
TABLES_DIR = os.path.join("reports", "tables")
INTEGRITY_DIR = os.path.join("data", "processed", "integrity")


class BaggingPUClassifier:
    """
    Classificador Semi-Supervisionado para Aprendizado com Amostras Positivas e Não-Rotuladas (PU Learning).
    Utiliza ensemble com bagging no conjunto não-rotulado para evitar viés de desbalanceamento extremo.
    """

    def __init__(self, n_estimators: int = 50, random_state: int = 42):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.estimators_ = []
        self.scaler_ = RobustScaler()

    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        X: matriz de features.
        y: 1 para casos positivos confirmados, 0 para instâncias não-rotuladas.
        """
        rng = np.random.RandomState(self.random_state)
        X_scaled = self.scaler_.fit_transform(X)

        pos_idx = np.where(y == 1)[0]
        unlabeled_idx = np.where(y == 0)[0]
        n_pos = len(pos_idx)

        self.estimators_ = []
        # Tamanho da amostra de não-rotulados por bag: 4x a quantidade de positivos
        sample_size = min(len(unlabeled_idx), max(n_pos * 4, 30))

        for i in range(self.n_estimators):
            sub_unlabeled = rng.choice(unlabeled_idx, size=sample_size, replace=False)
            bag_idx = np.concatenate([pos_idx, sub_unlabeled])

            X_bag = X_scaled[bag_idx]
            y_bag = y[bag_idx]

            clf = RandomForestClassifier(
                n_estimators=60,
                max_depth=4,
                class_weight="balanced",
                random_state=rng.randint(0, 10000)
            )
            clf.fit(X_bag, y_bag)
            self.estimators_.append(clf)

        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X_scaled = self.scaler_.transform(X)
        probas = np.zeros((len(X), 2))
        for clf in self.estimators_:
            probas += clf.predict_proba(X_scaled)
        probas /= len(self.estimators_)
        return probas

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        prob = self.predict_proba(X)[:, 1]
        return (prob >= threshold).astype(int)

    def save(self, filepath: str):
        """Salva componentes sklearn puros em joblib compactado para máxima portabilidade."""
        joblib.dump({
            "n_estimators": self.n_estimators,
            "random_state": self.random_state,
            "scaler": self.scaler_,
            "estimators": self.estimators_
        }, filepath, compress=3)

    @classmethod
    def load(cls, filepath: str):
        """Carrega componentes e restaura o classificador."""
        data = joblib.load(filepath)
        obj = cls(n_estimators=data["n_estimators"], random_state=data["random_state"])
        obj.scaler_ = data["scaler"]
        obj.estimators_ = data["estimators"]
        return obj


def train_match_classifiers(df_matches: pd.DataFrame, df_pm: pd.DataFrame):
    """Treina o Isolation Forest e o classificador PU no nível da partida."""
    # NOTA (F1-02): `exposure_total_partida` foi retirada do espaço de features. Estimar a
    # associação entre exposição a bets e cartões pela econometria e, ao mesmo tempo, usar a
    # mesma exposição como preditor de suspeição faz o modelo confirmar a hipótese por
    # construção. A coluna segue na base como contexto e variável de estratificação.
    feature_cols = [
        "prop_cartoes_1t", "prop_cartoes_30m", "total_cartoes", "z_cartoes",
        "cartoes_reclamacao_cera", "penaltis_1t",
        "score_tempo", "score_precoce"
    ]

    X = df_matches[feature_cols].copy().fillna(0).values

    # 1. Isolation Forest (Contaminação de 3% das partidas mais discrepantes)
    print("     Treinando Isolation Forest para partidas...")
    iforest = IsolationForest(
        n_estimators=300,
        contamination=0.03,
        max_samples=0.8,
        random_state=42
    )
    iforest.fit(X)

    # Score de decisão invertido e normalizado [0, 100]
    raw_scores = -iforest.decision_function(X)
    min_s, max_s = raw_scores.min(), raw_scores.max()
    norm_scores = ((raw_scores - min_s) / (max_s - min_s) * 100.0).round(2)
    df_matches["iforest_anomaly_score"] = norm_scores
    df_matches["iforest_outlier"] = (iforest.predict(X) == -1).astype(int)

    # 2. Mapeamento de Ground Truth para PU Learning, via resolvedor explícito (F1-03).
    # A chave inclui a temporada: a `partida_id` da Série B reinicia a cada ano.
    resolucao = resolver_partidas(df_matches, df_pm)
    chaves_positivas = {
        (r["serie"], r["temporada"], r["partida_id"])
        for _, r in resolucao.iterrows() if pd.notna(r["partida_id"])
    }
    y_pu = df_matches.apply(
        lambda r: int((r["serie"], r["temporada"], r["partida_id"]) in chaves_positivas), axis=1
    ).values
    print(f"     Casos positivos de partidas mapeados no treino PU: {y_pu.sum()}")

    print("     Treinando Classificador Semi-Supervisionado (Bagging PU Learning)...")
    pu_clf = BaggingPUClassifier(n_estimators=50, random_state=42)
    pu_clf.fit(X, y_pu)

    prob_suspeicao = pu_clf.predict_proba(X)[:, 1]
    df_matches["prob_suspeicao_ml"] = prob_suspeicao.round(4)
    df_matches["score_suspeicao_ml"] = (prob_suspeicao * 100.0).round(2)

    # 3. Classificação Operacional em Tiers
    conditions = [
        (df_matches["prob_suspeicao_ml"] >= 0.60) | ((df_matches["iforest_outlier"] == 1) & (df_matches["prob_suspeicao_ml"] >= 0.45)),
        (df_matches["prob_suspeicao_ml"] >= 0.35) | (df_matches["iforest_outlier"] == 1),
    ]
    choices = [
        "Classe 2: Alto Risco / Alerta Investigativo",
        "Classe 1: Monitoramento / Risco Moderado",
    ]
    df_matches["classificacao_ml"] = np.select(conditions, choices, default="Classe 0: Basal / Conforme")
    df_matches["ranking_ml"] = df_matches["score_suspeicao_ml"].rank(ascending=False, method="min").astype(int)

    return iforest, pu_clf, df_matches, feature_cols


def train_athlete_classifiers(df_athletes: pd.DataFrame, df_pm: pd.DataFrame, df_cards: pd.DataFrame):
    """Treina o Isolation Forest e o classificador PU no nível do atleta."""
    feature_cols = [
        "prop_cartoes_1t", "cartoes_30m", "minuto_medio_partida",
        "total_cartoes", "score_atleta_tempo", "score_atleta_taxa", "score_atleta_minuto"
    ]

    X = df_athletes[feature_cols].copy().fillna(0).values

    print("     Treinando Isolation Forest para atletas...")
    iforest_ath = IsolationForest(
        n_estimators=300,
        contamination=0.03,
        max_samples=0.8,
        random_state=42
    )
    iforest_ath.fit(X)

    raw_scores = -iforest_ath.decision_function(X)
    min_s, max_s = raw_scores.min(), raw_scores.max()
    df_athletes["iforest_anomaly_score"] = ((raw_scores - min_s) / (max_s - min_s) * 100.0).round(2)
    df_athletes["iforest_outlier"] = (iforest_ath.predict(X) == -1).astype(int)

    # Mapeamento de Atletas do Ground Truth, via resolvedor explícito (F1-03).
    # Só entram como positivos os atletas efetivamente resolvidos na base pontuada; os demais
    # (não resolvidos ou abaixo do mínimo de cartões) ficam de fora — rotular o atleta errado
    # é pior do que não rotular.
    resolucao = resolver_atletas(df_cards, df_athletes, df_pm)
    resolvidos = resolucao[resolucao["status_atleta"] == "resolvido"]
    chaves_positivas = {
        (r["serie"], r["temporada"], r["atleta_slug_base"]) for _, r in resolvidos.iterrows()
    }
    y_pu = df_athletes.apply(
        lambda r: int((r["serie"], r["temporada"], r["atleta_slug"]) in chaves_positivas), axis=1
    ).values
    print(f"     Atletas positivos únicos mapeados no treino PU: {y_pu.sum()}")

    print("     Treinando Classificador PU para Atletas...")
    pu_ath = BaggingPUClassifier(n_estimators=50, random_state=42)
    pu_ath.fit(X, y_pu)

    prob_ath = pu_ath.predict_proba(X)[:, 1]
    df_athletes["prob_suspeicao_ml"] = prob_ath.round(4)
    df_athletes["score_suspeicao_ml"] = (prob_ath * 100.0).round(2)

    conditions = [
        (df_athletes["prob_suspeicao_ml"] >= 0.60) | ((df_athletes["iforest_outlier"] == 1) & (df_athletes["prob_suspeicao_ml"] >= 0.45)),
        (df_athletes["prob_suspeicao_ml"] >= 0.35) | (df_athletes["iforest_outlier"] == 1),
    ]
    choices = [
        "Classe 2: Extrema Anomalia / Alto Risco",
        "Classe 1: Monitoramento / Risco Moderado",
    ]
    df_athletes["classificacao_ml"] = np.select(conditions, choices, default="Classe 0: Padrão Basal Normal")
    df_athletes["ranking_ml"] = df_athletes["score_suspeicao_ml"].rank(ascending=False, method="min").astype(int)

    return iforest_ath, pu_ath, df_athletes, feature_cols


def evaluate_ground_truth_ml(df_matches: pd.DataFrame, df_athletes: pd.DataFrame,
                             df_pm: pd.DataFrame, df_cards: pd.DataFrame) -> pd.DataFrame:
    """
    Cruza as predições do modelo de ML contra os 14 casos da Operação Penalidade Máxima,
    usando o resolvedor de identidade explícito (F1-03).

    Atenção: esta é uma métrica **in-sample** — os mesmos casos compõem o rótulo positivo do
    treino PU. A estimativa fora da amostra está em `src/models/validacao_out_of_sample.py`.
    """
    res_partidas = resolver_partidas(df_matches, df_pm).set_index("caso_id")
    res_atletas = resolver_atletas(df_cards, df_athletes, df_pm).set_index("atleta_slug_ground_truth")

    results = []
    for _, row in df_pm.iterrows():
        rp = res_partidas.loc[row["caso_id"]]
        m_score_orig = m_prob_ml = np.nan
        m_class_ml = "Partida não resolvida"
        if pd.notna(rp["partida_id"]):
            alvo = df_matches[(df_matches["serie"] == row["serie"]) &
                              (df_matches["temporada"] == row["temporada"]) &
                              (df_matches["partida_id"] == rp["partida_id"])]
            if len(alvo) > 0:
                m_score_orig = float(alvo.iloc[0]["match_anomaly_score"])
                m_prob_ml = float(alvo.iloc[0]["prob_suspeicao_ml"])
                m_class_ml = str(alvo.iloc[0]["classificacao_ml"])

        ra = res_atletas.loc[row["atleta_slug"]]
        a_score_orig = a_prob_ml = np.nan
        a_class_ml = f"Atleta não avaliável ({ra['status_atleta']})"
        if ra["status_atleta"] == "resolvido":
            alvo = df_athletes[(df_athletes["serie"] == ra["serie"]) &
                               (df_athletes["temporada"] == ra["temporada"]) &
                               (df_athletes["atleta_slug"] == ra["atleta_slug_base"])]
            if len(alvo) > 0:
                a_score_orig = float(alvo.iloc[0]["athlete_anomaly_score"])
                a_prob_ml = float(alvo.iloc[0]["prob_suspeicao_ml"])
                a_class_ml = str(alvo.iloc[0]["classificacao_ml"])

        if "Alto Risco" in m_class_ml or "Extrema Anomalia" in a_class_ml:
            status_ml = "Detectado (Alto Risco / Alerta Investigativo)"
        elif "Monitoramento" in m_class_ml or "Monitoramento" in a_class_ml:
            status_ml = "Detectado (Risco Moderado / Triagem ML)"
        else:
            status_ml = "Basal / Não sinalizado"

        results.append({
            "caso_id": row["caso_id"],
            "temporada": row["temporada"],
            "serie": row["serie"],
            "rodada": rp["rodada_utilizada"],
            "confronto": row["confronto"],
            "atleta": row["atleta"],
            "evento_alvo": row["evento_alvo"],
            "evento_ocorreu": row["evento_ocorreu"],
            "status_atleta": ra["status_atleta"],
            "score_partida_heuristico": m_score_orig,
            "prob_partida_ml": m_prob_ml,
            "classe_partida_ml": m_class_ml,
            "score_atleta_heuristico": a_score_orig,
            "prob_atleta_ml": a_prob_ml,
            "classe_atleta_ml": a_class_ml,
            "status_deteccao_ml": status_ml,
        })

    return pd.DataFrame(results)


def run_integrity_classifier_pipeline():
    """Executa o pipeline completo de treinamento, calibração, auditoria e exportação."""
    print("\n" + "=" * 75)
    print("INICIANDO TREINAMENTO DO MODELO DE CLASSIFICAÇÃO DE INTEGRIDADE (MACHINE LEARNING)")
    print("=" * 75)

    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(TABLES_DIR, exist_ok=True)
    os.makedirs(INTEGRITY_DIR, exist_ok=True)

    print("\n--- 1. Carregando Dados Consolidados ---")
    from src.models.anomaly_detection import load_unified_data

    df_matches = pd.read_parquet(DATA_PARTIDAS)
    df_athletes = pd.read_parquet(DATA_ATLETAS)
    df_pm = pd.read_parquet(DATA_PM)
    _, df_cards, _ = load_unified_data()

    print(f"     Partidas: {len(df_matches)} | Atletas: {len(df_athletes)} | Casos Ground Truth: {len(df_pm)}")

    print("\n--- 2. Treinando Classificadores para Partidas ---")
    iforest_match, pu_match, df_matches_scored, match_features = train_match_classifiers(df_matches, df_pm)

    print("\n--- 3. Treinando Classificadores para Atletas ---")
    iforest_ath, pu_ath, df_athletes_scored, ath_features = train_athlete_classifiers(df_athletes, df_pm, df_cards)

    print("\n--- 4. Salvando Modelos Serializados (.joblib) ---")
    joblib.dump(iforest_match, os.path.join(MODELS_DIR, "match_isolation_forest.joblib"), compress=3)
    pu_match.save(os.path.join(MODELS_DIR, "match_pu_classifier.joblib"))
    joblib.dump(iforest_ath, os.path.join(MODELS_DIR, "athlete_isolation_forest.joblib"), compress=3)
    pu_ath.save(os.path.join(MODELS_DIR, "athlete_pu_classifier.joblib"))
    print("     [OK] Modelos serializados com sucesso em:", MODELS_DIR)

    print("\n--- 5. Salvando Datasets Enriquecidos (.parquet) ---")
    df_matches_scored.to_parquet(os.path.join(INTEGRITY_DIR, "partidas_ml_classified.parquet"), index=False)
    df_athletes_scored.to_parquet(os.path.join(INTEGRITY_DIR, "atletas_ml_classified.parquet"), index=False)
    print("     [OK] Datasets com features e predições ML salvos em:", INTEGRITY_DIR)

    print("\n--- 6. Avaliando Sensibilidade contra a Operação Penalidade Máxima ---")
    df_eval_ml = evaluate_ground_truth_ml(df_matches_scored, df_athletes_scored, df_pm, df_cards)
    t18_path = os.path.join(TABLES_DIR, "tabela_18_classificador_integridade_resultados.csv")
    df_eval_ml.to_csv(t18_path, index=False, encoding="utf-8")
    print("     [OK] Tabela 18 salva:", t18_path)

    n_detected = (df_eval_ml["status_deteccao_ml"].str.startswith("Detectado")).sum()
    pct_detected = (n_detected / len(df_eval_ml)) * 100.0
    print(f"     Sensibilidade de Detecção ML no Ground Truth: {n_detected}/{len(df_eval_ml)} ({pct_detected:.1f}%)")

    print("\n--- 7. Exportando Rankings Top 50 de Alertas ML ---")
    # Partidas Top 50
    top_matches = df_matches_scored.sort_values("prob_suspeicao_ml", ascending=False).head(50)
    top_matches_export = top_matches[[
        "partida_id", "temporada", "serie", "rodada", "data", "clube_mandante", "clube_visitante",
        "total_cartoes", "cartoes_1t", "penaltis_1t", "exposure_total_partida",
        "iforest_outlier", "prob_suspeicao_ml", "classificacao_ml", "match_anomaly_score"
    ]]
    t19_path = os.path.join(TABLES_DIR, "tabela_19_classificacao_partidas_ml.csv")
    top_matches_export.to_csv(t19_path, index=False, encoding="utf-8")
    print("     [OK] Tabela 19 salva:", t19_path)

    # Atletas Top 50
    top_athletes = df_athletes_scored.sort_values("prob_suspeicao_ml", ascending=False).head(50)
    top_athletes_export = top_athletes[[
        "temporada", "serie", "clube_slug", "atleta", "atleta_slug", "total_cartoes", "cartoes_1t",
        "prop_cartoes_1t", "minuto_medio_partida", "iforest_outlier",
        "prob_suspeicao_ml", "classificacao_ml", "athlete_anomaly_score"
    ]]
    t20_path = os.path.join(TABLES_DIR, "tabela_20_classificacao_atletas_ml.csv")
    # F4-02: mesma razao da Tabela 16 — probabilidade de suspeicao com nome e o artefato de
    # maior potencial de dano do repositorio.
    aplicar_camada(top_athletes_export, CAMADA_ABERTA).to_csv(
        t20_path, index=False, encoding="utf-8")
    print("     [OK] Tabela 20 salva:", t20_path)

    print("\n" + "=" * 75)
    print("PIPELINE DE CLASSIFICAÇÃO DE INTEGRIDADE (ML) CONCLUÍDO COM SUCESSO!")
    print("=" * 75)

    return df_matches_scored, df_athletes_scored, df_eval_ml


if __name__ == "__main__":
    run_integrity_classifier_pipeline()
