"""
src/models/ground_truth_resolver.py
-----------------------------------
Resolvedor de identidade entre o ground truth da Operação Penalidade Máxima e a base
harmonizada de partidas, cartões e atletas (tarefa F1-03, item B.1).

Motivação
---------
A versão anterior cruzava os 14 casos com a base por correspondência parcial de nome
(`str.contains` do primeiro token do slug) seguida do primeiro registro encontrado, sem filtrar
por série ou clube. O procedimento associava atletas errados na maioria dos casos — o percentil
de 99,67% atribuído a "Nino Paraíba (Ceará)" pertencia, na verdade, a "Nino (Fluminense)".

Este módulo substitui aquela heurística por um **mapa explícito, auditável e testado**, em que
cada associação carrega a evidência que a sustenta e o seu grau de confiança. Casos que não
podem ser resolvidos com segurança são marcados como `nao_resolvido` — e não adivinhados.

Uso
---
    from src.models.ground_truth_resolver import resolver_ground_truth
    partidas, atletas = resolver_ground_truth(df_matches, df_cards, df_athletes, df_pm)
"""

import os
import pandas as pd

TABLES_DIR = os.path.join("reports", "tables")

# =============================================================================
# 1. MAPA DE IDENTIDADE DOS ATLETAS
# -----------------------------------------------------------------------------
# Chave: `atleta_slug` como consta no ground truth.
# Valor: identificação na base harmonizada, mais a evidência que sustenta a associação.
#
# `confianca`:
#   alta          — slug exato na base, ou evento do ground truth confirmado na súmula.
#   media         — único candidato plausível no clube e temporada, sem confirmação de evento.
#   nao_resolvido — nenhum candidato defensável; o caso é excluído das métricas de atleta.
# =============================================================================

MAPA_IDENTIDADE_ATLETAS = {
    "paulo_miranda": {
        "atleta_slug": "paulo_miranda", "clube_slug": "juventude", "serie": "A", "temporada": 2022,
        "confianca": "alta",
        "evidencia": "Slug idêntico ao do ground truth, no clube e temporada corretos (5 cartões em 2022).",
    },
    "nino_paraiba": {
        "atleta_slug": "nino_paraiba", "clube_slug": "ceara", "serie": "A", "temporada": 2022,
        "confianca": "alta",
        "evidencia": "Slug idêntico, clube correto (11 cartões em 2022). Não confundir com 'nino' (Fluminense), "
                     "atleta sem relação com a operação e que a heurística anterior selecionava.",
    },
    "gabriel_tota": {
        "atleta_slug": "gabriel_tota", "clube_slug": "juventude", "serie": "A", "temporada": 2022,
        "confianca": "alta",
        "evidencia": "Slug idêntico, clube correto. Possui apenas 2 cartões em 2022, abaixo do mínimo de 3 "
                     "exigido pelo ATHLETE_ANOMALY_SCORE — presente nos cartões, ausente da base pontuada.",
    },
    "eduardo_bauermann": {
        "atleta_slug": "eduardo", "clube_slug": "santos", "serie": "A", "temporada": 2022,
        "confianca": "alta",
        "evidencia": "A fonte da Série A registra o atleta pelo nome curto 'Eduardo'. Confirmado pelo evento: "
                     "cartão vermelho aos 93' na rodada 37 (Botafogo x Santos), exatamente o incidente PM-011.",
    },
    "mateusinho": {
        "atleta_slug": "mateus_da_silva_duarte", "clube_slug": "sampaio_correa", "serie": "B", "temporada": 2022,
        "confianca": "alta",
        "evidencia": "Nome civil do atleta conhecido como 'Mateusinho', único no clube e temporada (7 cartões).",
    },
    "joseph": {
        "atleta_slug": "joseph_mauricio_de_oliveira_figueiredo", "clube_slug": "tombense", "serie": "B", "temporada": 2022,
        "confianca": "alta",
        "evidencia": "Único atleta chamado Joseph no Tombense em 2022 (4 cartões).",
    },
    "moraes_jr": {
        "atleta_slug": "onitlasi_junior_de_moraes_rodrigues", "clube_slug": "juventude", "serie": "A", "temporada": 2022,
        "confianca": "media",
        "evidencia": "Único atleta com 'Moraes' e 'Júnior' no nome, no Juventude em 2022 (4 cartões). "
                     "Sem confirmação por evento: o cartão registrado está aos 5' e o ground truth indica 31'.",
    },
    "ygor_catatau": {
        "atleta_slug": "ygor_de_oliveira_ferreira", "clube_slug": "sampaio_correa", "serie": "B", "temporada": 2022,
        "confianca": "media",
        "evidencia": "Único 'Ygor' no Sampaio Corrêa em 2022 (3 cartões). O apelido 'Catatau' não consta da base, "
                     "e o evento do ground truth é um pênalti cometido, que não deixa registro de cartão.",
    },
    "romario": {
        "atleta_slug": None, "clube_slug": "vila_nova", "serie": "B", "temporada": 2022,
        "confianca": "nao_resolvido",
        "evidencia": "Nenhum atleta chamado Romário recebeu cartão pelo Vila Nova em 2022. Coerente com o caso: "
                     "o atleta não foi escalado na partida-alvo e a fraude não se consumou.",
    },
    "igor_carius": {
        "atleta_slug": None, "clube_slug": "cuiaba", "serie": "A", "temporada": 2022,
        "confianca": "nao_resolvido",
        "evidencia": "Não há nenhum 'Cariús' na base em 2022, em qualquer série. O único Igor do Cuiabá é "
                     "'Igor Aquino da Silva', atacante — o ground truth descreve um lateral-esquerdo. "
                     "A heurística anterior associava 'Igor Marques Paciência Cardoso' (Ponte Preta, Série B).",
    },
}

