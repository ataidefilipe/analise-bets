"""
Script de ingestão para os dados brutos do Brasileirão (Adão Duque).
Repositório: https://github.com/adaoduque/Brasileirao_Dataset

Diretrizes (.agent.md):
- Preservar dados brutos intactos em data/raw/
- Registrar hashes SHA256 para reprodutibilidade e integridade
- Gerar metadados de auditoria (tamanho, linhas, colunas, cobertura temporal)
"""

import os
import json
import hashlib
import urllib.request
import pandas as pd
from datetime import datetime

BASE_URL = "https://raw.githubusercontent.com/adaoduque/Brasileirao_Dataset/master/"
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "adaoduque")

FILES = [
    "campeonato-brasileiro-full.csv",
    "campeonato-brasileiro-estatisticas-full.csv",
    "campeonato-brasileiro-cartoes.csv",
    "campeonato-brasileiro-gols.csv",
    "Legenda.txt"
]

def calculate_sha256(filepath: str) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def download_raw_files():
    os.makedirs(RAW_DIR, exist_ok=True)
    manifest = {
        "source": "https://github.com/adaoduque/Brasileirao_Dataset",
        "download_timestamp": datetime.now().isoformat(),
        "files": {}
    }
    
    print(f"[*] Iniciando download dos arquivos brutos para: {RAW_DIR}")
    for filename in FILES:
        url = BASE_URL + filename
        target_path = os.path.join(RAW_DIR, filename)
        print(f"  -> Baixando {filename}...")
        
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (DataAnalysis; BetsResearch)"})
        with urllib.request.urlopen(req) as resp, open(target_path, "wb") as out_file:
            content = resp.read()
            out_file.write(content)
        
        file_size = os.path.getsize(target_path)
        file_hash = calculate_sha256(target_path)
        manifest["files"][filename] = {
            "size_bytes": file_size,
            "sha256": file_hash,
            "url": url
        }
        print(f"     [OK] {filename} ({file_size:,} bytes | SHA256: {file_hash[:12]}...)")
    
    manifest_path = os.path.join(RAW_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[*] Manifesto de integridade salvo em: {manifest_path}")

def inspect_downloaded_data():
    print("\n" + "="*70)
    print("AUDITORIA ESTATÍSTICA INICIAL DOS DADOS BRUTOS")
    print("="*70)
    
    csv_files = [f for f in FILES if f.endswith(".csv")]
    
    for filename in csv_files:
        filepath = os.path.join(RAW_DIR, filename)
        print(f"\n--- Arquivo: {filename} ---")
        try:
            # Tentar leitura com utf-8 ou latin-1
            try:
                df = pd.read_csv(filepath, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(filepath, encoding="latin-1")
            
            print(f"Formato: {df.shape[0]:,} linhas x {df.shape[1]} colunas")
            print(f"Colunas: {list(df.columns)}")
            
            # Checagem de datas se houver coluna Data
            date_col = next((c for c in df.columns if c.lower() in ["data", "date"]), None)
            if date_col:
                # Tentar converter para datetime
                dates = pd.to_datetime(df[date_col], format="%d/%m/%Y", errors="coerce")
                if dates.isna().all():
                    dates = pd.to_datetime(df[date_col], errors="coerce")
                valid_dates = dates.dropna()
                if not valid_dates.empty:
                    print(f"Período temporal: {valid_dates.min().strftime('%d/%m/%Y')} até {valid_dates.max().strftime('%d/%m/%Y')}")
                    years = valid_dates.dt.year.value_counts().sort_index()
                    print(f"Temporadas cobertas ({len(years)} anos): {years.index.min()} a {years.index.max()}")
            
            # Checagem de nulos
            nulls = df.isnull().sum()
            high_nulls = nulls[nulls > 0]
            if not high_nulls.empty:
                print(f"Colunas com valores ausentes:")
                for col, count in high_nulls.items():
                    pct = (count / len(df)) * 100
                    print(f"  - {col}: {count:,} ({pct:.1f}%)")
            else:
                print("Nenhum valor ausente identificado.")
                
        except Exception as e:
            print(f"Erro ao auditar {filename}: {e}")

if __name__ == "__main__":
    download_raw_files()
    inspect_downloaded_data()
