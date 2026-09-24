"""
src/api/modelo.py
-----------------
Schema do banco da API, em SQLAlchemy Core para rodar igual em SQLite (local) e PostgreSQL.

Dois grupos de tabela:

* **De leitura** — recriadas a cada carga a partir das bases do pipeline (`carga.py`). A API
  nunca escreve nelas e nenhum escore é calculado em tempo de requisição.
* **Operacionais** — `clientes_api` e `consultas_atleta`. Sobrevivem à recarga: apagá-las
  apagaria credenciais e a trilha de due diligence.

A identidade do atleta é `registro_cbf`. Cartões herdam o registro da escalação da mesma
partida; nos anos sem súmula eletrônica ele fica nulo e o cartão não entra na ficha.
"""

from sqlalchemy import (
    Boolean, Column, DateTime, Float, Index, Integer, MetaData, String, Table, Text,
)

metadata = MetaData()

partidas = Table(
    "partidas", metadata,
    Column("serie", String(1), primary_key=True),
    Column("temporada", Integer, primary_key=True),
    Column("partida_id", Integer, primary_key=True),
    Column("rodada", Integer),
    Column("data", String(10)),
    Column("horario", String(8)),
    Column("clube_mandante", Text),
    Column("clube_mandante_slug", String(64)),
    Column("clube_visitante", Text),
    Column("clube_visitante_slug", String(64)),
    Column("gols_mandante", Integer),
    Column("gols_visitante", Integer),
    Column("arena", Text),
    Column("cidade", Text),
    Column("uf_estadio", String(2)),
    Column("arbitro", Text),
    # Escore retrospectivo de partida, materializado (janela: A 2015–2024, B 2022–2023).
    Column("match_anomaly_score", Float),
    Column("percentil_anomalia", Float),
    Column("tier_partida", Text),
    # Procedência: o produto vendido a P3 (documento 01 §4.5).
    Column("sumula_url", Text),
    Column("sumula_sha256", String(64)),
    Column("baixado_em", String(40)),
    Column("processado_em", String(40)),
    Index("ix_partidas_rodada", "serie", "temporada", "rodada"),
)

atletas = Table(
    "atletas", metadata,
    Column("registro_cbf", String(16), primary_key=True),
    Column("nome_completo", Text),
    Column("apelido", Text),
    Column("atleta_slug", String(128)),
    Column("apelido_slug", String(128)),
    # Nome completo + apelido sem acento e em minúsculas: é onde a busca casa.
    Column("busca_texto", Text),
    Column("clubes", Text),  # slugs separados por vírgula
    Column("clube_atual", String(64)),  # clube da última escalação
    Column("ultima_temporada", Integer),
    Index("ix_atletas_slug", "atleta_slug"),
)

escalacoes = Table(
    "escalacoes", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("serie", String(1), nullable=False),
    Column("temporada", Integer, nullable=False),
    Column("partida_id", Integer, nullable=False),
    Column("rodada", Integer),
    Column("clube_slug", String(64)),
    Column("num_camisa", Integer),
    Column("registro_cbf", String(16)),
    Column("condicao", String(16)),
    Column("goleiro", Boolean),
    Index("ix_esc_partida", "serie", "temporada", "partida_id"),
    Index("ix_esc_registro", "registro_cbf"),
)

cartoes = Table(
    "cartoes", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("serie", String(1), nullable=False),
    Column("temporada", Integer, nullable=False),
    Column("partida_id", Integer, nullable=False),
    Column("rodada", Integer),
    Column("clube_slug", String(64)),
    Column("num_camisa", Integer),
    Column("registro_cbf", String(16)),
    Column("atleta", Text),
    Column("cartao", String(16)),
    Column("minuto_continuo", Integer),
    Column("periodo", String(4)),
    Column("tipo_cartao_detalhe", Text),
    Column("categoria_infracao", Text),
    Column("motivo_completo", Text),
    Index("ix_cartoes_partida", "serie", "temporada", "partida_id"),
    Index("ix_cartoes_registro", "registro_cbf"),
)

minutos_em_campo = Table(
    "minutos_em_campo", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("serie", String(1), nullable=False),
    Column("temporada", Integer, nullable=False),
    Column("clube_slug", String(64)),
    Column("registro_cbf", String(16)),
    Column("partidas_jogadas", Integer),
    Column("minutos_em_campo", Integer),
    Index("ix_min_registro", "registro_cbf", "temporada"),
)

risco_pre_jogo = Table(
    "risco_pre_jogo", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("serie", String(1), nullable=False),
    Column("temporada", Integer, nullable=False),
    Column("rodada", Integer, nullable=False),
    Column("partida_id", Integer, nullable=False),
    Column("clube_slug", String(64)),
    Column("registro_cbf", String(16)),
    Column("num_camisa", Integer),
    Column("condicao", String(16)),
    Column("minutos_previos", Float),
    Column("cartoes_1t_previos", Float),
    Column("taxa_1t_ajustada", Float),
    Column("minutos_esperados", Float),
    Column("score_pre_jogo", Float),
    # Materializados na carga: percentil na distribuição da (série, temporada) e tier.
    Column("percentil", Float),
    Column("tier", Text),
    Index("ix_risco_rodada", "serie", "temporada", "rodada", "percentil"),
    Index("ix_risco_partida", "serie", "temporada", "partida_id"),
)

anomalia_atleta = Table(
    "anomalia_atleta", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("serie", String(1), nullable=False),
    Column("temporada", Integer, nullable=False),
    Column("clube_slug", String(64)),
    Column("atleta_slug", String(128)),
    Column("athlete_anomaly_score", Float),
    Column("percentil", Float),
    Column("tier", Text),
    Index("ix_anom_slug", "atleta_slug", "temporada"),
)

nominaveis = Table(
    "nominaveis", metadata,
    Column("atleta_slug", String(128), primary_key=True),
    Column("registro_cbf", String(16)),
    Column("atleta", Text),
    Column("sancao", Text),
    Column("fonte", Text),
)

TABELAS_DE_LEITURA = (
    partidas, atletas, escalacoes, cartoes, minutos_em_campo, risco_pre_jogo,
    anomalia_atleta, nominaveis,
)

# --- Operacionais: nunca recriadas pela carga ---

clientes_api = Table(
    "clientes_api", metadata,
    Column("id", String(36), primary_key=True),
    Column("nome", Text, nullable=False),
    Column("api_key_hash", String(64), nullable=False, unique=True),
    Column("perfil", String(32), nullable=False),
    Column("clube_slug", String(64)),
    Column("ativo", Boolean, nullable=False, default=True),
    Column("criado_em", DateTime(timezone=True)),
)

consultas_atleta = Table(
    "consultas_atleta", metadata,
    Column("id", String(36), primary_key=True),
    Column("cliente_api_id", String(36), nullable=False),
    Column("atleta_id", String(16)),
    Column("termo_busca", Text),
    Column("proprio_elenco", Boolean),
    Column("consultado_em", DateTime(timezone=True)),
    Index("ix_consultas_cliente", "cliente_api_id", "consultado_em"),
    Index("ix_consultas_atleta", "atleta_id"),
)

TABELAS_OPERACIONAIS = (clientes_api, consultas_atleta)
