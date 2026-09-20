import type { AgregadoClube, AgregadoRodada } from "@/lib/types/agregado";
import { listarPartidas, getDossiePartida } from "@/lib/mock/partidas";

/**
 * Simula `GET /agregados/clubes` (doc 01, ainda não recebido). Camada
 * aberta (doc 03, §5) — reaproveita os mesmos mocks de partida/dossiê da
 * T3 em vez de manter um dataset paralelo, então os números batem entre as
 * telas. Nenhum campo de atleta nunca deve ser adicionado aqui.
 */
export async function getAgregadoPorClube(competicao?: string): Promise<AgregadoClube[]> {
  const partidas = await listarPartidas();
  const filtradas = competicao ? partidas.filter((p) => p.competicao === competicao) : partidas;

  const acumulador = new Map<string, AgregadoClube>();

  for (const partida of filtradas) {
    for (const clubeNome of [partida.clubeMandante, partida.clubeVisitante]) {
      if (!acumulador.has(clubeNome)) {
        acumulador.set(clubeNome, { clubeNome, partidas: 0, cartoesTotais: 0, cartoes1T: 0 });
      }
      acumulador.get(clubeNome)!.partidas += 1;
    }

    const dossie = await getDossiePartida(partida.partidaId);
    for (const evento of dossie.eventos) {
      const agregado = acumulador.get(evento.clubeNome);
      if (!agregado) continue;
      agregado.cartoesTotais += 1;
      if (evento.periodo === "1T") agregado.cartoes1T += 1;
    }
  }

  return [...acumulador.values()];
}

/** Simula `GET /agregados/rodadas` (doc 01, ainda não recebido). Mesmas ressalvas de `getAgregadoPorClube`. */
export async function getAgregadoPorRodada(competicao?: string): Promise<AgregadoRodada[]> {
  const partidas = await listarPartidas();
  const filtradas = competicao ? partidas.filter((p) => p.competicao === competicao) : partidas;

  const acumulador = new Map<string, AgregadoRodada>();

  for (const partida of filtradas) {
    const chave = `${partida.competicao}-${partida.ano}-${partida.rodada}`;
    if (!acumulador.has(chave)) {
      acumulador.set(chave, {
        competicao: partida.competicao,
        ano: partida.ano,
        rodada: partida.rodada,
        partidas: 0,
        cartoesTotais: 0,
        cartoes1T: 0,
      });
    }
    const agregado = acumulador.get(chave)!;
    agregado.partidas += 1;

    const dossie = await getDossiePartida(partida.partidaId);
    agregado.cartoesTotais += dossie.eventos.length;
    agregado.cartoes1T += dossie.eventos.filter((evento) => evento.periodo === "1T").length;
  }

  return [...acumulador.values()].sort((a, b) => b.ano - a.ano || b.rodada - a.rodada);
}
