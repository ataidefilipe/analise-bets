import type { Serie } from "@/lib/opcoes";

/** Opaco (doc 03, §1.2) — o front não deriva nada dele nem assume formato. */
export type AtletaId = string;

export interface ClubePassagem {
  slug: string;
  nome: string;
}

/** Item da lista de busca (doc 03, §3): só identificação e clubes — nunca escore ou tier. */
export interface AtletaResumo {
  atletaId: AtletaId;
  nome: string;
  clubes: ClubePassagem[];
  ultimoAno: number;
}

/**
 * Uma linha do histórico por temporada (doc 03, §3): "é onde o padrão
 * aparece — proporção de 1º tempo consistentemente alta ao longo de
 * temporadas diz mais que um escore isolado".
 */
export interface TemporadaResumo {
  ano: number;
  serie: Serie;
  clubeNome: string;
  partidasJogadas: number;
  minutosJogados: number;
  cartoesTotais: number;
  cartoes1T: number;
  /**
   * Rótulo pronto vindo do backend — o front nunca recalcula (doc 03, §1.3).
   * `null` fora da janela do escore retrospectivo (doc 02, §7): a tela não
   * promete escore que não existe.
   */
  tier: string | null;
  percentil: number | null;
}

export type TipoCartao = "amarelo" | "vermelho";

export interface CartaoEvento {
  ano: number;
  minuto: number;
  periodo: "1T" | "2T";
  tipo: TipoCartao;
  categoria: string | null;
  /** null = não registrado na súmula (doc 03, §3: ~86% dos casos na Série A). */
  motivoCompleto: string | null;
}

/** `GET /v1/atletas/{id}`, já adaptado. */
export interface FichaAtleta {
  atletaId: AtletaId;
  nome: string;
  clubes: ClubePassagem[];
  historicoPorTemporada: TemporadaResumo[];
  linhaDoTempoCartoes: CartaoEvento[];
  avisoInterpretativo: string;
}
