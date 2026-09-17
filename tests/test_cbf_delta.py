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
    align_dataframe_types,
    categorize_card_reason,
    parse_single_cbf_pdf,
    slugify,
    unir_schema_historico,
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


# ---------------------------------------------------------------------------
# F2-01 — União de schema, motivo do cartão e atribuição de clube em expulsões
# ---------------------------------------------------------------------------

def test_align_dataframe_types_preserva_coluna_nova():
    """
    Regressão da F2-01: `align_dataframe_types` truncava o dado novo para o schema do
    histórico. Como a base da Série A veio do Kaggle, sem `motivo_completo`, o motivo textual
    do árbitro era descartado em silêncio a cada execução do pipeline delta.
    """
    df_existing = pd.DataFrame({"partida_id": [1], "atleta": ["Fulano"]})
    df_new = pd.DataFrame({
        "partida_id": [2], "atleta": ["Beltrano"],
        "motivo_completo": ["A1.11. Golpear um adversario"],
        "categoria_infracao": ["falta_temeraria"],
    })

    alinhado = align_dataframe_types(df_new, df_existing)

    assert "motivo_completo" in alinhado.columns, "coluna nova foi descartada"
    assert "categoria_infracao" in alinhado.columns
    assert alinhado["motivo_completo"].iloc[0] == "A1.11. Golpear um adversario"
    # A ordem do histórico é preservada, com as colunas novas ao final.
    assert list(alinhado.columns)[:2] == ["partida_id", "atleta"]


def test_unir_schema_historico_cria_colunas_vazias():
    df_existing = pd.DataFrame({"partida_id": [1], "atleta": ["Fulano"]})
    unido = unir_schema_historico(df_existing, ["motivo_completo"])
    assert "motivo_completo" in unido.columns
    assert unido["motivo_completo"].isna().all()
    assert len(unido) == 1


def test_expulsao_nao_atribui_secao_da_sumula_como_clube():
    """
    Regressão da F2-01: a seção de cartões vermelhos da súmula não tem coluna "Equipe" — o
    clube vem embutido no nome ("Nome - Clube/UF") e o token seguinte é o subtipo da expulsão.
    Lendo a posição fixa das duas seções, o subtipo virava o nome do clube.
    """
    sample_pdf = Path("data/raw/cbf/sumulas_serie_a_2026/142100se.pdf")
    if not sample_pdf.exists():
        pytest.skip("PDF de teste 142100se.pdf não encontrado")

    _, cards, _ = parse_single_cbf_pdf(sample_pdf, temporada_default=2026, serie_default="A")
    vermelhos = [c for c in cards if c["cartao"] == "Vermelho"]
    assert vermelhos, "a súmula de referência tem ao menos uma expulsão"

    for c in vermelhos:
        assert not c["clube_slug"].startswith("cartao_"), (
            f"seção da súmula atribuída como clube: {c['clube']!r}"
        )
        assert not c["clube_slug"].startswith("2o_cartao"), (
            f"seção da súmula atribuída como clube: {c['clube']!r}"
        )
        assert " - " not in c["atleta"], "o clube continua embutido no nome do atleta"
        assert c["tipo_cartao_detalhe"], "subtipo da expulsão não foi capturado"


def test_base_serie_a_carrega_motivo_do_cartao():
    """A Série A passou a carregar o motivo; o histórico do Kaggle permanece nulo."""
    caminho = Path("data/processed/serie_a/cartoes.parquet")
    if not caminho.exists():
        pytest.skip("base de cartões da Série A não encontrada")

    df = pd.read_parquet(caminho)
    for coluna in ("motivo_completo", "categoria_infracao", "tipo_cartao_detalhe"):
        assert coluna in df.columns, f"coluna ausente após a migração: {coluna}"

    das_sumulas = df[df["temporada"] >= 2026]
    if len(das_sumulas):
        preenchimento = das_sumulas["motivo_completo"].notna().mean()
        assert preenchimento > 0.95, (
            f"apenas {preenchimento:.1%} dos cartões vindos de súmula têm motivo"
        )

    # Nenhum clube pode ser uma seção da súmula, em nenhuma das duas bases.
    for base in ("serie_a", "serie_b"):
        p = Path("data/processed") / base / "cartoes.parquet"
        if not p.exists():
            continue
        d = pd.read_parquet(p)
        das_sumulas = d[d["temporada"] >= 2026]
        invalidos = das_sumulas["clube_slug"].str.startswith(("cartao_", "2o_cartao")).sum()
        assert invalidos == 0, f"{base}: {invalidos} cartões com seção da súmula como clube"
