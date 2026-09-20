import type { AtletaResumo } from "@/lib/types/atleta";
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
 * Simula `GET /atletas?q=` (doc 01, ainda não recebido). Sem `consulta` (ou
 * com menos de 3 caracteres), devolve a base inteira em ordem alfabética —
 * a pedido do usuário, a tela agora navega a base toda, não só o resultado
 * de uma busca (ver docs/passo-05-tabela-completa-atletas.md). Com consulta
 * de 3+ caracteres, filtra por nome antes de ordenar.
 */
export async function listarAtletas(consulta: string = ""): Promise<AtletaResumo[]> {
  const termo = consulta.trim().toLowerCase();
  const base = termo.length >= 3 ? POOL_BUSCA.filter((atleta) => atleta.nome.toLowerCase().includes(termo)) : POOL_BUSCA;
  return [...base].sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"));
}

/** Usado por `getFichaAtleta` para devolver nome/clubes consistentes com o resultado de busca. */
export function listarPoolBusca(): AtletaResumo[] {
  return POOL_BUSCA;
}
