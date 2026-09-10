"""
src/ingestion/build_integrity_data.py
--------------------------------------
Compila e estrutura a base de casos reais investigados judicialmente pelo
Ministério Público do Estado de Goiás (MP-GO) no âmbito da Operação Penalidade Máxima
(Fases 1 e 2, Autos Judiciais nº 5174092-25.2023.8.09.0001 e 5240212-68.2023.8.09.0001).

Contém:
- Temporada, Competição, Série, Rodada, Partida, Clubes
- Jogador investigado, Posição
- Evento manipulado/tentado (Cartão Amarelo 1T, Pênalti 1T, Cartão Vermelho)
- Desfecho no jogo (Executado / Falhou)
- Situação processual e punição desportiva (STJD / FIFA)
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

RAW_DIR = Path("data/raw/integrity")
PROCESSED_DIR = Path("data/processed/integrity")

CASES: List[Dict] = [
    # Série B 2022 (Fase 1 - O estopim da operação)
    {
        "caso_id": "PM-001",
        "operacao": "Penalidade Maxima I",
        "temporada": 2022,
        "serie": "B",
        "rodada": 38,
        "data": "2022-11-06",
        "confronto": "Vila Nova x Sport",
        "clube_mandante": "Vila Nova",
        "clube_visitante": "Sport",
        "clube_atleta": "Vila Nova",
        "atleta": "Romario",
        "atleta_slug": "romario",
        "posicao": "Volante",
        "evento_alvo": "cometer_penalti_1t",
        "minuto_alvo": "1T",
        "mercado_aposta": "penalti_1t",
        "executado_com_sucesso": False,
        "evento_ocorreu": False,
        "minuto_real": None,
        "detalhes": "Recebeu R$ 10 mil adiantados, nao foi escalado titular e tentou cooptar Gabriel Domingos. Penalti nao ocorreu; gerou cobranca da quadrilha e estopim da denuncia.",
        "situacao_stjd": "Banido do futebol",
        "fonte_documental": "Autos MP-GO / Acordao STJD Processo 003/2023"
    },
    {
        "caso_id": "PM-002",
        "operacao": "Penalidade Maxima I",
        "temporada": 2022,
        "serie": "B",
        "rodada": 38,
        "data": "2022-11-05",
        "confronto": "Criciuma x Tombense",
        "clube_mandante": "Criciuma",
        "clube_visitante": "Tombense",
        "clube_atleta": "Tombense",
        "atleta": "Joseph",
        "atleta_slug": "joseph",
        "posicao": "Zagueiro",
        "evento_alvo": "cometer_penalti_1t",
        "minuto_alvo": "1T",
        "mercado_aposta": "penalti_1t",
        "executado_com_sucesso": True,
        "evento_ocorreu": True,
        "minuto_real": 23,
        "detalhes": "Cometeu penalti aos 23' do 1T convertido pelo adversario. Recebeu R$ 10 mil de adiantamento.",
        "situacao_stjd": "Suspenso por 360 dias",
        "fonte_documental": "Autos MP-GO / Confissao em Juizo"
    },
    {
        "caso_id": "PM-003",
        "operacao": "Penalidade Maxima I",
        "temporada": 2022,
        "serie": "B",
        "rodada": 38,
        "data": "2022-11-05",
        "confronto": "Sampaio Correa x Londrina",
        "clube_mandante": "Sampaio Correa",
        "clube_visitante": "Londrina",
        "clube_atleta": "Sampaio Correa",
        "atleta": "Mateusinho",
        "atleta_slug": "mateusinho",
        "posicao": "Lateral-Direito",
        "evento_alvo": "cometer_penalti_1t",
        "minuto_alvo": "1T",
        "mercado_aposta": "penalti_1t",
        "executado_com_sucesso": True,
        "evento_ocorreu": True,
        "minuto_real": 19,
        "detalhes": "Cometeu penalti aos 19' do 1T convertido pelo Londrina. Negociou R$ 150 mil com a quadrilha.",
        "situacao_stjd": "Suspenso por 720 dias",
        "fonte_documental": "Autos MP-GO / Julgamento STJD"
    },
    {
        "caso_id": "PM-004",
        "operacao": "Penalidade Maxima I",
        "temporada": 2022,
        "serie": "B",
        "rodada": 38,
        "data": "2022-11-05",
        "confronto": "Sampaio Correa x Londrina",
        "clube_mandante": "Sampaio Correa",
        "clube_visitante": "Londrina",
        "clube_atleta": "Sampaio Correa",
        "atleta": "Ygor Catatau",
        "atleta_slug": "ygor_catatau",
        "posicao": "Atacante",
        "evento_alvo": "cometer_penalti_1t",
        "minuto_alvo": "1T",
        "mercado_aposta": "penalti_1t",
        "executado_com_sucesso": True,
        "evento_ocorreu": True,
        "minuto_real": 19,
        "detalhes": "Intermediou e garantiu a participacao de atletas no esquema de penalti no 1T.",
        "situacao_stjd": "Banido do futebol",
        "fonte_documental": "Autos MP-GO / Acordao STJD"
    },
    {
        "caso_id": "PM-005",
        "operacao": "Penalidade Maxima II",
        "temporada": 2022,
        "serie": "B",
        "rodada": 23,
        "data": "2022-08-10",
        "confronto": "Nautico x Sampaio Correa",
        "clube_mandante": "Nautico",
        "clube_visitante": "Sampaio Correa",
        "clube_atleta": "Sampaio Correa",
        "atleta": "Mateusinho",
        "atleta_slug": "mateusinho",
        "posicao": "Lateral-Direito",
        "evento_alvo": "cartao_amarelo_1t",
        "minuto_alvo": "1T",
        "mercado_aposta": "cartao_jogador",
        "executado_com_sucesso": True,
        "evento_ocorreu": True,
        "minuto_real": 31,
        "detalhes": "Recebeu cartao amarelo no 1T conforme acordado com apostadores.",
        "situacao_stjd": "Suspenso por 720 dias",
        "fonte_documental": "Autos MP-GO"
    },
    # Série A 2022 (Fase 2 - Expansão para a Elite)
    {
        "caso_id": "PM-006",
        "operacao": "Penalidade Maxima II",
        "temporada": 2022,
        "serie": "A",
        "rodada": 25,
        "data": "2022-09-03",
        "confronto": "Juventude x Avai",
        "clube_mandante": "Juventude",
        "clube_visitante": "Avai",
        "clube_atleta": "Juventude",
        "atleta": "Paulo Miranda",
        "atleta_slug": "paulo_miranda",
        "posicao": "Zagueiro",
        "evento_alvo": "cartao_amarelo_1t",
        "minuto_alvo": "1T",
        "mercado_aposta": "cartao_jogador",
        "executado_com_sucesso": True,
        "evento_ocorreu": True,
        "minuto_real": 47,
        "detalhes": "Cartao amarelo forçado aos 45+2' do 1T por retardar o reinicio do jogo.",
        "situacao_stjd": "Suspenso por 720 dias",
        "fonte_documental": "Autos MP-GO / Sumula CBF"
    },
    {
        "caso_id": "PM-007",
        "operacao": "Penalidade Maxima II",
        "temporada": 2022,
        "serie": "A",
        "rodada": 26,
        "data": "2022-09-10",
        "confronto": "Palmeiras x Juventude",
        "clube_mandante": "Palmeiras",
        "clube_visitante": "Juventude",
        "clube_atleta": "Juventude",
        "atleta": "Paulo Miranda",
        "atleta_slug": "paulo_miranda",
        "posicao": "Zagueiro",
        "evento_alvo": "cartao_amarelo_1t",
        "minuto_alvo": "1T",
        "mercado_aposta": "cartao_jogador",
        "executado_com_sucesso": True,
        "evento_ocorreu": True,
        "minuto_real": 38,
        "detalhes": "Cartao amarelo aos 38' do 1T por cometer falta temeraria.",
        "situacao_stjd": "Suspenso por 720 dias",
        "fonte_documental": "Autos MP-GO / Sumula CBF"
    },
    {
        "caso_id": "PM-008",
        "operacao": "Penalidade Maxima II",
        "temporada": 2022,
        "serie": "A",
        "rodada": 27,
        "data": "2022-09-18",
        "confronto": "Juventude x Fortaleza",
        "clube_mandante": "Juventude",
        "clube_visitante": "Fortaleza",
        "clube_atleta": "Juventude",
        "atleta": "Gabriel Tota",
        "atleta_slug": "gabriel_tota",
        "posicao": "Meio-campo",
        "evento_alvo": "cartao_amarelo_1t",
        "minuto_alvo": "1T",
        "mercado_aposta": "cartao_jogador",
        "executado_com_sucesso": True,
        "evento_ocorreu": True,
        "minuto_real": 38,
        "detalhes": "Cartao amarelo forçado aos 38' do 1T.",
        "situacao_stjd": "Banido do futebol",
        "fonte_documental": "Autos MP-GO / Julgamento STJD"
    },
    {
        "caso_id": "PM-009",
        "operacao": "Penalidade Maxima II",
        "temporada": 2022,
        "serie": "A",
        "rodada": 28,
        "data": "2022-09-28",
        "confronto": "Fluminense x Juventude",
        "clube_mandante": "Fluminense",
        "clube_visitante": "Juventude",
        "clube_atleta": "Juventude",
        "atleta": "Gabriel Tota",
        "atleta_slug": "gabriel_tota",
        "posicao": "Meio-campo",
        "evento_alvo": "cartao_amarelo_1t",
        "minuto_alvo": "1T",
        "mercado_aposta": "cartao_jogador",
        "executado_com_sucesso": True,
        "evento_ocorreu": True,
        "minuto_real": 39,
        "detalhes": "Cartao amarelo forçado aos 39' do 1T.",
        "situacao_stjd": "Banido do futebol",
        "fonte_documental": "Autos MP-GO / Sumula CBF"
    },
    {
        "caso_id": "PM-010",
        "operacao": "Penalidade Maxima II",
        "temporada": 2022,
        "serie": "A",
        "rodada": 36,
        "data": "2022-11-05",
        "confronto": "Santos x Avai",
        "clube_mandante": "Santos",
        "clube_visitante": "Avai",
        "clube_atleta": "Santos",
        "atleta": "Eduardo Bauermann",
        "atleta_slug": "eduardo_bauermann",
        "posicao": "Zagueiro",
        "evento_alvo": "cartao_amarelo",
        "minuto_alvo": "Jogo",
        "mercado_aposta": "cartao_jogador",
        "executado_com_sucesso": False,
        "evento_ocorreu": False,
        "minuto_real": None,
        "detalhes": "Recebeu R$ 50 mil para tomar amarelo, mas nao tomou no jogo. Foi ameacado e prometeu tomar vermelho na rodada seguinte.",
        "situacao_stjd": "Suspenso por 360 dias (FIFA estendeu)",
        "fonte_documental": "Prints WhatsApp Autos MP-GO"
    },
    {
        "caso_id": "PM-011",
        "operacao": "Penalidade Maxima II",
        "temporada": 2022,
        "serie": "A",
        "rodada": 37,
        "data": "2022-11-10",
        "confronto": "Botafogo x Santos",
        "clube_mandante": "Botafogo",
        "clube_visitante": "Santos",
        "clube_atleta": "Santos",
        "atleta": "Eduardo Bauermann",
        "atleta_slug": "eduardo_bauermann",
        "posicao": "Zagueiro",
        "evento_alvo": "cartao_vermelho",
        "minuto_alvo": "Fim de Jogo",
        "mercado_aposta": "expulsao_jogador",
        "executado_com_sucesso": True,
        "evento_ocorreu": True,
        "minuto_real": 95,
        "detalhes": "Expulso apos o apito final por ofender deliberadamente o arbitro Braulio da Silva Machado para pagar a divida com a quadrilha.",
        "situacao_stjd": "Suspenso por 360 dias",
        "fonte_documental": "Sumula CBF / Autos MP-GO"
    },
    {
        "caso_id": "PM-012",
        "operacao": "Penalidade Maxima II",
        "temporada": 2022,
        "serie": "A",
        "rodada": 32,
        "data": "2022-10-16",
        "confronto": "Ceara x Cuiaba",
        "clube_mandante": "Ceara",
        "clube_visitante": "Cuiaba",
        "clube_atleta": "Ceara",
        "atleta": "Nino Paraiba",
        "atleta_slug": "nino_paraiba",
        "posicao": "Lateral-Direito",
        "evento_alvo": "cartao_amarelo",
        "minuto_alvo": "Jogo",
        "mercado_aposta": "cartao_jogador",
        "executado_com_sucesso": True,
        "evento_ocorreu": True,
        "minuto_real": 45,
        "detalhes": "Recebeu amarelo no final do 1T. Fez acordo de delacao/nao persecucao penal.",
        "situacao_stjd": "Suspenso por 480 dias",
        "fonte_documental": "Acordo ANPC MP-GO"
    },
    {
        "caso_id": "PM-013",
        "operacao": "Penalidade Maxima II",
        "temporada": 2022,
        "serie": "A",
        "rodada": 36,
        "data": "2022-11-05",
        "confronto": "Goias x Juventude",
        "clube_mandante": "Goias",
        "clube_visitante": "Juventude",
        "clube_atleta": "Juventude",
        "atleta": "Moraes Jr",
        "atleta_slug": "moraes_jr",
        "posicao": "Lateral-Esquerdo",
        "evento_alvo": "cartao_amarelo_1t",
        "minuto_alvo": "1T",
        "mercado_aposta": "cartao_jogador",
        "executado_com_sucesso": True,
        "evento_ocorreu": True,
        "minuto_real": 31,
        "detalhes": "Recebeu cartao amarelo aos 31' do 1T. Confessou e firmou acordo com o MP-GO.",
        "situacao_stjd": "Suspenso por 720 dias",
        "fonte_documental": "Depoimento em Juizo MP-GO"
    },
    {
        "caso_id": "PM-014",
        "operacao": "Penalidade Maxima II",
        "temporada": 2022,
        "serie": "A",
        "rodada": 36,
        "data": "2022-11-05",
        "confronto": "Cuiaba x Palmeiras",
        "clube_mandante": "Cuiaba",
        "clube_visitante": "Palmeiras",
        "clube_atleta": "Cuiaba",
        "atleta": "Igor Carius",
        "atleta_slug": "igor_carius",
        "posicao": "Lateral-Esquerdo",
        "evento_alvo": "cartao_amarelo_1t",
        "minuto_alvo": "1T",
        "mercado_aposta": "cartao_jogador",
        "executado_com_sucesso": True,
        "evento_ocorreu": True,
        "minuto_real": 46,
        "detalhes": "Recebeu amarelo nos acrescimos do 1T (45+1'). Denunciado criminalmente.",
        "situacao_stjd": "Suspenso por 540 dias",
        "fonte_documental": "Autos MP-GO"
    },
]


def calculate_sha256(filepath: Path) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def build_and_save_integrity_data() -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(CASES)

    raw_csv = RAW_DIR / "casos_penalidade_maxima.csv"
    proc_csv = PROCESSED_DIR / "casos_penalidade_maxima.csv"
    proc_parquet = PROCESSED_DIR / "casos_penalidade_maxima.parquet"

    df.to_csv(raw_csv, index=False, encoding="utf-8")
    df.to_csv(proc_csv, index=False, encoding="utf-8")
    df.to_parquet(proc_parquet, index=False, engine="pyarrow")

    manifest = {
        "fonte_primaria": "Ministerio Publico de Goias (MP-GO) - Operacao Penalidade Maxima I e II",
        "created_at": datetime.now().isoformat(),
        "total_casos": len(df),
        "temporadas": [2022],
        "series": ["A", "B"],
        "files": {
            "casos_penalidade_maxima.csv": {
                "size_bytes": raw_csv.stat().st_size,
                "sha256": calculate_sha256(raw_csv),
            },
            "casos_penalidade_maxima.parquet": {
                "size_bytes": proc_parquet.stat().st_size,
                "sha256": calculate_sha256(proc_parquet),
            },
        }
    }

    manifest_path = PROCESSED_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info("Dataset de Integridade gerado com sucesso: %d casos registrados.", len(df))
    logger.info("Manifesto salvo em %s", manifest_path)
    return df


if __name__ == "__main__":
    build_and_save_integrity_data()
