"""
Script de ingestão para os dados brutos de scouts da Série A 2024 via Sofascore.
Repositório de origem: https://github.com/leeofernandes1980/brasileirao-dataset

Diretrizes (.agent.md):
- Preservar dados brutos intactos em data/raw/sofascore/
- Registrar hashes SHA256 para reprodutibilidade e integridade
- Gerar metadados de auditoria (tamanho, linhas, colunas, faltas totais)
"""

import hashlib
import json
import logging
import os
import ssl
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "sofascore"
BASE_URL = "https://raw.githubusercontent.com/leeofernandes1980/brasileirao-dataset/master/datalake/silver/"

FILES = [
    "estatisticas.parquet",
    "partidas.parquet"
]

def calculate_sha256(filepath: Path) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def download_raw_sofascore_files() -> Dict[str, Dict]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "source": "https://github.com/leeofernandes1980/brasileirao-dataset",
        "provider": "Sofascore Public API",
        "download_timestamp": datetime.now().isoformat(),
        "files": {}
    }

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    logger.info("Iniciando download dos arquivos brutos do Sofascore para: %s", RAW_DIR)
    for filename in FILES:
        url = BASE_URL + filename
        target_path = RAW_DIR / filename
        logger.info("Baixando %s...", filename)

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (DataAnalysis; BetsResearch)"})
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp, open(target_path, "wb") as out_file:
            content = resp.read()
            out_file.write(content)

        file_size = target_path.stat().st_size
        file_hash = calculate_sha256(target_path)
        manifest["files"][filename] = {
            "size_bytes": file_size,
            "sha256": file_hash,
            "url": url
        }
        logger.info("[OK] %s (%d bytes | SHA256: %s...)", filename, file_size, file_hash[:12])

    manifest_path = RAW_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info("Manifesto salvo em: %s", manifest_path)
    return manifest

def audit_sofascore_2024():
    logger.info("Executando auditoria estatística dos dados 2024...")
    stats_path = RAW_DIR / "estatisticas.parquet"
    partidas_path = RAW_DIR / "partidas.parquet"

    df_stats = pd.read_parquet(stats_path)
    df_partidas = pd.read_parquet(partidas_path)

    stats_2024 = df_stats[df_stats["temporada"] == 2024]
    partidas_2024 = df_partidas[df_partidas["temporada"] == 2024]

    logger.info("Partidas 2024 no dataset Sofascore: %d", len(partidas_2024))
    logger.info("Registros de scouts 2024 no dataset Sofascore: %d", len(stats_2024))
    logger.info("Soma de faltas 2024: %d", stats_2024["faltas"].sum())
    logger.info("Soma de escanteios 2024: %d", stats_2024["escanteios"].sum())
    logger.info("Média de faltas por registro de clube: %.2f", stats_2024["faltas"].mean())
    logger.info("Média estimada de faltas por partida: %.2f", stats_2024["faltas"].mean() * 2)

if __name__ == "__main__":
    download_raw_sofascore_files()
    audit_sofascore_2024()
