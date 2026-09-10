"""
Testes unitários para o parser de Súmulas Eletrônicas da CBF.
Valida extração de metadados, cartões, gols e classificação de infrações.
"""

from pathlib import Path
import pandas as pd
import pytest

from src.cleaning.parse_cbf_sumulas import (
    categorize_card_reason,
    parse_single_sumula,
    slugify
)

SAMPLE_DIR = Path("data/raw/cbf/sumulas_serie_b_2022")
PROCESSED_DIR = Path("data/processed/serie_b")

def test_categorize_card_reason():
    assert categorize_card_reason("Por calçar o adversário de forma temerária") == "falta_temeraria"
    assert categorize_card_reason("Desaprovar com palavras ou gestos as decisões da arbitragem") == "reclamacao"
    assert categorize_card_reason("Retardar o reinício de jogo na cobrança de falta") == "cera_retardar"
    assert categorize_card_reason("Conduta antidesportiva por discutir com adversário") == "conduta_antidesportiva"
    assert categorize_card_reason("Tocar deliberadamente a bola com a mão") == "mao_intencional"
    assert categorize_card_reason("Comemoração excessiva sem camisa") == "conduta_antidesportiva"

def test_slugify():
    assert slugify("Ponte Preta / SP") == "ponte_preta_sp"
    assert slugify("Grêmio / RS") == "gremio_rs"
    assert slugify(None) == ""

def test_parse_single_sumula():
    pdf_path = SAMPLE_DIR / "2421se.pdf"
    if not pdf_path.exists():
        pytest.skip("PDF de teste 2421se.pdf não encontrado")

    meta, cards, goals = parse_single_sumula(pdf_path, temporada_default=2022, serie_default="B")

    assert meta["rodada"] == 1
    assert "Ponte Preta" in meta["clube_mandante"]
    assert "Paulo Roberto Alves Junior" in meta["arbitro"]
    assert len(cards) >= 5

    for c in cards:
        assert c["cartao"] in ["Amarelo", "Vermelho"]
        assert c["periodo"] in ["1T", "2T"]
        assert 0 <= c["minuto_nominal"] <= 130
        assert len(c["motivo_completo"]) > 0
        assert c["categoria_infracao"] in [
            "falta_temeraria", "reclamacao", "cera_retardar",
            "conduta_antidesportiva", "mao_intencional", "outro"
        ]

def test_processed_serie_b_datasets():
    if not (PROCESSED_DIR / "partidas.parquet").exists():
        pytest.skip("Datasets processados da Série B não encontrados")

    df_p = pd.read_parquet(PROCESSED_DIR / "partidas.parquet")
    df_c = pd.read_parquet(PROCESSED_DIR / "cartoes.parquet")
    df_g = pd.read_parquet(PROCESSED_DIR / "gols.parquet")

    assert len(df_p) == 760, f"Esperado 760 partidas da Série B (2022-2023), obtido {len(df_p)}"
    assert len(df_c) >= 3500, f"Esperado >= 3500 cartões, obtido {len(df_c)}"
    assert len(df_g) >= 2000, f"Esperado >= 2000 gols, obtido {len(df_g)}"
    assert "categoria_infracao" in df_c.columns
    assert set(df_c["cartao"].unique()).issubset({"Amarelo", "Vermelho"})
    assert set(df_c["periodo"].unique()).issubset({"1T", "2T"})
    assert set(df_p["temporada"].unique()) == {2022, 2023}

def test_integrity_dataset():
    proc_cases = Path("data/processed/integrity/casos_penalidade_maxima.parquet")
    if not proc_cases.exists():
        pytest.skip("Dataset de integridade não encontrado")

    df = pd.read_parquet(proc_cases)
    assert len(df) == 14
    assert set(df["serie"].unique()).issubset({"A", "B"})
    assert df["atleta_slug"].notna().all()
    assert df["evento_alvo"].isin(["cometer_penalti_1t", "cartao_amarelo_1t", "cartao_amarelo", "cartao_vermelho"]).all()

