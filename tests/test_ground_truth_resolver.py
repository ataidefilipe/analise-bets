"""
tests/test_ground_truth_resolver.py
-----------------------------------
Testes do resolvedor de identidade do ground truth da Operação Penalidade Máxima (F1-03):
1. Exatidão da resolução das 14 partidas e dos 10 atletas.
2. Regressões específicas contra os erros da heurística anterior de correspondência parcial.
3. Consistência interna do mapa de identidade e dos artefatos de auditoria.
"""

import os
import pandas as pd
import pytest

from src.models import anomaly_detection as ad
from src.models import ground_truth_resolver as gtr

TABLES_DIR = os.path.join("reports", "tables")


@pytest.fixture(scope="module")
def base():
    df_matches, df_cards, _ = ad.load_unified_data()
    df_athletes = pd.read_parquet(
        os.path.join("data", "processed", "integrity", "atletas_anomaly_scored.parquet")
    )
    df_pm = pd.read_parquet(ad.GROUND_TRUTH_PATH)
    return df_matches, df_cards, df_athletes, df_pm


@pytest.fixture(scope="module")
def resolucao(base):
    df_matches, df_cards, df_athletes, df_pm = base
    partidas = gtr.resolver_partidas(df_matches, df_pm)
    atletas = gtr.resolver_atletas(df_cards, df_athletes, df_pm)
    return partidas, atletas


# ---------------------------------------------------------------------------
# 1. Exatidão da resolução
# ---------------------------------------------------------------------------

def test_todas_as_partidas_do_ground_truth_sao_resolvidas(resolucao):
    """Os 14 casos precisam apontar para exatamente uma partida da base."""
    partidas, _ = resolucao
    assert len(partidas) == 14
    nao_resolvidas = partidas[~partidas["status_partida"].str.startswith("resolvido")]
    assert len(nao_resolvidas) == 0, (
        f"Casos sem partida resolvida: {nao_resolvidas['caso_id'].tolist()}"
    )
    assert partidas["partida_id"].notna().all()


def test_correcao_de_fixture_do_pm_005(resolucao):
    """
    O ground truth registra Náutico x Sampaio Corrêa na rodada 23, em que o Náutico enfrentou o
    CRB. A partida correta é a da rodada 31.
    """
    partidas, _ = resolucao
    caso = partidas[partidas["caso_id"] == "PM-005"].iloc[0]
    assert caso["rodada_ground_truth"] == 23
    assert caso["rodada_utilizada"] == 31
    assert caso["status_partida"] == "resolvido_corrigido"


def test_mapa_de_identidade_cobre_todos_os_atletas(base):
    """Nenhum atleta do ground truth pode ficar fora do mapa explícito."""
    _, _, _, df_pm = base
    faltantes = set(df_pm["atleta_slug"].unique()) - set(gtr.MAPA_IDENTIDADE_ATLETAS)
    assert not faltantes, f"Atletas sem entrada no mapa de identidade: {faltantes}"


def test_toda_entrada_do_mapa_declara_evidencia_e_confianca():
    """Uma associação sem evidência registrada é indistinguível de um palpite."""
    validos = {"alta", "media", "nao_resolvido"}
    for slug, entrada in gtr.MAPA_IDENTIDADE_ATLETAS.items():
        assert entrada["confianca"] in validos, f"{slug}: confiança inválida"
        assert len(entrada["evidencia"]) > 40, f"{slug}: evidência ausente ou vaga"
        if entrada["confianca"] == "nao_resolvido":
            assert entrada["atleta_slug"] is None, f"{slug}: não resolvido não pode apontar atleta"
        else:
            assert entrada["atleta_slug"], f"{slug}: resolução sem atleta de destino"


# ---------------------------------------------------------------------------
# 2. Regressões contra os erros da heurística anterior
# ---------------------------------------------------------------------------

