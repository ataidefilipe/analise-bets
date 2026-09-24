"""
src/api/carga.py
----------------
Carga do banco da API a partir das bases canônicas do pipeline.

    python -m src.api.carga              # recria as tabelas de leitura
    python -m src.api.carga --sem-demo   # idem, sem cadastrar as chaves de demonstração

Lê o Parquet de `data/processed/` — não o `brasileirao.db`, que é pseudonimizado e não serve
à camada identificada. As tabelas de leitura são apagadas e recriadas numa transação; as
operacionais (`clientes_api`, `consultas_atleta`) são preservadas.

Na primeira carga, cadastra uma chave de demonstração por perfil e grava as chaves em
`data/restrito/chaves_api_poc.json`, que está fora do versionamento.
"""

import argparse
import json
import logging
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import func, select

from src.api import config, db
from src.api.clientes import criar_cliente
from src.api.modelo import (
    TABELAS_DE_LEITURA, TABELAS_OPERACIONAIS, anomalia_atleta, atletas, cartoes, clientes_api, clubes,
    escalacoes, metadata, minutos_em_campo, nominaveis, partidas, risco_pre_jogo,
)
from src.pipeline.camadas_de_exposicao import STATUS_CONDENADO, status_juridico_por_atleta

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("carga_api")

PROCESSED = Path("data") / "processed"
MANIFEST = Path("data") / "raw" / "cbf" / "manifest_delta.json"
ARQUIVO_CHAVES_DEMO = Path("data") / "restrito" / "chaves_api_poc.json"
FUSO_BRT = "-03:00"

CLIENTES_DEMO = (
    ("Demo — Federação/STJD", "federacao_stjd", None),
    ("Demo — Compliance Flamengo", "clube", "flamengo"),
    ("Demo — Operadora (integrity)", "operadora_integrity", None),
    ("Demo — Imprensa/academia", "imprensa_academia", None),
)


def normalizar(texto) -> str:
    sem_acento = unicodedata.normalize("NFKD", str(texto or ""))
    return "".join(c for c in sem_acento if not unicodedata.combining(c)).lower().strip()


def _ambas_series(nome: str) -> pd.DataFrame:
    quadros = []
    for serie in ("a", "b"):
        df = pd.read_parquet(PROCESSED / f"serie_{serie}" / f"{nome}.parquet")
        # Os anos de origem Kaggle da Série A vêm com `serie` nula.
        df["serie"] = df["serie"].fillna(serie.upper()) if "serie" in df.columns else serie.upper()
        quadros.append(df)
    return pd.concat(quadros, ignore_index=True)


def _com_fuso(ts) -> str | None:
    return f"{ts}{FUSO_BRT}" if ts else None


def montar_partidas(processado_em: str) -> pd.DataFrame:
    df = _ambas_series("partidas")
    anom = pd.read_parquet(PROCESSED / "integrity" / "partidas_anomaly_scored.parquet")[
        ["serie", "temporada", "partida_id", "match_anomaly_score", "percentil_anomalia",
         "prioridade_triagem"]].rename(columns={"prioridade_triagem": "tier_partida"})
    df = df.merge(anom, on=["serie", "temporada", "partida_id"], how="left")

    procedencia = []
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for temporada in manifest.get("seasons", {}).values():
            for m in temporada.get("matches", {}).values():
                procedencia.append({
                    "serie": temporada["serie"], "temporada": int(temporada["ano"]),
                    "partida_id": int(m["partida_num"]), "sumula_url": m.get("url"),
                    "sumula_sha256": m.get("sha256"), "baixado_em": _com_fuso(m.get("downloaded_at")),
                })
    if procedencia:
        df = df.merge(pd.DataFrame(procedencia), on=["serie", "temporada", "partida_id"], how="left")
        df.loc[df["sumula_sha256"].notna(), "processado_em"] = processado_em
    df["busca_texto"] = (df["clube_mandante"].map(normalizar) + " " + df["clube_visitante"].map(normalizar))
    colunas = [c.name for c in partidas.columns]
    for c in colunas:
        if c not in df.columns:
            df[c] = None
    df = df[colunas].replace({"": None})
    return df.drop_duplicates(["serie", "temporada", "partida_id"])


def montar_clubes(tab_partidas: pd.DataFrame) -> pd.DataFrame:
    lados = [tab_partidas[["temporada", f"clube_{lado}_slug", f"clube_{lado}"]]
             .set_axis(["temporada", "clube_slug", "nome"], axis=1) for lado in ("mandante", "visitante")]
    df = pd.concat(lados).dropna(subset=["clube_slug", "nome"]).sort_values("temporada")
    return df.groupby("clube_slug", as_index=False).last()[["clube_slug", "nome"]]


def montar_escalacoes() -> pd.DataFrame:
    df = _ambas_series("escalacoes")
    # Documento 02 §6: atleta sem registro CBF é regressão do parser. Loga e exclui.
    sem_registro = df["registro_cbf"].isna() | (df["registro_cbf"].astype(str).str.strip() == "")
    if sem_registro.any():
        logger.error("%d linhas de escalação sem registro_cbf excluídas", int(sem_registro.sum()))
    return df[~sem_registro].copy()


def montar_atletas(esc: pd.DataFrame) -> pd.DataFrame:
    esc = esc.sort_values(["temporada", "rodada"])
    ultimo = esc.groupby("registro_cbf").tail(1).set_index("registro_cbf")
    clubes = esc.groupby("registro_cbf")["clube_slug"].apply(lambda s: ",".join(sorted(set(s))))
    df = pd.DataFrame({
        "registro_cbf": ultimo.index,
        "nome_completo": ultimo["nome_completo"].values,
        "apelido": ultimo["apelido"].values,
        "atleta_slug": ultimo["atleta_slug"].values,
        "apelido_slug": ultimo["apelido_slug"].values,
        "clubes": clubes.reindex(ultimo.index).values,
        "clube_atual": ultimo["clube_slug"].values,
        "ultima_temporada": ultimo["temporada"].values,
    })
    df["busca_texto"] = (df["nome_completo"].map(normalizar) + " " + df["apelido"].map(normalizar))
    return df


