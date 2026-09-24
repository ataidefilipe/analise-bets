"""
src/api/auth.py
---------------
Resolução do contexto do chamador (documento 01 §2).

A identidade vem do token, nunca da requisição: `perfil` e `clube` são atributos da credencial.
Quem tenta passá-los na query recebe 400.
"""

from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Request
from sqlalchemy import select

from src.api import db
from src.api.clientes import hash_chave
from src.api.erros import ErroApi
from src.api.modelo import clientes_api
from src.pipeline.perfis_de_acesso import PERFIS

PARAMETROS_PROIBIDOS = {"perfil", "clube", "clube_slug", "camada"}


@dataclass(frozen=True)
class Contexto:
    cliente_id: str
    nome: str
    perfil: str
    clube_slug: Optional[str]

    @property
    def config(self) -> dict:
        return PERFIS[self.perfil]

    @property
    def camada(self) -> str:
        return self.config["camada"]

    @property
    def identificada(self) -> bool:
        return self.camada == "identificada"


def contexto(request: Request) -> Contexto:
    proibidos = PARAMETROS_PROIBIDOS & set(request.query_params)
    if proibidos:
        raise ErroApi(400, "parametro_invalido",
                      f"Parâmetro não aceito: {', '.join(sorted(proibidos))}. "
                      "Perfil e clube vêm da credencial.")

    cabecalho = request.headers.get("authorization", "")
    tipo, _, chave = cabecalho.partition(" ")
    if tipo.lower() != "bearer" or not chave.strip():
        raise ErroApi(401, "nao_autenticado")

    with db.engine().connect() as conn:
        linha = conn.execute(
            select(clientes_api).where(clientes_api.c.api_key_hash == hash_chave(chave.strip()))
        ).mappings().first()
    if linha is None or not linha["ativo"]:
        raise ErroApi(401, "nao_autenticado")

    config = PERFIS.get(linha["perfil"])
    if config is None or not config["atendido"]:
        raise ErroApi(403, "sem_permissao", (config or {}).get("motivo_da_recusa", "Perfil não atendido."))

    return Contexto(linha["id"], linha["nome"], linha["perfil"], linha["clube_slug"])


def exigir(*perfis: str):
    """Dependência que restringe o endpoint a uma lista de perfis (documento 01 §5)."""
    def _verificar(ctx: Contexto = Depends(contexto)) -> Contexto:
        if ctx.perfil not in perfis:
            raise ErroApi(403, "sem_permissao", "Seu perfil não tem acesso a esta consulta.")
        return ctx
    return _verificar