# =============================================================================
# 2. CORREÇÕES DE PARTIDA
# -----------------------------------------------------------------------------
# Casos em que os metadados de rodada/data do ground truth não correspondem ao calendário
# oficial da competição na base harmonizada.
# =============================================================================

CORRECOES_PARTIDA = {
    "PM-005": {
        "rodada": 31,
        "evidencia": "O ground truth registra 'Náutico x Sampaio Corrêa' na rodada 23 (2022-08-10), mas naquela "
                     "rodada o Náutico enfrentou o CRB. O único Náutico x Sampaio Corrêa da Série B 2022 é o da "
                     "rodada 31 (2022-09-23). Sem a correção, o caso era pontuado contra uma partida que o "
                     "Sampaio Corrêa não disputou.",
    },
}


def _slug_clube(nome: str) -> str:
    return nome.lower().replace(" ", "_").replace("-", "_")


def resolver_partidas(df_matches: pd.DataFrame, df_pm: pd.DataFrame) -> pd.DataFrame:
    """
    Resolve cada caso do ground truth para uma partida da base, exigindo coincidência de série,
    temporada, rodada e **ambos** os clubes — não apenas o prefixo do mandante.
    """
    linhas = []
    for _, caso in df_pm.iterrows():
        rodada = CORRECOES_PARTIDA.get(caso["caso_id"], {}).get("rodada", caso["rodada"])
        mandante = _slug_clube(caso["clube_mandante"])[:5]
        visitante = _slug_clube(caso["clube_visitante"])[:5]

        candidatas = df_matches[
            (df_matches["serie"] == caso["serie"]) &
            (df_matches["temporada"] == caso["temporada"]) &
            (df_matches["rodada"] == rodada) &
            (df_matches["clube_mandante_slug"].str.startswith(mandante, na=False)) &
            (df_matches["clube_visitante_slug"].str.startswith(visitante, na=False))
        ]

        if len(candidatas) == 1:
            partida = candidatas.iloc[0]
            status = "resolvido_corrigido" if caso["caso_id"] in CORRECOES_PARTIDA else "resolvido"
            linhas.append({
                "caso_id": caso["caso_id"], "serie": caso["serie"], "temporada": caso["temporada"],
                "rodada_ground_truth": caso["rodada"], "rodada_utilizada": rodada,
                "confronto": caso["confronto"], "partida_id": partida["partida_id"],
                "status_partida": status,
            })
        else:
            linhas.append({
                "caso_id": caso["caso_id"], "serie": caso["serie"], "temporada": caso["temporada"],
                "rodada_ground_truth": caso["rodada"], "rodada_utilizada": rodada,
                "confronto": caso["confronto"], "partida_id": None,
                "status_partida": "ambiguo" if len(candidatas) > 1 else "nao_encontrado",
            })

    return pd.DataFrame(linhas)


