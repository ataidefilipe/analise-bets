const MOTIVOS_CARTAO = [
  "Reclamação enérgica após marcação da arbitragem.",
  "Interrompeu o avanço da jogada de forma proposital.",
  "Entrada de sola no adversário em disputa de bola.",
  "Atraso deliberado no reinício da partida.",
  "Simulação de falta dentro da grande área.",
];

/**
 * ~86% dos cartões da Série A não têm motivo registrado na súmula (doc 03,
 * §3) — usado tanto na ficha do atleta quanto no dossiê de partida.
 */
export function sortearMotivoCartao(rand: () => number): string | null {
  return rand() >= 0.86 ? MOTIVOS_CARTAO[Math.floor(rand() * MOTIVOS_CARTAO.length)] : null;
}
