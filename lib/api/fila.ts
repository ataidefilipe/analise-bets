import type { Serie } from "@/lib/opcoes";
import type { FilaTriagemResponse } from "@/lib/types/fila-triagem";
import { ApiError, apiGet } from "@/lib/api/cliente";

interface FilaApi {
  contexto: {
    percentil_aplicado: number;
    clube_slug: string | null;
    clube: string | null;
    total_relacionados: number;
    total_sinalizados: number;
    base_rasa: boolean;
  };
  dados: {
    atleta_id: string;
    atleta: string | null;
    num_camisa: number | null;
    clube_slug: string;
    clube: string | null;
    partida_id: number;
    confronto: string | null;
    condicao: "Titular" | "Reserva";
    percentil: number;
    tier: string;
    componentes: {
      minutos_previos: number;
      cartoes_1t_previos: number;
      taxa_1t_ajustada: number;
      minutos_esperados: number;
    };
  }[];
  aviso_interpretativo: string;
}

export interface ParametrosFilaTriagem {
  serie: Serie;
  ano: number;
  rodada: number;
  /** Corte. Sem ele, o backend aplica o limiar padrão do perfil. */
  percentil?: number;
  avisoInterpretativo: string;
}

/** Máximo que a API devolve por chamada (doc 01, §4.2). */
export const LIMITE_FILA = 200;

/**
 * `GET /v1/rodadas/{serie}/{temporada}/{rodada}/fila`. O corte é aplicado no
 * backend — inclusive o recorte do perfil `clube` ao próprio elenco, que
 * acontece antes do corte e nunca é decidido aqui.
 */
export async function getFilaTriagem(p: ParametrosFilaTriagem): Promise<FilaTriagemResponse> {
  const base = { serie: p.serie, ano: p.ano, rodada: p.rodada, baseRasa: p.rodada <= 5 };
  let r: FilaApi;
  try {
    r = await apiGet<FilaApi>(`/v1/rodadas/${p.serie}/${p.ano}/${p.rodada}/fila`, {
      percentil: p.percentil,
      limite: LIMITE_FILA,
    });
  } catch (e) {
    // 422 é o estado normal de rodada sem súmula publicada (doc 03, §6), não erro.
    if (e instanceof ApiError && e.status === 422) {
      return {
        ...base,
        escalacaoPublicada: false,
        avisoInterpretativo: p.avisoInterpretativo,
        percentilAplicado: p.percentil ?? 0,
        totalRelacionados: 0,
        totalSinalizados: 0,
        itens: [],
      };
    }
    throw e;
  }

  const c = r.contexto;
  return {
    ...base,
    escalacaoPublicada: true,
    baseRasa: c.base_rasa,
    avisoInterpretativo: r.aviso_interpretativo,
    percentilAplicado: c.percentil_aplicado,
    totalRelacionados: c.total_relacionados,
    totalSinalizados: c.total_sinalizados,
    clubeEscopo: c.clube_slug ? { slug: c.clube_slug, nome: c.clube ?? c.clube_slug } : undefined,
    itens: r.dados.map((d) => ({
      atletaId: d.atleta_id,
      atleta: d.atleta ?? undefined,
      numCamisa: d.num_camisa ?? undefined,
      clubeSlug: d.clube_slug,
      clubeNome: d.clube ?? d.clube_slug,
      partidaId: d.partida_id,
      confronto: d.confronto ?? "—",
      condicao: d.condicao === "Reserva" ? "reserva" : "titular",
      tier: d.tier,
      percentil: d.percentil,
      componentes: {
        cartoes1T: d.componentes.cartoes_1t_previos,
        minutosJogados: d.componentes.minutos_previos,
        taxaAjustada: d.componentes.taxa_1t_ajustada,
        minutosEsperados: d.componentes.minutos_esperados,
      },
    })),
  };
}
