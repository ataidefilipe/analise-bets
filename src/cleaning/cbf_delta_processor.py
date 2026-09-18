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
                    nome_raw = sec_tokens[j + 3] if j + 3 < len(sec_tokens) else "Nao Informado"
                    seguinte = sec_tokens[j + 4] if j + 4 < len(sec_tokens) else ""

                    # As duas secoes da sumula tem layouts distintos, e a propria linha de
                    # cabecalho declara isso: a de amarelos tem coluna "Equipe"; a de vermelhos,
                    # nao. Nos vermelhos o clube vem embutido no nome ("Nome - Clube/UF") e o
                    # token seguinte e o subtipo da expulsao. Ler a posicao fixa nas duas fazia o
                    # subtipo virar nome do clube.
                    if card_type == "Vermelho" and " - " in nome_raw:
                        # Separa na PRIMEIRA ocorrencia: o nome do clube pode conter " - "
                        # (ex.: "Gremio Novorizontino - SAF/SP"), o nome do atleta nao.
                        atleta, _, clube_raw = nome_raw.partition(" - ")
                        atleta = atleta.strip()
                        tipo_detalhe = seguinte.strip()
                    else:
                        atleta = nome_raw
                        clube_raw = seguinte
                        tipo_detalhe = ""
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
                        "tipo_cartao_detalhe": tipo_detalhe,
                        "motivo_completo": motivo_full,
                        "categoria_infracao": categorize_card_reason(motivo_full),
                    })

    if idx_yellow != -1:
        end_y = idx_red if idx_red != -1 else idx_sub
        parse_card_section(tokens[idx_yellow:end_y], "Amarelo")

    if idx_red != -1:
        parse_card_section(tokens[idx_red:idx_sub], "Vermelho")

    return meta, cards_list, gols_list


# =============================================================================
# RELAÇÃO DE ATLETAS E SUBSTITUIÇÕES (tarefa F2-04)
# -----------------------------------------------------------------------------
# A súmula da CBF traz, antes dos eventos, a relação completa de atletas de cada equipe:
# número, apelido, nome completo, condição (titular ou reserva), presença e registro CBF.
# É o insumo que habilita a camada pré-jogo do produto — sem ela só se responde depois do
# apito final, quando os mercados de cartões já liquidaram.
# =============================================================================

RE_CONDICAO = re.compile(r"^([TR])(\(([a-z])?.*)?$")
RE_CLUBE_UF = re.compile(r"^(.+?)\s*/\s*[A-Z]{2}$")
RE_NUM_NOME = re.compile(r"^(\d{1,3})\s*-\s*(.+)$")


def _fim_da_secao(tokens: List[str], inicio: int, marcadores: Tuple[str, ...]) -> int:
    for i in range(inicio + 1, len(tokens)):
        if any(tokens[i].startswith(m) for m in marcadores):
            return i
    return len(tokens)


def _e_numero_de_camisa(token: str) -> bool:
    """
    Distingue um numero de camisa de um registro CBF pela quantidade de digitos.

    Nao vale limitar a 1..99: o Ceara em 2025 relacionou a camisa 100, e o Palmeiras a 188.
    O que separa os dois campos e o tamanho — camisa tem ate tres digitos, registro tem seis
    ou sete. Um limite mais apertado descartaria atletas reais, que foi o efeito da primeira
    versao desta funcao.
    """
    return token.isdigit() and len(token) <= 3 and int(token) >= 1


