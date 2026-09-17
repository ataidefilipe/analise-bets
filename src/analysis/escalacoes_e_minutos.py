"""
src/analysis/escalacoes_e_minutos.py
------------------------------------
Qualidade da extração de escalações e derivação de minutos em campo (tarefa F2-04).

Três entregas:

1. **Taxa de extração por temporada** — quantas partidas têm relação de atletas, e quantas
   ficaram sem. Súmulas com layout não reconhecido são listadas, não silenciadas.
2. **Consistência com os eventos** — todo atleta que recebeu cartão ou marcou gol numa partida
   precisa constar da relação daquela partida. As divergências são listadas.
3. **Minutos em campo por atleta-temporada** — escalação cruzada com substituições. Corrige uma
   limitação conhecida do `ATHLETE_ANOMALY_SCORE`, que usa a minutagem do cartão como proxy de
   exposição em vez do tempo real em campo.

Chave de junção
---------------
O cruzamento entre escalação, cartões e substituições usa `(partida_id, clube_slug,
num_camisa)`, e **não** o nome. A coluna de nome completo da súmula é truncada pela largura da
coluna em cerca de 40% dos registros; o número da camisa e o registro CBF são as identificações
confiáveis. Essa é também a saída para o problema de identidade encontrado na F1-03.

Saídas:
  data/processed/serie_{a,b}/minutos_em_campo.parquet e .csv
  reports/tables/qualidade_escalacoes.csv
  reports/tables/divergencias_escalacao_eventos.csv
"""

import os

import numpy as np
import pandas as pd


def numpy_divide(numerador, denominador):
    """Divisao que devolve NaN onde o denominador e zero, em vez de erro ou infinito."""
    return pd.Series(
        np.divide(numerador.to_numpy(dtype=float), denominador.to_numpy(dtype=float),
                  out=np.full(len(numerador), np.nan), where=denominador.to_numpy() > 0),
        index=numerador.index,
    ).round(1)

PROCESSED = os.path.join("data", "processed")
TABLES_DIR = os.path.join("reports", "tables")

DURACAO_NOMINAL = 90


def _ler(serie: str, nome: str) -> pd.DataFrame:
    caminho = os.path.join(PROCESSED, f"serie_{serie}", f"{nome}.parquet")
    return pd.read_parquet(caminho) if os.path.exists(caminho) else pd.DataFrame()


def taxa_de_extracao() -> pd.DataFrame:
    """Cobertura da relação de atletas, por série e temporada."""
    linhas = []
    for serie in ("a", "b"):
        partidas = _ler(serie, "partidas")
        escalacoes = _ler(serie, "escalacoes")
        if partidas.empty:
            continue

        com_escalacao = set()
        if not escalacoes.empty:
            com_escalacao = set(zip(escalacoes["temporada"], escalacoes["partida_id"]))

        for temporada, g in partidas.groupby("temporada"):
            chaves = set(zip(g["temporada"], g["partida_id"]))
            cobertas = chaves & com_escalacao
            atletas = 0
            if not escalacoes.empty:
                sel = escalacoes[escalacoes["temporada"] == temporada]
                atletas = len(sel)
            linhas.append({
                "serie": serie.upper(),
                "temporada": int(temporada),
                "partidas": len(g),
                "partidas_com_escalacao": len(cobertas),
                "pct_extraido": round(len(cobertas) / len(g) * 100, 1),
                "atletas_relacionados": atletas,
                "media_por_partida": round(atletas / len(cobertas), 1) if cobertas else 0.0,
                "fonte": "Súmula CBF" if cobertas else "Sem súmula disponível",
            })
    return pd.DataFrame(linhas).sort_values(["serie", "temporada"]).reset_index(drop=True)


def partidas_sem_escalacao() -> pd.DataFrame:
    """
    Partidas de temporada coberta por súmula cujo layout não foi reconhecido pelo parser.

    A DoD da F2-04 exige que essas partidas sejam listadas, e não silenciadas: sem a lista, uma
    queda de cobertura passa despercebida na próxima ingestão.
    """
    linhas = []
    for serie in ("a", "b"):
        partidas = _ler(serie, "partidas")
        escalacoes = _ler(serie, "escalacoes")
        if partidas.empty or escalacoes.empty:
            continue
        cobertas = set(zip(escalacoes["temporada"], escalacoes["partida_id"]))
        temporadas = set(escalacoes["temporada"].unique())
        alvo = partidas[partidas["temporada"].isin(temporadas)]
        for _, r in alvo.iterrows():
            if (r["temporada"], r["partida_id"]) in cobertas:
                continue
            linhas.append({
                "serie": serie.upper(),
                "temporada": int(r["temporada"]),
                "partida_id": int(r["partida_id"]),
                "rodada": r.get("rodada"),
                "data": r.get("data"),
                "confronto": f"{r.get('clube_mandante','')} x {r.get('clube_visitante','')}",
                # A relação de atletas fica na primeira página da súmula. Quando ela falta,
                # faltam também o cabeçalho, os clubes e a rodada — sinal de PDF incompleto
                # na origem, e não de layout desconhecido.
                "motivo": ("Súmula incompleta na origem (primeira página ausente)"
                           if not str(r.get("clube_mandante", "")).strip()
                           else "Layout da relação de atletas não reconhecido"),
            })
    return pd.DataFrame(linhas)


