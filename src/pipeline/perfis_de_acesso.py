"""
src/pipeline/perfis_de_acesso.py
--------------------------------
Controle técnico de granularidade por perfil de cliente (tarefa F4-03).

Por que isto existe no código, e não só no contrato
---------------------------------------------------
O mesmo artefato serve a dois propósitos opostos. Um escore que indica "este atleta concentra
70% dos cartões no 1º tempo" é, ao mesmo tempo, um sinal de integridade — útil para priorizar
auditoria — e um sinal de trading, útil para precificar micro-mercados de cartão. Vendido à
mesa de precificação de uma operadora, o produto deixa de proteger o esporte e passa a dar
vantagem competitiva nos exatos mercados que o projeto identifica como vetor de
vulnerabilidade.

A resposta adotada não é recusar o segmento inteiro: é **restringir granularidade por
finalidade**. E uma cláusula contratual sem controle técnico não se sustenta — por isso a
matriz do termo de uso é executável, e é este módulo que a executa.

Camadas de exposição (alinhadas à tarefa F4-02)
-----------------------------------------------
* **Aberta** — agregados por clube, rodada e temporada. Sem identificação individual.
* **Pseudonimizada** — perfil individual sob identificador estável, sem nome. O identificador
  deriva do registro CBF por HMAC-SHA256 com segredo do projeto: é estável entre execuções,
  permite acompanhar o mesmo atleta ao longo do tempo e não é reversível sem o segredo.
* **Identificada** — nome do atleta. Apenas em ambiente contratado, com finalidade declarada.

Exceção: atletas com condenação transitada em julgado são fato público e podem ser nominados
em qualquer camada. Hoje são os 10 atletas da Operação Penalidade Máxima.

Limitação declarada
-------------------
Este módulo protege as saídas geradas por `serve_product_feed`. Os artefatos já publicados no
repositório — Tabela 16, rankings nominais do relatório 07 — continuam identificados e são
objeto da tarefa F4-02, que faz a varredura retroativa.
"""

import hashlib
import hmac
import os
from typing import Any, Dict, Iterable, Optional

import pandas as pd

# Segredo de pseudonimização. Em produção vem do ambiente; o valor de desenvolvimento existe
# apenas para tornar os testes determinísticos e NÃO protege nada em uso real.
SEGREDO_PSEUDONIMIZACAO = os.environ.get(
    "ANALISE_BETS_PSEUDONIMO_SECRET", "desenvolvimento-nao-usar-em-producao"
)

CAMADA_ABERTA = "aberta"
CAMADA_PSEUDONIMIZADA = "pseudonimizada"
CAMADA_IDENTIFICADA = "identificada"

# Campos que identificam uma pessoa natural. Nenhum deles sai da camada identificada.
CAMPOS_IDENTIFICADORES = (
    "apelido", "atleta", "atleta_slug", "apelido_slug", "nome_completo",
    "registro_cbf", "num_camisa", "atleta_entrou", "atleta_saiu",
    "atleta_entrou_slug", "atleta_saiu_slug",
)

PERFIS: Dict[str, Dict[str, Any]] = {
    "federacao_stjd": {
        "rotulo": "Federação, STJD ou órgão de investigação",
        "atendido": True,
        "camada": CAMADA_IDENTIFICADA,
        "granularidade": ("partida", "atleta"),
        "finalidade": "Auditoria desportiva e instrução de procedimento",
        "restrito_ao_proprio_elenco": False,
    },
    "clube": {
        "rotulo": "Clube",
        "atendido": True,
        "camada": CAMADA_IDENTIFICADA,
        "granularidade": ("atleta",),
        "finalidade": "Compliance interno e due diligence de contratação",
        # O clube só enxerga o próprio elenco e alvos de contratação declarados.
        "restrito_ao_proprio_elenco": True,
    },
    "operadora_integrity": {
        "rotulo": "Operadora — área de integrity ou compliance",
        "atendido": True,
        "camada": CAMADA_ABERTA,
        "granularidade": ("partida",),
        "finalidade": "Monitoramento regulatório e registro de diligência",
        "restrito_ao_proprio_elenco": False,
    },
    "operadora_trading": {
        "rotulo": "Operadora — mesa de trading ou precificação",
        "atendido": False,
        "camada": None,
        "granularidade": (),
        "finalidade": None,
        "motivo_da_recusa": (
            "Fornecer sinal de atipicidade disciplinar a quem precifica micro-mercados de "
            "cartão converteria um instrumento de integridade em vantagem competitiva nos "
            "mercados que o projeto identifica como vetor de vulnerabilidade à manipulação. "
            "A recusa é decisão de posicionamento, registrada na tarefa F4-03."
        ),
        "restrito_ao_proprio_elenco": False,
    },
    "imprensa_academia": {
        "rotulo": "Imprensa e academia",
        "atendido": True,
        "camada": CAMADA_ABERTA,
        "granularidade": ("partida",),
        "finalidade": "Divulgação e pesquisa",
        "restrito_ao_proprio_elenco": False,
    },
}


class PerfilNaoAtendido(PermissionError):
    """Erguida quando um perfil sem atendimento tenta obter dados."""


