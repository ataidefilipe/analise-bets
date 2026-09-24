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
      className="mb-4 flex size-8 items-center justify-center rounded-full border border-line-strong text-muted transition-colors hover:border-link hover:bg-surface-muted hover:text-link print:hidden"
    >
      <House size={16} weight="bold" />
    </Link>
  );
}