def divergencias_com_eventos() -> pd.DataFrame:
    """
    Atletas com cartão ou gol que não constam da relação da própria partida.

    A junção é por número de camisa dentro do clube — o nome não serve, porque a súmula trunca
    o nome completo na relação e o escreve por extenso nos eventos.
    """
    linhas = []
    for serie in ("a", "b"):
        escalacoes = _ler(serie, "escalacoes")
        if escalacoes.empty:
            continue
        relacionados = set(zip(escalacoes["temporada"], escalacoes["partida_id"],
                               escalacoes["clube_slug"], escalacoes["num_camisa"]))
        temporadas_cobertas = set(escalacoes["temporada"].unique())

        for nome_evento in ("cartoes", "gols"):
            eventos = _ler(serie, nome_evento)
            if eventos.empty or "num_camisa" not in eventos.columns:
                continue
            eventos = eventos[eventos["temporada"].isin(temporadas_cobertas)].copy()
            eventos["num_camisa"] = pd.to_numeric(eventos["num_camisa"], errors="coerce")
            eventos = eventos[eventos["num_camisa"].notna()]

            for _, r in eventos.iterrows():
                chave = (r["temporada"], r["partida_id"], r["clube_slug"], int(r["num_camisa"]))
                if chave not in relacionados:
                    linhas.append({
                        "serie": serie.upper(), "evento": nome_evento,
                        "temporada": int(r["temporada"]), "partida_id": int(r["partida_id"]),
                        "clube_slug": r["clube_slug"], "num_camisa": int(r["num_camisa"]),
                        "atleta": r.get("atleta", ""),
                    })
    return pd.DataFrame(linhas)


def minutos_em_campo(serie: str) -> pd.DataFrame:
    """
    Minutos em campo por atleta e partida, a partir da escalação e das substituições.

    Titular que não sai joga a partida inteira; titular substituído joga até o minuto da
    substituição; reserva que entra joga do minuto de entrada ao fim; reserva que não entra
    fica com zero. A duração é a nominal de 90 minutos — acréscimos não são distribuídos por
    atleta, porque a súmula não os atribui individualmente.
    """
    escalacoes = _ler(serie, "escalacoes")
    subs = _ler(serie, "substituicoes")
    if escalacoes.empty:
        return pd.DataFrame()

    saidas, entradas = {}, {}
    if not subs.empty:
        for _, r in subs.iterrows():
            chave = (r["temporada"], r["partida_id"], r["clube_slug"])
            minuto = min(int(r["minuto_continuo"]), DURACAO_NOMINAL)
            saidas[chave + (int(r["num_saiu"]),)] = minuto
            entradas[chave + (int(r["num_entrou"]),)] = minuto

    df = escalacoes.copy()
    chaves = list(zip(df["temporada"], df["partida_id"], df["clube_slug"], df["num_camisa"]))

    minutos, entrou, saiu = [], [], []
    for (chave, condicao, presente) in zip(chaves, df["condicao"], df["presente"]):
        m_saida = saidas.get(chave)
        m_entrada = entradas.get(chave)
        entrou.append(m_entrada is not None)
        saiu.append(m_saida is not None)

        if not presente:
            minutos.append(0)
        elif condicao == "Titular":
            minutos.append(m_saida if m_saida is not None else DURACAO_NOMINAL)
        elif m_entrada is not None:
            fim = m_saida if m_saida is not None else DURACAO_NOMINAL
            minutos.append(max(0, fim - m_entrada))
        else:
            minutos.append(0)

    df["minutos_em_campo"] = minutos
    df["entrou_como_substituto"] = entrou
    df["foi_substituido"] = saiu
    df["participou"] = df["minutos_em_campo"] > 0
    return df


