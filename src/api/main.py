"""
src/api/main.py
---------------
API REST da POC (documento 01 da especificação). Camada de leitura sobre tabelas
pré-calculadas: nenhum escore é computado em tempo de requisição.

    set ANALISE_BETS_AMBIENTE=dev          # só em máquina local
    python -m src.api.carga                # uma vez, e após cada execução do pipeline
    uvicorn src.api.main:app --reload

Documentação interativa em http://localhost:8000/docs.
"""

import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Literal, Optional

from fastapi import Depends, FastAPI, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import insert, text

from src.api import config, db, erros
from src.api.auth import Contexto, contexto, exigir
from src.api.carga import normalizar
from src.api.erros import ErroApi
from src.api.modelo import consultas_atleta

logger = logging.getLogger("api")

IDENTIFICADOS = ("federacao_stjd", "clube")
Serie = Literal["A", "B"]


@asynccontextmanager
async def _ciclo_de_vida(_: FastAPI):
    config.verificar_segredo()
    yield


app = FastAPI(
    lifespan=_ciclo_de_vida,
    title="Análise Bets — API da POC",
    version="0.1.0",
    description="Triagem de atipicidade disciplinar. O escore mede atipicidade estatística, não fraude.",
)
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGENS, allow_methods=["GET"],
                   allow_headers=["Authorization", "Content-Type"])
erros.registrar(app)


# --- utilitários ---------------------------------------------------------------------------

def _linhas(sql: str, **params) -> list[dict]:
    with db.engine().connect() as conn:
        return [dict(r) for r in conn.execute(text(sql), params).mappings()]


def _linha(sql: str, **params) -> Optional[dict]:
    linhas = _linhas(sql, **params)
    return linhas[0] if linhas else None


def _r(valor, casas=4):
    return None if valor is None else round(float(valor), casas)


def _nome(apelido, nome_completo):
    return apelido or nome_completo


def _registrar_consulta(ctx: Contexto, atleta_id: Optional[str] = None,
                        termo: Optional[str] = None, proprio_elenco: Optional[bool] = None) -> None:
    """Trilha de due diligence (documento 01 §5). Falha não derruba a requisição — mas alarma."""
    try:
        with db.engine().begin() as conn:
            conn.execute(insert(consultas_atleta).values(
                id=str(uuid.uuid4()), cliente_api_id=ctx.cliente_id, atleta_id=atleta_id,
                termo_busca=termo, proprio_elenco=proprio_elenco,
                consultado_em=datetime.now(timezone.utc)))
    except Exception:
        logger.critical("ALARME: falha ao gravar consultas_atleta (cliente=%s, atleta_id=%s)",
                        ctx.cliente_id, atleta_id, exc_info=True)


def _padrao_like(termo: str) -> str:
    """Termo normalizado como padrão LIKE, com curingas escapados (usar com ESCAPE '\\')."""
    return "%" + termo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"


def _nomes_clubes() -> dict:
    return {r["clube_slug"]: r["nome"] for r in _linhas("SELECT clube_slug, nome FROM clubes")}


def _clubes(slugs, nomes: dict) -> list[dict]:
    return [{"clube_slug": s, "clube": nomes.get(s)} for s in slugs]


def _registros_nominaveis() -> set:
    return {r["registro_cbf"] for r in _linhas(
        "SELECT registro_cbf FROM nominaveis WHERE registro_cbf IS NOT NULL")}


# --- endpoints -----------------------------------------------------------------------------

@app.get("/saude", tags=["infra"])
def saude():
    """Verificação de vida, sem autenticação. Não expõe dado."""
    return {"status": "ok"}


@app.get("/v1/cobertura", tags=["sessão"])
def cobertura(ctx: Contexto = Depends(contexto)):
    """Temporadas e rodadas disponíveis, para montar os filtros do front."""
    partidas = _linhas("SELECT DISTINCT serie, temporada FROM partidas ORDER BY serie, temporada DESC")
    fila = _linhas("""SELECT serie, temporada, MAX(rodada) AS ultima_rodada FROM risco_pre_jogo
                      GROUP BY serie, temporada ORDER BY serie, temporada DESC""")
    return {
        serie: {
            "temporadas": [r["temporada"] for r in partidas if r["serie"] == serie],
            "fila": [{"temporada": r["temporada"], "ultima_rodada": r["ultima_rodada"]}
                     for r in fila if r["serie"] == serie],
        }
        for serie in ("A", "B")
    }


