import type { Condicao, FilaTriagemItem, FilaTriagemResponse } from "@/lib/types/fila-triagem";
import { CLUBES_MOCK, type ClubeMock } from "@/lib/mock/clubes";
import { gerarNome } from "@/lib/mock/nomes";
import { criarGeradorAleatorio, seedFromString } from "@/lib/mock/random";
import { tierPorPercentil } from "@/lib/mock/tier";

export interface ParametrosFilaTriagem {
  competicao: string;
  ano: number;
  rodada: number;
  /** Presente para perfis do tipo clube — escopa a fila ao próprio elenco (doc 03, §2). */
  clubeSlug?: string;
}

/** Rodada mais recente com escalação publicada, por competição — controla o caso 422 do doc 03 §6. */
const RODADA_ATUAL_POR_COMPETICAO: Record<string, number> = {
  "serie-a": 30,
  "serie-b": 30,
};

const AVISO_INTERPRETATIVO =
  "Este escore mede atipicidade estatística do perfil disciplinar do atleta, e não probabilidade de fraude. A finalidade é priorizar atenção humana.";

function gerarConfrontos(clubes: ClubeMock[], rand: () => number): Map<string, string> {
  const embaralhados = [...clubes];
  for (let i = embaralhados.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [embaralhados[i], embaralhados[j]] = [embaralhados[j], embaralhados[i]];
  }

  const confrontoPorSlug = new Map<string, string>();
  for (let i = 0; i < embaralhados.length - 1; i += 2) {
    const mandante = embaralhados[i];
    const visitante = embaralhados[i + 1];
    confrontoPorSlug.set(mandante.slug, `${mandante.nome} x ${visitante.nome}`);
    confrontoPorSlug.set(visitante.slug, `${visitante.nome} x ${mandante.nome}`);
  }
  return confrontoPorSlug;
}

/** Simula `GET /rodadas/.../fila` (doc 01, ainda não recebido neste repositório). */
export async function getFilaTriagem(params: ParametrosFilaTriagem): Promise<FilaTriagemResponse> {
  const { competicao, ano, rodada, clubeSlug } = params;
  const rodadaAtual = RODADA_ATUAL_POR_COMPETICAO[competicao] ?? 30;
  const escalacaoPublicada = rodada <= rodadaAtual;
  const baseRasa = rodada <= 5;

  if (!escalacaoPublicada) {
    return {
      competicao,
      ano,
      rodada,
      escalacaoPublicada: false,
      baseRasa,
      avisoInterpretativo: AVISO_INTERPRETATIVO,
      totalRelacionados: 0,
      itens: [],
    };
  }

  const rand = criarGeradorAleatorio(seedFromString(`${competicao}-${ano}-${rodada}`));
  const confrontoPorClube = gerarConfrontos(CLUBES_MOCK, rand);

  const itens: FilaTriagemItem[] = [];
  let indiceNome = 0;

  for (const clube of CLUBES_MOCK) {
    const confronto = confrontoPorClube.get(clube.slug);
    if (!confronto) continue;

    const relacionadosNoClube = 18 + Math.floor(rand() * 6); // 18–23, faixa típica de um jogo
    for (let i = 0; i < relacionadosNoClube; i++) {
      const condicao: Condicao = i < 11 ? "titular" : "reserva";
      const minutosJogados = 200 + Math.floor(rand() * 2800);
      // Cauda longa: a maioria fica baixa, poucos casos chegam perto de 99.
      const percentil = Math.min(99, Math.round(Math.pow(rand(), 3) * 100));
      const cartoes1T = Math.max(0, Math.round((percentil / 100) * 8 + rand() * 2));

      itens.push({
        atletaId: `mock-${clube.slug}-${rodada}-${i}`,
        atleta: gerarNome(indiceNome++),
        numCamisa: 1 + Math.floor(rand() * 40),
        clubeSlug: clube.slug,
        clubeNome: clube.nome,
        confronto,
        condicao,
        tier: tierPorPercentil(percentil),
        percentil,
        componentes: { cartoes1T, minutosJogados, taxaAjustada: cartoes1T / minutosJogados },
      });
    }
  }

  const escopo = clubeSlug ? itens.filter((item) => item.clubeSlug === clubeSlug) : itens;
  const ordenados = escopo.sort((a, b) => b.percentil - a.percentil);
  const clube = clubeSlug ? CLUBES_MOCK.find((c) => c.slug === clubeSlug) : undefined;

  return {
    competicao,
    ano,
    rodada,
    escalacaoPublicada: true,
    baseRasa,
    avisoInterpretativo: AVISO_INTERPRETATIVO,
    totalRelacionados: ordenados.length,
    itens: ordenados,
    clubeEscopo: clube ? { slug: clube.slug, nome: clube.nome } : undefined,
  };
}
