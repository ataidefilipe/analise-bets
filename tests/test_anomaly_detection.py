"""
tests/test_anomaly_detection.py
-------------------------------
Testes unitários e de integração para o Sistema de Triagem e Anomaly Scoring
de Integridade Esportiva (Fase 8):
1. Contrato da especificação canônica do índice (pesos, subscores e tiers) — tarefas F1-01/F1-02.
2. Integridade das chaves e da harmonização entre as Séries A e B.
3. Limites matemáticos e ausência de NaNs nos scores [0, 100].
4. Integridade das tabelas analíticas exportadas (Tabelas 15, 16 e 17).
"""

import os
import pytest
import pandas as pd
import numpy as np

from src.models import anomaly_detection as ad

DATA_PARTIDAS = os.path.join("data", "processed", "integrity", "partidas_anomaly_scored.parquet")
DATA_ATLETAS = os.path.join("data", "processed", "integrity", "atletas_anomaly_scored.parquet")
TABLES_DIR = os.path.join("reports", "tables")


@pytest.fixture(scope="module")
def partidas_scored():
    assert os.path.exists(DATA_PARTIDAS), f"Dataset não encontrado: {DATA_PARTIDAS}"
    return pd.read_parquet(DATA_PARTIDAS)


@pytest.fixture(scope="module")
def atletas_scored():
    assert os.path.exists(DATA_ATLETAS), f"Dataset não encontrado: {DATA_ATLETAS}"
    return pd.read_parquet(DATA_ATLETAS)


# ---------------------------------------------------------------------------
# 1. Contrato da especificação canônica (F1-01 e F1-02)
# ---------------------------------------------------------------------------

def test_pesos_do_indice_somam_um():
    """Os coeficientes do índice composto devem somar exatamente 1,0 nos dois níveis."""
    assert sum(ad.MATCH_SCORE_WEIGHTS.values()) == pytest.approx(1.0, abs=1e-9), (
        f"Pesos de partida somam {sum(ad.MATCH_SCORE_WEIGHTS.values())}, esperado 1,0"
    )
    assert sum(ad.ATHLETE_SCORE_WEIGHTS.values()) == pytest.approx(1.0, abs=1e-9), (
        f"Pesos de atleta somam {sum(ad.ATHLETE_SCORE_WEIGHTS.values())}, esperado 1,0"
    )


def test_pesos_publicados_nao_mudam_sem_atualizar_o_teste():
    """
    Congela a especificação publicada no relatório 07. Se este teste falhar, a fórmula mudou:
    atualize o relatório, regenere as Tabelas 15-17 e só então ajuste os valores aqui.
    """
    assert ad.MATCH_SCORE_WEIGHTS == {
        "score_tempo": 0.39,
        "score_precoce": 0.28,
        "score_volume": 0.22,
        "score_penalti": 0.11,
    }
    assert ad.ATHLETE_SCORE_WEIGHTS == {
        "score_atleta_tempo": 0.50,
        "score_atleta_taxa": 0.30,
        "score_atleta_minuto": 0.20,
    }
    assert ad.PENALTI_1T_FAIXAS == ((2, 80.0), (1, 40.0))
    assert (ad.P0_CARTAO_1T, ad.P0_CARTAO_30MIN) == (0.351, 0.156)
    assert (ad.LOG_P_MULTIPLICADOR, ad.Z_VOLUME_MULTIPLICADOR) == (25.0, 25.0)


def test_exposicao_comercial_nao_compoe_o_escore(partidas_scored):
    """
    F1-02: a exposição a casas de apostas é contexto, nunca componente. A coluna precisa
    continuar na base (estratificação), mas não pode participar de nenhum índice.
    """
    for coluna in ad.COLUNAS_CONTEXTO_NAO_COMPONENTE:
        assert coluna not in ad.MATCH_SCORE_WEIGHTS, f"{coluna} voltou a compor o índice de partida"
        assert coluna not in ad.ATHLETE_SCORE_WEIGHTS, f"{coluna} voltou a compor o índice de atleta"

    assert "score_bet" not in partidas_scored.columns, (
        "score_bet foi reintroduzido no dataset de partidas"
    )
    assert "exposure_total_partida" in partidas_scored.columns, (
        "exposure_total_partida deve ser preservada como coluna de contexto"
    )


def test_indice_composto_reproduz_a_especificacao(partidas_scored):
    """O escore gravado tem de ser exatamente a combinação dos pesos declarados."""
    esperado = sum(
        peso * partidas_scored[coluna] for coluna, peso in ad.MATCH_SCORE_WEIGHTS.items()
    ).round(2)
    assert np.allclose(partidas_scored["match_anomaly_score"], esperado, atol=0.011), (
        "match_anomaly_score divergiu da fórmula declarada em MATCH_SCORE_WEIGHTS"
    )


