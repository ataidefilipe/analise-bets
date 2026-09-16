"""
src/pipeline/run_delta_pipeline.py
---------------------------------
Orquestrador mestre do Pipeline Delta CBF D+1.
Executa a esteira ponta a ponta:
1. CBFDeltaIngestor: detecção incremental via HTTP HEAD e download de novas/alteradas súmulas.
2. CBFDeltaProcessor: parsing canônico e Upsert idempotente nas bases Parquet/CSV.
3. ProductFeedServer: geração de feeds JSON e atualização do banco SQLite para o produto.
4. Geração de sumário de auditoria e métricas de execução.
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.cleaning.cbf_delta_processor import CBFDeltaProcessor
from src.ingestion.cbf_delta_updater import CBFDeltaIngestor
from src.pipeline.serve_product_feed import ProductFeedServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CBFDeltaPipeline")


class CBFDeltaPipeline:
    def __init__(
        self,
        raw_base: Optional[Path] = None,
        processed_base: Optional[Path] = None,
        feed_base: Optional[Path] = None,
    ):
        self.raw_base = Path(raw_base) if raw_base else Path("data/raw/cbf")
        self.processed_base = Path(processed_base) if processed_base else Path("data/processed")
        self.feed_base = Path(feed_base) if feed_base else Path("data/processed/product_feed")

        self.ingestor = CBFDeltaIngestor(base_dir=self.raw_base)
        self.processor = CBFDeltaProcessor(processed_base=self.processed_base)
        self.feed_server = ProductFeedServer(processed_dir=self.processed_base, feed_dir=self.feed_base)

    def run(
        self,
        ano: int = 2024,
        series: List[str] = ["A", "B"],
        match_start: int = 1,
        match_end: int = 380,
        rolling_days: int = 7,
        force_recheck: bool = False,
        skip_ingest: bool = False,
        skip_feed: bool = False,
    ) -> Dict[str, Any]:
        start_time = time.time()
        logger.info("=" * 70)
        logger.info("INICIANDO EXECUÇÃO DO PIPELINE DELTA CBF (D+1)")
        logger.info("Temporada: %d | Séries: %s | Partidas: %d a %d", ano, series, match_start, match_end)
        logger.info("=" * 70)

        pipeline_report: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "temporada": ano,
            "series": series,
            "etapas": {},
            "resumo": {
                "novos_downloads": 0,
                "downloads_atualizados": 0,
                "partidas_upserted": 0,
                "gols_upserted": 0,
                "cartoes_upserted": 0,
            },
            "sucesso": True,
            "duracao_segundos": 0.0,
        }

        all_updated_files: Dict[str, List[Path]] = {}

        # 1. INGESTÃO DELTA
        if not skip_ingest:
            for s in series:
                s_upper = s.upper().strip()
                logger.info(">>> [ETAPA 1/3] Sincronizando Delta Súmulas - Série %s / %d...", s_upper, ano)
                try:
                    ingest_res = self.ingestor.sync_season_serie(
                        ano=ano,
                        serie=s_upper,
                        match_start=match_start,
                        match_end=match_end,
                        rolling_days=rolling_days,
                        force_recheck=force_recheck,
                    )
                    # Serializar caminhos para evitar erro de JSON com Path
                    ingest_res_clean = {
                        k: ([str(p) for p in v] if k == "updated_files" else v)
                        for k, v in ingest_res.items()
                    }
                    pipeline_report["etapas"][f"ingestao_serie_{s_upper}"] = ingest_res_clean
                    pipeline_report["resumo"]["novos_downloads"] += ingest_res["new_downloads"]
                    pipeline_report["resumo"]["downloads_atualizados"] += ingest_res["updated_downloads"]
                    all_updated_files[s_upper] = ingest_res.get("updated_files", [])
                except Exception as e:
                    logger.error("Erro na ingestão da Série %s: %s", s_upper, e)
                    pipeline_report["etapas"][f"ingestao_serie_{s_upper}"] = {"erro": str(e)}
                    pipeline_report["sucesso"] = False
        else:
            logger.info("Ingestão ignorada (--skip-ingest).")

        # 2. PROCESSAMENTO E UPSERT IDEMPOTENTE
        for s in series:
            s_upper = s.upper().strip()
            files_to_process = all_updated_files.get(s_upper, [])

            if not files_to_process:
                raw_season_dir = self.raw_base / f"sumulas_serie_{s_upper.lower()}_{ano}"
                if raw_season_dir.exists():
                    existing_pdfs = sorted(list(raw_season_dir.glob("*.pdf")))
                    if existing_pdfs:
                        files_to_process = [
                            p for p in existing_pdfs
                            if match_start <= int(p.stem.replace("se", "")[3:]) <= match_end
                        ]

            if files_to_process:
                logger.info(">>> [ETAPA 2/3] Processando e Upserting %d súmulas - Série %s / %d...", len(files_to_process), s_upper, ano)
                try:
                    proc_res = self.processor.process_and_upsert(
                        pdf_paths=files_to_process,
                        temporada=ano,
                        serie=s_upper,
                    )
                    pipeline_report["etapas"][f"processamento_serie_{s_upper}"] = proc_res
                    pipeline_report["resumo"]["partidas_upserted"] += proc_res.get("matches_upserted", 0)
                    pipeline_report["resumo"]["gols_upserted"] += proc_res.get("goals_upserted", 0)
                    pipeline_report["resumo"]["cartoes_upserted"] += proc_res.get("cards_upserted", 0)
                except Exception as e:
                    logger.error("Erro no processamento da Série %s: %s", s_upper, e)
                    pipeline_report["etapas"][f"processamento_serie_{s_upper}"] = {"erro": str(e)}
                    pipeline_report["sucesso"] = False
            else:
                logger.info("Nenhuma súmula pendente de processamento para Série %s / %d.", s_upper, ano)

        # 3. GERAÇÃO DE FEEDS DO PRODUTO (JSON + SQLITE)
        if not skip_feed:
            logger.info(">>> [ETAPA 3/3] Atualizando Feeds de Produto (JSON + SQLite)...")
            try:
                feed_res = self.feed_server.generate_all_feeds(target_season=ano)
                pipeline_report["etapas"]["feeds_produto"] = feed_res
            except Exception as e:
                logger.error("Erro na geração de feeds do produto: %s", e)
                pipeline_report["etapas"]["feeds_produto"] = {"erro": str(e)}
                pipeline_report["sucesso"] = False
        else:
            logger.info("Geração de feeds ignorada (--skip-feed).")

        pipeline_report["duracao_segundos"] = round(time.time() - start_time, 2)

        # Salvar relatório de auditoria
        audit_path = self.processed_base / "delta_pipeline_last_run.json"
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(pipeline_report, f, indent=2, ensure_ascii=False)

        logger.info("=" * 70)
        logger.info(
            "PIPELINE DELTA FINALIZADO EM %.2f segundos (Sucesso: %s)",
            pipeline_report["duracao_segundos"], pipeline_report["sucesso"]
        )
        logger.info(
            "Resumo: %d downloads novos, %d partidas upserted, %d gols, %d cartões.",
            pipeline_report["resumo"]["novos_downloads"],
            pipeline_report["resumo"]["partidas_upserted"],
            pipeline_report["resumo"]["gols_upserted"],
            pipeline_report["resumo"]["cartoes_upserted"],
        )
        logger.info("Relatório de auditoria salvo em: %s", audit_path)
        logger.info("=" * 70)

        return pipeline_report


def main():
    parser = argparse.ArgumentParser(description="Pipeline Delta CBF D+1")
    parser.add_argument("--ano", type=int, default=2024, help="Temporada (ex: 2024)")
    parser.add_argument("--series", type=str, default="A,B", help="Séries separadas por vírgula (ex: A,B)")
    parser.add_argument("--inicio", type=int, default=1, help="Partida inicial (1-380)")
    parser.add_argument("--fim", type=int, default=380, help="Partida final (1-380)")
    parser.add_argument("--rolling-days", type=int, default=7, help="Janela móvel de segurança em dias")
    parser.add_argument("--force-recheck", action="store_true", help="Forçar rechecagem de todos os jogos")
    parser.add_argument("--skip-ingest", action="store_true", help="Pular etapa de ingestão")
    parser.add_argument("--skip-feed", action="store_true", help="Pular geração de feeds")
    args = parser.parse_args()

    series_list = [s.strip().upper() for s in args.series.split(",") if s.strip()]
    pipeline = CBFDeltaPipeline()
    report = pipeline.run(
        ano=args.ano,
        series=series_list,
        match_start=args.inicio,
        match_end=args.fim,
        rolling_days=args.rolling_days,
        force_recheck=args.force_recheck,
        skip_ingest=args.skip_ingest,
        skip_feed=args.skip_feed,
    )

    if not report["sucesso"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
