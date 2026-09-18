"""
src/models/score_pre_jogo.py
----------------------------
Escore de risco pré-jogo por atleta escalado (tarefa F3-01).

O que o escore é
----------------
Uma estimativa do **número esperado de cartões no 1º tempo** que cada atleta relacionado
receberá na partida, calculada exclusivamente com informação disponível antes do apito
inicial. Mede **atipicidade estatística do perfil disciplinar**, e nada além disso: um atleta
com estilo de falta tática precoce e um atleta aliciado produzem assinaturas semelhantes. A
finalidade é priorizar atenção, nunca imputar conduta.

Fonte de escalação (decisão registrada)
---------------------------------------
Das três opções previstas na tarefa, adotou-se a **opção 3 — modo retroativo**: a escalação
real da súmula é usada para medir o poder preditivo do modelo antes de assumir dependência de
terceiros. A escolha da fonte de produção (escalação provável de provedor externo, ou elenco
inscrito) permanece em aberto e depende deste resultado. Em produção, o único insumo que muda
é a lista de quem entra em campo; o perfil histórico e o cálculo são idênticos.

Modelo
------
Para cada atleta, a taxa de cartões no 1º tempo por minuto jogado é estimada com encolhimento
bayesiano empírico em direção à taxa populacional:

    taxa_ajustada = (cartoes_1t_previos + M0 * p0) / (minutos_previos + M0)

`M0` é a força do prior, em minutos. Sem ele, um atleta com um único cartão em 20 minutos
jogados teria a maior taxa da liga — o encolhimento resolve o problema de amostra pequena sem
descartar o atleta. O escore é a taxa ajustada multiplicada pelos minutos esperados na
partida, que dependem apenas da condição de titular ou reserva.

Vazamento temporal
------------------
É o maior risco técnico da tarefa. Toda estatística de um atleta usada para pontuar a rodada
`r` vem estritamente de rodadas anteriores a `r` — dentro da temporada e nas temporadas
anteriores da mesma série — inclusive a taxa populacional para a qual o escore encolhe.
`teste_de_vazamento()` corrompe todo o futuro a partir de uma rodada de corte e exige que os
escores anteriores fiquem idênticos.
"""

import os

import numpy as np
import pandas as pd

from src.analysis.escalacoes_e_minutos import minutos_em_campo
from src.pipeline.camadas_de_exposicao import (
    CAMADA_ABERTA,
    DIR_RESTRITO,
    aplicar_camada,
    salvar_mapa_pseudonimos,
)

PROCESSED = os.path.join("data", "processed")
TABLES_DIR = os.path.join("reports", "tables")

# Força do prior, em minutos jogados. 500 minutos equivalem a cerca de cinco partidas
# completas: abaixo disso, o histórico do atleta pesa menos que a taxa populacional.
FORCA_DO_PRIOR_EM_MINUTOS = 500.0

# Minutos esperados em campo, por condição na relação. Estimados na própria base.
MINUTOS_ESPERADOS = {"Titular": 82.0, "Reserva": 13.0}

KS_AVALIADOS = (1, 3, 5, 10)


def carregar_base() -> pd.DataFrame:
    """
    Monta a tabela longa de atleta × partida, com minutos jogados e os cartões recebidos.

    A junção com os eventos é por `(temporada, partida_id, clube_slug, num_camisa)`, e a
    identidade do atleta é o `registro_cbf` — nunca o nome (ver F2-04).
    """
    quadros = []
    for serie in ("a", "b"):
        detalhe = minutos_em_campo(serie)
        if detalhe.empty:
            continue

        caminho_cartoes = os.path.join(PROCESSED, f"serie_{serie}", "cartoes.parquet")
        cartoes = pd.read_parquet(caminho_cartoes)
        cartoes = cartoes[cartoes["temporada"].isin(detalhe["temporada"].unique())].copy()
        cartoes["num_camisa"] = pd.to_numeric(cartoes["num_camisa"], errors="coerce")
        cartoes = cartoes[cartoes["num_camisa"].notna()]
        cartoes["num_camisa"] = cartoes["num_camisa"].astype(int)

        def _chaves(df, filtro=None):
            sel = df if filtro is None else df[filtro]
            return set(zip(sel["temporada"], sel["partida_id"], sel["clube_slug"], sel["num_camisa"]))

        com_cartao = _chaves(cartoes)
        com_cartao_1t = _chaves(cartoes, cartoes["periodo"] == "1T")
        com_cartao_30 = _chaves(cartoes, cartoes["minuto_continuo"] <= 30)

        chaves = list(zip(detalhe["temporada"], detalhe["partida_id"],
                          detalhe["clube_slug"], detalhe["num_camisa"]))
        detalhe = detalhe.copy()
        detalhe["cartao"] = [k in com_cartao for k in chaves]
        detalhe["cartao_1t"] = [k in com_cartao_1t for k in chaves]
        detalhe["cartao_30m"] = [k in com_cartao_30 for k in chaves]
        detalhe["serie"] = serie.upper()
        quadros.append(detalhe)

    base = pd.concat(quadros, ignore_index=True)
    base = base[base["rodada"] > 0]
    return base.sort_values(["serie", "temporada", "rodada", "partida_id"]).reset_index(drop=True)