def perfil_ou_erro(perfil: str) -> Dict[str, Any]:
    if perfil not in PERFIS:
        raise KeyError(f"Perfil desconhecido: {perfil!r}. Conhecidos: {sorted(PERFIS)}")
    config = PERFIS[perfil]
    if not config["atendido"]:
        raise PerfilNaoAtendido(f"{config['rotulo']}: {config['motivo_da_recusa']}")
    return config


def pseudonimizar(registro: Any, segredo: Optional[str] = None) -> str:
    """
    Identificador estável e não reversível a partir do registro CBF.

    HMAC, e não hash simples: o espaço de registros da CBF é pequeno o bastante para que um
    SHA-256 puro fosse revertido por força bruta em minutos.
    """
    chave = (segredo or SEGREDO_PSEUDONIMIZACAO).encode("utf-8")
    mensagem = str(registro).encode("utf-8")
    return "atl_" + hmac.new(chave, mensagem, hashlib.sha256).hexdigest()[:16]


def registros_publicos(caminho_ground_truth: Optional[str] = None) -> set:
    """
    Atletas que podem ser nominados em qualquer camada: condenação transitada em julgado.

    Atleta investigado sem condenação **não** entra aqui, e atleta apenas atípico do ponto de
    vista estatístico muito menos — é o grupo mais numeroso e mais exposto.
    """
    caminho = caminho_ground_truth or os.path.join(
        "data", "processed", "integrity", "casos_penalidade_maxima.parquet")
    if not os.path.exists(caminho):
        return set()
    df = pd.read_parquet(caminho)
    if "situacao_stjd" not in df.columns:
        return set(df["atleta_slug"].unique())
    julgados = df[df["situacao_stjd"].astype(str).str.strip() != ""]
    return set(julgados["atleta_slug"].unique())


def aplicar_perfil(df: pd.DataFrame, perfil: str,
                   clube_do_cliente: Optional[str] = None,
                   slugs_publicos: Optional[Iterable[str]] = None) -> pd.DataFrame:
    """
    Projeta o quadro conforme a camada do perfil.

    Camada identificada devolve o dado como está. Camada pseudonimizada troca os campos de
    identificação por um identificador estável. Camada aberta remove qualquer granularidade
    individual e agrega por clube, temporada e rodada.
    """
    config = perfil_ou_erro(perfil)
    if df.empty:
        return df.copy()

    if config["restrito_ao_proprio_elenco"]:
        if not clube_do_cliente:
            raise ValueError(
                f"O perfil {perfil!r} só recebe dados do próprio elenco: informe clube_do_cliente."
            )
        if "clube_slug" in df.columns:
            df = df[df["clube_slug"] == clube_do_cliente]

    camada = config["camada"]
    if camada == CAMADA_IDENTIFICADA:
        return df.copy()

    if camada == CAMADA_PSEUDONIMIZADA:
        saida = df.copy()
        publicos = set(slugs_publicos or [])
        if "registro_cbf" in saida.columns:
            saida["atleta_pseudonimo"] = saida["registro_cbf"].map(pseudonimizar)
        for coluna in CAMPOS_IDENTIFICADORES:
            if coluna not in saida.columns:
                continue
            if publicos and "atleta_slug" in saida.columns:
                # Condenados com trânsito em julgado seguem nominados: é fato público.
                e_publico = saida["atleta_slug"].isin(publicos)
                saida.loc[~e_publico, coluna] = None
            else:
                saida = saida.drop(columns=[coluna])
        return saida

    # Camada aberta: nenhuma linha individual sobrevive.
    chaves = [c for c in ("serie", "temporada", "rodada", "partida_id", "clube_slug")
              if c in df.columns]
    if not chaves:
        return pd.DataFrame()

    numericas = [c for c in df.select_dtypes("number").columns
                 if c not in chaves and c not in CAMPOS_IDENTIFICADORES]
    agregado = df.groupby(chaves, as_index=False)[numericas].mean().round(6)
    agregado["atletas_no_agregado"] = (
        df.groupby(chaves, as_index=False).size()["size"].to_numpy())
    return agregado


def descrever_matriz() -> pd.DataFrame:
    """Matriz de granularidade por segmento, para publicação junto ao termo de uso."""
    linhas = []
    for chave, config in PERFIS.items():
        linhas.append({
            "perfil": chave,
            "segmento": config["rotulo"],
            "atendido": config["atendido"],
            "camada": config["camada"] or "—",
            "granularidade": ", ".join(config["granularidade"]) or "—",
            "finalidade_permitida": config["finalidade"] or "—",
            "restrito_ao_proprio_elenco": config["restrito_ao_proprio_elenco"],
            "observacao": config.get("motivo_da_recusa", ""),
        })
    return pd.DataFrame(linhas)


if __name__ == "__main__":
    matriz = descrever_matriz()
    destino = os.path.join("reports", "tables", "matriz_de_granularidade_por_segmento.csv")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    matriz.to_csv(destino, index=False, encoding="utf-8")
    print(matriz.drop(columns=["observacao"]).to_string(index=False))
    print("\nPseudonimo de exemplo:", pseudonimizar("123456"))
    print("Atletas nominaveis por condenacao transitada em julgado:", len(registros_publicos()))
