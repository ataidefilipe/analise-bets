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
      <label htmlFor="chave" className="text-sm font-medium text-body">
        Chave de acesso
      </label>
      <input
        id="chave"
        name="chave"
        type="password"
        autoComplete="off"
        required
        className="w-full rounded-full border border-line-strong bg-surface px-4 py-2 font-mono text-sm text-ink focus-visible:border-link focus-visible:outline-none"
      />
      {estado.erro && <p className="text-sm text-muted">{estado.erro}</p>}
      <button
        type="submit"
        disabled={enviando}
        className="rounded-full bg-brand px-5 py-2.5 text-sm font-medium text-brand-foreground shadow-lg shadow-brand/20 transition hover:bg-brand-strong disabled:opacity-60 disabled:hover:bg-brand"
      >
        {enviando ? "Verificando..." : "Entrar"}
      </button>
    </form>
  );
}
