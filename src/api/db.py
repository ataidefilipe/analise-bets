"""
src/api/db.py
-------------
Conexão com o banco. Um engine por processo; a URL vem de `ANALISE_BETS_DATABASE_URL`.
"""

from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from src.api import config

_engine: Optional[Engine] = None


def criar_engine(url: str) -> Engine:
    if url.startswith("sqlite:///"):
        Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url, pool_pre_ping=True)


def engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = criar_engine(config.DATABASE_URL)
    return _engine


def definir_engine(novo: Engine) -> None:
    """Troca o engine do processo. Usado pelos testes para apontar para um banco temporário."""
    global _engine
    _engine = novo
