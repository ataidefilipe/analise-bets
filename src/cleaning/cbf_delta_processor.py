"""
src/cleaning/cbf_delta_processor.py
----------------------------------
Processador incremental (Delta) e Upsert Idempotente para Súmulas CBF.
Lê PDFs baixados pelo Ingestor Delta, extrai metadados, gols e cartões,
e realiza o Upsert (Merge) nas bases consolidadas de Série A e Série B.

Garante:
- Extração canônica do placar oficial via cabeçalho 'Resultado Final: X X Y'.
- Extração precisa de gols individuais e cartões disciplinares.
- Semântica correta para gols contra (atribuídos ao placar do adversário).
- Categorização textual do motivo de cartões disciplinares.
- Alinhamento de tipos (Int64, float, string) com tolerância a não-numéricos (ex: camisa de comissão técnica 'AT').
- Idempotência: rodar múltiplas vezes sobre a mesma partida atualiza os registros sem gerar duplicatas.
- Compatibilidade com formatos Parquet e CSV existentes.
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
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CBFDeltaProcessor")


def slugify(text: Optional[str]) -> str:
    if pd.isna(text) or text is None:
        return ""
    text = str(text).strip()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text.lower()


def categorize_card_reason(motivo: str) -> str:
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


def parse_single_cbf_pdf(
    filepath: Path,
    temporada_default: int = 2024,
    serie_default: str = "A"
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
        "saldo_mandante": 0,
        "resultado": "Empate",
        "vencedor": "-",
        "arena": "",
        "formacao_mandante": None,
        "formacao_visitante": None,
        "tecnico_mandante": None,
        "tecnico_visitante": None,
    }

    file_stem = filepath.stem.replace("se", "")
    match_digits = re.search(r"^\d{3}(\d+)$", file_stem)
    if match_digits:
        meta["partida_id"] = int(match_digits.group(1))

    score_mandante_official: Optional[int] = None
    score_visitante_official: Optional[int] = None

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
                meta["arena"] = e_parts[0]
                meta["cidade"] = e_parts[1]
            else:
                meta["estadio"] = est_raw
                meta["arena"] = est_raw
        elif t == "Arbitro:" and i + 1 < len(tokens):
            meta["arbitro"] = tokens[i + 1].split("(")[0].strip()
        elif "Resultado Final:" in t:
            match_res = re.search(r"Resultado Final:\s*(\d+)\s*[xX]\s*(\d+)", t)
            if match_res:
                score_mandante_official = int(match_res.group(1))
                score_visitante_official = int(match_res.group(2))

    idx_gols = -1
    idx_yellow = -1
    idx_red = -1
    idx_sub = len(tokens)

    for i, t in enumerate(tokens):
        if t == "Gols" and idx_gols == -1:
            idx_gols = i
        elif "Amarelo" in t and idx_yellow == -1 and not t.startswith("2"):
            idx_yellow = i
        elif "Vermelho" in t and idx_red == -1:
            idx_red = i
        elif "Substitui" in t and idx_sub == len(tokens):
            idx_sub = i

    time_regex = re.compile(r"^(\+|\d{1,2}:)\d{1,2}(?::\d{2})?$|^\+\d{1,2}$")

    # Extração de Gols
    gols_list: List[Dict[str, Any]] = []
    if idx_gols != -1:
        end_g = idx_yellow if idx_yellow != -1 else (idx_red if idx_red != -1 else idx_sub)
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

    if score_mandante_official is not None and score_visitante_official is not None:
        gm = score_mandante_official
        gv = score_visitante_official
    elif gols_list:
        gm = 0
        gv = 0
        m_slug = meta["clube_mandante_slug"]
        for g in gols_list:
            is_own_goal = (g["tipo_de_gol"] == "Gol Contra")
            scorer_is_mandante = (g["clube_slug"] == m_slug)
            if is_own_goal:
                if scorer_is_mandante:
                    gv += 1
                else:
                    gm += 1
            else:
                if scorer_is_mandante:
                    gm += 1
                else:
                    gv += 1
    else:
        gm = 0
        gv = 0

    meta["gols_mandante"] = gm
    meta["gols_visitante"] = gv
    meta["total_gols"] = gm + gv
    meta["saldo_mandante"] = gm - gv

    if gm > gv:
        meta["resultado"] = "Vitoria Mandante"
        meta["vencedor"] = meta["clube_mandante"]
    elif gv > gm:
        meta["resultado"] = "Vitoria Visitante"
        meta["vencedor"] = meta["clube_visitante"]
    else:
        meta["resultado"] = "Empate"
        meta["vencedor"] = "-"

    # Extração de Cartões
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
                        and not sec_tokens[k].startswith("2")
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


def align_dataframe_types(df_new: pd.DataFrame, df_existing: pd.DataFrame) -> pd.DataFrame:
    """
    Alinha o schema e os dtypes de df_new para corresponder perfeitamente a df_existing,
    convertendo tipos com segurança (ex: strings numéricas para Int64 com suporte a NaN).
    """
    target_cols = list(df_existing.columns)
    aligned_df = df_new.copy()

    for col in target_cols:
        if col not in aligned_df.columns:
            aligned_df[col] = None
        else:
            target_dtype = df_existing[col].dtype
            if pd.api.types.is_integer_dtype(target_dtype):
                aligned_df[col] = pd.to_numeric(aligned_df[col], errors="coerce").astype(target_dtype)
            elif pd.api.types.is_float_dtype(target_dtype):
                aligned_df[col] = pd.to_numeric(aligned_df[col], errors="coerce").astype(target_dtype)

    return aligned_df[target_cols]


class CBFDeltaProcessor:
    def __init__(self, processed_base: Optional[Path] = None):
        self.processed_base = Path(processed_base) if processed_base else Path("data/processed")

    def _get_serie_dir(self, serie: str) -> Path:
        s_clean = serie.lower().strip()
        p = self.processed_base / f"serie_{s_clean}"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def process_and_upsert(
        self,
        pdf_paths: List[Path],
        temporada: int,
        serie: str
    ) -> Dict[str, Any]:
        serie = serie.upper()
        if not pdf_paths:
            logger.info("Nenhum PDF fornecido para processamento em Série %s / %d.", serie, temporada)
            return {"matches_upserted": 0, "goals_upserted": 0, "cards_upserted": 0}

        serie_dir = self._get_serie_dir(serie)
        partidas_parquet = serie_dir / "partidas.parquet"
        partidas_csv = serie_dir / "partidas.csv"
        gols_parquet = serie_dir / "gols.parquet"
        gols_csv = serie_dir / "gols.csv"
        cartoes_parquet = serie_dir / "cartoes.parquet"
        cartoes_csv = serie_dir / "cartoes.csv"

        new_matches = []
        new_goals = []
        new_cards = []

        for p in pdf_paths:
            try:
                meta, c_list, g_list = parse_single_cbf_pdf(p, temporada_default=temporada, serie_default=serie)
                new_matches.append(meta)
                new_goals.extend(g_list)
                new_cards.extend(c_list)
            except Exception as e:
                logger.error("Erro ao processar súmula %s: %s", p.name, e)

        if not new_matches:
            return {"matches_upserted": 0, "goals_upserted": 0, "cards_upserted": 0}

        df_new_matches = pd.DataFrame(new_matches)
        df_new_goals = pd.DataFrame(new_goals) if new_goals else pd.DataFrame()
        df_new_cards = pd.DataFrame(new_cards) if new_cards else pd.DataFrame()

        partidas_upsert_ids = set(df_new_matches["partida_id"].unique())

        # 1. UPSERT PARTIDAS
        if partidas_parquet.exists():
            df_existing_p = pd.read_parquet(partidas_parquet)
            mask = ~((df_existing_p["temporada"] == temporada) & (df_existing_p["partida_id"].isin(partidas_upsert_ids)))
            df_p_filtered = df_existing_p[mask]
            df_new_matches_aligned = align_dataframe_types(df_new_matches, df_existing_p)
            df_final_p = pd.concat([df_p_filtered, df_new_matches_aligned], ignore_index=True)
        else:
            df_final_p = df_new_matches

        sort_cols = [c for c in ["temporada", "rodada", "partida_id"] if c in df_final_p.columns]
        if sort_cols:
            df_final_p = df_final_p.sort_values(sort_cols).reset_index(drop=True)

        df_final_p.to_parquet(partidas_parquet, index=False)
        df_final_p.to_csv(partidas_csv, index=False, encoding="utf-8")

        # 2. UPSERT GOLS
        if gols_parquet.exists():
            df_existing_g = pd.read_parquet(gols_parquet)
            mask_g = ~((df_existing_g["temporada"] == temporada) & (df_existing_g["partida_id"].isin(partidas_upsert_ids)))
            df_g_filtered = df_existing_g[mask_g]

            if not df_new_goals.empty:
                df_new_goals_aligned = align_dataframe_types(df_new_goals, df_existing_g)
                df_final_g = pd.concat([df_g_filtered, df_new_goals_aligned], ignore_index=True)
            else:
                df_final_g = df_g_filtered
        else:
            df_final_g = df_new_goals

        if not df_final_g.empty:
            sort_g = [c for c in ["temporada", "rodada", "partida_id", "minuto_continuo"] if c in df_final_g.columns]
            if sort_g:
                df_final_g = df_final_g.sort_values(sort_g).reset_index(drop=True)
            df_final_g.to_parquet(gols_parquet, index=False)
            df_final_g.to_csv(gols_csv, index=False, encoding="utf-8")

        # 3. UPSERT CARTÕES
        if cartoes_parquet.exists():
            df_existing_c = pd.read_parquet(cartoes_parquet)
            mask_c = ~((df_existing_c["temporada"] == temporada) & (df_existing_c["partida_id"].isin(partidas_upsert_ids)))
            df_c_filtered = df_existing_c[mask_c]

            if not df_new_cards.empty:
                df_new_cards_aligned = align_dataframe_types(df_new_cards, df_existing_c)
                df_final_c = pd.concat([df_c_filtered, df_new_cards_aligned], ignore_index=True)
            else:
                df_final_c = df_c_filtered
        else:
            df_final_c = df_new_cards

        if not df_final_c.empty:
            sort_c = [c for c in ["temporada", "rodada", "partida_id", "minuto_continuo"] if c in df_final_c.columns]
            if sort_c:
                df_final_c = df_final_c.sort_values(sort_c).reset_index(drop=True)
            df_final_c.to_parquet(cartoes_parquet, index=False)
            df_final_c.to_csv(cartoes_csv, index=False, encoding="utf-8")

        # 4. Atualizar manifesto de processamento
        manifest_path = serie_dir / "manifest_processed.json"
        manifest_data = {
            "last_updated": datetime.now().isoformat(),
            "temporadas": sorted([int(x) for x in df_final_p["temporada"].unique()]),
            "datasets": {
                "partidas": {"linhas": len(df_final_p), "colunas": df_final_p.shape[1]},
                "cartoes": {"linhas": len(df_final_c), "colunas": df_final_c.shape[1]},
                "gols": {"linhas": len(df_final_g), "colunas": df_final_g.shape[1]},
            }
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)

        logger.info(
            "Upsert concluído com sucesso para Série %s / %d: %d partidas, %d gols, %d cartões.",
            serie, temporada, len(new_matches), len(new_goals), len(new_cards)
        )

        return {
            "matches_upserted": len(new_matches),
            "goals_upserted": len(new_goals),
            "cards_upserted": len(new_cards),
            "total_partidas_dataset": len(df_final_p),
        }
