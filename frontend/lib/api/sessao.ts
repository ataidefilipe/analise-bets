import { cache } from "react";
import { redirect } from "next/navigation";
import type { Camada, Perfil, TelaId } from "@/lib/types/perfil";
import { ApiError, apiGet } from "@/lib/api/cliente";

export interface MeResposta {
  perfil: string;
  rotulo: string;
  camada: Camada;
  granularidade: string[];
  clube_slug: string | null;
  clube: string | null;
  limiar_padrao: { percentil: number; alertas_por_rodada_esperados: number } | null;
  aviso_interpretativo: string;
}

/**
 * A API não devolve lista de telas: o menu sai da camada (doc 03, §0; guia de
 * integração, §4). T1 e T2 só existem para a camada identificada.
 */
const TELAS_POR_CAMADA: Record<Camada, TelaId[]> = {
  identificada: ["fila-triagem", "busca-atleta", "dossie-partida", "panorama-agregado"],
  aberta: ["dossie-partida", "panorama-agregado"],
};

export function montarPerfil(me: MeResposta): Perfil {
  return {
    perfil: me.perfil,
    nome: me.perfil === "clube" && me.clube ? `${me.rotulo} ${me.clube}` : me.rotulo,
    camada: me.camada,
    telasPermitidas: TELAS_POR_CAMADA[me.camada],
    limiarPadrao: me.limiar_padrao?.percentil ?? null,
    clube: me.clube_slug ? { slug: me.clube_slug, nome: me.clube ?? me.clube_slug } : undefined,
    avisoInterpretativo: me.aviso_interpretativo,
  };
}

/**
 * Perfil da sessão, ou `null` sem sessão válida. `cache` evita chamar
 * `/v1/me` duas vezes na mesma renderização (layout + página).
 */
export const getPerfilAtual = cache(async (): Promise<Perfil | null> => {
  try {
    return montarPerfil(await apiGet<MeResposta>("/v1/me", {}, { tratarNavegacao: false }));
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) return null;
    throw e;
  }
});

/**
 * Mesma regra do menu, aplicada à rota: sem sessão vai para `/entrar`; sem
 * acesso à tela, para `/`. Chamar no topo de cada `page.tsx` protegida, antes
 * de buscar dados. O backend também recusa (403) — isto é só a primeira camada.
 */
export async function exigirAcessoTela(tela: TelaId): Promise<Perfil> {
  const perfil = await getPerfilAtual();
  if (!perfil) redirect("/entrar");
  if (!perfil.telasPermitidas.includes(tela)) redirect("/");
  return perfil;
}
