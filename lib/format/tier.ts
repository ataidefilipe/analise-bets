interface ItemComTier {
  tier: string;
  percentil: number;
}

/** Combina tier + percentil como no mockup ("Extrema (p99)") — nunca recalcula o tier em si. */
export function formatarTier(item: ItemComTier): string {
  return `${item.tier} (p${item.percentil})`;
}
