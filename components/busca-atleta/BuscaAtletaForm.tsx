"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { MagnifyingGlass, X } from "@phosphor-icons/react";

interface BuscaAtletaFormProps {
  valorInicial: string;
}

/**
 * Campo único + botão de busca (doc 03, §3). O botão fica inativo com menos
 * de 3 caracteres — é submissão explícita, não busca instantânea a cada
 * tecla, como o mockup do doc (campo + ícone de lupa) deixa claro. O "x"
 * dentro do campo limpa a busca e volta para a tabela com todos os atletas
 * (`/atletas`, sem `q` nem `pagina`).
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

  function limpar() {
    setValor("");
    router.push("/atletas");
  }

  return (
    <form onSubmit={buscar} className="flex gap-2">
      <div className="relative flex-1">
        <input
          type="text"
          value={valor}
          onChange={(e) => setValor(e.target.value)}
          placeholder="nome ou apelido..."
          className="w-full rounded border border-zinc-300 bg-white px-3 py-2 pr-9 text-sm text-zinc-900 focus-visible:border-brand focus-visible:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50 dark:focus-visible:border-link"
        />
        {valor.length > 0 && (
          <button
            type="button"
            onClick={limpar}
            aria-label="Limpar busca"
            title="Limpar busca"
            className="absolute inset-y-0 right-2 flex items-center text-zinc-400 transition-colors hover:text-brand dark:text-zinc-500 dark:hover:text-link"
          >
            <X size={16} weight="bold" />
          </button>
        )}
      </div>
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