def resolver_atletas(df_cards: pd.DataFrame, df_athletes: pd.DataFrame, df_pm: pd.DataFrame) -> pd.DataFrame:
    """
    Resolve cada atleta do ground truth para o seu registro de atleta-temporada, distinguindo
    três situações: resolvido, presente nos cartões mas abaixo do mínimo de pontuação, e não
    resolvido.
    """
    linhas = []
    for slug_gt in df_pm["atleta_slug"].unique():
        casos = df_pm[df_pm["atleta_slug"] == slug_gt]
        nome_gt = casos.iloc[0]["atleta"]
        mapa = MAPA_IDENTIDADE_ATLETAS.get(slug_gt)

        if mapa is None:
            linhas.append({
                "atleta_ground_truth": nome_gt, "atleta_slug_ground_truth": slug_gt,
                "atleta_slug_base": None, "clube_slug": None, "serie": None, "temporada": None,
                "cartoes_na_temporada": 0, "status_atleta": "nao_mapeado", "confianca": "nao_resolvido",
                "casos": ", ".join(casos["caso_id"]),
                "evidencia": "Slug ausente do MAPA_IDENTIDADE_ATLETAS.",
            })
            continue

        slug_base = mapa["atleta_slug"]
        registro = {
            "atleta_ground_truth": nome_gt, "atleta_slug_ground_truth": slug_gt,
            "atleta_slug_base": slug_base, "clube_slug": mapa["clube_slug"],
            "serie": mapa["serie"], "temporada": mapa["temporada"],
            "casos": ", ".join(casos["caso_id"]), "confianca": mapa["confianca"],
            "evidencia": mapa["evidencia"],
        }

        if slug_base is None:
            registro.update({"cartoes_na_temporada": 0, "status_atleta": "nao_resolvido"})
            linhas.append(registro)
            continue

        cartoes = df_cards[
            (df_cards["serie"] == mapa["serie"]) &
            (df_cards["temporada"] == mapa["temporada"]) &
            (df_cards["clube_slug"] == mapa["clube_slug"]) &
            (df_cards["atleta_slug"] == slug_base)
        ]
        pontuado = df_athletes[
            (df_athletes["serie"] == mapa["serie"]) &
            (df_athletes["temporada"] == mapa["temporada"]) &
            (df_athletes["atleta_slug"] == slug_base)
        ]

        if len(pontuado) > 0:
            status = "resolvido"
        elif len(cartoes) > 0:
            status = "abaixo_do_minimo_de_cartoes"
        else:
            status = "ausente_da_base"

        registro.update({"cartoes_na_temporada": len(cartoes), "status_atleta": status})
        linhas.append(registro)

    return pd.DataFrame(linhas)


