import { cookies } from "next/headers";
import { notFound, redirect } from "next/navigation";

/**
 * Cliente HTTP da API (doc 01). Só roda no servidor do Next: a chave fica num
 * cookie httpOnly e nunca chega ao JavaScript do navegador.
 */

export const COOKIE_CHAVE = "ab_api_key";

const BASE_URL = process.env.ANALISE_BETS_API_URL ?? "http://localhost:8000";

/** Corpo de erro da API: `{"erro": "<codigo>", "detalhe": "..."}` (doc 01, §6). */
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly erro: string,
    public readonly detalhe?: string,
  ) {
    super(detalhe ?? erro);
  }
}

type Query = Record<string, string | number | undefined>;

interface Opcoes {
  /** Chave explícita (login). Sem ela, usa a do cookie da sessão. */
  chave?: string;
  /**
   * Com `true` (padrão), 401 manda para `/entrar`, 403 para `/` e 404 para a
   * página de não encontrado — os três estados que nenhuma tela trata de
   * forma própria. Os demais erros (400, 422, 500) sobem como `ApiError`.
   */
  tratarNavegacao?: boolean;
}

export async function apiGet<T>(caminho: string, query: Query = {}, opcoes: Opcoes = {}): Promise<T> {
  const { tratarNavegacao = true } = opcoes;
  const chave = opcoes.chave ?? (await cookies()).get(COOKIE_CHAVE)?.value;
  if (!chave) {
    if (tratarNavegacao) redirect("/entrar");
    throw new ApiError(401, "nao_autenticado");
  }

  const url = new URL(caminho, BASE_URL);
  for (const [k, v] of Object.entries(query)) {
    if (v !== undefined && v !== "") url.searchParams.set(k, String(v));
  }

  let resposta: Response;
  try {
    resposta = await fetch(url, { headers: { Authorization: `Bearer ${chave}` }, cache: "no-store" });
  } catch {
    throw new ApiError(503, "api_indisponivel", `API fora do ar em ${BASE_URL}.`);
  }

  if (resposta.ok) return (await resposta.json()) as T;

  const corpo = (await resposta.json().catch(() => ({}))) as { erro?: string; detalhe?: string };
  if (tratarNavegacao) {
    if (resposta.status === 401) redirect("/entrar");
    if (resposta.status === 403) redirect("/");
    if (resposta.status === 404) notFound();
  }
  throw new ApiError(resposta.status, corpo.erro ?? "erro", corpo.detalhe);
}
