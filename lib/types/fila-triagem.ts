import type { AtletaId } from "@/lib/types/atleta";
import type { Serie } from "@/lib/opcoes";

export type Condicao = "titular" | "reserva";

/**
 * Componentes que fundamentam o escore (doc 03, §2 "A linha de justificativa
 * é requisito, não enfeite"): a conta aberta `taxa_1t_ajustada × minutos_esperados`.
 */
export interface ComponentesEscore {
  cartoes1T: number;
  minutosJogados: number;
  taxaAjustada: number;
  minutosEsperados: number;
}

export interface FilaTriagemItem {
  atletaId: AtletaId;
  /** Ausente quando a granularidade do perfil não permite identificar (doc 03, §1.5). */
  atleta?: string;
  numCamisa?: number;
  clubeSlug: string;
  clubeNome: string;
  partidaId: number;
  confronto: string;
  condicao: Condicao;
  /** Rótulo pronto vindo do backend — o front nunca recalcula (doc 03, §1.3). */
  tier: string;
  percentil: number;
  componentes: ComponentesEscore;
}

/** `GET /v1/rodadas/{serie}/{temporada}/{rodada}/fila`, já adaptado. */
export interface FilaTriagemResponse {
  serie: Serie;
  ano: number;
  rodada: number;
  /** false = súmula ainda não publicada pela CBF (resposta 422, doc 03 §6) — não é erro. */
  escalacaoPublicada: boolean;
  /** true nas rodadas 1–5 (doc 03, §6, "Base rasa"). */
  baseRasa: boolean;
  avisoInterpretativo: string;
  /** Corte que o backend aplicou — a fila vem recortada do servidor. */
  percentilAplicado: number;
  totalRelacionados: number;
  /** Quantos passaram do corte. `itens` pode trazer menos, limitado a 200. */
  totalSinalizados: number;
  itens: FilaTriagemItem[];
  /** Presente quando a resposta já vem escopada a um clube (perfil clube). */
  clubeEscopo?: { slug: string; nome: string };
}
