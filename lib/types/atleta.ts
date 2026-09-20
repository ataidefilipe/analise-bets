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
 * Formato esperado de `GET /atletas?q=&pagina=` com paginação (pedido do
 * usuário — o doc 03 §3 originalmente descrevia 20 resultados sem
 * paginação; ver docs/passo-04-paginacao-busca.md sobre essa mudança).
 */
export interface ResultadoBusca {
  itens: AtletaResumo[];
  total: number;
  pagina: number;
  porPagina: number;
}

/**
 * Uma linha do histórico por temporada (doc 03, §3): "é onde o padrão
 * aparece — proporção de 1º tempo consistentemente alta ao longo de
 * temporadas diz mais que um escore isolado".
 */
export interface TemporadaResumo {
  ano: number;
  clubeNome: string;
  partidasJogadas: number;
  minutosJogados: number;
  cartoesTotais: number;
  cartoes1T: number;
  /** Rótulo pronto vindo do backend — o front nunca recalcula (doc 03, §1.3). */
  tier: string;
  percentil: number;
}

export type TipoCartao = "amarelo" | "vermelho";

export interface CartaoEvento {
  ano: number;
  minuto: number;
  periodo: "1T" | "2T";
  tipo: TipoCartao;
  categoria: string;
  /** null = não registrado na súmula (doc 03, §3: ~86% dos casos na Série A). */
  motivoCompleto: string | null;
}

/** Formato esperado de `GET /atletas/{id}` (doc 01, ainda não recebido). */
export interface FichaAtleta {
  atletaId: AtletaId;
  nome: string;
  clubes: ClubePassagem[];
  historicoPorTemporada: TemporadaResumo[];
  linhaDoTempoCartoes: CartaoEvento[];
  avisoInterpretativo: string;
}
