"""
src/pipeline/serve_product_feed.py
---------------------------------
Camada de Serviço e Entrega para Produto (Serving Layer).
Transforma as bases canônicas Parquet (Série A e B) em feeds de alto desempenho
para consumo direto por produtos, APIs REST/GraphQL, mobile apps e dashboards:

1. Feeds JSON leves:
   - `data/processed/product_feed/latest_matches.json`: últimas partidas com gols e cartões embutidos.
   - `data/processed/product_feed/tabela_classificacao.json`: classificação oficial consolidada por temporada/série.
2. Banco Relacional SQLite:
   - `data/processed/product_feed/brasileirao.db`: banco SQLite com índices otimizados, modo WAL e esquema relacional pronto para ORMs (SQLAlchemy, Prisma, Drizzle, etc).
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ProductFeedServer")

from src.pipeline.perfis_de_acesso import (
    CAMADA_ABERTA,
    CAMADA_IDENTIFICADA,
    CAMADA_PSEUDONIMIZADA,
    PERFIS,
    aplicar_perfil,
    pseudonimizar,
    registros_publicos,
)

FEED_DIR = Path("data/processed/product_feed")

# Saídas com identificação nominal não ficam no diretório servido por padrão: vão para um
# subdiretório que sinaliza a restrição contratual (tarefa F4-03).
SUBDIR_RESTRITO = "restrito"

# Ressalva que acompanha toda saída de risco, no feed e em qualquer interface derivada dele.
# A obrigação de exibi-la vem da tarefa F3-01 e das diretrizes de governança do projeto.
AVISO_INTERPRETATIVO = (
    "Este escore mede ATIPICIDADE ESTATÍSTICA do perfil disciplinar do atleta, e não "
    "probabilidade de fraude. Um atleta com estilo de falta tática precoce e um atleta "
    "aliciado produzem assinaturas semelhantes. A finalidade é priorizar atenção humana; "
    "não constitui acusação, indício ou prova de conduta irregular."
)
PROCESSED_DIR = Path("data/processed")


def normalize_club_name(nome: Optional[str]) -> str:
    if pd.isna(nome) or not nome:
        return ""
    import re
    n = str(nome).strip()
    n = re.sub(r"\s+s\.?a\.?f\.?$", "", n, flags=re.IGNORECASE).strip()
    n = re.sub(r"\s+f\.?c\.?$", "", n, flags=re.IGNORECASE).strip()
    return n


def compute_standings(df_partidas: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula tabela de classificação (pontos corridos) a partir do DataFrame de partidas:
    Pontos (V=3, E=1, D=0), Jogos, Vitórias, Empates, Derrotas, GP, GC, SG, Aproveitamento.
    """
    if df_partidas.empty:
        return pd.DataFrame()

    records: Dict[str, Dict[str, Any]] = {}

    for _, row in df_partidas.iterrows():
        # Apenas partidas com placar computado
        gm = row.get("gols_mandante")
        gv = row.get("gols_visitante")
        if pd.isna(gm) or pd.isna(gv):
            continue

        gm = int(gm)
        gv = int(gv)
        mandante_raw = row.get("clube_mandante")
        visitante_raw = row.get("clube_visitante")

        if not mandante_raw or not visitante_raw:
            continue

        mandante = normalize_club_name(mandante_raw)
        visitante = normalize_club_name(visitante_raw)

        for time_nome in [mandante, visitante]:
            if time_nome not in records:
                records[time_nome] = {
                    "clube": time_nome,
                    "pontos": 0,
                    "jogos": 0,
                    "vitorias": 0,
                    "empates": 0,
                    "derrotas": 0,
                    "gols_pro": 0,
                    "gols_contra": 0,
                    "saldo_gols": 0,
                }

        # Atualizar mandante
        records[mandante]["jogos"] += 1
        records[mandante]["gols_pro"] += gm
        records[mandante]["gols_contra"] += gv
        # Atualizar visitante
        records[visitante]["jogos"] += 1
        records[visitante]["gols_pro"] += gv
        records[visitante]["gols_contra"] += gm

        if gm > gv:
            records[mandante]["pontos"] += 3
            records[mandante]["vitorias"] += 1
            records[visitante]["derrotas"] += 1
        elif gv > gm:
            records[visitante]["pontos"] += 3
            records[visitante]["vitorias"] += 1
            records[mandante]["derrotas"] += 1
        else:
            records[mandante]["pontos"] += 1
            records[mandante]["empates"] += 1
            records[visitante]["pontos"] += 1
            records[visitante]["empates"] += 1

    for r in records.values():
        r["saldo_gols"] = r["gols_pro"] - r["gols_contra"]
        max_pts = r["jogos"] * 3
        r["aproveitamento_pct"] = round((r["pontos"] / max_pts * 100), 1) if max_pts > 0 else 0.0

    df_standings = pd.DataFrame(list(records.values()))
    if not df_standings.empty:
        df_standings = df_standings.sort_values(
            by=["pontos", "vitorias", "saldo_gols", "gols_pro"],
            ascending=[False, False, False, False]
        ).reset_index(drop=True)
        df_standings["posicao"] = df_standings.index + 1
        # Reordenar colunas
        cols_order = [
            "posicao", "clube", "pontos", "jogos", "vitorias",
            "empates", "derrotas", "gols_pro", "gols_contra", "saldo_gols", "aproveitamento_pct"
        ]
        df_standings = df_standings[cols_order]

    return df_standings


