"use client";

import { ArrowLeft } from "@phosphor-icons/react";
import { usePathname, useRouter } from "next/navigation";

/**
 * Botão de voltar, presente em toda tela exceto a home. Usa o histórico do
 * navegador (não um link fixo para "/") para que, mais adiante, voltar de
 * uma ficha de atleta aberta a partir de uma busca retorne à busca, e não
 * sempre para a home. Sem histórico (ex.: acesso direto pela URL), cai para
 * a home.
 */
export function BackButton() {
  const pathname = usePathname();
  const router = useRouter();

  if (pathname === "/") {
    return null;
  }

  function voltar() {
    if (window.history.length > 1) {
      router.back();
    } else {
      router.push("/");
    }
  }

  return (
    <button
      type="button"
      onClick={voltar}
      aria-label="Voltar"
      title="Voltar"
      className="mb-4 flex size-8 items-center justify-center rounded-full border border-zinc-300 text-zinc-500 transition-colors hover:border-zinc-400 hover:bg-zinc-100 hover:text-zinc-900 dark:border-zinc-700 dark:text-zinc-400 dark:hover:border-zinc-600 dark:hover:bg-zinc-800 dark:hover:text-zinc-50"
    >
      <ArrowLeft size={16} weight="bold" />
    </button>
  );
}
