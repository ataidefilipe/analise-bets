"""
src/ingestion/cbf_delta_updater.py
---------------------------------
Ingestor incremental (Delta) de Súmulas Oficiais da CBF (PDFs).
Projetado para ambientes de produção em regime D+1:
- Utiliza requisições HTTP HEAD ultraleves para verificar disponibilidade sem baixar o corpo do arquivo.
- Compara cabeçalhos ETag e Last-Modified para identificar súmulas novas ou retificadas pela arbitragem.
- Baixa estritamente o delta (arquivos modificados ou inéditos).
- Mantém integridade com hashes SHA-256 e manifesto estruturado.
- Suporta varredura de partidas pendentes e janela de segurança móvel (rolling safety window).
"""

import argparse
import hashlib
import json
import logging
import os
import ssl
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CBFDeltaIngestor")

COMPETITION_CODES = {
    "A": 142,
    "B": 242,
    "C": 342,
    "D": 542,
}

DEFAULT_BASE_URL = "https://conteudo.cbf.com.br/sumulas"
DEFAULT_RAW_BASE = Path("data/raw/cbf")
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CBF-DataProduct/1.0"


def calculate_sha256(filepath: Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


class CBFDeltaIngestor:
    def __init__(
        self,
        base_dir: Optional[Path] = None,
        base_url: str = DEFAULT_BASE_URL,
        user_agent: str = DEFAULT_USER_AGENT,
        max_workers: int = 6,
        timeout: int = 10,
    ):
        self.base_dir = Path(base_dir) if base_dir else DEFAULT_RAW_BASE
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.max_workers = max_workers
        self.timeout = timeout

        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

        self.manifest_path = self.base_dir / "manifest_delta.json"
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning("Manifesto existente corrompido ou ilegível (%s). Criando novo.", e)
        return {
            "version": "1.0",
            "last_updated": None,
            "seasons": {}
        }

    def _save_manifest(self) -> None:
        self.manifest["last_updated"] = datetime.now().isoformat()
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)

    def get_url(self, ano: int, serie: str, match_num: int) -> str:
        code = COMPETITION_CODES[serie.upper()]
        return f"{self.base_url}/{ano}/{code}{match_num}se.pdf"

    def head_check(self, url: str) -> Tuple[int, Optional[str], Optional[str], Optional[int]]:
        """
        Executa HTTP HEAD para inspecionar status, ETag, Last-Modified e Content-Length.
        Retorna: (status_code, etag, last_modified, content_length)
        """
        req = urllib.request.Request(
            url,
            headers={"User-Agent": self.user_agent},
            method="HEAD"
        )
        try:
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=self.timeout) as resp:
                headers = resp.headers
                etag = headers.get("ETag")
                last_modified = headers.get("Last-Modified")
                c_len = headers.get("Content-Length")
                content_len = int(c_len) if c_len and c_len.isdigit() else None
                return resp.status, etag, last_modified, content_len
        except urllib.error.HTTPError as e:
            return e.code, None, None, None
        except Exception as e:
            logger.debug("Falha HEAD em %s: %s", url, e)
            return 0, None, None, None

    def download_pdf(self, url: str, target_path: Path, max_retries: int = 3) -> Optional[bytes]:
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        for attempt in range(1, max_retries + 1):
            try:
                with urllib.request.urlopen(req, context=self.ssl_context, timeout=self.timeout) as resp:
                    if resp.status == 200:
                        content = resp.read()
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(target_path, "wb") as f:
                            f.write(content)
                        return content
            except Exception as e:
                time.sleep(0.5 * attempt)
        return None

    def sync_season_serie(
        self,
        ano: int,
        serie: str,
        match_start: int = 1,
        match_end: int = 380,
        rolling_days: int = 7,
        force_recheck: bool = False,
    ) -> Dict[str, Any]:
        """
        Executa sincronização incremental de uma temporada e divisão:
        - Verifica partidas nunca baixadas até match_end.
        - Se rolling_days > 0, reavalia partidas baixadas nos últimos N dias para checar retificações.
        """
        serie = serie.upper()
        if serie not in COMPETITION_CODES:
            raise ValueError(f"Série inválida: {serie}. Permitidas: {list(COMPETITION_CODES.keys())}")

        season_key = f"{ano}_{serie}"
        if season_key not in self.manifest["seasons"]:
            self.manifest["seasons"][season_key] = {
                "ano": ano,
                "serie": serie,
                "competition_code": COMPETITION_CODES[serie],
                "matches": {}
            }

        season_manifest = self.manifest["seasons"][season_key]["matches"]
        target_dir = self.base_dir / f"sumulas_serie_{serie.lower()}_{ano}"
        target_dir.mkdir(parents=True, exist_ok=True)

        cutoff_date = datetime.now() - timedelta(days=rolling_days) if rolling_days > 0 else None

        matches_to_check: List[int] = []
        for m_num in range(match_start, match_end + 1):
            m_str = str(m_num)
            if m_str not in season_manifest or force_recheck:
                matches_to_check.append(m_num)
            elif cutoff_date:
                m_info = season_manifest[m_str]
                last_sync = m_info.get("last_checked_at") or m_info.get("downloaded_at")
                if last_sync:
                    try:
                        sync_dt = datetime.fromisoformat(last_sync)
                        if sync_dt >= cutoff_date:
                            matches_to_check.append(m_num)
                    except Exception:
                        matches_to_check.append(m_num)

        logger.info(
            "Iniciando delta Série %s / %d: %d partidas a inspecionar (de %d a %d).",
            serie, ano, len(matches_to_check), match_start, match_end
        )

        results: Dict[str, Any] = {
            "ano": ano,
            "serie": serie,
            "total_inspected": len(matches_to_check),
            "new_downloads": 0,
            "updated_downloads": 0,
            "unmodified": 0,
            "not_available_404": 0,
            "errors": 0,
            "updated_files": [],
        }

        def process_match(m_num: int) -> Tuple[int, str, Optional[Path]]:
            url = self.get_url(ano, serie, m_num)
            m_str = str(m_num)
            code = COMPETITION_CODES[serie]
            filename = f"{code}{m_num}se.pdf"
            file_path = target_dir / filename

            status, etag, last_modified, c_len = self.head_check(url)

            if status == 404:
                return m_num, "404", None
            if status != 200:
                return m_num, f"status_{status}", None

            existing_info = season_manifest.get(m_str)
            needs_download = False
            is_update = False

            if not existing_info or not file_path.exists():
                needs_download = True
            else:
                stored_etag = existing_info.get("etag")
                if etag and stored_etag and etag != stored_etag:
                    needs_download = True
                    is_update = True
                elif not stored_etag:
                    needs_download = True

            if needs_download:
                content = self.download_pdf(url, file_path)
                if content:
                    sha = calculate_sha256(file_path)
                    season_manifest[m_str] = {
                        "partida_num": m_num,
                        "filename": filename,
                        "url": url,
                        "etag": etag,
                        "last_modified": last_modified,
                        "size_bytes": len(content),
                        "sha256": sha,
                        "downloaded_at": datetime.now().isoformat(),
                        "last_checked_at": datetime.now().isoformat(),
                    }
                    return m_num, "updated" if is_update else "new", file_path
                else:
                    return m_num, "download_error", None
            else:
                season_manifest[m_str]["last_checked_at"] = datetime.now().isoformat()
                return m_num, "unmodified", file_path

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_match = {executor.submit(process_match, m): m for m in matches_to_check}
            for future in as_completed(future_to_match):
                m_num = future_to_match[future]
                try:
                    m_id, outcome, p_path = future.result()
                    if outcome == "new":
                        results["new_downloads"] += 1
                        results["updated_files"].append(p_path)
                    elif outcome == "updated":
                        results["updated_downloads"] += 1
                        results["updated_files"].append(p_path)
                    elif outcome == "unmodified":
                        results["unmodified"] += 1
                    elif outcome == "404":
                        results["not_available_404"] += 1
                    else:
                        results["errors"] += 1
                except Exception as e:
                    logger.warning("Exceção no processamento do jogo %d: %s", m_num, e)
                    results["errors"] += 1

        self._save_manifest()
        logger.info(
            "Delta Série %s / %d concluído: %d novas, %d atualizadas, %d inalteradas, %d pendentes (404), %d erros.",
            serie, ano, results["new_downloads"], results["updated_downloads"],
            results["unmodified"], results["not_available_404"], results["errors"]
        )
        return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CBF Delta Ingestor")
    parser.add_argument("--ano", type=int, default=2024, help="Ano da temporada")
    parser.add_argument("--serie", type=str, default="A", help="Divisão (A ou B)")
    parser.add_argument("--inicio", type=int, default=1, help="Partida inicial (1-380)")
    parser.add_argument("--fim", type=int, default=380, help="Partida final (1-380)")
    parser.add_argument("--rolling-days", type=int, default=7, help="Janela de rechecagem em dias")
    parser.add_argument("--force", action="store_true", help="Forçar rechecagem de todos")
    args = parser.parse_args()

    ingestor = CBFDeltaIngestor()
    ingestor.sync_season_serie(
        ano=args.ano,
        serie=args.serie,
        match_start=args.inicio,
        match_end=args.fim,
        rolling_days=args.rolling_days,
        force_recheck=args.force,
    )
