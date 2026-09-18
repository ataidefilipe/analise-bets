"""
src/pipeline/camadas_de_exposicao.py
------------------------------------
Status jurídico por atleta e aplicação de camada a qualquer artefato (tarefa F4-02).

O problema que esta tarefa resolve
----------------------------------
O repositório publica rankings nominais de "atletas anômalos" que incluem pessoas **nunca
investigadas**. O topo do ranking histórico de atipicidade não tem qualquer relação com a
Operação Penalidade Máxima: são atletas cuja única particularidade é uma distribuição de
cartões fora do padrão. Publicar essa lista com nome é exposição direta a ação por dano moral,
e contradiz a diretriz de presunção de inocência que o próprio relatório 07 declara.

A distinção que a arquitetura preserva
--------------------------------------
* **Condenado** — decisão desportiva ou penal. Fato público, pode ser nominado em qualquer
  camada. Hoje são os 10 atletas da Operação Penalidade Máxima, todos com sanção do STJD.
* **Investigado sem condenação** — não pode ser nominado fora de ambiente restrito.
* **Sem registro** — apenas estatisticamente atípico. É o grupo mais numeroso e o mais exposto.
  **Não pode ser nominado em nenhuma camada aberta, sob nenhuma circunstância.**

A camada é parâmetro explícito de `aplicar_camada()`, e não uma convenção que cada chamador
lembra de seguir.
"""

import os
import unicodedata
from typing import Iterable, Optional

import pandas as pd

from src.pipeline.perfis_de_acesso import (
    CAMADA_ABERTA,
    CAMADA_IDENTIFICADA,
    CAMADA_PSEUDONIMIZADA,
    pseudonimizar,
)

GROUND_TRUTH = os.path.join("data", "processed", "integrity", "casos_penalidade_maxima.parquet")

# O mapeamento pseudônimo <-> nome vive fora das bases analíticas e fora do versionamento.
DIR_RESTRITO = os.path.join("data", "restrito")
MAPA_PSEUDONIMOS = os.path.join(DIR_RESTRITO, "mapa_pseudonimos.csv")

STATUS_CONDENADO = "condenado"
STATUS_INVESTIGADO = "investigado_sem_condenacao"
STATUS_SEM_REGISTRO = "sem_registro"


def status_juridico_por_atleta() -> pd.DataFrame:
    """
    Classificação formal de cada atleta citado no ground truth.

    A fonte é a coluna `situacao_stjd` dos casos da Operação Penalidade Máxima. Atleta que não
    aparece nesta tabela é `sem_registro` — e é justamente quem não pode ser nominado.
    """
    if not os.path.exists(GROUND_TRUTH):
        return pd.DataFrame(columns=["atleta", "atleta_slug", "status_juridico", "sancao", "fonte"])

    df = pd.read_parquet(GROUND_TRUTH)
    linhas = []
    for slug, g in df.groupby("atleta_slug"):
        sancoes = sorted({str(s).strip() for s in g["situacao_stjd"] if str(s).strip()})
        linhas.append({
            "atleta": g["atleta"].iloc[0],
            "atleta_slug": slug,
            "status_juridico": STATUS_CONDENADO if sancoes else STATUS_INVESTIGADO,
            "sancao": " / ".join(sancoes),
            "fonte": g["fonte_documental"].iloc[0] if "fonte_documental" in g.columns else "",
        })
    return pd.DataFrame(linhas).sort_values("atleta").reset_index(drop=True)


def nomes_nominaveis() -> set:
    """
    Nomes que podem aparecer em camada aberta, por serem fato público.

    Devolve variações do nome — como consta do ground truth e como consta das bases — porque a
    varredura precisa reconhecer o mesmo atleta escrito de formas diferentes.
    """
    status = status_juridico_por_atleta()
    condenados = status[status["status_juridico"] == STATUS_CONDENADO]
    nomes = set()
    for _, r in condenados.iterrows():
        nomes.add(str(r["atleta"]).strip())
        nomes.add(str(r["atleta_slug"]).strip())
    return {n for n in nomes if n}


def normalizar_nome(texto: str) -> str:
    """
    Remove acentos e caixa para comparar nomes.

    O ground truth grava "Nino Paraiba" e as bases escrevem "Nino Paraíba". Sem normalizar, um
    condenado — nominável — seria pseudonimizado como se fosse atleta sem registro, e o
    relatório perderia a capacidade de discutir os casos julgados pelo nome.
    """
    sem_acento = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in sem_acento if not unicodedata.combining(c)).strip().lower()


