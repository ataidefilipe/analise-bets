import type { Perfil, PersonaCodigo } from "@/lib/types/perfil";

/**
 * Simula `GET /v1/me` (doc 01, ainda não recebido neste repositório).
 *
 * Os 5 perfis abaixo refletem a coluna "Personas" da tabela do doc 03, §0:
 * T1 → P2/P1, T2 → P2/P1, T3 → P3/P2, T4 → P5/P3. P4 não aparece em nenhuma
 * tela do doc 03, então fica sem acesso até o doc 02 esclarecer seu papel.
 *
 * Quando a API real existir, este arquivo é o único ponto a trocar por um
 * fetch de verdade — nada que consome `Perfil` deveria precisar mudar.
 */
const PERFIS_MOCK: Record<PersonaCodigo, Perfil> = {
  P1: {
    persona: "P1",
    nome: "Clube Exemplo FC",
    granularidade: "identificada",
    telasPermitidas: ["fila-triagem", "busca-atleta"],
    limiarPadrao: 80,
    clube: { slug: "exemplo_fc", nome: "Exemplo FC" },
  },
  P2: {
    persona: "P2",
    nome: "Federação",
    granularidade: "identificada",
    telasPermitidas: ["fila-triagem", "busca-atleta", "dossie-partida"],
    limiarPadrao: 70,
  },
  P3: {
    persona: "P3",
    nome: "Operadora",
    granularidade: "identificada",
    telasPermitidas: ["dossie-partida", "panorama-agregado"],
    limiarPadrao: 70,
  },
  P4: {
    persona: "P4",
    nome: "Perfil P4",
    granularidade: "agregada",
    telasPermitidas: [],
    limiarPadrao: 70,
  },
  P5: {
    persona: "P5",
    nome: "Imprensa",
    granularidade: "agregada",
    telasPermitidas: ["panorama-agregado"],
    limiarPadrao: 70,
  },
};

export const PERFIL_PADRAO: PersonaCodigo = "P2";

/**
 * `persona` permite trocar o perfil ativo para demonstração/QA do menu
 * dinâmico (doc 03, §0) enquanto não há autenticação real (doc 01). Em
 * produção, a origem do perfil deixa de ser um parâmetro e passa a vir da
 * sessão autenticada.
 */
export async function getMe(persona: PersonaCodigo = PERFIL_PADRAO): Promise<Perfil> {
  return PERFIS_MOCK[persona];
}

export function listarPersonasMock(): Perfil[] {
  return Object.values(PERFIS_MOCK);
}
