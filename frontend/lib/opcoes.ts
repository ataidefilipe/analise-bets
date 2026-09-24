/**
 * Opções fixas de filtro. As temporadas e rodadas disponíveis não ficam aqui:
 * vêm de `GET /v1/cobertura`, porque mudam a cada execução do pipeline.
 */

export type Serie = "A" | "B";

export const SERIES: readonly { codigo: Serie; nome: string }[] = [
  { codigo: "A", nome: "Série A" },
  { codigo: "B", nome: "Série B" },
];

/** Rodadas de um Brasileirão de pontos corridos. Rodada sem súmula ainda devolve 422. */
export const TOTAL_RODADAS = 38;

export function nomeSerie(serie: Serie): string {
  return SERIES.find((s) => s.codigo === serie)?.nome ?? `Série ${serie}`;
}

type ValorParam = string | string[] | undefined;

export function primeiroParam(valor: ValorParam): string | undefined {
  return Array.isArray(valor) ? valor[0] : valor;
}

export function lerSerie(valor: ValorParam): Serie {
  return primeiroParam(valor) === "B" ? "B" : "A";
}

export function lerInteiro(valor: ValorParam): number | undefined {
  const n = Number(primeiroParam(valor));
  return Number.isInteger(n) && n > 0 ? n : undefined;
}
