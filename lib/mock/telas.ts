import type { TelaId } from "@/lib/types/perfil";

export interface TelaConfig {
  id: TelaId;
  rota: string;
  rotulo: string;
  descricaoCurta: string;
}

/**
 * Metadados fixos das 4 telas do MVP (doc 03, §0). Não depende de perfil —
 * a filtragem por permissão acontece em quem consome esta lista.
 */
export const TELAS: readonly TelaConfig[] = [
  {
    id: "fila-triagem",
    rota: "/triagem",
    rotulo: "Fila de triagem da rodada",
    descricaoCurta: "Da rodada inteira, quais casos mandar para revisão.",
  },
  {
    id: "busca-atleta",
    rota: "/atletas",
    rotulo: "Busca e ficha do atleta",
    descricaoCurta: "Histórico disciplinar de um atleta específico.",
  },
  {
    id: "dossie-partida",
    rota: "/partidas",
    rotulo: "Dossiê de partida",
    descricaoCurta: "Procedência e eventos de uma partida monitorada.",
  },
  {
    id: "panorama-agregado",
    rota: "/agregados",
    rotulo: "Panorama agregado",
    descricaoCurta: "Cartões por clube ou rodada, sem nenhum atleta.",
  },
];

export function getTelaConfig(id: TelaId): TelaConfig {
  const tela = TELAS.find((t) => t.id === id);
  if (!tela) {
    throw new Error(`Tela desconhecida: ${id}`);
  }
  return tela;
}
