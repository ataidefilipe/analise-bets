"""
tests/test_camadas_de_exposicao.py
----------------------------------
Testes da separação por camada de exposição e da varredura retroativa (F4-02).

O teste central é `test_nenhum_atleta_sem_condenacao_nominado_em_camada_aberta`: ele falha se
o nome de um atleta sem condenação reaparecer em qualquer artefato destinado a circular. É a
guarda que transforma a diretriz de presunção de inocência — declarada no relatório 07 desde a
primeira versão — em controle efetivo.
"""

import os

import pandas as pd
import pytest

from src.analysis import varredura_exposicao_nominal as varredura
from src.pipeline import camadas_de_exposicao as cam
from src.pipeline.perfis_de_acesso import CAMADA_ABERTA, CAMADA_IDENTIFICADA, CAMADA_PSEUDONIMIZADA

TABLES_DIR = os.path.join("reports", "tables")


@pytest.fixture
def amostra():
    """Um condenado (Nino Paraíba) e dois atletas sem qualquer registro."""
    return pd.DataFrame([
        {"atleta": "Nino Paraiba", "atleta_slug": "nino_paraiba", "registro_cbf": "111",
         "athlete_anomaly_score": 72.2},
        {"atleta": "Fulano de Tal Silva", "atleta_slug": "fulano_de_tal_silva",
         "registro_cbf": "222", "athlete_anomaly_score": 80.5},
        {"atleta": "Beltrano Souza Lima", "atleta_slug": "beltrano_souza_lima",
         "registro_cbf": "333", "athlete_anomaly_score": 65.0},
    ])


# ---------------------------------------------------------------------------
# 1. Status jurídico
# ---------------------------------------------------------------------------

def test_status_juridico_classifica_os_atletas_do_ground_truth():
    status = cam.status_juridico_por_atleta()
    if status.empty:
        pytest.skip("ground truth indisponível")

    assert len(status) == 10, f"esperados 10 atletas do ground truth, obtidos {len(status)}"
    assert (status["status_juridico"] == cam.STATUS_CONDENADO).all()
    assert status["sancao"].str.len().gt(0).all(), "condenação sem sanção registrada"


def test_apenas_condenados_sao_nominaveis():
    nominaveis = cam.nomes_nominaveis()
    assert nominaveis, "nenhum atleta nominável — a exceção de fato público sumiu"
    assert len(nominaveis) <= 30, "a lista de nomináveis cresceu além dos casos julgados"
    assert any("Nino" in n for n in nominaveis)


# ---------------------------------------------------------------------------
# 2. Aplicação da camada
# ---------------------------------------------------------------------------

def test_camada_aberta_preserva_condenado_e_protege_os_demais(amostra):
    aberta = cam.aplicar_camada(amostra, CAMADA_ABERTA)
    assert aberta.loc[0, "atleta"] == "Nino Paraiba", "condenado deixou de ser nominado"
    for i in (1, 2):
        assert aberta.loc[i, "atleta"].startswith("atl_"), "atleta sem condenação segue nominado"
        assert aberta.loc[i, "atleta_slug"].startswith("atl_"), "o slug ainda revela o nome"


def test_pseudonimo_e_o_mesmo_entre_artefatos(amostra):
    """O mesmo atleta precisa ser reconhecível entre tabelas, ou a análise fica inviável."""
    primeira = cam.aplicar_camada(amostra, CAMADA_ABERTA)
    segunda = cam.aplicar_camada(amostra.sample(frac=1, random_state=7), CAMADA_ABERTA)
    mapa = dict(zip(segunda["registro_cbf"], segunda["atleta_pseudonimo"]))
    for _, r in primeira.iterrows():
        assert mapa[r["registro_cbf"]] == r["atleta_pseudonimo"]


def test_camada_identificada_nao_altera_nada(amostra):
    identificada = cam.aplicar_camada(amostra, CAMADA_IDENTIFICADA)
    pd.testing.assert_frame_equal(identificada, amostra)


def test_camada_desconhecida_e_rejeitada(amostra):
    with pytest.raises(ValueError):
        cam.aplicar_camada(amostra, "publica_geral")


def test_mapa_de_reidentificacao_fica_fora_do_versionamento():
    """
    Versionar o mapa anularia a pseudonimização: qualquer clone traria a chave junto.
    """
    gitignore = open(".gitignore", encoding="utf-8").read()
    assert "data/restrito" in gitignore, "o diretório restrito não está no .gitignore"
    assert cam.MAPA_PSEUDONIMOS.replace("\\", "/").startswith("data/restrito")


# ---------------------------------------------------------------------------
# 3. A guarda retroativa
# ---------------------------------------------------------------------------

def test_nenhum_atleta_sem_condenacao_nominado_em_camada_aberta():
    """
    Varre tabelas, relatórios, notebooks e a apresentação em busca de nome de atleta sem
    condenação. Qualquer ocorrência reprova.

    Se este teste falhar depois de uma alteração legítima, a saída não é afrouxá-lo: é aplicar
    `aplicar_camada` no ponto de exportação que voltou a nominar.
    """
    achados = varredura.executar()
    if achados.empty:
        return

    resumo = achados.groupby("arquivo")["nome_encontrado"].nunique().to_dict()
    pytest.fail(
        f"{len(achados)} ocorrências de atleta sem condenação em artefato de camada aberta: "
        f"{resumo}"
    )


def test_varredura_reconhece_condenado_com_grafia_diferente():
    """
    O ground truth grava "Nino Paraiba" e os relatórios escrevem "Nino Paraíba". Sem normalizar
    acento, um condenado — nominável — seria acusado como exposição indevida, e o ruído
    afogaria os casos reais.
    """
    assert varredura._normalizar("Nino Paraíba") == varredura._normalizar("Nino Paraiba")
    publicos = {varredura._normalizar(n) for n in cam.nomes_nominaveis()}
    assert varredura._normalizar("Nino Paraíba") in publicos


def test_tabelas_nominais_saem_pseudonimizadas():
    """As três tabelas que rankeiam atletas por atipicidade não podem sair com nome."""
    alvos = {
        "tabela_03_atletas_outliers_1T.csv": "atleta",
        "tabela_16_ranking_atletas_anomalos.csv": "atleta",
        "tabela_20_classificacao_atletas_ml.csv": "atleta",
    }
    nominaveis = {cam.normalizar_nome(n) for n in cam.nomes_nominaveis()}
    for arquivo, coluna in alvos.items():
        caminho = os.path.join(TABLES_DIR, arquivo)
        if not os.path.exists(caminho):
            continue
        df = pd.read_csv(caminho)
        expostos = df[~df[coluna].astype(str).str.startswith("atl_")][coluna]
        nao_permitidos = [n for n in expostos if cam.normalizar_nome(n) not in nominaveis]
        assert not nao_permitidos, f"{arquivo} expõe {nao_permitidos[:3]}"
