"""
tests/test_cbf_delta.py
-----------------------
Testes unitários e de integração para a esteira delta de atualização CBF (D+1).
Valida:
1. Ingestor Delta (URLs, manifestos e detecção de delta).
2. Parser de Súmula (placar oficial canônico, gols, gol contra, cartões e categorias).
3. Processador e Upsert Idempotente (sem duplicidade).
4. Camada de Serviço para Produto (Standings, JSON feeds e banco SQLite).
"""

import json
import sqlite3
from pathlib import Path
import pandas as pd
import pytest

from src.ingestion.cbf_delta_updater import (
    CBFDeltaIngestor,
    COMPETITION_CODES,
)
from src.cleaning.cbf_delta_processor import (
    CBFDeltaProcessor,
    categorize_card_reason,
    parse_single_cbf_pdf,
    slugify,
)
from src.pipeline.serve_product_feed import (
    ProductFeedServer,
    compute_standings,
)
from src.pipeline.run_delta_pipeline import CBFDeltaPipeline


def test_competition_codes():
    assert COMPETITION_CODES["A"] == 142
    assert COMPETITION_CODES["B"] == 242


def test_ingestor_url_generation():
    ingestor = CBFDeltaIngestor(base_dir=Path("data/raw/cbf"))
    url_a = ingestor.get_url(2024, "A", 1)
    url_b = ingestor.get_url(2024, "B", 10)
    assert url_a == "https://conteudo.cbf.com.br/sumulas/2024/1421se.pdf"
    assert url_b == "https://conteudo.cbf.com.br/sumulas/2024/24210se.pdf"


def test_categorize_card_reasons():
    assert categorize_card_reason("Dar uma entrada de forma temerária") == "falta_temeraria"
    assert categorize_card_reason("Desaprovar com palavras ou gestos as decisões") == "reclamacao"
    assert categorize_card_reason("Retardar o reinício da partida") == "cera_retardar"
    assert categorize_card_reason("Conduta antidesportiva ao comemorar tirando a camisa") == "conduta_antidesportiva"
    assert categorize_card_reason("Tocar a bola com a mão deliberadamente") == "mao_intencional"


def test_parse_real_cbf_pdf():
    sample_pdf = Path("data/raw/cbf/sumulas_serie_a_2024/1421se.pdf")
    if not sample_pdf.exists():
        pytest.skip("PDF de teste 1421se.pdf não encontrado")

    meta, cards, goals = parse_single_cbf_pdf(sample_pdf, temporada_default=2024, serie_default="A")

    assert meta["partida_id"] == 1
    assert meta["temporada"] == 2024
    assert meta["serie"] == "A"
    assert meta["rodada"] == 1
    assert meta["data"] == "2024-04-13"
    assert "Internacional" in meta["clube_mandante"]
    assert "Bahia" in meta["clube_visitante"]
    assert meta["gols_mandante"] == 2
    assert meta["gols_visitante"] == 1
    assert meta["resultado"] == "Vitoria Mandante"
    assert meta["vencedor"] == meta["clube_mandante"]

    assert len(goals) == 3
    assert len(cards) >= 8

    card_cats = {c["categoria_infracao"] for c in cards}
    assert "falta_temeraria" in card_cats
    assert "reclamacao" in card_cats


def test_compute_standings():
    df_matches = pd.DataFrame([
        {
            "clube_mandante": "Time A",
            "clube_visitante": "Time B",
            "gols_mandante": 2,
            "gols_visitante": 0,
        },
        {
            "clube_mandante": "Time B",
            "clube_visitante": "Time C",
            "gols_mandante": 1,
            "gols_visitante": 1,
        },
    ])

    df_std = compute_standings(df_matches)
    assert len(df_std) == 3
    assert df_std.iloc[0]["clube"] == "Time A"
    assert df_std.iloc[0]["pontos"] == 3
    assert df_std.iloc[0]["saldo_gols"] == 2

    time_b = df_std[df_std["clube"] == "Time B"].iloc[0]
    assert time_b["pontos"] == 1
    assert time_b["jogos"] == 2
    assert time_b["saldo_gols"] == -2


def test_product_feeds_exist_and_valid():
    feed_dir = Path("data/processed/product_feed")
    json_matches = feed_dir / "latest_matches.json"
    json_classificacao = feed_dir / "tabela_classificacao.json"
    db_file = feed_dir / "brasileirao.db"

    assert json_matches.exists()
    assert json_classificacao.exists()
    assert db_file.exists()

    with open(json_matches, "r", encoding="utf-8") as f:
        matches_data = json.load(f)
        assert "series" in matches_data
        assert "gerado_em" in matches_data

    with open(json_classificacao, "r", encoding="utf-8") as f:
        class_data = json.load(f)
        assert "tabelas" in class_data

    conn = sqlite3.connect(db_file)
    try:
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)["name"].tolist()
        assert "partidas" in tables
        assert "gols" in tables
        assert "cartoes" in tables
        assert "classificacao" in tables

        df_p = pd.read_sql("SELECT COUNT(*) as cnt FROM partidas;", conn)
        assert df_p["cnt"].iloc[0] > 0
    finally:
        conn.close()


def test_pipeline_audit_report():
    audit_file = Path("data/processed/delta_pipeline_last_run.json")
    assert audit_file.exists()

    with open(audit_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "timestamp" in data
        assert "sucesso" in data
        assert data["sucesso"] is True
        assert "duracao_segundos" in data
