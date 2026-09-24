import type { Serie } from "@/lib/opcoes";

export interface Placar {
  mandante: number;
  visitante: number;
}

/**
 * A chave de uma partida é o trio série + temporada + id: `partida_id`
 * sozinho repete entre séries e anos (guia do backend, §4.2).
 */
export interface ChavePartida {
  serie: Serie;
  ano: number;
  partidaId: number;
}

export interface IdentificacaoPartida extends ChavePartida {
  rodada: number;
  /** ISO (AAAA-MM-DD). Pode faltar em partidas antigas da fonte. */
  data: string | null;
  arena: string | null;
  arbitro: string | null;
  clubeMandante: string;
  clubeVisitante: string;
  placar: Placar;
}

/** Item da listagem `GET /v1/partidas` — navegação até um dossiê. */
export interface PartidaResumo extends IdentificacaoPartida {
  temProcedencia: boolean;
}

export interface PaginaPartidas {
  itens: PartidaResumo[];
  pagina: number;
  totalPaginas: number;
  totalItens: number;
}

/**
 * "Coração da tela" (doc 03, §4): o que P3 de fato compra é procedência, não
 * predição — precisa ser copiável e legível, nunca um rodapé técnico.
 */
export interface Procedencia {
  fonte: string;
  urlSumula: string;
  sha256: string;
  /** ISO-8601 com fuso. */
  dataDownload: string | null;
  /** ISO-8601 com fuso. */
  dataProcessamento: string | null;
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

/** `GET /v1/partidas/{serie}/{temporada}/{id}/dossie`, já adaptado. */
export interface DossiePartida {
  identificacao: IdentificacaoPartida;
  /** `null` onde não há súmula eletrônica com URL e hash registrados. */
  procedencia: Procedencia | null;
  eventos: EventoPartida[];
  avisoInterpretativo: string;
  /** `null` fora da janela do escore de anomalia de partida (doc 02, §7). */
  escoreAnomaliaPercentil: number | null;
  tierPartida: string | null;
  /** Doc 03, §4: sem esta ressalva, a tela promete o que a validação não sustenta. */
  ressalvaPartida: string;
  /** Ausente na camada aberta — a seção nem é renderizada (doc 03, §1.5). */
  atletasSinalizados?: AtletaSinalizado[];
}
