/**
 * Identificador estável de cada uma das 4 telas do MVP (doc 03, §0).
 * Usado tanto para roteamento quanto para checar permissão vinda de `/v1/me`.
 */
export type TelaId = "fila-triagem" | "busca-atleta" | "dossie-partida" | "panorama-agregado";

/**
 * Códigos de persona citados no doc 03. Mantido como union simples por ora;
 * o doc 02 (regras de negócio), que define a granularidade de cada persona
 * em detalhe, ainda não foi incorporado a este repositório.
 */
export type PersonaCodigo = "P1" | "P2" | "P3" | "P4" | "P5";

/**
 * Camada de dado que o perfil enxerga. Controla, por exemplo, se a T1 mostra
 * nome do atleta ou fica restrita a agregados (doc 03, §1.5 e §5).
 */
export type Granularidade = "identificada" | "agregada";

export interface ClubeEscopo {
  slug: string;
  nome: string;
}

/**
 * Formato esperado de `GET /v1/me`. É este objeto que decide o que o front
 * mostra — nunca o inverso. Uma tela fora de `telasPermitidas` não deve ser
 * renderizada nem como link desabilitado (doc 03, §0: "não aparece").
 */
export interface Perfil {
  persona: PersonaCodigo;
  nome: string;
  granularidade: Granularidade;
  telasPermitidas: TelaId[];
  /** Percentil inicial do slider de corte da T1 (doc 03, §2). */
  limiarPadrao: number;
  /** Presente apenas para perfis do tipo clube, já escopados ao próprio elenco. */
  clube?: ClubeEscopo;
}