class ProductFeedServer:
    def __init__(self, processed_dir: Path = PROCESSED_DIR, feed_dir: Path = FEED_DIR):
        self.processed_dir = Path(processed_dir)
        self.feed_dir = Path(feed_dir)
        self.feed_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.feed_dir / "brasileirao.db"

    def generate_all_feeds(self, target_season: Optional[int] = None) -> Dict[str, Any]:
        """
        Lê todas as bases de Série A e Série B, gera JSONs e atualiza o banco SQLite.
        """
        logger.info("Iniciando geração de feeds de produto em %s...", self.feed_dir)
        series_data: Dict[str, Dict[str, pd.DataFrame]] = {}

        for s in ["serie_a", "serie_b"]:
            serie_label = "A" if s == "serie_a" else "B"
            s_path = self.processed_dir / s
            p_file = s_path / "partidas.parquet"
            g_file = s_path / "gols.parquet"
            c_file = s_path / "cartoes.parquet"
            e_file = s_path / "escalacoes.parquet"
            m_file = s_path / "minutos_em_campo.parquet"

            df_p = pd.read_parquet(p_file) if p_file.exists() else pd.DataFrame()
            df_g = pd.read_parquet(g_file) if g_file.exists() else pd.DataFrame()
            df_c = pd.read_parquet(c_file) if c_file.exists() else pd.DataFrame()
            df_e = pd.read_parquet(e_file) if e_file.exists() else pd.DataFrame()
            df_m = pd.read_parquet(m_file) if m_file.exists() else pd.DataFrame()

            if not df_p.empty and "serie" not in df_p.columns:
                df_p["serie"] = serie_label
            if not df_g.empty and "serie" not in df_g.columns:
                df_g["serie"] = serie_label
            if not df_c.empty and "serie" not in df_c.columns:
                df_c["serie"] = serie_label
            for df_aux in (df_e, df_m):
                if not df_aux.empty and "serie" not in df_aux.columns:
                    df_aux["serie"] = serie_label

            series_data[serie_label] = {
                "partidas": df_p,
                "gols": df_g,
                "cartoes": df_c,
                "escalacoes": df_e,
                "minutos_em_campo": df_m,
            }

        # 1. Gerar Classificação JSON
        classificacao_payload: Dict[str, Any] = {
            "gerado_em": datetime.now().isoformat(),
            "tabelas": {}
        }

        all_standings_rows: List[Dict[str, Any]] = []

        for serie_label, datasets in series_data.items():
            df_p = datasets["partidas"]
            if df_p.empty:
                continue

            seasons = [target_season] if target_season else sorted(list(df_p["temporada"].unique()), reverse=True)
            for ano in seasons:
                df_season = df_p[df_p["temporada"] == ano]
                if df_season.empty:
                    continue
                df_std = compute_standings(df_season)
                key = f"Série {serie_label} - {ano}"
                classificacao_payload["tabelas"][key] = {
                    "serie": serie_label,
                    "temporada": int(ano),
                    "total_clubes": len(df_std),
                    "classificacao": df_std.to_dict(orient="records")
                }

                for row in df_std.to_dict(orient="records"):
                    row["temporada"] = int(ano)
                    row["serie"] = serie_label
                    all_standings_rows.append(row)

        classificacao_path = self.feed_dir / "tabela_classificacao.json"
        with open(classificacao_path, "w", encoding="utf-8") as f:
            json.dump(classificacao_payload, f, indent=2, ensure_ascii=False)

        # 2. Gerar Feed de Partidas Recentes JSON
        latest_matches_payload: Dict[str, Any] = {
            "gerado_em": datetime.now().isoformat(),
            "series": {}
        }

        for serie_label, datasets in series_data.items():
            df_p = datasets["partidas"]
            df_g = datasets["gols"]
            df_c = datasets["cartoes"]

            if df_p.empty:
                continue

            seasons = [target_season] if target_season else sorted(list(df_p["temporada"].unique()), reverse=True)
            cur_season = seasons[0]
            df_recent = df_p[df_p["temporada"] == cur_season]
            if "data" in df_recent.columns:
                df_recent = df_recent.sort_values(by=["data", "partida_id"], ascending=[False, False])

            # Top 30 partidas recentes com detalhes
            matches_list = []
            for _, r in df_recent.head(30).iterrows():
                p_id = r.get("partida_id")
                t_ano = r.get("temporada")

                m_goals = []
                if not df_g.empty and p_id is not None:
                    g_match = df_g[(df_g["temporada"] == t_ano) & (df_g["partida_id"] == p_id)]
                    for _, g in g_match.iterrows():
                        m_goals.append({
                            "minuto": g.get("minuto_nominal"),
                            "acrescimo": g.get("acrescimo", 0),
                            "periodo": g.get("periodo"),
                            "atleta": g.get("atleta"),
                            "clube": g.get("clube"),
                            "tipo": g.get("tipo_de_gol"),
                        })

                m_cards = []
                if not df_c.empty and p_id is not None:
                    c_match = df_c[(df_c["temporada"] == t_ano) & (df_c["partida_id"] == p_id)]
                    for _, c in c_match.iterrows():
                        m_cards.append({
                            "minuto": c.get("minuto_nominal"),
                            "periodo": c.get("periodo"),
                            "atleta": c.get("atleta"),
                            "clube": c.get("clube"),
                            "cartao": c.get("cartao"),
                            "motivo": c.get("categoria_infracao"),
                        })

                matches_list.append({
                    "partida_id": int(p_id) if pd.notna(p_id) else None,
                    "temporada": int(t_ano) if pd.notna(t_ano) else None,
                    "serie": serie_label,
                    "rodada": int(r.get("rodada")) if pd.notna(r.get("rodada")) else None,
                    "data": str(r.get("data")),
                    "horario": str(r.get("horario", "")),
                    "mandante": r.get("clube_mandante"),
                    "visitante": r.get("clube_visitante"),
                    "gols_mandante": int(r.get("gols_mandante")) if pd.notna(r.get("gols_mandante")) else None,
                    "gols_visitante": int(r.get("gols_visitante")) if pd.notna(r.get("gols_visitante")) else None,
                    "resultado": r.get("resultado"),
                    "vencedor": r.get("vencedor"),
                    "estadio": r.get("estadio") or r.get("arena", ""),
                    "arbitro": r.get("arbitro", ""),
                    "gols": m_goals,
                    "cartoes": m_cards,
                })

            latest_matches_payload["series"][f"Série {serie_label}"] = {
                "temporada": int(cur_season),
                "total_partidas_recentes": len(matches_list),
                "partidas": matches_list,
            }

        latest_path = self.feed_dir / "latest_matches.json"
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(latest_matches_payload, f, indent=2, ensure_ascii=False)

        # 3. Feed de elenco e minutos em campo (F2-04)
        elenco_payload: Dict[str, Any] = {
            "gerado_em": datetime.now().isoformat(),
            "descricao": (
                "Participação e minutos em campo por atleta e temporada, derivados da relação "
                "de atletas da súmula oficial cruzada com as substituições. Cobertura restrita "
                "às temporadas com súmula disponível."
            ),
            "series": {},
        }
        for serie_label, dsets in series_data.items():
            df_m = dsets.get("minutos_em_campo", pd.DataFrame())
            if df_m.empty:
                continue
            por_temporada: Dict[str, Any] = {}
            for temporada, g in df_m.groupby("temporada"):
                elencos: Dict[str, Any] = {}
                for clube, gc in g.groupby("clube_slug"):
                    elencos[str(clube)] = [
                        {
                            "atleta": row["apelido"],
                            "atleta_slug": row["atleta_slug"],
                            "registro_cbf": row.get("registro_cbf"),
                            "partidas_jogadas": int(row["partidas_jogadas"]),
                            "partidas_como_titular": int(row["partidas_como_titular"]),
                            "minutos_em_campo": int(row["minutos_em_campo"]),
                            "media_minutos_por_jogo": (
                                None if pd.isna(row["media_minutos_por_jogo"])
                                else float(row["media_minutos_por_jogo"])
                            ),
                        }
                        for _, row in gc.sort_values("minutos_em_campo", ascending=False).iterrows()
                    ]
                por_temporada[str(int(temporada))] = {
                    "atletas": int(len(g)),
                    "clubes": elencos,
                }
            elenco_payload["series"][f"Série {serie_label}"] = por_temporada

        elenco_path = self.feed_dir / "elenco_e_minutos.json"
        with open(elenco_path, "w", encoding="utf-8") as f:
            json.dump(elenco_payload, f, indent=2, ensure_ascii=False)

        # 4. Feed de risco pré-jogo por atleta escalado (F3-01), segmentado por perfil (F4-03)
        risco_path = self.feed_dir / "risco_pre_jogo.json"
        score_file = self.processed_dir / "integrity" / "score_pre_jogo.parquet"
        df_risco = pd.read_parquet(score_file) if score_file.exists() else pd.DataFrame()
        df_risco_pseudonimo = pd.DataFrame()

        if not df_risco.empty:
            publicos = registros_publicos()
            restrito_dir = self.feed_dir / SUBDIR_RESTRITO
            restrito_dir.mkdir(parents=True, exist_ok=True)

            cabecalho = {
                "gerado_em": datetime.now().isoformat(),
                "aviso": AVISO_INTERPRETATIVO,
                "descricao": (
                    "Cartões no 1º tempo esperados por atleta relacionado, estimados apenas com "
                    "informação anterior à rodada. Modo retroativo: usa a escalação da súmula "
                    "oficial, que só existe após a partida."
                ),
            }

            # O feed servido por padrão é o da camada aberta: nenhum atleta identificado.
            # Publicar nominalmente atletas apenas atípicos, nunca investigados, é o risco que
            # a F4-02 descreve — e este produto tem 6.445 deles.
            aberto = aplicar_perfil(df_risco, "imprensa_academia")
            payload_aberto = dict(cabecalho)
            payload_aberto["perfil"] = "imprensa_academia"
            payload_aberto["camada"] = CAMADA_ABERTA
            payload_aberto["partidas"] = [
                {k: (int(v) if isinstance(v, (int, float)) and k in
                     ("temporada", "rodada", "partida_id", "atletas_no_agregado") else v)
                 for k, v in linha.items()}
                for linha in aberto.to_dict("records")
            ]
            with open(risco_path, "w", encoding="utf-8") as f:
                json.dump(payload_aberto, f, indent=2, ensure_ascii=False)

            # Camada pseudonimizada: perfil individual sob identificador estável, sem nome.
            df_risco_pseudonimo = aplicar_perfil(
                df_risco.assign(atleta_slug=df_risco["apelido"].str.lower().str.replace(" ", "_")),
                "federacao_stjd",
            )
            df_risco_pseudonimo = df_risco_pseudonimo.copy()
            df_risco_pseudonimo["atleta_pseudonimo"] = df_risco_pseudonimo["registro_cbf"].map(
                pseudonimizar)
            df_risco_pseudonimo = df_risco_pseudonimo.drop(
                columns=[c for c in ("apelido", "registro_cbf", "atleta_slug", "num_camisa")
                         if c in df_risco_pseudonimo.columns])

            payload_pseudo = dict(cabecalho)
            payload_pseudo["perfil"] = "demonstracao"
            payload_pseudo["camada"] = CAMADA_PSEUDONIMIZADA
            payload_pseudo["registros"] = df_risco_pseudonimo.head(5000).to_dict("records")
            with open(restrito_dir / "risco_pre_jogo__pseudonimizado.json", "w",
                      encoding="utf-8") as f:
                json.dump(payload_pseudo, f, indent=2, ensure_ascii=False, default=str)

            # Camada identificada: só para perfis contratados, em diretório restrito.
            ordenado = df_risco.sort_values(
                ["serie", "temporada", "rodada", "partida_id", "score_pre_jogo"],
                ascending=[True, True, True, True, False],
            )
            payload_identificado = dict(cabecalho)
            payload_identificado["perfil"] = "federacao_stjd"
            payload_identificado["camada"] = CAMADA_IDENTIFICADA
            payload_identificado["condicao_de_uso"] = (
                "Uso restrito a federação, STJD ou órgão de investigação, com finalidade de "
                "auditoria declarada e registro de acesso. Redistribuição vedada."
            )
            payload_identificado["partidas"] = []
            for (serie, temporada, partida_id), g in ordenado.groupby(
                    ["serie", "temporada", "partida_id"], sort=False):
                payload_identificado["partidas"].append({
                    "serie": serie,
                    "temporada": int(temporada),
                    "rodada": int(g["rodada"].iloc[0]),
                    "partida_id": int(partida_id),
                    "atletas": [
                        {
                            "atleta": row["apelido"],
                            "registro_cbf": row["registro_cbf"],
                            "clube": row["clube_slug"],
                            "num_camisa": int(row["num_camisa"]),
                            "condicao": row["condicao"],
                            "minutos_previos": int(row["minutos_previos"]),
                            "cartoes_1t_previos": int(row["cartoes_1t_previos"]),
                            "score_pre_jogo": float(row["score_pre_jogo"]),
                        }
                        for _, row in g.head(5).iterrows()
                    ],
                })
            with open(restrito_dir / "risco_pre_jogo__federacao_stjd.json", "w",
                      encoding="utf-8") as f:
                json.dump(payload_identificado, f, indent=2, ensure_ascii=False)

            aviso_md = restrito_dir / "AVISO.md"
            aviso_md.write_text(
                "# Camada identificada — uso restrito\n\n"
                "Os arquivos deste diretório contêm **nome de atleta** e devem ser entregues\n"
                "apenas a perfis contratados, com finalidade declarada e registro de acesso,\n"
                "conforme `docs/termo_de_uso_e_licenciamento.md` (tarefa F4-03).\n\n"
                "A maioria dos atletas aqui listados **nunca foi investigada**: são apenas\n"
                "estatisticamente atípicos. Publicá-los nominalmente expõe o projeto a ação por\n"
                "dano moral e contradiz a diretriz de presunção de inocência do relatório 07.\n\n"
                f"{AVISO_INTERPRETATIVO}\n",
                encoding="utf-8",
            )

        # 5. Exportar para SQLite com tabelas e índices otimizados
        self._export_to_sqlite(series_data, all_standings_rows, df_risco_pseudonimo)

        feed_stats = {
            "json_classificacao": str(classificacao_path),
            "json_latest_matches": str(latest_path),
            "json_elenco_e_minutos": str(elenco_path),
            "json_risco_pre_jogo": str(risco_path) if not df_risco.empty else None,
            "camada_do_feed_padrao": CAMADA_ABERTA,
            "perfis_atendidos": [p for p, c in PERFIS.items() if c["atendido"]],
            "sqlite_db": str(self.db_path),
            "total_tabelas_classificacao": len(classificacao_payload["tabelas"]),
        }
        logger.info("Feeds de produto gerados com sucesso: %s", feed_stats)
        return feed_stats

    def _export_to_sqlite(
        self,
        series_data: Dict[str, Dict[str, pd.DataFrame]],
        all_standings_rows: List[Dict[str, Any]],
        df_risco: Optional[pd.DataFrame] = None,
    ) -> None:
        """
        Exporta os dados consolidados para SQLite, ativando modo WAL e criando índices.
        """
        logger.info("Exportando dados consolidados para SQLite em %s...", self.db_path)
        all_partidas = []
        all_gols = []
        all_cartoes = []
        all_escalacoes = []
        all_minutos = []

        for s_label, dsets in series_data.items():
            if not dsets["partidas"].empty:
                all_partidas.append(dsets["partidas"])
            if not dsets["gols"].empty:
                all_gols.append(dsets["gols"])
            if not dsets["cartoes"].empty:
                all_cartoes.append(dsets["cartoes"])
            if not dsets.get("escalacoes", pd.DataFrame()).empty:
                all_escalacoes.append(dsets["escalacoes"])
            if not dsets.get("minutos_em_campo", pd.DataFrame()).empty:
                all_minutos.append(dsets["minutos_em_campo"])

        df_all_p = pd.concat(all_partidas, ignore_index=True) if all_partidas else pd.DataFrame()
        df_all_g = pd.concat(all_gols, ignore_index=True) if all_gols else pd.DataFrame()
        df_all_c = pd.concat(all_cartoes, ignore_index=True) if all_cartoes else pd.DataFrame()
        df_all_std = pd.DataFrame(all_standings_rows) if all_standings_rows else pd.DataFrame()
        df_all_e = pd.concat(all_escalacoes, ignore_index=True) if all_escalacoes else pd.DataFrame()
        df_all_m = pd.concat(all_minutos, ignore_index=True) if all_minutos else pd.DataFrame()

        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("PRAGMA journal_mode = WAL;")
            cur.execute("PRAGMA synchronous = NORMAL;")

            if not df_all_p.empty:
                df_all_p.to_sql("partidas", conn, if_exists="replace", index=False)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_partidas_temp_serie ON partidas(temporada, serie);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_partidas_rodada ON partidas(temporada, serie, rodada);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_partidas_data ON partidas(data);")

            if not df_all_g.empty:
                df_all_g.to_sql("gols", conn, if_exists="replace", index=False)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_gols_partida ON gols(temporada, partida_id);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_gols_atleta ON gols(atleta_slug);")

            if not df_all_c.empty:
                df_all_c.to_sql("cartoes", conn, if_exists="replace", index=False)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_cartoes_partida ON cartoes(temporada, partida_id);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_cartoes_atleta ON cartoes(atleta_slug);")

            if not df_all_std.empty:
                df_all_std.to_sql("classificacao", conn, if_exists="replace", index=False)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_std_temp_serie ON classificacao(temporada, serie);")

            if not df_all_e.empty:
                df_all_e.to_sql("escalacoes", conn, if_exists="replace", index=False)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_esc_partida ON escalacoes(temporada, partida_id);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_esc_atleta ON escalacoes(atleta_slug);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_esc_camisa ON escalacoes(temporada, partida_id, clube_slug, num_camisa);")

            if not df_all_m.empty:
                df_all_m.to_sql("minutos_em_campo", conn, if_exists="replace", index=False)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_min_atleta ON minutos_em_campo(temporada, serie, atleta_slug);")

            if df_risco is not None and not df_risco.empty:
                # O banco recebe a camada PSEUDONIMIZADA: mantém utilidade analítica —
                # acompanhar o mesmo atleta ao longo do tempo — sem expor nome nem registro.
                colunas = ["serie", "temporada", "rodada", "partida_id", "clube_slug",
                           "atleta_pseudonimo", "condicao", "minutos_previos",
                           "cartoes_1t_previos", "taxa_1t_ajustada", "score_pre_jogo"]
                presentes = [c for c in colunas if c in df_risco.columns]
                df_risco[presentes].to_sql("risco_pre_jogo", conn, if_exists="replace", index=False)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_risco_partida ON risco_pre_jogo(temporada, partida_id);")
                if "atleta_pseudonimo" in presentes:
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_risco_atleta ON risco_pre_jogo(atleta_pseudonimo);")
                # A ressalva viaja junto com o dado: quem consome a tabela ve o aviso.
                pd.DataFrame([{"chave": "aviso_interpretativo", "valor": AVISO_INTERPRETATIVO}]).to_sql(
                    "avisos", conn, if_exists="replace", index=False)

            conn.commit()
            logger.info(
                "SQLite atualizado: %d partidas, %d gols, %d cartões, %d linhas de classificação, "
                "%d registros de escalação, %d de minutos em campo.",
                len(df_all_p), len(df_all_g), len(df_all_c), len(df_all_std),
                len(df_all_e), len(df_all_m)
            )
        finally:
            conn.close()


if __name__ == "__main__":
    server = ProductFeedServer()
    server.generate_all_feeds()
