"""
src/api/config.py
-----------------
Configuração da API e regras de produto que o backend aplica (documento 02 da especificação).

Tudo o que muda por ambiente vem de variável de ambiente; o resto é regra de negócio e fica
aqui, num lugar só, para que o front nunca precise replicá-la.
"""

import os
from pathlib import Path

from src.models.anomaly_detection import TIER_ATLETA_BASAL, TIERS_ATLETA
from src.pipeline.perfis_de_acesso import SEGREDO_PSEUDONIMIZACAO
from src.pipeline.serve_product_feed import AVISO_INTERPRETATIVO

# O banco da API contém dado pessoal identificado: fica fora do versionamento (.gitignore).
CAMINHO_BANCO_PADRAO = Path("data") / "api" / "analise_bets_api.db"
_database_url = (
    os.environ.get("ANALISE_BETS_DATABASE_URL")
    or os.environ.get("DATABASE_URL")
    or f"sqlite:///{CAMINHO_BANCO_PADRAO.as_posix()}"
)
# Railway exposes PostgreSQL as DATABASE_URL; select psycopg v3 explicitly because the
# unqualified `postgresql://` SQLAlchemy URL otherwise defaults to the psycopg2 driver.
if _database_url.startswith("postgres://"):
    _database_url = "postgresql+psycopg://" + _database_url.removeprefix("postgres://")
elif _database_url.startswith("postgresql://"):
    _database_url = "postgresql+psycopg://" + _database_url.removeprefix("postgresql://")
DATABASE_URL = _database_url

# Origens liberadas para o front. Lista separada por vírgula; "*" libera qualquer uma (POC).
CORS_ORIGENS = [o.strip() for o in os.environ.get("ANALISE_BETS_CORS", "*").split(",") if o.strip()]

AMBIENTE = os.environ.get("ANALISE_BETS_AMBIENTE", "producao")
SEGREDO_DE_DESENVOLVIMENTO = "desenvolvimento-nao-usar-em-producao"

# Limiar padrão por perfil (documento 02 §3). Perfis sem fila não têm limiar.
LIMIARES = {
    "federacao_stjd": {"percentil": 70.0, "alertas_por_rodada_esperados": 3.0},
    "clube": {"percentil": 90.0, "alertas_por_rodada_esperados": 1.0},
    "operadora_integrity": {"percentil": 50.0, "alertas_por_rodada_esperados": 5.0},
    "imprensa_academia": None,
}

AVISO_PARTIDA = (
    "No nível da partida, o escore de anomalia não discrimina melhor que sorteio. "
    "É informação de contexto, não recomendação de ação."
)
AVISO_BASE_RASA = (
    "Histórico insuficiente nas primeiras rodadas; os escores são dominados pela média da liga."
)
MOTIVO_AUSENTE = "motivo não registrado na súmula desta temporada"
RODADAS_BASE_RASA = 5

__all__ = [
    "AVISO_INTERPRETATIVO", "TIERS_ATLETA", "TIER_ATLETA_BASAL", "LIMIARES", "DATABASE_URL",
]


def verificar_segredo() -> None:
    """
    Recusa subir com o segredo de pseudonimização de desenvolvimento (documento 04 §5).

    Fora de `ANALISE_BETS_AMBIENTE=dev`, a falta do segredo derruba a aplicação em vez de
    seguir em silêncio com um valor que está no código-fonte.
    """
    if AMBIENTE == "dev":
        return
    if SEGREDO_PSEUDONIMIZACAO == SEGREDO_DE_DESENVOLVIMENTO:
        raise RuntimeError(
            "ANALISE_BETS_PSEUDONIMO_SECRET não definido (ou igual ao valor de desenvolvimento). "
            "Defina o segredo ou, só em máquina local, ANALISE_BETS_AMBIENTE=dev."
        )


def tier_atleta(percentil: float) -> str:
    for corte, rotulo in TIERS_ATLETA:
        if percentil >= corte:
            return rotulo
    return TIER_ATLETA_BASAL
