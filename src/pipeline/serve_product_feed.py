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

FEED_DIR = Path("data/processed/product_feed")
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

            df_p = pd.read_parquet(p_file) if p_file.exists() else pd.DataFrame()
            df_g = pd.read_parquet(g_file) if g_file.exists() else pd.DataFrame()
            df_c = pd.read_parquet(c_file) if c_file.exists() else pd.DataFrame()

            if not df_p.empty and "serie" not in df_p.columns:
                df_p["serie"] = serie_label
            if not df_g.empty and "serie" not in df_g.columns:
                df_g["serie"] = serie_label
            if not df_c.empty and "serie" not in df_c.columns:
                df_c["serie"] = serie_label

            series_data[serie_label] = {
                "partidas": df_p,
                "gols": df_g,
                "cartoes": df_c,
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

        # 3. Exportar para SQLite com tabelas e índices otimizados
        self._export_to_sqlite(series_data, all_standings_rows)

        feed_stats = {
            "json_classificacao": str(classificacao_path),
            "json_latest_matches": str(latest_path),
            "sqlite_db": str(self.db_path),
            "total_tabelas_classificacao": len(classificacao_payload["tabelas"]),
        }
        logger.info("Feeds de produto gerados com sucesso: %s", feed_stats)
        return feed_stats

    def _export_to_sqlite(
        self,
        series_data: Dict[str, Dict[str, pd.DataFrame]],
        all_standings_rows: List[Dict[str, Any]]
    ) -> None:
        """
        Exporta os dados consolidados para SQLite, ativando modo WAL e criando índices.
        """
        logger.info("Exportando dados consolidados para SQLite em %s...", self.db_path)
        all_partidas = []
        all_gols = []
        all_cartoes = []

        for s_label, dsets in series_data.items():
            if not dsets["partidas"].empty:
                all_partidas.append(dsets["partidas"])
            if not dsets["gols"].empty:
                all_gols.append(dsets["gols"])
            if not dsets["cartoes"].empty:
                all_cartoes.append(dsets["cartoes"])

        df_all_p = pd.concat(all_partidas, ignore_index=True) if all_partidas else pd.DataFrame()
        df_all_g = pd.concat(all_gols, ignore_index=True) if all_gols else pd.DataFrame()
        df_all_c = pd.concat(all_cartoes, ignore_index=True) if all_cartoes else pd.DataFrame()
        df_all_std = pd.DataFrame(all_standings_rows) if all_standings_rows else pd.DataFrame()

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

            conn.commit()
            logger.info(
                "SQLite atualizado com sucesso: %d partidas, %d gols, %d cartões, %d linhas de classificação.",
                len(df_all_p), len(df_all_g), len(df_all_c), len(df_all_std)
            )
        finally:
            conn.close()


if __name__ == "__main__":
    server = ProductFeedServer()
    server.generate_all_feeds()
