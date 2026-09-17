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

    assert len(df_p) >= 760, f"Esperado >= 760 partidas da Série B, obtido {len(df_p)}"
    assert len(df_c) >= 3500, f"Esperado >= 3500 cartões, obtido {len(df_c)}"
    assert len(df_g) >= 2000, f"Esperado >= 2000 gols, obtido {len(df_g)}"
    assert "categoria_infracao" in df_c.columns
    assert set(df_c["cartao"].unique()).issubset({"Amarelo", "Vermelho"})
    assert set(df_c["periodo"].unique()).issubset({"1T", "2T"})
    assert {2022, 2023}.issubset(set(df_p["temporada"].unique()))

def test_integrity_dataset():
    proc_cases = Path("data/processed/integrity/casos_penalidade_maxima.parquet")
    if not proc_cases.exists():
        pytest.skip("Dataset de integridade não encontrado")

    df = pd.read_parquet(proc_cases)
    assert len(df) == 14
    assert set(df["serie"].unique()).issubset({"A", "B"})
    assert df["atleta_slug"].notna().all()
    assert df["evento_alvo"].isin(["cometer_penalti_1t", "cartao_amarelo_1t", "cartao_amarelo", "cartao_vermelho"]).all()



# ---------------------------------------------------------------------------
# F2-04 — Relação de atletas, substituições e minutos em campo
# ---------------------------------------------------------------------------

TEMPORADAS_COM_SUMULA = [
    ("a", 2026), ("b", 2022), ("b", 2023), ("b", 2024), ("b", 2026),
]


@pytest.mark.parametrize("serie,temporada", TEMPORADAS_COM_SUMULA)
def test_relacao_de_atletas_extraida_em_cada_temporada(serie, temporada):
    """
    A DoD da F2-04 exige cobertura de ao menos uma súmula por temporada disponível. Cada
    súmula relaciona 22 a 23 atletas por equipe — 11 titulares e o banco.
    """
    from src.cleaning.cbf_delta_processor import parse_single_cbf_pdf, parse_escalacao_from_pdf

    diretorio = Path(f"data/raw/cbf/sumulas_serie_{serie}_{temporada}")
    pdfs = sorted(diretorio.glob("*.pdf"))
    if not pdfs:
        pytest.skip(f"sem súmulas para Série {serie.upper()} {temporada}")

    # A primeira súmula de algumas temporadas vem incompleta na origem; tenta algumas.
    for pdf in pdfs[:5]:
        meta, _, _ = parse_single_cbf_pdf(pdf, temporada_default=temporada, serie_default=serie.upper())
        atletas, _ = parse_escalacao_from_pdf(pdf, meta)
        if atletas:
            break
    else:
        pytest.fail(f"nenhuma das 5 primeiras súmulas de {serie}{temporada} teve relação extraída")

    assert 30 <= len(atletas) <= 60, f"{len(atletas)} atletas relacionados — fora do esperado"

    clubes = {a["clube_slug"] for a in atletas}
    assert len(clubes) == 2, f"esperadas duas equipes, obtidas {clubes}"

    for clube in clubes:
        do_clube = [a for a in atletas if a["clube_slug"] == clube]
        titulares = [a for a in do_clube if a["condicao"] == "Titular"]
        assert len(titulares) == 11, f"{clube}: {len(titulares)} titulares"
        assert any(a["goleiro"] for a in titulares), f"{clube}: nenhum goleiro titular"

    assert all(a["registro_cbf"] for a in atletas), "há atleta sem registro CBF"
    assert all(a["num_camisa"] > 0 for a in atletas), "há atleta sem número de camisa"


def test_substituicoes_extraidas_com_minuto_e_equipe():
    from src.cleaning.cbf_delta_processor import parse_single_cbf_pdf, parse_escalacao_from_pdf

    pdf = Path("data/raw/cbf/sumulas_serie_a_2026/142100se.pdf")
    if not pdf.exists():
        pytest.skip("PDF de referência não encontrado")

    meta, _, _ = parse_single_cbf_pdf(pdf, temporada_default=2026, serie_default="A")
    _, subs = parse_escalacao_from_pdf(pdf, meta)

    assert subs, "nenhuma substituição extraída"
    for s in subs:
        assert s["periodo"] in ("1T", "2T")
        assert 0 < s["minuto_continuo"] <= 120
        assert s["num_entrou"] > 0 and s["num_saiu"] > 0
        assert s["num_entrou"] != s["num_saiu"]
        assert s["clube_slug"], "substituição sem equipe"


def test_escalacoes_materializadas_e_consistentes():
    """A tabela `escalacoes` tem chave partida + camisa única e cobre as duas séries."""
    for serie in ("a", "b"):
        caminho = Path(f"data/processed/serie_{serie}/escalacoes.parquet")
        if not caminho.exists():
            continue
        df = pd.read_parquet(caminho)
        assert len(df) > 0

        duplicadas = df.duplicated(subset=["temporada", "partida_id", "clube_slug", "num_camisa"]).sum()
        assert duplicadas == 0, f"série {serie}: {duplicadas} linhas com chave repetida"

        assert df["registro_cbf"].notna().all(), "registro CBF ausente"
        assert set(df["condicao"].unique()).issubset({"Titular", "Reserva"})

        # Onze titulares por equipe em cada partida extraída.
        titulares = df[df["condicao"] == "Titular"].groupby(
            ["temporada", "partida_id", "clube_slug"]).size()
        fora_do_padrao = (titulares != 11).sum()
        assert fora_do_padrao / len(titulares) < 0.02, (
            f"série {serie}: {fora_do_padrao} equipes sem 11 titulares"
        )


def test_minutos_em_campo_dentro_dos_limites_da_temporada():
    """
    Guarda contra o erro de agregar por nome: dois atletas homônimos no mesmo elenco viravam
    um só, com mais jogos do que a temporada tem rodadas. A chave é o registro CBF.
    """
    for serie in ("a", "b"):
        caminho = Path(f"data/processed/serie_{serie}/minutos_em_campo.parquet")
        if not caminho.exists():
            continue
        df = pd.read_parquet(caminho)
        assert len(df) > 0

        assert (df["partidas_jogadas"] <= 38).all(), (
            f"série {serie}: atleta com mais jogos do que a temporada tem rodadas"
        )
        assert (df["minutos_em_campo"] <= 38 * 90).all()
        assert (df["minutos_em_campo"] >= 0).all()
        assert (df["partidas_jogadas"] <= df["partidas_relacionado"]).all(), (
            "atleta com mais jogos do que convocações"
        )

        duplicadas = df.duplicated(subset=["temporada", "serie", "clube_slug", "registro_cbf"]).sum()
        assert duplicadas == 0, f"série {serie}: registro CBF repetido no mesmo clube e temporada"


def test_consistencia_entre_eventos_e_relacao_de_atletas():
    """
    Todo atleta com cartão precisa constar da relação da sua partida. As exceções conhecidas
    são as súmulas incompletas na origem, listadas em partidas_sem_escalacao.csv.
    """
    divergencias = Path("reports/tables/divergencias_escalacao_eventos.csv")
    if not divergencias.exists():
        pytest.skip("auditoria de divergências não gerada")

    df = pd.read_csv(divergencias)
    if df.empty:
        return

    reais = df[~df.get("partida_sem_escalacao", pd.Series(False, index=df.index)).fillna(False)]
    assert len(reais) <= 5, (
        f"{len(reais)} atletas com evento fora da relação da partida: {reais.head().to_dict('records')}"
    )