def _acumulados_anteriores(base: pd.DataFrame) -> pd.DataFrame:
    """
    Acumula, por atleta, o histórico **estritamente anterior** a cada partida.

    A soma acumulada é deslocada em uma posição dentro de cada atleta, de modo que a linha da
    rodada `r` enxerga apenas o que aconteceu até `r-1`. Como a base está ordenada por série,
    temporada e rodada, o deslocamento respeita a cronologia inclusive entre temporadas.
    """
    df = base.sort_values(["serie", "registro_cbf", "temporada", "rodada"]).copy()
    grupo = df.groupby(["serie", "registro_cbf"], sort=False)

    for origem, destino in (("minutos_em_campo", "minutos_previos"),
                            ("cartao_1t", "cartoes_1t_previos"),
                            ("cartao_30m", "cartoes_30m_previos"),
                            ("cartao", "cartoes_previos"),
                            ("participou", "partidas_previas")):
        df[destino] = grupo[origem].transform(lambda s: s.cumsum().shift(1).fillna(0))

    return df


def _taxa_populacional_anterior(df: pd.DataFrame) -> np.ndarray:
    """
    Taxa basal de cartões no 1º tempo por minuto, medida **apenas com rodadas anteriores**.

    Estimá-la sobre a base inteira pareceria inofensivo — é um agregado de liga, sem poder de
    discriminar atletas — mas é informação do futuro entrando no escore do passado, e o teste
    de vazamento a detecta. Aqui ela é acumulada no tempo, como tudo o mais.
    """
    por_rodada = df.groupby(["serie", "temporada", "rodada"], sort=True).agg(
        cartoes=("cartao_1t", "sum"), minutos=("minutos_em_campo", "sum")
    ).reset_index().sort_values(["serie", "temporada", "rodada"])

    acumulado = por_rodada.groupby("serie", sort=False)
    por_rodada["cartoes_ate_aqui"] = acumulado["cartoes"].transform(
        lambda x: x.cumsum().shift(1).fillna(0))
    por_rodada["minutos_ate_aqui"] = acumulado["minutos"].transform(
        lambda x: x.cumsum().shift(1).fillna(0))
    por_rodada["taxa_populacional"] = np.where(
        por_rodada["minutos_ate_aqui"] > 0,
        por_rodada["cartoes_ate_aqui"] / por_rodada["minutos_ate_aqui"],
        0.0,
    )

    chave = ["serie", "temporada", "rodada"]
    return df[chave].merge(por_rodada[chave + ["taxa_populacional"]], on=chave,
                           how="left")["taxa_populacional"].to_numpy()


def calcular_score(base: pd.DataFrame) -> pd.DataFrame:
    """
    Escore pré-jogo: cartões no 1º tempo esperados na partida.

    Não há parâmetro estimado sobre o alvo. A taxa populacional para a qual o escore encolhe é
    ela própria acumulada no tempo, de modo que a pontuação de uma rodada não depende de
    nenhuma informação posterior a ela.
    """
    df = _acumulados_anteriores(base)
    df["taxa_populacional"] = _taxa_populacional_anterior(df)

    df["taxa_1t_ajustada"] = (
        (df["cartoes_1t_previos"] + FORCA_DO_PRIOR_EM_MINUTOS * df["taxa_populacional"])
        / (df["minutos_previos"] + FORCA_DO_PRIOR_EM_MINUTOS)
    )
    df["minutos_esperados"] = df["condicao"].map(MINUTOS_ESPERADOS).fillna(0.0)
    df["score_pre_jogo"] = (df["taxa_1t_ajustada"] * df["minutos_esperados"]).round(8)

    # Linha de base ingênua exigida pela DoD: ranquear por cartões acumulados.
    df["baseline_cartoes_acumulados"] = df["cartoes_previos"]
    return df


def _precisao_em_k(grupo: pd.DataFrame, coluna: str, k: int) -> tuple[int, int]:
    """Acertos entre os k primeiros do ranking, com desempate estável."""
    topo = grupo.sort_values([coluna, "minutos_esperados"], ascending=False).head(k)
    return int(topo["cartao_1t"].sum()), len(topo)


