"use client";

import { useActionState } from "react";
import { entrar, type EstadoEntrar } from "@/lib/api/acoes";

/**
 * Formulário da chave. A validação acontece na Server Action (`entrar`), que
 * consulta `/v1/me` antes de gravar o cookie — a chave nunca fica acessível
 * ao JavaScript do navegador depois disso (cookie httpOnly).
 */
export function EntrarForm() {
  const [estado, acao, enviando] = useActionState<EstadoEntrar, FormData>(entrar, {});

  return (
    <form action={acao} className="flex flex-col gap-3">
      <label htmlFor="chave" className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
        Chave de acesso
      </label>
      <input
        id="chave"
        name="chave"
        type="password"
        autoComplete="off"
        required
        className="w-full rounded border border-zinc-300 bg-white px-3 py-2 font-mono text-sm text-zinc-900 focus-visible:border-brand focus-visible:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50 dark:focus-visible:border-link"
      />
      {estado.erro && <p className="text-sm text-zinc-600 dark:text-zinc-400">{estado.erro}</p>}
      <button
        type="submit"
        disabled={enviando}
        className="rounded bg-brand px-3 py-2 text-sm font-medium text-brand-foreground transition-opacity disabled:opacity-60"
      >
        {enviando ? "Verificando..." : "Entrar"}
      </button>
    </form>
  );
}