def aplicar_camada(df: pd.DataFrame, camada: str,
                   colunas_de_nome: Iterable[str] = ("atleta", "apelido", "nome_completo",
                                                     "atleta_slug", "apelido_slug"),
                   coluna_identificador: str = "registro_cbf",
                   coluna_slug: str = "atleta_slug",
                   nominaveis: Optional[set] = None) -> pd.DataFrame:
    """
    Aplica a camada de exposição a um quadro qualquer.

    Na camada aberta e na pseudonimizada, o nome de atleta **sem condenação** é substituído por
    um pseudônimo estável. Atleta condenado permanece nominado, porque é fato público — a
    exceção existe para que o relatório possa continuar discutindo os casos julgados.
    """
    if camada not in (CAMADA_ABERTA, CAMADA_PSEUDONIMIZADA, CAMADA_IDENTIFICADA):
        raise ValueError(f"Camada desconhecida: {camada!r}")
    if camada == CAMADA_IDENTIFICADA or df.empty:
        return df.copy()

    publicos = {normalizar_nome(n)
                for n in (nomes_nominaveis() if nominaveis is None else nominaveis)}
    saida = df.copy()

    # A base do pseudônimo é o registro CBF quando existe; senão, o slug do nome. O segundo é
    # menos robusto — dois homônimos colidem —, mas é o que há em tabelas antigas.
    if coluna_identificador in saida.columns:
        base = saida[coluna_identificador].astype(str)
    elif coluna_slug in saida.columns:
        base = saida[coluna_slug].astype(str)
    else:
        base = None

    if base is not None:
        saida["atleta_pseudonimo"] = base.map(pseudonimizar)

    # O slug e derivado do nome: mante-lo seria publicar o nome em outro formato.
    referencia_publica = None
    if coluna_slug in saida.columns:
        referencia_publica = saida[coluna_slug].map(normalizar_nome).isin(publicos)

    for coluna in colunas_de_nome:
        if coluna not in saida.columns:
            continue
        valores = saida[coluna].astype(str)
        e_publico = valores.map(normalizar_nome).isin(publicos)
        if referencia_publica is not None:
            e_publico = e_publico | referencia_publica
        substituto = saida["atleta_pseudonimo"] if "atleta_pseudonimo" in saida.columns else "[protegido]"
        saida[coluna] = valores.where(e_publico, substituto)

    return saida


def salvar_mapa_pseudonimos(df: pd.DataFrame, coluna_identificador: str = "registro_cbf",
                            colunas_de_nome: Iterable[str] = ("apelido", "atleta")) -> str:
    """
    Persiste o mapeamento pseudônimo ↔ nome **fora das bases analíticas**.

    O arquivo fica em `data/restrito/`, que está no `.gitignore`: versioná-lo anularia a
    pseudonimização, já que qualquer clone traria a chave de reidentificação junto.
    """
    os.makedirs(DIR_RESTRITO, exist_ok=True)
    coluna_nome = next((c for c in colunas_de_nome if c in df.columns), None)
    if coluna_identificador not in df.columns or coluna_nome is None:
        raise ValueError("O quadro precisa do identificador e de ao menos uma coluna de nome.")

    mapa = df[[coluna_identificador, coluna_nome]].drop_duplicates().copy()
    mapa["atleta_pseudonimo"] = mapa[coluna_identificador].astype(str).map(pseudonimizar)
    mapa = mapa.rename(columns={coluna_nome: "nome"})[
        ["atleta_pseudonimo", coluna_identificador, "nome"]]
    mapa.to_csv(MAPA_PSEUDONIMOS, index=False, encoding="utf-8")
    return MAPA_PSEUDONIMOS


if __name__ == "__main__":
    status = status_juridico_por_atleta()
    destino = os.path.join("reports", "tables", "status_juridico_atletas.csv")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    status.to_csv(destino, index=False, encoding="utf-8")
    print(status[["atleta", "status_juridico", "sancao"]].to_string(index=False))
    print(f"\nNominaveis em camada aberta: {len(status[status['status_juridico'] == STATUS_CONDENADO])}")
