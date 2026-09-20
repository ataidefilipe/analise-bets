/** Proporção de cartões no 1º tempo (doc 03, §3: "é onde o padrão aparece"). */
export function formatarProporcao1T(cartoes1T: number, cartoesTotais: number): string {
  if (cartoesTotais === 0) return "—";
  return `${Math.round((cartoes1T / cartoesTotais) * 100)}%`;
}
