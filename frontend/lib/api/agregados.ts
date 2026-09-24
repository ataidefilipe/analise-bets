import type { Serie } from "@/lib/opcoes";
import type { AgregadoClube, AgregadoRodada } from "@/lib/types/agregado";
import { apiGet } from "@/lib/api/cliente";

interface LinhaApi {
  partidas: number;
  cartoes: number;
  cartoes_1t: number;
}

interface PorClubeApi {
  dados: (LinhaApi & { clube_slug: string; clube: string | null })[];
}

interface PorRodadaApi {
  dados: (LinhaApi & { rodada: number })[];
}

/** `GET /v1/agregados/{serie}/{temporada}?por=clube` — camada aberta, sem atleta. */
export async function getAgregadoPorClube(serie: Serie, ano: number): Promise<AgregadoClube[]> {
  const r = await apiGet<PorClubeApi>(`/v1/agregados/${serie}/${ano}`, { por: "clube" });
  return r.dados.map((d) => ({
    clubeNome: d.clube ?? d.clube_slug,
    partidas: d.partidas,
    cartoesTotais: d.cartoes,
    cartoes1T: d.cartoes_1t,
  }));
}

/** `GET /v1/agregados/{serie}/{temporada}?por=rodada`. */
export async function getAgregadoPorRodada(serie: Serie, ano: number): Promise<AgregadoRodada[]> {
  const r = await apiGet<PorRodadaApi>(`/v1/agregados/${serie}/${ano}`, { por: "rodada" });
  return r.dados.map((d) => ({
    serie,
    ano,
    rodada: d.rodada,
    partidas: d.partidas,
    cartoesTotais: d.cartoes,
    cartoes1T: d.cartoes_1t,
  }));
}
