/**
 * Identificador estável de cada uma das 4 telas do MVP (doc 03, §0).
 * Usado tanto para roteamento quanto para checar permissão.
 */
export type TelaId = "fila-triagem" | "busca-atleta" | "dossie-partida" | "panorama-agregado";

/**
 * Camada de dado do perfil (doc 01, §3). `identificada` vê atleta; `aberta`
 * só agregados, sem nenhuma linha individual.
 */
export type Camada = "identificada" | "aberta";

export interface ClubeEscopo {
  slug: string;
  nome: string;
}

/**
 * Sessão do usuário, montada a partir de `GET /v1/me`. É este objeto que
 * decide o que o front mostra — nunca o inverso. Uma tela fora de
 * `telasPermitidas` não é renderizada nem como link desabilitado (doc 03, §0).
 */
export interface Perfil {
  /** Código do perfil na API (`federacao_stjd`, `clube`...). */
  perfil: string;
  /** Rótulo legível do perfil, vindo da API. */
  nome: string;
  camada: Camada;
  telasPermitidas: TelaId[];
  /** Percentil inicial do slider da T1 (doc 02, §3). `null` para perfis sem fila. */
  limiarPadrao: number | null;
  /** Presente apenas no perfil `clube`, já escopado ao próprio elenco. */
  clube?: ClubeEscopo;
  avisoInterpretativo: string;
}
