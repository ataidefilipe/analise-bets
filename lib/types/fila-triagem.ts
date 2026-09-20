/** Opaco (doc 03, §1.2) — o front não deriva nada dele nem assume formato. */
export type AtletaId = string;

export type Condicao = "titular" | "reserva";

/**
 * Componentes que fundamentam o escore (doc 03, §2 "A linha de justificativa
 * é requisito, não enfeite"): a conta aberta `taxa_1t_ajustada × minutos_esperados`.
 */
export interface ComponentesEscore {
  cartoes1T: number;
  minutosJogados: number;
  taxaAjustada: number;
}

export interface FilaTriagemItem {
  atletaId: AtletaId;
  /** Ausente quando a granularidade do perfil não permite identificar (doc 03, §1.5). */
  atleta?: string;
  numCamisa?: number;
  clubeSlug: string;
  clubeNome: string;
  confronto: string;
  condicao: Condicao;
  /** Rótulo pronto vindo do backend — o front nunca recalcula (doc 03, §1.3). */
  tier: string;
  percentil: number;
  componentes: ComponentesEscore;
}

/** Formato esperado de `GET /rodadas/.../fila` (doc 01, ainda não recebido). */
export interface FilaTriagemResponse {
  competicao: string;
  ano: number;
  rodada: number;
  /** false = súmula ainda não publicada pela CBF (doc 03, §6, 422) — não é erro. */
  escalacaoPublicada: boolean;
  /** true nas rodadas 1–5 (doc 03, §6, "Base rasa"). */
  baseRasa: boolean;
  avisoInterpretativo: string;
  totalRelacionados: number;
  itens: FilaTriagemItem[];
  /** Presente quando a resposta já vem escopada a um clube (perfil P1). */
  clubeEscopo?: { slug: string; nome: string };
}