@app.get("/v1/me", tags=["sessão"])
def me(ctx: Contexto = Depends(contexto)):
    return {
        "perfil": ctx.perfil,
        "rotulo": ctx.config["rotulo"],
        "camada": ctx.camada,
        "granularidade": list(ctx.config["granularidade"]),
        "clube_slug": ctx.clube_slug,
        "clube": _nomes_clubes().get(ctx.clube_slug) if ctx.clube_slug else None,
        "limiar_padrao": config.LIMIARES.get(ctx.perfil),
        "aviso_interpretativo": config.AVISO_INTERPRETATIVO,
    }


@app.get("/v1/rodadas/{serie}/{temporada}/{rodada}/fila", tags=["triagem"])
def fila(serie: Serie, temporada: int, rodada: int = Path(ge=1),
         percentil: Optional[float] = Query(None, ge=0, le=100),
         limite: int = Query(50, ge=1, le=200),
         ctx: Contexto = Depends(exigir(*IDENTIFICADOS))):
    corte = percentil if percentil is not None else config.LIMIARES[ctx.perfil]["percentil"]
    filtro_clube = " AND r.clube_slug = :clube" if ctx.perfil == "clube" else ""
    params = dict(serie=serie, temporada=temporada, rodada=rodada, clube=ctx.clube_slug)

    # O clube é filtrado ANTES do corte: vê os seus atletas no tier, não a fila geral recortada.
    total = _linha(f"SELECT COUNT(*) AS n FROM risco_pre_jogo r WHERE r.serie = :serie "
                   f"AND r.temporada = :temporada AND r.rodada = :rodada{filtro_clube}", **params)["n"]
    if total == 0:
        raise ErroApi(422, "sem_escalacao",
                      "A escalação desta rodada ainda não foi publicada pela CBF, ou a temporada "
                      "está fora da janela do escore pré-jogo.")

    base = f"""
        FROM risco_pre_jogo r
        LEFT JOIN atletas a ON a.registro_cbf = r.registro_cbf
        LEFT JOIN partidas p ON p.serie = r.serie AND p.temporada = r.temporada
                            AND p.partida_id = r.partida_id
        WHERE r.serie = :serie AND r.temporada = :temporada AND r.rodada = :rodada
          AND r.percentil >= :corte{filtro_clube}"""
    sinalizados = _linha(f"SELECT COUNT(*) AS n {base}", corte=corte, **params)["n"]
    linhas = _linhas(
        f"""SELECT r.*, a.apelido, a.nome_completo, p.clube_mandante, p.clube_visitante {base}
            ORDER BY r.percentil DESC, r.score_pre_jogo DESC LIMIT :limite""",
        corte=corte, limite=limite, **params)

    nomes = _nomes_clubes()
    dados = [{
        "atleta_id": r["registro_cbf"],
        "atleta": _nome(r["apelido"], r["nome_completo"]),
        "nome_completo": r["nome_completo"],
        "num_camisa": r["num_camisa"],
        "clube_slug": r["clube_slug"],
        "clube": nomes.get(r["clube_slug"]),
        "partida_id": r["partida_id"],
        "confronto": f"{r['clube_mandante']} x {r['clube_visitante']}" if r["clube_mandante"] else None,
        "condicao": r["condicao"],
        "score_pre_jogo": _r(r["score_pre_jogo"]),
        "percentil": _r(r["percentil"], 1),
        "tier": r["tier"],
        "componentes": {
            "minutos_previos": _r(r["minutos_previos"], 0),
            "cartoes_1t_previos": _r(r["cartoes_1t_previos"], 0),
            "taxa_1t_ajustada": _r(r["taxa_1t_ajustada"], 5),
            "minutos_esperados": _r(r["minutos_esperados"], 1),
        },
    } for r in linhas]

    return {
        "contexto": {
            "serie": serie, "temporada": temporada, "rodada": rodada,
            "percentil_aplicado": corte,
            "clube_slug": ctx.clube_slug,
            "clube": nomes.get(ctx.clube_slug) if ctx.clube_slug else None,
            "total_relacionados": total,
            "total_sinalizados": sinalizados,
            "base_rasa": rodada <= config.RODADAS_BASE_RASA,
            "aviso_base_rasa": config.AVISO_BASE_RASA if rodada <= config.RODADAS_BASE_RASA else None,
        },
        "dados": dados,
        "total": len(dados),
        "aviso_interpretativo": config.AVISO_INTERPRETATIVO,
    }


