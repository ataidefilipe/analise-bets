export type ModoAgregacao = "clube" | "rodada";

/**
 * Doc 03, §5: "Nenhum atleta, em nenhuma circunstância. Se um dia aparecer
 * um campo de atleta nesta tela, é vazamento de camada e o backend está com
 * defeito." Nenhum tipo abaixo tem — nem pode ganhar — um campo de atleta.
 */
export interface AgregadoClube {
  clubeNome: string;
  partidas: number;
  cartoesTotais: number;
  cartoes1T: number;
}

export interface AgregadoRodada {
  competicao: string;
  ano: number;
  rodada: number;
  partidas: number;
  cartoesTotais: number;
  cartoes1T: number;
}
