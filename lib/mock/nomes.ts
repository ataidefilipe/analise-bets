const PRIMEIROS_NOMES = [
  "Carlos", "João", "Pedro", "Lucas", "Rafael", "Bruno", "Diego", "Felipe",
  "Gustavo", "Hugo", "Igor", "Júlio", "Kaique", "Leandro", "Marcelo", "Nelson",
  "Otávio", "Paulo", "Renato", "Sérgio", "Thiago", "Vinícius",
];

const SOBRENOMES = [
  "Silva", "Santos", "Oliveira", "Souza", "Pereira", "Costa", "Rodrigues",
  "Almeida", "Nascimento", "Carvalho", "Gomes", "Martins", "Araújo", "Melo",
  "Barbosa", "Ribeiro", "Alves", "Monteiro", "Cardoso", "Teixeira",
];

/**
 * Combina sobrenomes comuns no Brasil (nenhum ligado a uma pessoa real) para
 * gerar nomes de atleta plausíveis e variados para o mock da fila de
 * triagem, evitando tanto nomes repetidos demais quanto qualquer semelhança
 * com um jogador de verdade.
 */
export function gerarNome(indice: number): string {
  const primeiro = PRIMEIROS_NOMES[indice % PRIMEIROS_NOMES.length];
  const sobrenome = SOBRENOMES[Math.floor(indice / PRIMEIROS_NOMES.length) % SOBRENOMES.length];
  return `${primeiro} ${sobrenome}`;
}