def parse_relacao_de_atletas(tokens: List[str], meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extrai a relação de atletas de uma súmula já tokenizada.

    Layout, estável entre temporadas e séries:

        'Relação de Jogadores'
        '<Clube> / <UF>'
        'Nº' 'Apelido' 'Nome Completo' 'T/R' 'P/A' 'CBF'
        <numero> <apelido> <nome completo> <T|R[(g]> <P|A> <registro CBF>
        ... (repete; depois vem a segunda equipe, com novo cabeçalho de clube)

    A âncora é o token de condição (`T` ou `R`), e os demais campos são lidos em relação a
    ele. Ancorar no número da camisa seria frágil: números aparecem em vários contextos.
    """
    inicio = next(
        (i for i, t in enumerate(tokens) if t.startswith("Rela") and "Jogadores" in t), None
    )
    if inicio is None:
        return []

    fim = _fim_da_secao(tokens, inicio, ("Comiss", "Substitui", "Gols", "Cart"))
    secao = tokens[inicio:fim]

    atletas: List[Dict[str, Any]] = []
    clube_atual = ""

    for j, tok in enumerate(secao):
        m_clube = RE_CLUBE_UF.match(tok)
        if m_clube and not RE_CONDICAO.match(tok) and j + 1 < len(secao) and secao[j + 1].startswith("N"):
            clube_atual = m_clube.group(1).strip()
            continue

        m_cond = RE_CONDICAO.match(tok)
        if not m_cond or j < 3 or j + 1 >= len(secao):
            continue

        numero_raw, apelido, nome_completo = secao[j - 3], secao[j - 2], secao[j - 1]

        # Quando o apelido vem vazio na sumula, a coluna desaparece e todos os campos
        # deslizam uma posicao: o token em `j-3` passa a ser o registro CBF da linha
        # anterior — seis digitos que `isdigit()` aceita sem reclamar. Sem esta validacao a
        # linha entra na base com o registro no lugar da camisa e sem registro nenhum, e o
        # atleta fica sem identidade: e exatamente o defeito que a F2-04 existe para evitar.
        if not _e_numero_de_camisa(numero_raw) and _e_numero_de_camisa(apelido):
            numero_raw, apelido, nome_completo = apelido, "", nome_completo
        if not _e_numero_de_camisa(numero_raw):
            continue

        # A marca de presenca (P/A) tambem pode faltar; nesse caso o registro vem logo apos
        # a condicao.
        seguinte = secao[j + 1]
        if seguinte in ("P", "A"):
            presenca = seguinte
            registro = secao[j + 2] if j + 2 < len(secao) else ""
        else:
            presenca = ""
            registro = seguinte
        nome_truncado = nome_completo.rstrip().endswith("...")
        nome_limpo = nome_completo.replace("...", "").strip()

        atletas.append({
            "partida_id": meta["partida_id"],
            "temporada": meta["temporada"],
            "serie": meta["serie"],
            "rodada": meta.get("rodada"),
            "clube": clube_atual,
            "clube_slug": slugify(clube_atual),
            "num_camisa": int(numero_raw),
            "apelido": apelido,
            "nome_completo": nome_limpo,
            "nome_truncado": nome_truncado,
            # Quando o nome completo vem truncado pela largura da coluna, o apelido e o
            # numero de registro sao as identificacoes confiaveis.
            "atleta_slug": slugify(apelido if (nome_truncado and apelido) else nome_limpo),
            "apelido_slug": slugify(apelido),
            "condicao": "Titular" if m_cond.group(1) == "T" else "Reserva",
            "goleiro": m_cond.group(3) == "g",
            "presente": presenca == "P",
            "registro_cbf": registro if registro.isdigit() else None,
        })

    return atletas


def parse_substituicoes(tokens: List[str], meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extrai as substituicoes de uma sumula ja tokenizada.

    Layout: 'Substituições' 'Tempo' '1T/2T' 'Equipe' 'Entrou' 'Saiu', seguido de grupos
    <tempo> <periodo> <Clube/UF> '<num> - <entrou>' '<num> - <saiu>'. O periodo pode ser
    `INT` (intervalo), tratado como minuto 45.
    """
    inicio = next((i for i, t in enumerate(tokens) if t.startswith("Substitui")), None)
    if inicio is None:
        return []

    fim = _fim_da_secao(tokens, inicio, ("Ocorr", "Observa", "Relat", "Confedera"))
    secao = tokens[inicio:fim]
    tempo_regex = re.compile(r"^(\+|\d{1,2}:)\d{1,2}(?::\d{2})?$|^\+\d{1,2}$")

    subs: List[Dict[str, Any]] = []
    for j, tok in enumerate(secao):
        if not tempo_regex.match(tok) or j + 4 >= len(secao):
            continue
        periodo_raw = secao[j + 1]
        if periodo_raw not in ("1T", "2T", "INT"):
            continue

        periodo = "1T" if periodo_raw == "1T" else "2T"
        if periodo_raw == "INT":
            min_nom, acr, min_cont = 45, 0, 45
        else:
            min_nom, acr, min_cont = parse_sumula_time(tok, periodo)

        clube_raw = secao[j + 2]
        m_entrou = RE_NUM_NOME.match(secao[j + 3])
        m_saiu = RE_NUM_NOME.match(secao[j + 4])
        if not m_entrou or not m_saiu:
            continue

        nome_entrou = m_entrou.group(2).replace("...", "").strip()
        nome_saiu = m_saiu.group(2).replace("...", "").strip()

        subs.append({
            "partida_id": meta["partida_id"],
            "temporada": meta["temporada"],
            "serie": meta["serie"],
            "rodada": meta.get("rodada"),
            "clube": clube_raw.split("/")[0].strip(),
            "clube_slug": slugify(clube_raw.split("/")[0].strip()),
            "momento": periodo_raw,
            "periodo": periodo,
            "minuto_nominal": min_nom,
            "acrescimo": acr,
            "minuto_continuo": min_cont,
            "num_entrou": int(m_entrou.group(1)),
            "atleta_entrou": nome_entrou,
            "atleta_entrou_slug": slugify(nome_entrou),
            "num_saiu": int(m_saiu.group(1)),
            "atleta_saiu": nome_saiu,
            "atleta_saiu_slug": slugify(nome_saiu),
        })

    return subs


def parse_escalacao_from_pdf(filepath: Path, meta: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Tokeniza a súmula e devolve (relação de atletas, substituições)."""
    tokens = extract_tokens_from_pdf(filepath)
    return parse_relacao_de_atletas(tokens, meta), parse_substituicoes(tokens, meta)


def align_dataframe_types(df_new: pd.DataFrame, df_existing: pd.DataFrame) -> pd.DataFrame:
    """
    Alinha os dtypes de df_new aos de df_existing e **une** os dois schemas.

    A versão anterior truncava `df_new` para as colunas da base existente. Como a base histórica
    da Série A veio do Kaggle, que não tem `motivo_completo` nem `categoria_infracao`, o motivo
    textual do árbitro — o atributo de maior valor competitivo do projeto — era descartado em
    silêncio a cada execução do pipeline delta (tarefa F2-01).

    Colunas presentes só no dado novo são preservadas; colunas presentes só no histórico são
    criadas vazias no dado novo. A ordem do histórico é mantida, com as colunas novas ao final.
    """
    target_cols = list(df_existing.columns)
    novas_cols = [c for c in df_new.columns if c not in target_cols]
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

    return aligned_df[target_cols + novas_cols]


def unir_schema_historico(df_existing: pd.DataFrame, novas_cols: list) -> pd.DataFrame:
    """Cria no histórico, vazias, as colunas que só existem no dado novo."""
    df = df_existing.copy()
    for col in novas_cols:
        if col not in df.columns:
            df[col] = pd.NA
    return df


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
            return {"matches_upserted": 0, "goals_upserted": 0, "cards_upserted": 0,
            "escalacoes_upserted": len(df_new_lineups),
            "substituicoes_upserted": len(df_new_subs),
            "total_escalacoes_dataset": total_escalacoes,
            "total_substituicoes_dataset": total_subs,
        }

        serie_dir = self._get_serie_dir(serie)
        partidas_parquet = serie_dir / "partidas.parquet"
        partidas_csv = serie_dir / "partidas.csv"
        gols_parquet = serie_dir / "gols.parquet"
        gols_csv = serie_dir / "gols.csv"
        cartoes_parquet = serie_dir / "cartoes.parquet"
        cartoes_csv = serie_dir / "cartoes.csv"
        escalacoes_parquet = serie_dir / "escalacoes.parquet"
        escalacoes_csv = serie_dir / "escalacoes.csv"
        substituicoes_parquet = serie_dir / "substituicoes.parquet"
        substituicoes_csv = serie_dir / "substituicoes.csv"

        new_matches = []
        new_goals = []
        new_cards = []
        new_lineups = []
        new_subs = []

        for p in pdf_paths:
            try:
                meta, c_list, g_list = parse_single_cbf_pdf(p, temporada_default=temporada, serie_default=serie)
                new_matches.append(meta)
                new_goals.extend(g_list)
                new_cards.extend(c_list)
                esc_list, sub_list = parse_escalacao_from_pdf(p, meta)
                new_lineups.extend(esc_list)
                new_subs.extend(sub_list)
            except Exception as e:
                logger.error("Erro ao processar súmula %s: %s", p.name, e)

        if not new_matches:
            return {"matches_upserted": 0, "goals_upserted": 0, "cards_upserted": 0,
                    "escalacoes_upserted": 0, "substituicoes_upserted": 0}

        df_new_matches = pd.DataFrame(new_matches)
        df_new_goals = pd.DataFrame(new_goals) if new_goals else pd.DataFrame()
        df_new_cards = pd.DataFrame(new_cards) if new_cards else pd.DataFrame()
        df_new_lineups = pd.DataFrame(new_lineups) if new_lineups else pd.DataFrame()
        df_new_subs = pd.DataFrame(new_subs) if new_subs else pd.DataFrame()

        partidas_upsert_ids = set(df_new_matches["partida_id"].unique())

        # 1. UPSERT PARTIDAS
        if partidas_parquet.exists():
            df_existing_p = pd.read_parquet(partidas_parquet)
            mask = ~((df_existing_p["temporada"] == temporada) & (df_existing_p["partida_id"].isin(partidas_upsert_ids)))
            df_p_filtered = df_existing_p[mask]
            df_new_matches_aligned = align_dataframe_types(df_new_matches, df_existing_p)
            df_p_filtered = unir_schema_historico(
                df_p_filtered,
                [c for c in df_new_matches_aligned.columns if c not in df_p_filtered.columns],
            )
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
                df_g_filtered = unir_schema_historico(
                    df_g_filtered,
                    [c for c in df_new_goals_aligned.columns if c not in df_g_filtered.columns],
                )
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
                df_c_filtered = unir_schema_historico(
                    df_c_filtered,
                    [c for c in df_new_cards_aligned.columns if c not in df_c_filtered.columns],
                )
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

        # 4. UPSERT RELAÇÃO DE ATLETAS E SUBSTITUIÇÕES (F2-04)
        def _upsert_auxiliar(df_novo, caminho_parquet, caminho_csv, ordenacao):
            """Substitui as linhas das partidas reprocessadas e preserva o restante."""
            if caminho_parquet.exists():
                df_ant = pd.read_parquet(caminho_parquet)
                mask = ~((df_ant["temporada"] == temporada) & (df_ant["partida_id"].isin(partidas_upsert_ids)))
                df_filtrado = df_ant[mask]
                if not df_novo.empty:
                    df_alinhado = align_dataframe_types(df_novo, df_ant)
                    df_filtrado = unir_schema_historico(
                        df_filtrado,
                        [c for c in df_alinhado.columns if c not in df_filtrado.columns],
                    )
                    df_final = pd.concat([df_filtrado, df_alinhado], ignore_index=True)
                else:
                    df_final = df_filtrado
            else:
                df_final = df_novo

            if df_final.empty:
                return 0
            cols = [c for c in ordenacao if c in df_final.columns]
            if cols:
                df_final = df_final.sort_values(cols).reset_index(drop=True)
            df_final.to_parquet(caminho_parquet, index=False)
            df_final.to_csv(caminho_csv, index=False, encoding="utf-8")
            return len(df_final)

        total_escalacoes = _upsert_auxiliar(
            df_new_lineups, escalacoes_parquet, escalacoes_csv,
            ["temporada", "rodada", "partida_id", "clube_slug", "num_camisa"],
        )
        total_subs = _upsert_auxiliar(
            df_new_subs, substituicoes_parquet, substituicoes_csv,
            ["temporada", "rodada", "partida_id", "minuto_continuo"],
        )

        # 5. Atualizar manifesto de processamento
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
            "escalacoes_upserted": len(df_new_lineups),
            "substituicoes_upserted": len(df_new_subs),
            "total_partidas_dataset": len(df_final_p),
            "total_escalacoes_dataset": total_escalacoes,
            "total_substituicoes_dataset": total_subs,
        }
