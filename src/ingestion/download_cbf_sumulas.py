"""
src/ingestion/download_cbf_sumulas.py
--------------------------------------
Downloader resiliente e automatizado de Súmulas Eletrônicas da CBF (PDFs).
Cobertura: Séries A, B, C e D.
Endpoint padrão: https://conteudo.cbf.com.br/sumulas/{ano}/{codigo}{jogo_id}se.pdf

Códigos de competição oficiais CBF:
- Série A: 142
- Série B: 242
- Série C: 342
- Série D: 542
"""

import argparse
import hashlib
import json
import logging
import os
import ssl
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

COMPETITION_CODES = {
    "A": 142,
    "B": 242,
    "C": 342,
    "D": 542,
}

DEFAULT_BASE_URL = "https://conteudo.cbf.com.br/sumulas"

def calculate_sha256(filepath: Path) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def get_sumula_url(ano: int, serie: str, match_num: int, base_url: str = DEFAULT_BASE_URL) -> str:
    code = COMPETITION_CODES.get(serie.upper())
    if not code:
        raise ValueError(f"Série desconhecida: {serie}. Válidas: A, B, C, D.")
    return f"{base_url}/{ano}/{code}{match_num}se.pdf"

def download_sumulas_batch(
    ano: int,
    serie: str,
    match_start: int = 1,
    match_end: int = 380,
    dest_dir: Optional[Path] = None,
    delay_sec: float = 0.15,
    max_retries: int = 3,
) -> Tuple[int, int, Path]:
    """
    Baixa lote de súmulas da CBF preservando integridade criptográfica.
    """
    if dest_dir is None:
        dest_dir = Path("data/raw/cbf") / f"sumulas_serie_{serie.lower()}_{ano}"
    dest_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = dest_dir / "manifest.json"
    manifest: Dict = {
        "competicao": f"Campeonato Brasileiro Série {serie.upper()}",
        "ano": ano,
        "serie": serie.upper(),
        "created_at": datetime.now().isoformat(),
        "files": {},
    }
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            pass

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    headers = {"User-Agent": "Mozilla/5.0 (DataAnalysis; BetsResearch; Educational)"}

    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading

    manifest_lock = threading.Lock()
    success_count = 0
    fail_count = 0

    logger.info("Iniciando download Série %s / %d (jogos %d a %d) para: %s",
                serie.upper(), ano, match_start, match_end, dest_dir)

    def download_match(match_num: int) -> bool:
        nonlocal success_count, fail_count
        filename = f"{COMPETITION_CODES[serie.upper()]}{match_num}se.pdf"
        target_path = dest_dir / filename
        url = get_sumula_url(ano, serie, match_num)

        with manifest_lock:
            if target_path.exists() and filename in manifest.get("files", {}):
                success_count += 1
                return True

        for attempt in range(1, max_retries + 1):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
                    if resp.status == 200:
                        content = resp.read()
                        with open(target_path, "wb") as f_out:
                            f_out.write(content)
                        file_hash = calculate_sha256(target_path)
                        with manifest_lock:
                            manifest["files"][filename] = {
                                "partida_num": match_num,
                                "size_bytes": len(content),
                                "sha256": file_hash,
                                "url": url,
                                "downloaded_at": datetime.now().isoformat(),
                            }
                            success_count += 1
                        return True
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    break
                time.sleep(0.5 * attempt)
            except Exception:
                time.sleep(0.5 * attempt)

        if not target_path.exists():
            with manifest_lock:
                fail_count += 1
            return False
        return True

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(download_match, m): m for m in range(match_start, match_end + 1)}
        for future in as_completed(futures):
            m_num = futures[future]
            try:
                future.result()
            except Exception as e:
                logger.warning("Erro no download do jogo %d: %s", m_num, e)

    manifest["total_sucesso"] = success_count
    manifest["total_falhas"] = fail_count
    manifest["updated_at"] = datetime.now().isoformat()
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info("Concluído: %d súmulas salvas com manifesto em %s", success_count, manifest_path)
    return success_count, fail_count, dest_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downloader de Súmulas CBF")
    parser.add_argument("--ano", type=int, default=2022, help="Ano da temporada (ex: 2022)")
    parser.add_argument("--serie", type=str, default="B", help="Divisão (A, B, C, D)")
    parser.add_argument("--inicio", type=int, default=1, help="Número do jogo inicial")
    parser.add_argument("--fim", type=int, default=380, help="Número do jogo final")
    parser.add_argument("--delay", type=float, default=0.15, help="Delay em segundos entre requisições")
    args = parser.parse_args()

    download_sumulas_batch(
        ano=args.ano,
        serie=args.serie,
        match_start=args.inicio,
        match_end=args.fim,
        delay_sec=args.delay,
    )
