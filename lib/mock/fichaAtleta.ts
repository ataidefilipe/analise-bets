import type { CartaoEvento, ClubePassagem, FichaAtleta, TemporadaResumo, TipoCartao } from "@/lib/types/atleta";
import { CLUBES_MOCK } from "@/lib/mock/clubes";
import { gerarNome } from "@/lib/mock/nomes";
import { criarGeradorAleatorio, seedFromString } from "@/lib/mock/random";
import { tierPorPercentil } from "@/lib/mock/tier";
import { listarPoolBusca } from "@/lib/mock/buscaAtletas";

const AVISO_INTERPRETATIVO =
  "Este escore mede atipicidade estatística do perfil disciplinar do atleta, e não probabilidade de fraude. A finalidade é priorizar atenção humana.";

const CATEGORIAS_MOCK = [
  "Reclamação",
  "Falta tática",
  "Conduta antidesportiva",
  "Demora no reinício de jogo",
  "Entrada violenta",
  "Simulação",
];

const MOTIVOS_MOCK = [
  "Reclamação enérgica após marcação da arbitragem.",
  "Interrompeu o avanço da jogada de forma proposital.",
  "Entrada de sola no adversário em disputa de bola.",
  "Atraso deliberado no reinício da partida.",
  "Simulação de falta dentro da grande área.",
];

/**
 * Simula `GET /atletas/{id}` (doc 01, ainda não recebido). Qualquer id
 * produz uma ficha plausível e estável (mesmo id → mesma ficha sempre) — não
 * existe uma "base de atletas" real por trás, só um gerador determinístico
 * a partir do próprio id como seed. Ids vindos do pool de busca
 * (`lib/mock/buscaAtletas.ts`) usam o nome/clubes reais desse pool, para a
 * ficha bater com o que apareceu no resultado da busca; ids vindos de outro
 * lugar (ex.: a fila de triagem) geram identificação própria.
 */
export async function getFichaAtleta(atletaId: string): Promise<FichaAtleta> {
  const rand = criarGeradorAleatorio(seedFromString(atletaId));
  const doPool = listarPoolBusca().find((a) => a.atletaId === atletaId);

  const nome = doPool?.nome ?? gerarNome(Math.floor(rand() * 1000));
  const clubes: ClubePassagem[] = doPool?.clubes ?? [CLUBES_MOCK[Math.floor(rand() * CLUBES_MOCK.length)]];
  const anoFinal = doPool?.ultimoAno ?? 2025;

  const numTemporadas = 2 + Math.floor(rand() * 4); // 2–5 temporadas
  const historicoPorTemporada: TemporadaResumo[] = [];
  const linhaDoTempoCartoes: CartaoEvento[] = [];

  for (let i = 0; i < numTemporadas; i++) {
    const ano = anoFinal - (numTemporadas - 1 - i);
    const clube = clubes[Math.min(i, clubes.length - 1)];
    const partidasJogadas = 5 + Math.floor(rand() * 33);
    const minutosJogados = partidasJogadas * (40 + Math.floor(rand() * 50));
    const cartoesTotais = Math.floor(rand() * 12);
    const cartoes1T = Math.min(cartoesTotais, Math.round(cartoesTotais * (0.2 + rand() * 0.6)));
    const percentil = Math.min(99, Math.round(Math.pow(rand(), 2) * 100));

    historicoPorTemporada.push({
      ano,
      clubeNome: clube.nome,
      partidasJogadas,
      minutosJogados,
      cartoesTotais,
      cartoes1T,
      tier: tierPorPercentil(percentil),
      percentil,
    });

    for (let c = 0; c < cartoesTotais; c++) {
      const noPrimeiroTempo = c < cartoes1T;
      const minuto = noPrimeiroTempo ? 1 + Math.floor(rand() * 45) : 46 + Math.floor(rand() * 49);
      const tipo: TipoCartao = rand() < 0.92 ? "amarelo" : "vermelho";
      const temMotivo = rand() >= 0.86; // ~86% nulo na Série A — doc 03, §3

      linhaDoTempoCartoes.push({
        ano,
        minuto,
        periodo: noPrimeiroTempo ? "1T" : "2T",
        tipo,
        categoria: CATEGORIAS_MOCK[Math.floor(rand() * CATEGORIAS_MOCK.length)],
        motivoCompleto: temMotivo ? MOTIVOS_MOCK[Math.floor(rand() * MOTIVOS_MOCK.length)] : null,
      });
    }
  }

  linhaDoTempoCartoes.sort((a, b) => b.ano - a.ano || a.minuto - b.minuto);

  return {
    atletaId,
    nome,
    clubes,
    historicoPorTemporada: historicoPorTemporada.reverse(), // temporada mais recente primeiro
    linhaDoTempoCartoes,
    avisoInterpretativo: AVISO_INTERPRETATIVO,
  };
}
