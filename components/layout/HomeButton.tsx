"use client";

import Link from "next/link";
import { House } from "@phosphor-icons/react";
import { usePathname } from "next/navigation";

/** Botão para a página inicial, presente em toda tela exceto a própria home. */
export function HomeButton() {
  const pathname = usePathname();

  if (pathname === "/") {
    return null;
  }

  return (
    <Link
      href="/"
      aria-label="Página inicial"
      title="Página inicial"
      className="mb-4 flex size-8 items-center justify-center rounded-full border border-zinc-300 text-zinc-500 transition-colors hover:border-brand hover:bg-zinc-100 hover:text-brand print:hidden dark:border-zinc-700 dark:text-zinc-400 dark:hover:border-link dark:hover:bg-zinc-800 dark:hover:text-link"
    >
      <House size={16} weight="bold" />
    </Link>
  );
}
