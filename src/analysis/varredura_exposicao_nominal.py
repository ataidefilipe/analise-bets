"""
src/analysis/varredura_exposicao_nominal.py
-------------------------------------------
Varredura retroativa de exposição nominal nos artefatos publicados (tarefa F4-02).

Por que uma varredura, e não só uma regra para daqui em diante
--------------------------------------------------------------
O controle criado na F4-03 protege as saídas novas. O dado problemático, porém, **já está
publicado**: tabelas, relatórios, notebooks e a apresentação HTML nomeiam atletas cuja única
particularidade é uma distribuição de cartões fora do padrão. Uma correção que não alcança o
que já existe não corrige nada.

Como a varredura funciona
-------------------------
Monta o conjunto de nomes de atleta conhecidos das bases, remove os que podem ser nominados
por serem fato público — condenados na Operação Penalidade Máxima — e procura o restante nos
artefatos destinados a circular. Reporta arquivo, linha e nome encontrado.

Ela é deliberadamente conservadora: nomes com menos de três palavras e apelidos que coincidem
com palavras comuns produzem falso positivo, e por isso o resultado é uma **lista para
tratamento**, não uma decisão automática de remoção.

Saída: reports/tables/varredura_exposicao_nominal.csv
"""

import os
import re
import unicodedata
from typing import Dict, Iterable, List, Set

import pandas as pd

from src.pipeline.camadas_de_exposicao import nomes_nominaveis

TABLES_DIR = os.path.join("reports", "tables")

# Artefatos que circulam: repositório público, white paper, banca, imprensa.
ALVOS_CAMADA_ABERTA = [
    os.path.join("reports", "analysis"),
    os.path.join("reports", "tables"),
    os.path.join("reports", "white_paper_impacto_bets_futebol_brasileiro.md"),
    os.path.join("reports", "apresentacao_processo_projeto.html"),
    os.path.join("notebooks"),
    os.path.join("docs"),
]

EXTENSOES = (".md", ".csv", ".html", ".ipynb")

# Arquivos que existem justamente para registrar a exposição, e que citam nomes ao descrevê-la.
ISENTOS = {
    "varredura_exposicao_nominal.csv",
    "status_juridico_atletas.csv",
    "auditoria_ground_truth_atletas.csv",
    "comparacao_f1_reconciliacao_atletas_gt.csv",
    "divergencias_escalacao_eventos.csv",
}

# Placeholders e papéis que não são atleta, mas aparecem nas mesmas colunas.
NAO_SAO_ATLETAS = {"nao informado", "não informado", "nao informada"}

# Palavras que aparecem como apelido de atleta e também como termo comum do texto.
APELIDOS_AMBIGUOS = {
    "marlon", "dudu", "nino", "eduardo", "paulo", "gabriel", "felipe", "bruno", "diego",
    "rafael", "lucas", "matheus", "pedro", "carlos", "jean", "alex", "igor", "joao", "luiz",
}


def _normalizar(texto: str) -> str:
    """
    Remove acentos e caixa para comparar nomes.

    Necessário porque o ground truth grava "Nino Paraiba" e os relatórios escrevem "Nino
    Paraíba": sem normalizar, um atleta condenado — nominável — seria tratado como exposição
    indevida, e o ruído afogaria os casos reais.
    """
    sem_acento = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in sem_acento if not unicodedata.combining(c)).strip().lower()


def nomes_de_atletas_conhecidos(minimo_de_palavras: int = 2) -> Set[str]:
    """
    Nomes presentes nas bases de atletas, que são os que podem ter vazado para os artefatos.

    Nomes de uma só palavra são descartados: o ruído que produzem afoga o sinal.
    """
    nomes: Set[str] = set()
    for serie in ("a", "b"):
        for base in ("escalacoes", "cartoes"):
            caminho = os.path.join("data", "processed", f"serie_{serie}", f"{base}.parquet")
            if not os.path.exists(caminho):
                continue
            df = pd.read_parquet(caminho)
            for coluna in ("atleta", "apelido", "nome_completo"):
                if coluna in df.columns:
                    nomes.update(str(v).strip() for v in df[coluna].dropna().unique())

    return {
        n for n in nomes
        if len(n.split()) >= minimo_de_palavras
        and _normalizar(n) not in APELIDOS_AMBIGUOS
        and _normalizar(n) not in NAO_SAO_ATLETAS
        and len(n) >= 8
    }


def _arquivos_alvo() -> List[str]:
    arquivos = []
    for alvo in ALVOS_CAMADA_ABERTA:
        if os.path.isfile(alvo):
            arquivos.append(alvo)
        elif os.path.isdir(alvo):
            for raiz, _, nomes in os.walk(alvo):
                for nome in nomes:
                    if nome.endswith(EXTENSOES) and nome not in ISENTOS:
                        arquivos.append(os.path.join(raiz, nome))
    return sorted(arquivos)


def varrer(nomes_proibidos: Iterable[str]) -> pd.DataFrame:
    """Procura cada nome proibido nos artefatos de camada aberta."""
    proibidos = sorted(nomes_proibidos, key=len, reverse=True)
    if not proibidos:
        return pd.DataFrame()

    padrao = re.compile("|".join(re.escape(n) for n in proibidos))
    achados: List[Dict] = []

    for caminho in _arquivos_alvo():
        try:
            conteudo = open(caminho, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        if not padrao.search(conteudo):
            continue
        for numero, linha in enumerate(conteudo.splitlines(), 1):
            for encontrado in set(padrao.findall(linha)):
                achados.append({
                    "arquivo": caminho.replace("\\", "/"),
                    "linha": numero,
                    "nome_encontrado": encontrado,
                    "trecho": linha.strip()[:160],
                })

    return pd.DataFrame(achados)


def executar() -> pd.DataFrame:
    conhecidos = nomes_de_atletas_conhecidos()
    publicos = {_normalizar(n) for n in nomes_nominaveis()}
    # Um condenado citado com grafia diferente continua sendo o mesmo condenado.
    proibidos = {n for n in conhecidos if _normalizar(n) not in publicos}

    achados = varrer(proibidos)
    os.makedirs(TABLES_DIR, exist_ok=True)
    achados.to_csv(os.path.join(TABLES_DIR, "varredura_exposicao_nominal.csv"),
                   index=False, encoding="utf-8")
    return achados


if __name__ == "__main__":
    achados = executar()
    if achados.empty:
        print("Nenhum atleta sem condenacao nominado em artefato de camada aberta.")
    else:
        print(f"{len(achados)} ocorrencias em {achados['arquivo'].nunique()} arquivos:\n")
        print(achados.groupby("arquivo").agg(
            ocorrencias=("nome_encontrado", "size"),
            atletas=("nome_encontrado", "nunique"),
        ).sort_values("ocorrencias", ascending=False).to_string())
