"""
src/api/clientes.py
-------------------
Cadastro manual de chaves de API (documento 01 §2). Não há auto-atendimento.

    python -m src.api.clientes criar --nome "STJD" --perfil federacao_stjd
    python -m src.api.clientes criar --nome "Compliance Flamengo" --perfil clube --clube flamengo
    python -m src.api.clientes listar
    python -m src.api.clientes desativar --id <uuid>

A chave em claro é impressa uma única vez. O banco guarda só o SHA-256.
"""

import argparse
import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import insert, select, update
from sqlalchemy.engine import Engine

from src.api import db
from src.api.modelo import clientes_api, metadata, TABELAS_OPERACIONAIS
from src.pipeline.perfis_de_acesso import PERFIS


def hash_chave(chave: str) -> str:
    return hashlib.sha256(chave.encode("utf-8")).hexdigest()


def criar_cliente(eng: Engine, nome: str, perfil: str, clube_slug: Optional[str] = None,
                  chave: Optional[str] = None) -> dict:
    if perfil not in PERFIS:
        raise ValueError(f"Perfil desconhecido: {perfil!r}")
    # O perfil de trading não é cadastrável; a API também o recusa, como defesa em profundidade.
    if not PERFIS[perfil]["atendido"]:
        raise ValueError(f"O perfil {perfil!r} não é atendido e não pode ser cadastrado.")
    if perfil == "clube" and not clube_slug:
        raise ValueError("O perfil 'clube' exige --clube.")
    if perfil != "clube":
        clube_slug = None

    chave = chave or "ab_" + secrets.token_urlsafe(32)
    registro = {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "api_key_hash": hash_chave(chave),
        "perfil": perfil,
        "clube_slug": clube_slug,
        "ativo": True,
        "criado_em": datetime.now(timezone.utc),
    }
    metadata.create_all(eng, tables=list(TABELAS_OPERACIONAIS))
    with eng.begin() as conn:
        conn.execute(insert(clientes_api).values(**registro))
    return {**registro, "api_key": chave}


def main():
    parser = argparse.ArgumentParser(description="Cadastro de chaves da API")
    sub = parser.add_subparsers(dest="comando", required=True)
    p_criar = sub.add_parser("criar")
    p_criar.add_argument("--nome", required=True)
    p_criar.add_argument("--perfil", required=True, choices=[p for p, c in PERFIS.items() if c["atendido"]])
    p_criar.add_argument("--clube")
    sub.add_parser("listar")
    p_desativar = sub.add_parser("desativar")
    p_desativar.add_argument("--id", required=True)
    args = parser.parse_args()

    eng = db.engine()
    metadata.create_all(eng, tables=list(TABELAS_OPERACIONAIS))
    if args.comando == "criar":
        cliente = criar_cliente(eng, args.nome, args.perfil, args.clube)
        print(f"id:      {cliente['id']}")
        print(f"perfil:  {cliente['perfil']}  clube: {cliente['clube_slug'] or '-'}")
        print(f"api_key: {cliente['api_key']}   <- guarde agora; não é exibida de novo")
    elif args.comando == "listar":
        with eng.connect() as conn:
            for r in conn.execute(select(clientes_api)).mappings():
                print(f"{r['id']}  {r['perfil']:<20} {r['clube_slug'] or '-':<16} "
                      f"{'ativo' if r['ativo'] else 'inativo':<8} {r['nome']}")
    else:
        with eng.begin() as conn:
            n = conn.execute(update(clientes_api).where(clientes_api.c.id == args.id)
                             .values(ativo=False)).rowcount
        print("desativado" if n else "id não encontrado")


if __name__ == "__main__":
    main()