def verificar_eventos(df_cards: pd.DataFrame, partidas: pd.DataFrame,
                      atletas: pd.DataFrame, df_pm: pd.DataFrame) -> pd.DataFrame:
    """
    Verifica, caso a caso, se o evento descrito pelo ground truth esta registrado na sumula.

    E o teste de ancoragem mais forte disponivel: um rotulo positivo cujo evento definidor nao
    aparece na base nao pode ser usado para calibrar nem para avaliar um detector desse evento.
    Eventos de penalti cometido nao deixam registro de cartao e sao marcados como
    `nao_verificavel` — a ausencia, neles, nao e evidencia de erro.
    """
    mapa_partida = partidas.set_index("caso_id")["partida_id"].to_dict()
    mapa_atleta = atletas.set_index("atleta_slug_ground_truth")["atleta_slug_base"].to_dict()

    linhas = []
    for _, caso in df_pm.iterrows():
        pid = mapa_partida.get(caso["caso_id"])
        slug = mapa_atleta.get(caso["atleta_slug"])
        evento = str(caso["evento_alvo"])
        registro = {
            "caso_id": caso["caso_id"], "atleta": caso["atleta"], "evento_alvo": evento,
            "minuto_ground_truth": caso["minuto_real"], "evento_ocorreu": caso["evento_ocorreu"],
        }

        if "penalti" in evento:
            registro.update({"minuto_na_base": None, "status_evento": "nao_verificavel",
                             "observacao": "Penalti cometido nao gera registro de cartao na sumula."})
        elif not caso["evento_ocorreu"]:
            registro.update({"minuto_na_base": None, "status_evento": "nao_aplicavel",
                             "observacao": "O evento combinado nao se consumou em campo."})
        elif pid is None or slug is None:
            registro.update({"minuto_na_base": None, "status_evento": "nao_verificavel",
                             "observacao": "Partida ou atleta nao resolvido."})
        else:
            achados = df_cards[(df_cards["serie"] == caso["serie"]) &
                               (df_cards["temporada"] == caso["temporada"]) &
                               (df_cards["partida_id"] == pid) &
                               (df_cards["atleta_slug"] == slug)]
            if len(achados) == 0:
                registro.update({"minuto_na_base": None, "status_evento": "ausente",
                                 "observacao": "O atleta nao recebeu cartao nesta partida segundo a base."})
            else:
                minutos = sorted(float(m) for m in achados["minuto_partida"])
                alvo = float(caso["minuto_real"])
                proximo = min(minutos, key=lambda m: abs(m - alvo))
                coincide = abs(proximo - alvo) <= 5.0
                registro.update({
                    "minuto_na_base": proximo,
                    "status_evento": "confirmado" if coincide else "divergencia_de_minuto",
                    "observacao": f"Cartoes do atleta na partida: {minutos}.",
                })
        linhas.append(registro)

    return pd.DataFrame(linhas)


def auditar_ground_truth(df_matches: pd.DataFrame, df_cards: pd.DataFrame,
                         df_athletes: pd.DataFrame, df_pm: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Resolve e exporta a auditoria de ancoragem do ground truth."""
    partidas = resolver_partidas(df_matches, df_pm)
    atletas = resolver_atletas(df_cards, df_athletes, df_pm)
    eventos = verificar_eventos(df_cards, partidas, atletas, df_pm)

    os.makedirs(TABLES_DIR, exist_ok=True)
    partidas.to_csv(os.path.join(TABLES_DIR, "auditoria_ground_truth_partidas.csv"), index=False, encoding="utf-8")
    atletas.to_csv(os.path.join(TABLES_DIR, "auditoria_ground_truth_atletas.csv"), index=False, encoding="utf-8")
    eventos.to_csv(os.path.join(TABLES_DIR, "auditoria_ground_truth_eventos.csv"), index=False, encoding="utf-8")
    return partidas, atletas, eventos


if __name__ == "__main__":
    from src.models.anomaly_detection import load_unified_data, GROUND_TRUTH_PATH

    df_matches, df_cards, _ = load_unified_data()
    df_athletes = pd.read_parquet(os.path.join("data", "processed", "integrity", "atletas_anomaly_scored.parquet"))
    df_pm = pd.read_parquet(GROUND_TRUTH_PATH)

    partidas, atletas, eventos = auditar_ground_truth(df_matches, df_cards, df_athletes, df_pm)

    print("\n=== ANCORAGEM DAS PARTIDAS ===")
    print(partidas[["caso_id", "confronto", "rodada_ground_truth", "rodada_utilizada",
                    "partida_id", "status_partida"]].to_string(index=False))
    print("\n=== ANCORAGEM DOS ATLETAS ===")
    print(atletas[["atleta_ground_truth", "atleta_slug_base", "clube_slug",
                   "cartoes_na_temporada", "status_atleta", "confianca"]].to_string(index=False))
    print("\nResumo partidas:", partidas["status_partida"].value_counts().to_dict())
    print("Resumo atletas: ", atletas["status_atleta"].value_counts().to_dict())
