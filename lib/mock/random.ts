/**
 * Gerador determinístico (mulberry32) usado pelos mocks que precisam de
 * dados "aleatórios" mas estáveis entre renders — a mesma combinação de
 * competição/ano/rodada sempre produz a mesma fila.
 */
export function criarGeradorAleatorio(seed: number) {
  let estado = seed | 0;
  return function proximo(): number {
    estado = (estado + 0x6d2b79f5) | 0;
    let t = Math.imul(estado ^ (estado >>> 15), 1 | estado);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function seedFromString(valor: string): number {
  let h = 0;
  for (let i = 0; i < valor.length; i++) {
    h = (Math.imul(31, h) + valor.charCodeAt(i)) | 0;
  }
  return h;
}
