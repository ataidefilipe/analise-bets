"""
src/analysis/cobertura_motivo_cartao.py
---------------------------------------
Cobertura do motivo textual do cartão por temporada e série (tarefa F2-01).

O motivo digitado pelo árbitro é o atributo de maior valor competitivo do projeto: nenhum
provedor comercial de dados esportivos o disponibiliza estruturado. Ele existe apenas onde a
fonte é a súmula oficial da CBF; para o período histórico da Série A, originado da base do
Kaggle, o campo **não existe na fonte** e permanece nulo — o que é esperado, e não falha.

Saída: reports/tables/cobertura_motivo_cartao.csv
"""

import os
import pandas as pd

PROCESSED = os.path.join("data", "processed")
TABLES_DIR = os.path.join("reports", "tables")

CATEGORIAS_NAO_FISICAS = ("reclamacao", "cera_retardar", "conduta_antidesportiva", "mao_intencional")


def cobertura() -> pd.DataFrame:
    linhas = []
    for serie in ("a", "b"):
        caminho = os.path.join(PROCESSED, f"serie_{serie}", "cartoes.parquet")
        if not os.path.exists(caminho):
            continue
        df = pd.read_parquet(caminho)
        tem_motivo = "motivo_completo" in df.columns

        for temporada, g in df.groupby("temporada"):
            com_motivo = int(g["motivo_completo"].notna().sum()) if tem_motivo else 0
            if tem_motivo and com_motivo:
                categorias = g.loc[g["motivo_completo"].notna(), "categoria_infracao"]
                nao_fisicas = int(categorias.isin(CATEGORIAS_NAO_FISICAS).sum())
                pct_nao_fisicas = round(nao_fisicas / com_motivo * 100, 1)
            else:
                nao_fisicas, pct_nao_fisicas = 0, None

            linhas.append({
                "serie": serie.upper(),
                "temporada": int(temporada),
                "cartoes": len(g),
                "com_motivo": com_motivo,
                "pct_com_motivo": round(com_motivo / len(g) * 100, 1),
                "fonte": "Súmula CBF" if com_motivo else "Base histórica (Kaggle)",
                "infracoes_nao_fisicas": nao_fisicas,
                "pct_nao_fisicas": pct_nao_fisicas,
            })

    return pd.DataFrame(linhas).sort_values(["serie", "temporada"]).reset_index(drop=True)


def executar() -> pd.DataFrame:
    df = cobertura()
    os.makedirs(TABLES_DIR, exist_ok=True)
    df.to_csv(os.path.join(TABLES_DIR, "cobertura_motivo_cartao.csv"), index=False, encoding="utf-8")
    return df


if __name__ == "__main__":
    df = executar()
    print("\n=== COBERTURA DO MOTIVO DO CARTAO ===")
    print(df.to_string(index=False))
    com = df[df["com_motivo"] > 0]
    print(f"\nCartoes com motivo: {int(com['com_motivo'].sum())} de {int(df['cartoes'].sum())} "
          f"({com['com_motivo'].sum() / df['cartoes'].sum() * 100:.1f}% da base)")
    if len(com):
        total_nf = com["infracoes_nao_fisicas"].sum()
        print(f"Infracoes comportamentais nao-fisicas: {int(total_nf)} "
              f"({total_nf / com['com_motivo'].sum() * 100:.1f}% dos cartoes com motivo)")
