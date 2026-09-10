"""
src/cleaning/parse_cbf_sumulas.py
---------------------------------
Parser robusto e de alta precisão para Súmulas Eletrônicas da CBF (PDFs).
Processa sem dependências externas pesadas (utilizando zlib nativo) os relatórios
de arbitragem das divisões do futebol brasileiro (Séries A, B, C e D).

Gera 3 datasets estruturados:
1. partidas_cbf: metadados, equipes, placar, arbitragem, estádio
2. cartoes_cbf: minuto contínuo, atleta, posição, tipo (amarelo/vermelho) e MOTIVO textual
3. gols_cbf: minuto, atleta, equipe e tipo (normal, pênalti, contra, falta)
"""

import json
import logging
import re
import unicodedata
import zlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def slugify(text: Optional[str]) -> str:
    if pd.isna(text) or text is None:
        return ""
    text = str(text).strip()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text.lower()


def categorize_card_reason(motivo: str) -> str:
    """
    Classifica a motivação da advertência disciplinar:
    - falta_temeraria: disputa de bola, calço, rasteira, tranco
    - reclamacao: desaprovar decisões, palavras ou gestos contra arbitragem
    - cera_retardar: atrasar reinício, chutar bola para longe, demorar para sair
    - conduta_antidesportiva: discussão, provocação, empurrão sem bola, tirar camisa
    - mao_intencional: toque de mão deliberado
    - outro: demais ocorrências
    """
    m = motivo.lower()
    if any(k in m for k in ["reclam", "desaprov", "gestos", "palavras"]):
        return "reclamacao"
    elif any(k in m for k in ["retardar", "cera", "rein", "demorar", "atrasar"]):
        return "cera_retardar"
    elif any(k in m for k in ["calco", "calço", "rasteira", "temeraria", "temerária", "disputa da bola", "tranco"]):
        return "falta_temeraria"
    elif any(k in m for k in ["mao", "mão", "tocar a bola com a mao"]):
        return "mao_intencional"
    elif any(k in m for k in ["antidesp", "discuss", "provoc", "camisa", "comemorar"]):
        return "conduta_antidesportiva"
    return "outro"


def extract_tokens_from_pdf(filepath: Path) -> List[str]:
    with open(filepath, "rb") as f:
        data = f.read()

    stream_regex = re.compile(rb"stream[\r\n]+(.*?)[\r\n]+endstream", re.DOTALL)
    decompressed_parts = []
    for m in stream_regex.finditer(data):
        try:
            dec = zlib.decompress(m.group(1))
            decompressed_parts.append(dec.decode("latin1", errors="ignore"))
        except Exception:
            pass

    full_text = "\n".join(decompressed_parts)
    raw_tokens = re.findall(r"\((.*?)\)", full_text)
    cleaned = []
    for t in raw_tokens:
        t = t.replace(r"\(", "(").replace(r"\)", ")").strip()
        if t:
            cleaned.append(t)
    return cleaned


def parse_sumula_time(time_str: str, periodo: str) -> Tuple[int, int, int]:
    """
    Retorna (minuto_nominal, acrescimo, minuto_continuo).
    - Se '29:00' e '1T' -> (29, 0, 29)
    - Se '29:00' e '2T' -> (29, 0, 74)
    - Se '+02:00' e '1T' -> (45, 2, 47)
    - Se '+04:00' e '2T' -> (90, 4, 94)
    """
    time_str = time_str.strip()
    if time_str.startswith("+"):
        clean_str = time_str.replace("+", "")
        try:
            acr = int(clean_str.split(":")[0])
        except ValueError:
            acr = 0
        if periodo == "1T":
            return (45, acr, 45 + acr)
        else:
            return (90, acr, 90 + acr)
    else:
        try:
            nom = int(time_str.split(":")[0])
        except ValueError:
            nom = 0
        if periodo == "1T":
            return (nom, 0, nom)
        else:
            return (nom, 0, nom + 45)