def consolidar_por_atleta_temporada(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega os minutos por atleta e temporada — o denominador que faltava ao escore."""
    if df.empty:
        return pd.DataFrame()
    # A chave e o registro CBF, nao o nome: dois atletas podem dividir o mesmo apelido no
    # mesmo elenco (ha um "Marcos Paulo" de camisa 10 e outro de camisa 47 no Juventude de
    # 2026). Agrupar por nome os fundiria num unico atleta com mais jogos do que a temporada
    # tem rodadas — a mesma confusao de identidade que a F1-03 encontrou no ground truth.
    agg = df.groupby(["temporada", "serie", "clube_slug", "registro_cbf"]).agg(
        apelido=("apelido", "first"),
        atleta_slug=("atleta_slug", "first"),
        num_camisa=("num_camisa", "first"),
        partidas_relacionado=("partida_id", "nunique"),
        partidas_jogadas=("participou", "sum"),
        partidas_como_titular=("condicao", lambda s: (s == "Titular").sum()),
        minutos_em_campo=("minutos_em_campo", "sum"),
    ).reset_index()
    jogadas = pd.to_numeric(agg["partidas_jogadas"], errors="coerce").fillna(0).astype(int)
    minutos = pd.to_numeric(agg["minutos_em_campo"], errors="coerce").fillna(0).astype(int)
    agg["partidas_jogadas"] = jogadas
    agg["minutos_em_campo"] = minutos
    agg["partidas_como_titular"] = pd.to_numeric(
        agg["partidas_como_titular"], errors="coerce").fillna(0).astype(int)
    # Atleta relacionado que nunca entrou tem media indefinida, nao zero.
    agg["media_minutos_por_jogo"] = numpy_divide(minutos, jogadas)
    return agg.sort_values(["temporada", "serie", "minutos_em_campo"], ascending=[True, True, False])


def executar():
    os.makedirs(TABLES_DIR, exist_ok=True)

    taxa = taxa_de_extracao()
    taxa.to_csv(os.path.join(TABLES_DIR, "qualidade_escalacoes.csv"), index=False, encoding="utf-8")

    sem_escalacao = partidas_sem_escalacao()
    sem_escalacao.to_csv(os.path.join(TABLES_DIR, "partidas_sem_escalacao.csv"),
                         index=False, encoding="utf-8")

    divergencias = divergencias_com_eventos()
    if not divergencias.empty and not sem_escalacao.empty:
        sem = set(zip(sem_escalacao["serie"], sem_escalacao["temporada"], sem_escalacao["partida_id"]))
        divergencias["partida_sem_escalacao"] = [
            (x, t, pid) in sem for x, t, pid in
            zip(divergencias["serie"], divergencias["temporada"], divergencias["partida_id"])
        ]
    divergencias.to_csv(os.path.join(TABLES_DIR, "divergencias_escalacao_eventos.csv"),
                        index=False, encoding="utf-8")

    consolidados = {}
    for serie in ("a", "b"):
        detalhe = minutos_em_campo(serie)
        if detalhe.empty:
            continue
        agg = consolidar_por_atleta_temporada(detalhe)
        destino = os.path.join(PROCESSED, f"serie_{serie}")
        agg.to_parquet(os.path.join(destino, "minutos_em_campo.parquet"), index=False)
        agg.to_csv(os.path.join(destino, "minutos_em_campo.csv"), index=False, encoding="utf-8")
        consolidados[serie.upper()] = agg

    return taxa, divergencias, consolidados, sem_escalacao


if __name__ == "__main__":
    taxa, divergencias, consolidados, sem_escalacao = executar()
    print("\n=== TAXA DE EXTRACAO DA RELACAO DE ATLETAS ===")
    print(taxa.to_string(index=False))

    print(f"\n=== PARTIDAS SEM RELACAO DE ATLETAS ===")
    if sem_escalacao.empty:
        print("Nenhuma: todas as partidas de temporada com sumula tiveram a relacao extraida.")
    else:
        print(sem_escalacao[["serie", "temporada", "partida_id", "confronto"]].to_string(index=False))

    print(f"\n=== CONSISTENCIA COM OS EVENTOS ===")
    if divergencias.empty:
        print("Nenhuma divergencia: todo atleta com cartao ou gol consta da relacao da partida.")
    else:
        reais = divergencias[~divergencias.get("partida_sem_escalacao", False)]
        print(f"{len(divergencias)} divergencias, das quais {len(reais)} em partidas "
              f"cuja relacao FOI extraida (as demais decorrem de layout nao reconhecido):")
        if not reais.empty:
            print(reais[["serie", "temporada", "partida_id", "clube_slug", "num_camisa", "atleta"]].to_string(index=False))

    print("\n=== MINUTOS EM CAMPO (atleta x temporada) ===")
    for serie, agg in consolidados.items():
        print(f"Serie {serie}: {len(agg)} registros | mediana de minutos: "
              f"{agg['minutos_em_campo'].median():.0f}")
        print(agg.head(3)[["temporada", "apelido", "clube_slug", "partidas_jogadas",
                           "minutos_em_campo", "media_minutos_por_jogo"]].to_string(index=False))
