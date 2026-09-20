export interface ClubeMock {
  slug: string;
  nome: string;
}

/**
 * 20 clubes fictícios (convenção "Exemplo" já usada no doc 03 para
 * `exemplo_fc`/`outro_fc`) — deliberadamente placeholders para não sugerir
 * dado disciplinar real sobre um clube real.
 */
export const CLUBES_MOCK: ClubeMock[] = Array.from({ length: 20 }, (_, i) => {
  const letra = String.fromCharCode(65 + i);
  return { slug: `exemplo-${letra.toLowerCase()}-fc`, nome: `Exemplo ${letra} FC` };
});
