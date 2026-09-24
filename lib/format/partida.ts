import type { Placar } from "@/lib/types/partida";

/**
 * Aceita data pura (`AAAA-MM-DD`) ou carimbo ISO com fuso. Data pura é lida
 * como data local: `new Date("2026-04-05")` seria meia-noite UTC e viraria
 * 04/04 no horário de Brasília.
 */
export function formatarData(dataISO: string | null): string {
  if (!dataISO) return "data não informada";
  const soData = /^(\d{4})-(\d{2})-(\d{2})$/.exec(dataISO);
  const data = soData ? new Date(Number(soData[1]), Number(soData[2]) - 1, Number(soData[3])) : new Date(dataISO);
  return data.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" });
}

export function formatarPlacar(placar: Placar): string {
  return `${placar.mandante} x ${placar.visitante}`;
}