def montar_cartoes(esc: pd.DataFrame) -> pd.DataFrame:
    df = _ambas_series("cartoes")
    df["num_camisa"] = pd.to_numeric(df["num_camisa"], errors="coerce").astype("Int64")
    chave = ["serie", "temporada", "partida_id", "clube_slug", "num_camisa"]
    vinculo = esc[chave + ["registro_cbf"]].drop_duplicates(chave)
    df = df.merge(vinculo, on=chave, how="left")
    colunas = [c.name for c in cartoes.columns if c.name != "id"]
    return df[colunas]


def montar_risco() -> pd.DataFrame:
    df = pd.read_parquet(PROCESSED / "integrity" / "score_pre_jogo.parquet")
    df = df[df["registro_cbf"].notna()].copy()
    # Percentil empírico na distribuição da série e temporada (documento 02 §2).
    df["percentil"] = (df.groupby(["serie", "temporada"])["score_pre_jogo"]
                       .rank(pct=True, method="max") * 100).round(1)
    df["tier"] = df["percentil"].map(config.tier_atleta)
    colunas = [c.name for c in risco_pre_jogo.columns if c.name != "id"]
    return df[colunas]


def montar_anomalia_atleta() -> pd.DataFrame:
    df = pd.read_parquet(PROCESSED / "integrity" / "atletas_anomaly_scored.parquet")
    df = df.rename(columns={"percentil_atleta": "percentil", "classificacao_atleta": "tier"})
    return df[[c.name for c in anomalia_atleta.columns if c.name != "id"]]


def montar_nominaveis(tab_atletas: pd.DataFrame) -> pd.DataFrame:
    status = status_juridico_por_atleta()
    condenados = status[status["status_juridico"] == STATUS_CONDENADO].copy()
    # Vincula ao registro CBF só quando o apelido identifica um único atleta da base.
    por_apelido = tab_atletas.groupby("apelido_slug")["registro_cbf"].agg(list)
    condenados["registro_cbf"] = condenados["atleta_slug"].map(
        lambda s: por_apelido[s][0] if s in por_apelido and len(por_apelido[s]) == 1 else None)
    return condenados[["atleta_slug", "registro_cbf", "atleta", "sancao", "fonte"]]


def carregar(com_demo: bool = True) -> dict:
    eng = db.engine()
    processado_em = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    logger.info("Montando tabelas a partir de %s", PROCESSED)
    esc = montar_escalacoes()
    tab_atletas = montar_atletas(esc)
    tab_partidas = montar_partidas(processado_em)
    quadros = {
        partidas: tab_partidas,
        clubes: montar_clubes(tab_partidas),
        atletas: tab_atletas,
        escalacoes: esc[[c.name for c in escalacoes.columns if c.name != "id"]],
        cartoes: montar_cartoes(esc),
        minutos_em_campo: _ambas_series("minutos_em_campo")[
            [c.name for c in minutos_em_campo.columns if c.name != "id"]],
        risco_pre_jogo: montar_risco(),
        anomalia_atleta: montar_anomalia_atleta(),
        nominaveis: montar_nominaveis(tab_atletas),
    }

    metadata.drop_all(eng, tables=list(TABELAS_DE_LEITURA))
    metadata.create_all(eng)
    contagens = {}
    with eng.begin() as conn:
        for tabela, df in quadros.items():
            df = df.astype(object).where(pd.notna(df), None)
            registros = df.to_dict("records")
            nuls_removidos = 0
            for i in range(0, len(registros), 5000):
                lote = registros[i:i + 5000]
                # PostgreSQL não aceita NUL (0x00) em colunas textuais; algumas súmulas
                # carregadas nos Parquets contêm esse caractere em campos de texto.
                for registro in lote:
                    for coluna, valor in registro.items():
                        if isinstance(valor, str) and "\x00" in valor:
                            nuls_removidos += valor.count("\x00")
                            registro[coluna] = valor.replace("\x00", "")
                conn.execute(tabela.insert(), lote)
            if nuls_removidos:
                logger.warning("  %s: removidos %d caracteres NUL", tabela.name, nuls_removidos)
            contagens[tabela.name] = len(registros)
            logger.info("  %-18s %8d linhas", tabela.name, len(registros))

    if com_demo:
        _cadastrar_demo(eng)
    return contagens


def _cadastrar_demo(eng) -> None:
    metadata.create_all(eng, tables=list(TABELAS_OPERACIONAIS))
    with eng.connect() as conn:
        if conn.execute(select(func.count()).select_from(clientes_api)).scalar():
            return
    chaves = []
    for nome, perfil, clube in CLIENTES_DEMO:
        c = criar_cliente(eng, nome, perfil, clube)
        chaves.append({"nome": nome, "perfil": perfil, "clube_slug": clube, "api_key": c["api_key"]})
    ARQUIVO_CHAVES_DEMO.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO_CHAVES_DEMO.write_text(json.dumps(chaves, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Chaves de demonstração gravadas em %s (fora do Git)", ARQUIVO_CHAVES_DEMO)


def main():
    parser = argparse.ArgumentParser(description="Carga do banco da API")
    parser.add_argument("--sem-demo", action="store_true", help="Não cadastra chaves de demonstração")
    args = parser.parse_args()
    carregar(com_demo=not args.sem_demo)


if __name__ == "__main__":
    main()
