"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { Perfil } from "@/lib/types/perfil";
import { TELAS } from "@/lib/telas";

interface NavMenuProps {
  perfil: Perfil;
}

/**
 * Menu montado a partir de `perfil.telasPermitidas` (doc 03, §0). Uma tela
 * fora dessa lista simplesmente não gera link — nunca aparece desabilitada.
 * Destaca a tela atual com a cor de marca para orientar onde o usuário está.
 */
export function NavMenu({ perfil }: NavMenuProps) {
  const pathname = usePathname();
  const telasVisiveis = TELAS.filter((tela) => perfil.telasPermitidas.includes(tela.id));

  if (telasVisiveis.length === 0) {
    return (
      <p className="px-4 py-3 text-sm text-muted">
        Nenhuma tela disponível para este perfil.
      </p>
    );
  }

  return (
    <nav className="flex flex-wrap gap-1 px-4 pb-3">
      {telasVisiveis.map((tela) => {
        const ativa = pathname.startsWith(tela.rota);
        return (
          <Link
            key={tela.id}
            href={tela.rota}
            aria-current={ativa ? "page" : undefined}
            className={
              ativa
                ? "rounded-full bg-brand px-4 py-1.5 text-sm font-medium text-brand-foreground shadow-sm"
                : "rounded-full px-4 py-1.5 text-sm text-body transition-colors hover:bg-surface-muted hover:text-ink"
            }
          >
            {tela.rotulo}
          </Link>
        );
      })}
    </nav>
  );
}