def avaliar_walk_forward(df: pd.DataFrame, rodada_minima: int = 6) -> pd.DataFrame:
    """
    Avalia o escore rodada a rodada, comparando com a linha de base e com o acaso.

    As primeiras rodadas de cada temporada são descartadas (`rodada_minima`): antes disso quase
    não há histórico, e o escore é praticamente a taxa populacional para todos.
    """
    alvo = df[df["rodada"] >= rodada_minima]
    linhas = []

    for k in KS_AVALIADOS:
        for coluna, rotulo in (("score_pre_jogo", "Escore pré-jogo"),
                               ("baseline_cartoes_acumulados", "Linha de base (cartões acumulados)")):
            acertos = inspecionados = 0
            rodadas = 0
            for _, grupo in alvo.groupby(["serie", "temporada", "rodada"], sort=False):
                a, n = _precisao_em_k(grupo, coluna, k)
                acertos += a
                inspecionados += n
                rodadas += 1
            taxa_base = float(alvo["cartao_1t"].mean())
            precisao = acertos / inspecionados if inspecionados else np.nan
            linhas.append({
                "k": k,
                "criterio": rotulo,
                "rodadas_avaliadas": rodadas,
                "atletas_inspecionados": inspecionados,
                "acertos": acertos,
                "precisao_at_k": round(precisao, 4),
                "taxa_base_da_populacao": round(taxa_base, 4),
                "ganho_sobre_o_acaso": round(precisao / taxa_base, 2) if taxa_base else np.nan,
            })

    return pd.DataFrame(linhas)


def teste_de_vazamento(base: pd.DataFrame, fracao_de_corte: float = 0.7) -> pd.DataFrame:
    """
    Verifica, de forma determinística, que o escore de uma rodada não depende do futuro.

    O corte é feito sobre a **ordem cronológica global** de cada série — o par
    `(temporada, rodada)` transformado em posição —, e não sobre o número da rodada: com várias
    temporadas na base, a rodada 10 de 2023 vem depois da rodada 30 de 2022, e cortar por
    número de rodada misturaria passado com futuro.

    Todo o alvo a partir do corte é corrompido, e os escores anteriores têm de ficar idênticos,
    bit a bit. Se alguma informação posterior vazasse, eles mudariam.

    Este teste substitui o embaralhamento da ordem temporal previsto na tarefa, que não
    discrimina: ao destruir a cronologia, o embaralhamento **dá** ao modelo acesso a partidas
    futuras, e o desempenho sobe em vez de cair. A comparação segue disponível em
    `comparar_com_ordem_embaralhada()`, como diagnóstico, não como guarda.
    """
    df = base.copy()
    momentos = (df[["serie", "temporada", "rodada"]].drop_duplicates()
                .sort_values(["serie", "temporada", "rodada"]))
    momentos["ordem"] = momentos.groupby("serie").cumcount()
    momentos["total"] = momentos.groupby("serie")["ordem"].transform("max") + 1
    momentos["depois_do_corte"] = momentos["ordem"] >= (momentos["total"] * fracao_de_corte).astype(int)

    df = df.merge(momentos[["serie", "temporada", "rodada", "depois_do_corte"]],
                  on=["serie", "temporada", "rodada"], how="left")

    corrompida = df.copy()
    corrompida.loc[corrompida["depois_do_corte"], ["cartao", "cartao_1t", "cartao_30m"]] = True

    chaves = ["serie", "temporada", "rodada", "partida_id", "clube_slug", "num_camisa"]
    antes = ~df["depois_do_corte"]

    original = calcular_score(df.drop(columns=["depois_do_corte"]))
    alterada = calcular_score(corrompida.drop(columns=["depois_do_corte"]))

    marcador = df.set_index(chaves)["depois_do_corte"]
    a = original.set_index(chaves)["score_pre_jogo"]
    b = alterada.set_index(chaves)["score_pre_jogo"]
    comparaveis = marcador[~marcador].index
    a = a.loc[comparaveis].sort_index()
    b = b.loc[comparaveis].sort_index()

    divergentes = int((a != b).sum())

    return pd.DataFrame([{
        "teste": "Escores anteriores ao corte não mudam quando o futuro é corrompido",
        "fracao_de_corte": fracao_de_corte,
        "rodadas_antes_do_corte": int(antes.sum()),
        "linhas_comparadas": len(a),
        "linhas_divergentes": divergentes,
        "aprovado": divergentes == 0,
    }])