# Rotas fixas de /v1/atletas antes de /v1/atletas/{atleta_id}, senão "nominaveis" vira um id.

@app.get("/v1/atletas/nominaveis", tags=["atletas"])
def atletas_nominaveis(ctx: Contexto = Depends(contexto)):
    linhas = _linhas("SELECT * FROM nominaveis ORDER BY atleta")
    dados = [{"atleta_id": r["registro_cbf"], "atleta": r["atleta"], "sancao": r["sancao"],
              "fonte": r["fonte"]} for r in linhas]
    return {"dados": dados, "total": len(dados)}


@app.get("/v1/atletas", tags=["atletas"])
def buscar_atletas(busca: str = Query(...), serie: Optional[Serie] = None,
                   temporada: Optional[int] = None,
                   ctx: Contexto = Depends(exigir(*IDENTIFICADOS))):
    termo = normalizar(busca)
    if len(termo) < 3:
        raise ErroApi(400, "parametro_invalido", "Digite ao menos 3 caracteres para buscar.")
    _registrar_consulta(ctx, termo=busca)

    filtros, params = "", {"padrao": _padrao_like(termo)}
    if serie or temporada:
        condicoes = ["e.registro_cbf = a.registro_cbf"]
        if serie:
            condicoes.append("e.serie = :serie")
            params["serie"] = serie
        if temporada:
            condicoes.append("e.temporada = :temporada")
            params["temporada"] = temporada
        filtros = f" AND EXISTS (SELECT 1 FROM escalacoes e WHERE {' AND '.join(condicoes)})"

    # Limite fixo de 20, sem paginação e sem escore: a busca acha uma pessoa, não varre a base.
    linhas = _linhas(f"""SELECT registro_cbf, apelido, nome_completo, clubes, ultima_temporada
                         FROM atletas a WHERE busca_texto LIKE :padrao ESCAPE '\\'{filtros}
                         ORDER BY ultima_temporada DESC, nome_completo LIMIT 20""", **params)
    nomes = _nomes_clubes()
    dados = [{"atleta_id": r["registro_cbf"], "atleta": _nome(r["apelido"], r["nome_completo"]),
              "nome_completo": r["nome_completo"], "clubes": _clubes(r["clubes"].split(","), nomes),
              "ultima_temporada": r["ultima_temporada"]} for r in linhas]
    return {"dados": dados, "total": len(dados)}


