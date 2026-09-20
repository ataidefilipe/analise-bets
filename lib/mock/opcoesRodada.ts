export interface CompeticaoMock {
  slug: string;
  nome: string;
}

export const COMPETICOES: CompeticaoMock[] = [
  { slug: "serie-a", nome: "Série A" },
  { slug: "serie-b", nome: "Série B" },
];

export const ANOS_DISPONIVEIS = [2026, 2025, 2024] as const;

export const TOTAL_RODADAS = 38;
