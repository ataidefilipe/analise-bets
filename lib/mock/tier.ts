/**
 * Vocabulário de tier ainda não confirmado pelo doc 02 (§5) — usado só para
 * os mocks produzirem rótulos plausíveis. Em produção o tier sempre vem
 * pronto do backend (doc 03, §1.3); o front nunca o recalcula a partir do
 * escore. Ponto único a apagar quando o doc 02 chegar com o vocabulário real.
 */
export function tierPorPercentil(percentil: number): string {
  if (percentil >= 99) return "Extrema";
  if (percentil >= 95) return "Muito alta";
  if (percentil >= 85) return "Alta";
  if (percentil >= 70) return "Moderada";
  return "Baixa";
}