@app.get("/v1/atletas/{atleta_id}", tags=["atletas"])
def ficha_atleta(atleta_id: str, ctx: Contexto = Depends(exigir(*IDENTIFICADOS))):
    atleta = _linha("SELECT * FROM atletas WHERE registro_cbf = :id", id=atleta_id)
    if atleta is None:
        raise ErroApi(404, "nao_encontrado")
    proprio = (atleta["clube_atual"] == ctx.clube_slug) if ctx.perfil == "clube" else None
    _registrar_consulta(ctx, atleta_id=atleta_id, proprio_elenco=proprio)

    minutos = _linhas("""SELECT serie, temporada, clube_slug, SUM(partidas_jogadas) AS partidas_jogadas,
                                SUM(minutos_em_campo) AS minutos_em_campo
                         FROM minutos_em_campo WHERE registro_cbf = :id
                         GROUP BY serie, temporada, clube_slug""", id=atleta_id)
    contagem = {(r["serie"], r["temporada"], r["clube_slug"]): r for r in _linhas(
        """SELECT serie, temporada, clube_slug, COUNT(*) AS total,
                  SUM(CASE WHEN periodo = '1T' THEN 1 ELSE 0 END) AS primeiro_tempo
           FROM cartoes WHERE registro_cbf = :id GROUP BY serie, temporada, clube_slug""", id=atleta_id)}
    # O escore retrospectivo é indexado por slug de nome (anos sem registro CBF na fonte).
    anomalia = {(r["serie"], r["temporada"], r["clube_slug"]): r for r in _linhas(
        """SELECT serie, temporada, clube_slug, athlete_anomaly_score, percentil, tier
           FROM anomalia_atleta WHERE atleta_slug IN (:s1, :s2)""",
        s1=atleta["atleta_slug"], s2=atleta["apelido_slug"])}

    nomes = _nomes_clubes()
    historico = []
    for m in sorted(minutos, key=lambda r: (r["temporada"], r["serie"]), reverse=True):
        chave = (m["serie"], m["temporada"], m["clube_slug"])
        c = contagem.get(chave, {"total": 0, "primeiro_tempo": 0})
        a = anomalia.get(chave, {})
        historico.append({
            "temporada": m["temporada"], "serie": m["serie"], "clube_slug": m["clube_slug"],
            "clube": nomes.get(m["clube_slug"]),
            "partidas_jogadas": m["partidas_jogadas"], "minutos_em_campo": m["minutos_em_campo"],
            "cartoes_total": c["total"], "cartoes_1t": c["primeiro_tempo"] or 0,
            "prop_cartoes_1t": _r(c["primeiro_tempo"] / c["total"], 3) if c["total"] else None,
            "athlete_anomaly_score": _r(a.get("athlete_anomaly_score"), 1),
            "percentil": _r(a.get("percentil"), 1),
            "tier": a.get("tier"),
        })

    cartoes = _linhas("""SELECT serie, temporada, partida_id, rodada, clube_slug, minuto_continuo,
                                periodo, cartao, tipo_cartao_detalhe, categoria_infracao, motivo_completo
                         FROM cartoes WHERE registro_cbf = :id
                         ORDER BY temporada DESC, rodada DESC, minuto_continuo""", id=atleta_id)
    for c in cartoes:
        c["clube"] = nomes.get(c["clube_slug"])
        c["motivo_disponivel"] = bool(c["motivo_completo"])
        c["motivo_completo"] = c["motivo_completo"] or config.MOTIVO_AUSENTE

    return {
        "atleta_id": atleta_id,
        "atleta": _nome(atleta["apelido"], atleta["nome_completo"]),
        "nome_completo": atleta["nome_completo"],
        "clubes": _clubes(atleta["clubes"].split(","), nomes),
        "clube_atual": atleta["clube_atual"],
        "historico": historico,
        "cartoes": cartoes,
        "aviso_interpretativo": config.AVISO_INTERPRETATIVO,
    }


