import type { Serie } from "@/lib/opcoes";
import type { DossiePartida, PaginaPartidas, Placar } from "@/lib/types/partida";
import { apiGet } from "@/lib/api/cliente";

interface PartidaApi {
  partida_id: number;
  serie: Serie;
  temporada: number;
  rodada: number;
  data: string | null;
  clube_mandante: string;
  clube_visitante: string;
  placar: string;
}

interface ListagemApi {
  dados: (PartidaApi & { tem_procedencia: boolean })[];
  paginacao: { pagina: number; total_itens: number; total_paginas: number };
}

interface DossieApi {
  partida: PartidaApi & { arena: string | null; arbitro: string | null };
  percentil: number | null;
  tier: string | null;
  aviso_partida: string;
  cartoes: {
    clube_slug: string;
    clube: string | null;
    cartao: "Amarelo" | "Vermelho";
    minuto_continuo: number;
    periodo: "1T" | "2T";
    motivo_completo: string;
    motivo_disponivel: boolean;
  }[];
  /** `null` na camada aberta. */
  atletas_sinalizados:
    | { atleta_id: string; atleta: string; clube_slug: string; clube: string | null; percentil: number; tier: string }[]
    | null;
  procedencia: {
    fonte: string | null;
    url: string | null;
    sha256: string | null;
    baixado_em: string | null;
    processado_em: string | null;
  };
  aviso_interpretativo: string;
}

/** A API devolve o placar como "2-1". */
function lerPlacar(placar: string): Placar {
  const [mandante, visitante] = placar.split("-").map(Number);
  return { mandante, visitante };
}

function identificacao(p: PartidaApi) {
  return {
    serie: p.serie,
    ano: p.temporada,
    partidaId: p.partida_id,
    rodada: p.rodada,
    data: p.data,
    clubeMandante: p.clube_mandante,
    clubeVisitante: p.clube_visitante,
    placar: lerPlacar(p.placar),
  };
}

export interface ParametrosListagem {
  serie: Serie;
  ano?: number;
  consulta?: string;
  pagina?: number;
}

export const POR_PAGINA_PARTIDAS = 20;

/** `GET /v1/partidas`: navegação até um dossiê, paginada no backend. */
export async function listarPartidas(p: ParametrosListagem): Promise<PaginaPartidas> {
  const r = await apiGet<ListagemApi>("/v1/partidas", {
    serie: p.serie,
    temporada: p.ano,
    busca: p.consulta,
    pagina: p.pagina,
    por_pagina: POR_PAGINA_PARTIDAS,
  });
  return {
    itens: r.dados.map((d) => ({ ...identificacao(d), arena: null, arbitro: null, temProcedencia: d.tem_procedencia })),
    pagina: r.paginacao.pagina,
    totalPaginas: r.paginacao.total_paginas,
    totalItens: r.paginacao.total_itens,
  };
}

/** `GET /v1/partidas/{serie}/{temporada}/{id}/dossie`. A camada decide o conteúdo, não o front. */
export async function getDossiePartida(serie: Serie, ano: number, partidaId: number): Promise<DossiePartida> {
  const r = await apiGet<DossieApi>(`/v1/partidas/${serie}/${ano}/${partidaId}/dossie`);
  const proc = r.procedencia;
  return {
    identificacao: { ...identificacao(r.partida), arena: r.partida.arena, arbitro: r.partida.arbitro },
    procedencia:
      proc.url && proc.sha256
        ? {
            fonte: proc.fonte ?? "Súmula Eletrônica CBF",
            urlSumula: proc.url,
            sha256: proc.sha256,
            dataDownload: proc.baixado_em,
            dataProcessamento: proc.processado_em,
          }
        : null,
    eventos: r.cartoes.map((c) => ({
      minuto: c.minuto_continuo,
      periodo: c.periodo,
      tipo: c.cartao === "Vermelho" ? "vermelho" : "amarelo",
      clubeNome: c.clube ?? c.clube_slug,
      motivo: c.motivo_disponivel ? c.motivo_completo : null,
    })),
    avisoInterpretativo: r.aviso_interpretativo,
    escoreAnomaliaPercentil: r.percentil,
    tierPartida: r.tier,
    ressalvaPartida: r.aviso_partida,
    atletasSinalizados: r.atletas_sinalizados?.map((a) => ({
      atletaId: a.atleta_id,
      atleta: a.atleta,
      clubeNome: a.clube ?? a.clube_slug,
      tier: a.tier,
      percentil: a.percentil,
    })),
  };
}