def comparar_com_ordem_embaralhada(base: pd.DataFrame, semente: int = 42) -> pd.DataFrame:
    """
    Diagnóstico: reexecuta a avaliação com a cronologia embaralhada.

    Serve para mostrar **por que** o embaralhamento não funciona como guarda de vazamento: com
    a ordem destruída, a janela "anterior" de cada atleta passa a conter partidas futuras, e o
    desempenho tende a subir. É informação útil, mas não é um teste que reprove vazamento.
    """
    rng = np.random.RandomState(semente)
    embaralhada = base.copy()
    permutacao = rng.permutation(len(embaralhada))
    for coluna in ("temporada", "rodada", "partida_id"):
        embaralhada[coluna] = embaralhada[coluna].to_numpy()[permutacao]
    embaralhada = embaralhada.sort_values(
        ["serie", "temporada", "rodada", "partida_id"]).reset_index(drop=True)
    return avaliar_walk_forward(calcular_score(embaralhada))


def ranking_por_partida(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """Saída de produto: os atletas de maior escore em cada partida."""
    colunas = ["serie", "temporada", "rodada", "partida_id", "clube_slug", "num_camisa",
               "apelido", "registro_cbf", "condicao", "minutos_previos", "cartoes_1t_previos",
               "taxa_1t_ajustada", "score_pre_jogo"]
    ordenado = df.sort_values(["serie", "temporada", "rodada", "partida_id", "score_pre_jogo"],
                              ascending=[True, True, True, True, False])
    return ordenado.groupby(["serie", "temporada", "partida_id"], sort=False).head(top_n)[colunas]


def executar():
    base = carregar_base()
    df = calcular_score(base)
    avaliacao = avaliar_walk_forward(df)
    vazamento = teste_de_vazamento(base)
    embaralhado = comparar_com_ordem_embaralhada(base)
    ranking = ranking_por_partida(df)

    os.makedirs(TABLES_DIR, exist_ok=True)
    avaliacao.to_csv(os.path.join(TABLES_DIR, "tabela_23_score_pre_jogo_avaliacao.csv"),
                     index=False, encoding="utf-8")
    vazamento.to_csv(os.path.join(TABLES_DIR, "tabela_23b_score_pre_jogo_teste_vazamento.csv"),
                     index=False, encoding="utf-8")
    embaralhado.to_csv(os.path.join(TABLES_DIR, "tabela_23d_score_pre_jogo_ordem_embaralhada.csv"),
                       index=False, encoding="utf-8")

    # F4-02: o quadro completo associa NOME a inferencia de risco. A versao versionada sai
    # pseudonimizada; a identificada vai para data/restrito/, fora do repositorio. Fatos
    # desportivos que a CBF publica — escalacao, cartoes — seguem nominados nas bases; o que
    # nao pode circular com nome e a inferencia que o projeto produz SOBRE a pessoa.
    destino = os.path.join(PROCESSED, "integrity")
    os.makedirs(destino, exist_ok=True)
    os.makedirs(DIR_RESTRITO, exist_ok=True)
    df.to_parquet(os.path.join(DIR_RESTRITO, "score_pre_jogo_identificado.parquet"), index=False)
    aplicar_camada(df, CAMADA_ABERTA).to_parquet(
        os.path.join(destino, "score_pre_jogo.parquet"), index=False)
    # F4-02: o ranking pre-jogo nomeia todo atleta relacionado. A versao publicada sai
    # pseudonimizada; o mapa de reidentificacao fica em data/restrito/.
    salvar_mapa_pseudonimos(ranking)
    aplicar_camada(ranking, CAMADA_ABERTA).to_csv(
        os.path.join(TABLES_DIR, "tabela_23c_score_pre_jogo_ranking.csv"),
        index=False, encoding="utf-8")

    return df, avaliacao, vazamento, embaralhado, ranking


if __name__ == "__main__":
    df, avaliacao, vazamento, embaralhado, ranking = executar()

    print("\n=== ESCORE PRE-JOGO — AVALIACAO WALK-FORWARD ===")
    print(avaliacao.to_string(index=False))

    print("\n=== TESTE DE VAZAMENTO (corrupcao do futuro) ===")
    print(vazamento.to_string(index=False))

    print("\n=== DIAGNOSTICO: ORDEM TEMPORAL EMBARALHADA ===")
    comparacao = avaliacao.merge(embaralhado, on=["k", "criterio"], suffixes=("_real", "_embaralhado"))
    print(comparacao[["k", "criterio", "ganho_sobre_o_acaso_real",
                      "ganho_sobre_o_acaso_embaralhado"]].to_string(index=False))

    print(f"\nRegistros pontuados: {len(df)} | taxa populacional de cartao no 1T por minuto: "
          f"{df['taxa_populacional'].mean():.6f}")
