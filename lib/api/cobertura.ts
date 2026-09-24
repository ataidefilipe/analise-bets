import { cache } from "react";
import type { Serie } from "@/lib/opcoes";
import { apiGet } from "@/lib/api/cliente";

export interface CoberturaSerie {
  /** Temporadas com partidas na base, da mais recente para a mais antiga. */
  temporadas: number[];
  /** Temporadas com escore pré-jogo (fila de triagem) e a última rodada com escalação. */
  fila: { temporada: number; ultima_rodada: number }[];
}

export type Cobertura = Record<Serie, CoberturaSerie>;

/** `GET /v1/cobertura`: o que existe na base para montar os filtros. */
export const getCobertura = cache(() => apiGet<Cobertura>("/v1/cobertura"));
