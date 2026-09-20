export interface Placar {
  mandante: number;
  visitante: number;
}

export interface IdentificacaoPartida {
  partidaId: string;
  competicao: string;
  ano: number;
  rodada: number;
  /** ISO (AAAA-MM-DD). */
  data: string;
  arena: string;
  arbitro: string;
  clubeMandante: string;
  clubeVisitante: string;
  placar: Placar;
}

/**
 * "Coração da tela" (doc 03, §4): o que P3 de fato compra é procedência, não
 * predição — precisa ser copiável e legível, nunca um rodapé técnico.
 */
export interface Procedencia {
  fonte: string;
  urlSumula: string;
  sha256: string;
  /** ISO (AAAA-MM-DD). */
  dataDownload: string;
  /** ISO (AAAA-MM-DD). */
  dataProcessamento: string;
}

export type TipoCartaoPartida = "amarelo" | "vermelho";

/** Doc 03, §4: só minuto, período e motivo — sem categoria, ao contrário da ficha do atleta (T2). */
export interface EventoPartida {
  minuto: number;
  periodo: "1T" | "2T";
  tipo: TipoCartaoPartida;
  clubeNome: string;
  motivo: string | null;
}

/** Item da seção "Atletas sinalizados" (doc 03, §4) — só camada identificada. */
export interface AtletaSinalizado {
  atletaId: string;
  atleta: string;
  clubeNome: string;
  tier: string;
  percentil: number;
}

/** Formato esperado de `GET /partidas/{id}/dossie` (doc 01, ainda não recebido). */
export interface DossiePartida {
  identificacao: IdentificacaoPartida;
  procedencia: Procedencia;
  eventos: EventoPartida[];
  avisoInterpretativo: string;
  escoreAnomaliaPercentil: number;
  /** Doc 03, §4: sem esta ressalva, a tela promete o que a validação não sustenta. */
  ressalvaPartida: string;
  /** Ausente quando a granularidade do perfil não permite identificar (doc 03, §1.5). */
  atletasSinalizados?: AtletaSinalizado[];
}
