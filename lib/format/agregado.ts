/** Média de cartões por partida (doc 03, §5). */
export function formatarMedia(cartoesTotais: number, partidas: number): string {
  if (partidas === 0) return "—";
  return (cartoesTotais / partidas).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}