def parse_single_sumula(
    filepath: Path,
    temporada_default: int = 2022,
    serie_default: str = "B"
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    tokens = extract_tokens_from_pdf(filepath)

    meta: Dict[str, Any] = {
        "partida_id": 0,
        "temporada": temporada_default,
        "serie": serie_default.upper(),
        "rodada": 0,
        "data": "",
        "horario": "",
        "estadio": "",
        "cidade": "",
        "uf_estadio": "",
        "clube_mandante": "",
        "clube_mandante_slug": "",
        "mandante_uf": "",
        "clube_visitante": "",
        "clube_visitante_slug": "",
        "visitante_uf": "",
        "arbitro": "",
        "gols_mandante": 0,
        "gols_visitante": 0,
        "total_gols": 0,
        "resultado": "Empate",
    }

    # Extrair ID numérico do arquivo (ex: 2421se.pdf -> 1)
    file_stem = filepath.stem.replace("se", "")
    match_digits = re.search(r"^\d{3}(\d+)$", file_stem)
    if match_digits:
        meta["partida_id"] = int(match_digits.group(1))

    for i, t in enumerate(tokens):
        if t == "Jogo:" and i + 1 < len(tokens):
            if "X" in tokens[i + 1]:
                confronto = tokens[i + 1]
                parts = confronto.split(" X ")
                if len(parts) == 2:
                    m_raw = parts[0].strip()
                    v_raw = parts[1].strip()
                    m_split = [p.strip() for p in re.split(r"[\/\-]", m_raw) if p.strip()]
                    v_split = [p.strip() for p in re.split(r"[\/\-]", v_raw) if p.strip()]
                    meta["clube_mandante"] = m_split[0] if m_split else m_raw
                    meta["mandante_uf"] = m_split[1] if len(m_split) > 1 else ""
                    meta["clube_visitante"] = v_split[0] if v_split else v_raw
                    meta["visitante_uf"] = v_split[1] if len(v_split) > 1 else ""
                    meta["clube_mandante_slug"] = slugify(meta["clube_mandante"])
                    meta["clube_visitante_slug"] = slugify(meta["clube_visitante"])
        elif t == "Rodada:" and i + 1 < len(tokens):
            if tokens[i + 1].isdigit():
                meta["rodada"] = int(tokens[i + 1])
        elif t == "Data:" and i + 1 < len(tokens):
            d_raw = tokens[i + 1]
            if re.match(r"^\d{2}/\d{2}/\d{4}$", d_raw):
                d_parts = d_raw.split("/")
                meta["data"] = f"{d_parts[2]}-{d_parts[1]}-{d_parts[0]}"
        elif (t == "Horário:" or t.startswith("Hor")) and i + 1 < len(tokens):
            if re.match(r"^\d{2}:\d{2}$", tokens[i + 1]):
                meta["horario"] = tokens[i + 1]
        elif (t == "Estádio:" or t.startswith("Est")) and i + 1 < len(tokens):
            est_raw = tokens[i + 1]
            if "/" in est_raw:
                e_parts = [p.strip() for p in est_raw.split("/")]
                meta["estadio"] = e_parts[0]
                meta["cidade"] = e_parts[1]
            else:
                meta["estadio"] = est_raw
        elif t == "Arbitro:" and i + 1 < len(tokens):
            meta["arbitro"] = tokens[i + 1].split("(")[0].strip()

    # Identificar blocos de Gols e Cartões
    idx_gols = -1
    idx_yellow = -1
    idx_red = -1
    idx_sub = len(tokens)

    for i, t in enumerate(tokens):
        if t == "Gols":
            idx_gols = i
        elif "Cart" in t and "Amarelo" in t:
            idx_yellow = i
        elif "Cart" in t and "Vermelho" in t:
            idx_red = i
        elif "Substitui" in t:
            idx_sub = i

    time_regex = re.compile(r"^(\+|\d{1,2}:)\d{1,2}(?::\d{2})?$|^\+\d{1,2}$")

    # Parsing de Gols
    gols_list: List[Dict[str, Any]] = []
    if idx_gols != -1:
        end_g = idx_yellow if idx_yellow != -1 else idx_sub
        g_tokens = tokens[idx_gols:end_g]
        for j, tok in enumerate(g_tokens):
            if time_regex.match(tok):
                if j + 1 < len(g_tokens) and g_tokens[j + 1] in ["1T", "2T"]:
                    periodo = g_tokens[j + 1]
                    min_nom, acr, min_cont = parse_sumula_time(tok, periodo)
                    num_camisa = g_tokens[j + 2] if j + 2 < len(g_tokens) else ""
                    tipo_gol_raw = g_tokens[j + 3] if j + 3 < len(g_tokens) else "NR"
                    atleta = g_tokens[j + 4] if j + 4 < len(g_tokens) else "Nao Informado"
                    clube_raw = g_tokens[j + 5] if j + 5 < len(g_tokens) else ""
                    clube_nome = clube_raw.split("/")[0].strip()

                    tipo_map = {
                        "NR": "Normal",
                        "PN": "Penalty",
                        "CT": "Gol Contra",
                        "FT": "Falta"
                    }
                    tipo_gol = tipo_map.get(tipo_gol_raw, "Normal")

                    gols_list.append({
                        "partida_id": meta["partida_id"],
                        "temporada": meta["temporada"],
                        "serie": meta["serie"],
                        "rodada": meta["rodada"],
                        "clube": clube_nome,
                        "clube_slug": slugify(clube_nome),
                        "atleta": atleta,
                        "atleta_slug": slugify(atleta),
                        "num_camisa": num_camisa,
                        "minuto_nominal": min_nom,
                        "acrescimo": acr,
                        "minuto_continuo": min_cont,
                        "periodo": periodo,
                        "tipo_de_gol": tipo_gol,
                    })

    if gols_list:
        meta["total_gols"] = len(gols_list)
        gm = 0
        gv = 0
        m_slug = meta["clube_mandante_slug"]
        v_slug = meta["clube_visitante_slug"]
        for g in gols_list:
            if g["clube_slug"] == m_slug:
                gm += 1
            elif g["clube_slug"] == v_slug:
                gv += 1
        meta["gols_mandante"] = gm
        meta["gols_visitante"] = gv
        if gm > gv:
            meta["resultado"] = "Vitoria Mandante"
        elif gv > gm:
            meta["resultado"] = "Vitoria Visitante"
        else:
            meta["resultado"] = "Empate"

    # Parsing de Cartões
    cards_list: List[Dict[str, Any]] = []

    def parse_card_section(sec_tokens: List[str], card_type: str):
        for j, tok in enumerate(sec_tokens):
            if time_regex.match(tok):
                if j + 1 < len(sec_tokens) and sec_tokens[j + 1] in ["1T", "2T"]:
                    periodo = sec_tokens[j + 1]
                    min_nom, acr, min_cont = parse_sumula_time(tok, periodo)
                    num_camisa = sec_tokens[j + 2] if j + 2 < len(sec_tokens) else ""
                    atleta = sec_tokens[j + 3] if j + 3 < len(sec_tokens) else "Nao Informado"
                    clube_raw = sec_tokens[j + 4] if j + 4 < len(sec_tokens) else ""
                    clube_nome = clube_raw.split("/")[0].strip()

                    motivo_parts = []
                    k = j + 5
                    while (
                        k < len(sec_tokens)
                        and not time_regex.match(sec_tokens[k])
                        and not sec_tokens[k].startswith("TC -")
                        and not sec_tokens[k].startswith("Cart")
                        and not sec_tokens[k].startswith("Substitui")
                    ):
                        motivo_parts.append(sec_tokens[k])
                        k += 1
                    motivo_full = " ".join(motivo_parts).replace("Motivo: ", "").strip()

                    cards_list.append({
                        "partida_id": meta["partida_id"],
                        "temporada": meta["temporada"],
                        "serie": meta["serie"],
                        "rodada": meta["rodada"],
                        "clube": clube_nome,
                        "clube_slug": slugify(clube_nome),
                        "cartao": card_type,
                        "atleta": atleta,
                        "atleta_slug": slugify(atleta),
                        "num_camisa": num_camisa,
                        "minuto_nominal": min_nom,
                        "acrescimo": acr,
                        "minuto_continuo": min_cont,
                        "periodo": periodo,
                        "motivo_completo": motivo_full,
                        "categoria_infracao": categorize_card_reason(motivo_full),
                    })

    if idx_yellow != -1:
        end_y = idx_red if idx_red != -1 else idx_sub
        parse_card_section(tokens[idx_yellow:end_y], "Amarelo")

    if idx_red != -1:
        parse_card_section(tokens[idx_red:idx_sub], "Vermelho")

    return meta, cards_list, gols_list


def parse_seasons(
    season_dirs: List[Tuple[Path, int, str]],
    output_dir: Path = Path("data/processed/serie_b")
) -> Dict[str, Any]:
    from concurrent.futures import ThreadPoolExecutor

    output_dir.mkdir(parents=True, exist_ok=True)
    all_matches: List[Dict[str, Any]] = []
    all_cards: List[Dict[str, Any]] = []
    all_goals: List[Dict[str, Any]] = []

    for raw_dir, ano, serie in season_dirs:
        pdf_files = sorted(list(raw_dir.glob("*.pdf")))
        logger.info("Processando %d súmulas da Série %s / %d em %s...", len(pdf_files), serie, ano, raw_dir)

        def worker(p: Path):
            return parse_single_sumula(p, temporada_default=ano, serie_default=serie)

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(worker, pdf_files))

        for m, c, g in results:
            all_matches.append(m)
            all_cards.extend(c)
            all_goals.extend(g)

    df_matches = pd.DataFrame(all_matches).sort_values(["temporada", "rodada", "partida_id"])
    df_cards = pd.DataFrame(all_cards).sort_values(["temporada", "partida_id", "minuto_continuo"])
    df_goals = pd.DataFrame(all_goals).sort_values(["temporada", "partida_id", "minuto_continuo"])

    datasets = {
        "partidas": df_matches,
        "cartoes": df_cards,
        "gols": df_goals,
    }

    manifest: Dict[str, Any] = {
        "created_at": datetime.now().isoformat(),
        "temporadas": sorted(list(set(m["temporada"] for m in all_matches))),
        "datasets": {}
    }

    for name, df in datasets.items():
        csv_path = output_dir / f"{name}.csv"
        parquet_path = output_dir / f"{name}.parquet"

        df.to_csv(csv_path, index=False, encoding="utf-8")
        df.to_parquet(parquet_path, index=False, engine="pyarrow")

        manifest["datasets"][name] = {
            "linhas": len(df),
            "colunas": len(df.columns),
            "csv_bytes": csv_path.stat().st_size,
            "parquet_bytes": parquet_path.stat().st_size,
        }
        logger.info("[%s] %d linhas salvas.", name, len(df))

    manifest_path = output_dir / "manifest_processed.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info("Parsing completo concluído com sucesso: %s", manifest_path)
    return manifest


if __name__ == "__main__":
    seasons = [
        (Path("data/raw/cbf/sumulas_serie_b_2022"), 2022, "B"),
        (Path("data/raw/cbf/sumulas_serie_b_2023"), 2023, "B"),
    ]
    out = Path("data/processed/serie_b")
    parse_seasons(seasons, out)
