import type { AtletaResumo, ResultadoBusca } from "@/lib/types/atleta";
import { CLUBES_MOCK } from "@/lib/mock/clubes";
import { gerarNome } from "@/lib/mock/nomes";
import { criarGeradorAleatorio, seedFromString } from "@/lib/mock/random";

const TAMANHO_POOL = 60;

function gerarPool(): AtletaResumo[] {
  return Array.from({ length: TAMANHO_POOL }, (_, i) => {
    const rand = criarGeradorAleatorio(seedFromString(`busca-${i}`));
    const numClubes = 1 + Math.floor(rand() * 2);
    const clubes = Array.from(
      { length: numClubes },
      () => CLUBES_MOCK[Math.floor(rand() * CLUBES_MOCK.length)],
    );
    return {
      atletaId: `busca-${i}`,
      nome: gerarNome(i),
      clubes,
      ultimoAno: 2022 + Math.floor(rand() * 4), // 2022–2025
    };
  });
}

const POOL_BUSCA = gerarPool();

/**
 * Simula `GET /atletas?q=&pagina=` (doc 01, ainda não recebido). Mínimo de 3
 * caracteres é responsabilidade do front (botão inativo, doc 03 §3); aqui é
 * só uma segunda barreira defensiva. Pagina o resultado inteiro da busca —
 * `pagina` não reinicia o filtro, só a fatia exibida.
 */
export async function buscarAtletas(
  consulta: string,
  pagina: number = 1,
  porPagina: number = 10,
): Promise<ResultadoBusca> {
  const termo = consulta.trim().toLowerCase();
  if (termo.length < 3) {
    return { itens: [], total: 0, pagina: 1, porPagina };
  }

  const encontrados = POOL_BUSCA.filter((atleta) => atleta.nome.toLowerCase().includes(termo));
  const inicio = (pagina - 1) * porPagina;

  return {
    itens: encontrados.slice(inicio, inicio + porPagina),
    total: encontrados.length,
    pagina,
    porPagina,
  };
}

/** Usado por `getFichaAtleta` para devolver nome/clubes consistentes com o resultado de busca. */
export function listarPoolBusca(): AtletaResumo[] {
  return POOL_BUSCA;
}