def test_subscore_de_penalti_respeita_as_faixas(partidas_scored):
    """S_penalti é uma função escada de PENALTI_1T_FAIXAS, não um indicador binário."""
    for minimo, pontos in ad.PENALTI_1T_FAIXAS:
        faixa = partidas_scored[partidas_scored["penaltis_1t"] == minimo]
        if len(faixa) > 0:
            assert (faixa["score_penalti"] == pontos).all(), (
                f"Partidas com {minimo} pênalti(s) no 1ºT deveriam pontuar {pontos}"
            )
    sem_penalti = partidas_scored[partidas_scored["penaltis_1t"] == 0]
    assert (sem_penalti["score_penalti"] == 0.0).all()


def test_subscore_de_volume_nao_tem_piso(partidas_scored):
    """Partida de volume médio (z = 0) recebe 0 ponto: o subscore mede excesso, não nível."""
    media = partidas_scored[partidas_scored["z_cartoes"].abs() < 0.01]
    if len(media) > 0:
        assert media["score_volume"].max() < 1.0, (
            "Partidas de volume médio estão recebendo pontuação positiva em score_volume"
        )


# ---------------------------------------------------------------------------
# 2. Integridade de chave e harmonização entre séries
# ---------------------------------------------------------------------------

def test_chave_de_partida_e_unica(partidas_scored):
    """
    A `partida_id` da Série B reinicia a cada temporada. A chave precisa incluir a temporada,
    sob pena de os cartões de duas temporadas se somarem na mesma partida.
    """
    duplicadas = partidas_scored.duplicated(subset=ad.CHAVE_PARTIDA).sum()
    assert duplicadas == 0, f"{duplicadas} partidas com chave {ad.CHAVE_PARTIDA} repetida"


def test_volume_de_cartoes_comparavel_entre_series(partidas_scored):
    """
    Guarda contra a soma indevida de temporadas na Série B: o volume médio por partida
    precisa ficar na mesma ordem de grandeza nas duas divisões.
    """
    media_por_serie = partidas_scored.groupby("serie")["total_cartoes"].mean()
    assert media_por_serie.max() / media_por_serie.min() < 1.5, (
        f"Volume médio de cartões muito discrepante entre séries: {media_por_serie.to_dict()}"
    )
    assert media_por_serie.max() < 9.0, "Volume médio por partida implausível (> 9 cartões)"


def test_minuto_harmonizado_entre_series():
    """
    A Série B registra o minuto dentro do tempo; a Série A, o minuto de jogo. Após a
    harmonização, a fração de cartões até os 30 minutos tem de ser comparável nas duas.
    """
    _, df_cards, _ = ad.load_unified_data()
    assert "minuto_partida" in df_cards.columns
    frac = df_cards.groupby("serie")["minuto_partida"].apply(
        lambda s: (s <= ad.LIMITE_CARTAO_PRECOCE_MIN).mean()
    )
    assert abs(frac["A"] - frac["B"]) < 0.06, (
        f"Fração de cartões precoces incomparável entre séries: {frac.to_dict()}"
    )


def test_recorte_temporal_da_base(partidas_scored):
    """O recorte publicado é explícito e não pode variar por reingestão silenciosa."""
    serie_a = partidas_scored[partidas_scored["serie"] == "A"]
    serie_b = partidas_scored[partidas_scored["serie"] == "B"]
    assert serie_a["temporada"].min() >= ad.SERIE_A_TEMPORADA_MIN
    assert serie_a["temporada"].max() <= ad.SERIE_A_TEMPORADA_MAX
    assert set(serie_b["temporada"].unique()).issubset(set(ad.SERIE_B_TEMPORADAS))
    assert len(partidas_scored) == 4559, f"Esperado 4559 partidas, obtido {len(partidas_scored)}"


# ---------------------------------------------------------------------------
# 3. Limites matemáticos dos escores
# ---------------------------------------------------------------------------

def test_partidas_scored_structure(partidas_scored):
    """Valida colunas essenciais, faixas [0, 100] e ausência de NaNs no scoring de partidas."""
    score_cols = list(ad.MATCH_SCORE_WEIGHTS) + ["match_anomaly_score", "percentil_anomalia"]
    for col in score_cols:
        assert col in partidas_scored.columns, f"Coluna ausente: {col}"
        assert partidas_scored[col].isnull().sum() == 0, f"Coluna {col} contém NaNs"
        assert (partidas_scored[col] >= 0).all(), f"Valores negativos em {col}"
        assert (partidas_scored[col] <= 100.0001).all(), f"Valores acima de 100 em {col}"

    tiers_validos = {rotulo for _, rotulo in ad.TIERS_PARTIDA} | {ad.TIER_PARTIDA_BASAL}
    assert set(partidas_scored["prioridade_triagem"].unique()).issubset(tiers_validos)


