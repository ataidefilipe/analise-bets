import type { Serie } from "@/lib/opcoes";
import type { AtletaResumo, ClubePassagem, FichaAtleta } from "@/lib/types/atleta";
import { apiGet } from "@/lib/api/cliente";

interface ClubeApi {
  clube_slug: string;
  clube: string | null;
}

interface BuscaApi {
  dados: { atleta_id: string; atleta: string; clubes: ClubeApi[]; ultima_temporada: number }[];
}

interface FichaApi {
  atleta_id: string;
  atleta: string;
  clubes: ClubeApi[];
  historico: {
    temporada: number;
    serie: Serie;
    clube_slug: string;
    clube: string | null;
    partidas_jogadas: number;
    minutos_em_campo: number;
    cartoes_total: number;
    cartoes_1t: number;
    percentil: number | null;
    tier: string | null;
  }[];
  cartoes: {
    temporada: number;
    minuto_continuo: number;
    periodo: "1T" | "2T";
    cartao: "Amarelo" | "Vermelho";
    categoria_infracao: string | null;
    motivo_completo: string;
    motivo_disponivel: boolean;
  }[];
  aviso_interpretativo: string;
}

function clube(c: ClubeApi): ClubePassagem {
  return { slug: c.clube_slug, nome: c.clube ?? c.clube_slug };
}

/** Limite fixo da busca na API: 20 resultados, sem paginação (doc 01, §4.3). */
export const LIMITE_BUSCA = 20;

/**
 * `GET /v1/atletas?busca=`. Exige 3 caracteres e nunca devolve escore: a
 * busca acha uma pessoa, não percorre a base (doc 01, §5). Não existe
 * listagem completa de atletas.
 */
export async function buscarAtletas(consulta: string): Promise<AtletaResumo[]> {
  const r = await apiGet<BuscaApi>("/v1/atletas", { busca: consulta });
  return r.dados.map((d) => ({
    atletaId: d.atleta_id,
    nome: d.atleta,
    clubes: d.clubes.map(clube),
    ultimoAno: d.ultima_temporada,
  }));
}

/** `GET /v1/atletas/{id}`. Toda abertura de ficha fica registrada no backend. */
export async function getFichaAtleta(atletaId: string): Promise<FichaAtleta> {
  const r = await apiGet<FichaApi>(`/v1/atletas/${encodeURIComponent(atletaId)}`);
  return {
    atletaId: r.atleta_id,
    nome: r.atleta,
    clubes: r.clubes.map(clube),
    avisoInterpretativo: r.aviso_interpretativo,
    historicoPorTemporada: r.historico.map((h) => ({
      ano: h.temporada,
      serie: h.serie,
      clubeNome: h.clube ?? h.clube_slug,
      partidasJogadas: h.partidas_jogadas,
      minutosJogados: h.minutos_em_campo,
      cartoesTotais: h.cartoes_total,
      cartoes1T: h.cartoes_1t,
      tier: h.tier,
      percentil: h.percentil,
    })),
    linhaDoTempoCartoes: r.cartoes.map((c) => ({
      ano: c.temporada,
      minuto: c.minuto_continuo,
      periodo: c.periodo,
      tipo: c.cartao === "Vermelho" ? "vermelho" : "amarelo",
      categoria: c.categoria_infracao || null,
      motivoCompleto: c.motivo_disponivel ? c.motivo_completo : null,
    })),
  };
}