def test_nino_paraiba_nao_e_confundido_com_nino_do_fluminense(resolucao):
    """
    A heurística anterior buscava `contains('nino')` e retornava o primeiro registro — Nino, do
    Fluminense, cujo percentil de 99,67% foi publicado como se fosse de Nino Paraíba.
    """
    _, atletas = resolucao
    linha = atletas[atletas["atleta_slug_ground_truth"] == "nino_paraiba"].iloc[0]
    assert linha["atleta_slug_base"] == "nino_paraiba"
    assert linha["clube_slug"] == "ceara"
    assert linha["status_atleta"] == "resolvido"


def test_atletas_do_ground_truth_pertencem_ao_clube_e_serie_corretos(resolucao, base):
    """
    Erro central da heurística anterior: casar atletas de série e clube distintos dos do caso
    (Paulo Miranda do Juventude com um atleta do Tombense, na Série B).
    """
    _, atletas = resolucao
    _, _, _, df_pm = base
    resolvidos = atletas[atletas["atleta_slug_base"].notna()]
    for _, linha in resolvidos.iterrows():
        casos = df_pm[df_pm["atleta_slug"] == linha["atleta_slug_ground_truth"]]
        assert linha["serie"] == casos.iloc[0]["serie"], (
            f"{linha['atleta_ground_truth']}: série divergente do caso"
        )
        clube_caso = casos.iloc[0]["clube_atleta"].lower().replace(" ", "_")
        assert linha["clube_slug"].startswith(clube_caso[:5]), (
            f"{linha['atleta_ground_truth']}: clube divergente ({linha['clube_slug']} vs {clube_caso})"
        )


def test_casos_sem_correspondente_defensavel_ficam_nao_resolvidos(resolucao):
    """
    Romário não recebeu cartão pelo Vila Nova em 2022 e não há nenhum Cariús na base. Ambos
    precisam ficar explicitamente não resolvidos, e não receber o escore de um homônimo parcial.
    """
    _, atletas = resolucao
    for slug in ("romario", "igor_carius"):
        linha = atletas[atletas["atleta_slug_ground_truth"] == slug].iloc[0]
        assert linha["status_atleta"] == "nao_resolvido"
        assert pd.isna(linha["atleta_slug_base"]) or linha["atleta_slug_base"] is None


def test_gabriel_tota_esta_abaixo_do_minimo_de_cartoes(resolucao):
    """
    Gabriel Tota existe na base de cartões com 2 advertências, abaixo do mínimo de 3 do
    ATHLETE_ANOMALY_SCORE. O estado precisa ser distinguível de 'ausente'.
    """
    _, atletas = resolucao
    linha = atletas[atletas["atleta_slug_ground_truth"] == "gabriel_tota"].iloc[0]
    assert linha["status_atleta"] == "abaixo_do_minimo_de_cartoes"
    assert linha["cartoes_na_temporada"] == 2


# ---------------------------------------------------------------------------
# 3. Verificação de evento e artefatos de auditoria
# ---------------------------------------------------------------------------

def test_verificacao_de_evento_classifica_os_14_casos(base, resolucao):
    """Todo caso precisa receber um status de verificação de evento explícito."""
    _, df_cards, _, df_pm = base
    partidas, atletas = resolucao
    eventos = gtr.verificar_eventos(df_cards, partidas, atletas, df_pm)

    assert len(eventos) == 14
    validos = {"confirmado", "divergencia_de_minuto", "ausente", "nao_verificavel", "nao_aplicavel"}
    assert set(eventos["status_evento"]).issubset(validos)

    # PM-011 é o único evento confirmado na súmula: vermelho aos 93' na rodada 37.
    pm011 = eventos[eventos["caso_id"] == "PM-011"].iloc[0]
    assert pm011["status_evento"] == "confirmado"
    assert pm011["minuto_na_base"] == 93.0


def test_artefatos_de_auditoria_publicados():
    """A auditoria de ancoragem é entregável da F1-03 e precisa estar publicada."""
    for nome in ("partidas", "atletas", "eventos"):
        caminho = os.path.join(TABLES_DIR, f"auditoria_ground_truth_{nome}.csv")
        assert os.path.exists(caminho), f"Artefato de auditoria ausente: {caminho}"
