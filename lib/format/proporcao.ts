/** Proporção de uma parte sobre um total, como percentual (ex.: cartões no 1º tempo). */
export function formatarProporcao(parte: number, total: number): string {
  if (total === 0) return "—";
  return `${Math.round((parte / total) * 100)}%`;
}
