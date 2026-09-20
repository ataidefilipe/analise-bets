import type { Placar } from "@/lib/types/partida";

export function formatarData(dataISO: string): string {
  return new Date(dataISO).toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" });
}

export function formatarPlacar(placar: Placar): string {
  return `${placar.mandante} x ${placar.visitante}`;
}