@app.get("/v1/partidas", tags=["partidas"])
def listar_partidas(serie: Serie, temporada: Optional[int] = None, rodada: Optional[int] = None,
                    busca: Optional[str] = None, pagina: int = Query(1, ge=1),
                    por_pagina: int = Query(20, ge=1, le=50), ctx: Contexto = Depends(contexto)):
    """Navegação até um dossiê. Partida não é dado pessoal: vale para todos os perfis."""
    # Partidas de origem sem clube (ex.: Série B 2022, rodada 0) ficam fora da navegação.
    filtros, params = ["serie = :serie", "clube_mandante_slug IS NOT NULL"], {"serie": serie}
    if temporada:
        filtros.append("temporada = :temporada")
        params["temporada"] = temporada
    if rodada:
        filtros.append("rodada = :rodada")
        params["rodada"] = rodada
    if busca:
        termo = normalizar(busca)
        if len(termo) < 3:
            raise ErroApi(400, "parametro_invalido", "Digite ao menos 3 caracteres para buscar.")
        filtros.append("busca_texto LIKE :padrao ESCAPE '\\'")
        params["padrao"] = _padrao_like(termo)
    onde = " AND ".join(filtros)

    total = _linha(f"SELECT COUNT(*) AS n FROM partidas WHERE {onde}", **params)["n"]
    linhas = _linhas(f"""SELECT serie, temporada, partida_id, rodada, data, clube_mandante,
                                clube_mandante_slug, clube_visitante, clube_visitante_slug,
                                gols_mandante, gols_visitante, sumula_sha256
                         FROM partidas WHERE {onde}
                         ORDER BY temporada DESC, rodada DESC, data DESC, partida_id DESC
                         LIMIT :limite OFFSET :deslocamento""",
                     limite=por_pagina, deslocamento=(pagina - 1) * por_pagina, **params)
    campos = ("serie", "temporada", "partida_id", "rodada", "data", "clube_mandante",
              "clube_mandante_slug", "clube_visitante", "clube_visitante_slug")
    dados = [{**{k: r[k] for k in campos},
              "placar": f"{r['gols_mandante']}-{r['gols_visitante']}",
              "tem_procedencia": r["sumula_sha256"] is not None} for r in linhas]
    return {
        "dados": dados,
        "total": len(dados),
        "paginacao": {"pagina": pagina, "por_pagina": por_pagina, "total_itens": total,
                      "total_paginas": max(1, -(-total // por_pagina))},
    }


@app.get("/v1/partidas/{serie}/{temporada}/{partida_id}/dossie", tags=["partidas"])
def dossie(serie: Serie, temporada: int, partida_id: int, ctx: Contexto = Depends(contexto)):
    chave = dict(serie=serie, temporada=temporada, partida_id=partida_id)
    p = _linha("SELECT * FROM partidas WHERE serie = :serie AND temporada = :temporada "
               "AND partida_id = :partida_id", **chave)
    if p is None:
        raise ErroApi(404, "nao_encontrado")

    cartoes = _linhas("""SELECT clube_slug, num_camisa, registro_cbf, atleta, cartao, minuto_continuo,
                                periodo, tipo_cartao_detalhe, categoria_infracao, motivo_completo
                         FROM cartoes WHERE serie = :serie AND temporada = :temporada
                           AND partida_id = :partida_id ORDER BY minuto_continuo""", **chave)
    nominaveis = set() if ctx.identificada else _registros_nominaveis()
    nomes = _nomes_clubes()
    for c in cartoes:
        c["clube"] = nomes.get(c["clube_slug"])
        c["motivo_disponivel"] = bool(c["motivo_completo"])
        c["motivo_completo"] = c["motivo_completo"] or config.MOTIVO_AUSENTE
        registro = c.pop("registro_cbf")
        # Camada aberta: sem identificação individual, salvo condenado com trânsito em julgado.
        if ctx.identificada or registro in nominaveis:
            c["atleta_id"] = registro
        else:
            c["atleta_id"] = c["atleta"] = c["num_camisa"] = None

    sinalizados = None
    if ctx.identificada:
        filtro_clube = " AND r.clube_slug = :clube" if ctx.perfil == "clube" else ""
        sinalizados = [{
            "atleta_id": r["registro_cbf"], "atleta": _nome(r["apelido"], r["nome_completo"]),
            "num_camisa": r["num_camisa"], "clube_slug": r["clube_slug"],
            "clube": nomes.get(r["clube_slug"]), "condicao": r["condicao"],
            "percentil": _r(r["percentil"], 1), "tier": r["tier"],
        } for r in _linhas(
            f"""SELECT r.*, a.apelido, a.nome_completo FROM risco_pre_jogo r
                LEFT JOIN atletas a ON a.registro_cbf = r.registro_cbf
                WHERE r.serie = :serie AND r.temporada = :temporada AND r.partida_id = :partida_id
                  AND r.percentil >= :corte{filtro_clube}
                ORDER BY r.percentil DESC""",
            corte=config.LIMIARES[ctx.perfil]["percentil"], clube=ctx.clube_slug, **chave)]

    return {
        "partida": {
            "partida_id": partida_id, "serie": serie, "temporada": temporada, "rodada": p["rodada"],
            "data": p["data"], "horario": p["horario"], "arena": p["arena"], "cidade": p["cidade"],
            "arbitro": p["arbitro"],
            "clube_mandante": p["clube_mandante"], "clube_mandante_slug": p["clube_mandante_slug"],
            "clube_visitante": p["clube_visitante"], "clube_visitante_slug": p["clube_visitante_slug"],
            "placar": f"{p['gols_mandante']}-{p['gols_visitante']}",
        },
        "match_anomaly_score": _r(p["match_anomaly_score"], 1),
        "percentil": _r(p["percentil_anomalia"], 1),
        "tier": p["tier_partida"],
        "aviso_partida": config.AVISO_PARTIDA if p["match_anomaly_score"] is not None
        else "Partida fora da janela do escore de anomalia (Série A 2015–2024, Série B 2022–2023).",
        "cartoes": cartoes,
        "atletas_sinalizados": sinalizados,
        "procedencia": {
            "fonte": "Súmula Eletrônica CBF" if p["sumula_url"] else None,
            "url": p["sumula_url"], "sha256": p["sumula_sha256"],
            "baixado_em": p["baixado_em"], "processado_em": p["processado_em"],
        },
        "aviso_interpretativo": config.AVISO_INTERPRETATIVO,
    }


@app.get("/v1/agregados/{serie}/{temporada}", tags=["agregados"])
def agregados(serie: Serie, temporada: int, por: Literal["clube", "rodada"] = "clube",
              ctx: Contexto = Depends(contexto)):
    params = dict(serie=serie, temporada=temporada)
    if por == "clube":
        jogos = {r["chave"]: r for r in _linhas(
            """SELECT chave, MAX(nome) AS nome, COUNT(*) AS partidas FROM (
                 SELECT clube_mandante_slug AS chave, clube_mandante AS nome FROM partidas
                  WHERE serie = :serie AND temporada = :temporada
                 UNION ALL
                 SELECT clube_visitante_slug, clube_visitante FROM partidas
                  WHERE serie = :serie AND temporada = :temporada) t
               WHERE chave IS NOT NULL GROUP BY chave""", **params)}
        coluna_cartao = "clube_slug"
    else:
        jogos = {r["chave"]: r for r in _linhas(
            """SELECT rodada AS chave, COUNT(*) AS partidas FROM partidas
               WHERE serie = :serie AND temporada = :temporada GROUP BY rodada""", **params)}
        coluna_cartao = "rodada"
    if not jogos:
        raise ErroApi(404, "nao_encontrado")

    cartoes = {r["chave"]: r for r in _linhas(
        f"""SELECT {coluna_cartao} AS chave, COUNT(*) AS cartoes,
                   SUM(CASE WHEN periodo = '1T' THEN 1 ELSE 0 END) AS cartoes_1t
            FROM cartoes WHERE serie = :serie AND temporada = :temporada
            GROUP BY {coluna_cartao}""", **params)}

    dados = []
    for chave, j in jogos.items():
        c = cartoes.get(chave, {"cartoes": 0, "cartoes_1t": 0})
        linha = {"clube_slug": chave, "clube": j["nome"]} if por == "clube" else {"rodada": chave}
        linha.update({
            "partidas": j["partidas"], "cartoes": c["cartoes"], "cartoes_1t": c["cartoes_1t"] or 0,
            "prop_cartoes_1t": _r((c["cartoes_1t"] or 0) / c["cartoes"], 3) if c["cartoes"] else None,
            "media_cartoes_por_partida": _r(c["cartoes"] / j["partidas"], 2),
        })
        dados.append(linha)
    dados.sort(key=lambda d: d["clube_slug"] if por == "clube" else d["rodada"])
    return {"dados": dados, "total": len(dados)}
