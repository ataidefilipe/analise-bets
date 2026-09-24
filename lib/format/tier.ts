interface ItemComTier {
  tier: string | null;
  percentil: number | null;
}

/**
 * Combina tier + percentil como no mockup ("Extrema ... (p99)") — nunca
 * recalcula o tier em si. Sem tier (fora da janela do escore, doc 02 §7),
 * mostra um traço em vez de prometer um escore que não existe.
 */
export function formatarTier(item: ItemComTier): string {
  if (item.tier === null || item.percentil === null) return "—";
  return `${item.tier} (p${item.percentil.toLocaleString("pt-BR", { maximumFractionDigits: 1 })})`;
}