def test_atletas_scored_structure(atletas_scored):
    """Valida integridade e intervalos dos scores individuais de atletas."""
    assert len(atletas_scored) >= 3500, f"Esperado >= 3500 atleta-temporadas, obtido {len(atletas_scored)}"

    score_cols = list(ad.ATHLETE_SCORE_WEIGHTS) + ["athlete_anomaly_score", "percentil_atleta"]
    for col in score_cols:
        assert col in atletas_scored.columns, f"Coluna ausente: {col}"
        assert atletas_scored[col].isnull().sum() == 0, f"Coluna {col} contém NaNs"
        assert (atletas_scored[col] >= 0).all(), f"Valores negativos em {col}"
        assert (atletas_scored[col] <= 100.0001).all(), f"Valores acima de 100 em {col}"

    assert (atletas_scored["total_cartoes"] >= 3).all()
    tiers_validos = {rotulo for _, rotulo in ad.TIERS_ATLETA} | {ad.TIER_ATLETA_BASAL}
    assert set(atletas_scored["classificacao_atleta"].unique()).issubset(tiers_validos)


def test_tiers_respeitam_a_carga_operacional_declarada(partidas_scored):
    """
    Os tiers são definidos por percentil empírico: a carga de alerta é um parâmetro, não um
    efeito colateral da escala do escore. Insumo direto da tarefa F1-04.
    """
    for corte, rotulo in ad.TIERS_PARTIDA:
        fracao_esperada = (100.0 - corte) / 100.0
        fracao_obtida = (partidas_scored["percentil_anomalia"] >= corte).mean()
        assert abs(fracao_obtida - fracao_esperada) < 0.02, (
            f"Tier '{rotulo}' marcou {fracao_obtida:.3%} da base, esperado ~{fracao_esperada:.1%}"
        )


# ---------------------------------------------------------------------------
# 4. Tabelas exportadas
# ---------------------------------------------------------------------------

def test_tables_generation():
    """Valida formato, ordenação e preenchimento das tabelas 15, 16 e 17."""
    t15_path = os.path.join(TABLES_DIR, "tabela_15_ranking_partidas_anomalas.csv")
    t16_path = os.path.join(TABLES_DIR, "tabela_16_ranking_atletas_anomalos.csv")
    t17_path = os.path.join(TABLES_DIR, "tabela_17_validacao_ground_truth_pm.csv")

    for path in (t15_path, t16_path, t17_path):
        assert os.path.exists(path), f"Tabela ausente: {path}"

    df_t15 = pd.read_csv(t15_path)
    df_t16 = pd.read_csv(t16_path)
    df_t17 = pd.read_csv(t17_path)

    assert len(df_t15) == 50
    assert df_t15["match_anomaly_score"].is_monotonic_decreasing

    assert len(df_t16) == 50
    assert df_t16["athlete_anomaly_score"].is_monotonic_decreasing
    assert "minuto_medio_partida" in df_t16.columns

    assert len(df_t17) == 14


def test_comparacao_de_reconciliacao_publicada():
    """
    F1-01/F1-02 exigem o registro da comparação antes/depois. Os artefatos precisam existir
    e cobrir os 14 casos do ground truth.
    """
    base = os.path.join(TABLES_DIR, "comparacao_f1_reconciliacao_")
    for sufixo in ("resumo.csv", "migracao_tier.csv", "ground_truth.csv", "atletas_gt.csv"):
        assert os.path.exists(base + sufixo), f"Artefato de comparação ausente: {base + sufixo}"

    gt = pd.read_csv(base + "ground_truth.csv")
    assert len(gt) == 14
    for coluna in ("score_anterior", "score_novo", "tier_anterior", "tier_novo", "mudou_de_tier"):
        assert coluna in gt.columns


def test_tabela_17_carrega_a_proveniencia_da_resolucao():
    """
    F1-03: a Tabela 17 precisa declarar, caso a caso, como o atleta foi resolvido. Um percentil
    sem a sua proveniencia foi exatamente o que permitiu publicar o escore de Nino (Fluminense)
    como se fosse de Nino Paraiba (Ceara).
    """
    t17 = pd.read_csv(os.path.join(TABLES_DIR, "tabela_17_validacao_ground_truth_pm.csv"))
    for coluna in ("status_partida", "atleta_slug_base", "status_atleta", "confianca_identidade"):
        assert coluna in t17.columns, f"Coluna de proveniencia ausente na Tabela 17: {coluna}"

    # Nenhum caso pode exibir percentil de atleta sem identidade resolvida.
    com_percentil = t17[t17["athlete_percentil"].notna()]
    assert (com_percentil["status_atleta"] == "resolvido").all(), (
        "Ha casos com percentil de atleta cuja identidade nao foi resolvida"
    )

    nao_resolvidos = t17[t17["status_atleta"] != "resolvido"]
    assert nao_resolvidos["athlete_anomaly_score"].isna().all(), (
        "Casos nao resolvidos nao podem carregar escore de atleta"
    )
