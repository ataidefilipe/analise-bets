"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { MagnifyingGlass } from "@phosphor-icons/react";

interface BuscaAtletaFormProps {
  valorInicial: string;
}

/**
 * Campo único + botão de busca (doc 03, §3). O botão fica inativo com menos
 * de 3 caracteres — é submissão explícita, não busca instantânea a cada
 * tecla, como o mockup do doc (campo + ícone de lupa) deixa claro.
 */
export function BuscaAtletaForm({ valorInicial }: BuscaAtletaFormProps) {
  const [valor, setValor] = useState(valorInicial);
  const router = useRouter();
  const podeBuscar = valor.trim().length >= 3;

  function buscar(e: FormEvent) {
    e.preventDefault();
    if (!podeBuscar) return;
    router.push(`/atletas?q=${encodeURIComponent(valor.trim())}`);
  }

  return (
    <form onSubmit={buscar} className="flex gap-2">
      <input
        type="text"
        value={valor}
        onChange={(e) => setValor(e.target.value)}
        placeholder="nome ou apelido..."
        className="flex-1 rounded border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 focus-visible:border-brand focus-visible:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50 dark:focus-visible:border-link"
      />
      <button
        type="submit"
        disabled={!podeBuscar}
        aria-label="Buscar"
        title="Buscar"
        className="flex size-10 shrink-0 items-center justify-center rounded border border-zinc-300 text-zinc-500 transition-colors enabled:hover:border-brand enabled:hover:text-brand disabled:cursor-not-allowed disabled:opacity-40 dark:border-zinc-700 dark:text-zinc-400 dark:enabled:hover:border-link dark:enabled:hover:text-link"
      >
        <MagnifyingGlass size={18} weight="bold" />
      </button>
    </form>
  );
}
