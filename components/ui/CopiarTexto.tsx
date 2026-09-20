"use client";

import { useState } from "react";
import { Check, Copy } from "@phosphor-icons/react";

interface CopiarTextoProps {
  valor: string;
}

/**
 * Botão de copiar genérico — usado na procedência do dossiê de partida
 * (doc 03, §4: "deve ser copiável e legível, não um rodapé técnico"), mas
 * sem conhecimento de domínio, então pode ser reusado em qualquer campo
 * técnico que precise ser copiado.
 */
export function CopiarTexto({ valor }: CopiarTextoProps) {
  const [copiado, setCopiado] = useState(false);

  async function copiar() {
    try {
      await navigator.clipboard.writeText(valor);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2000);
    } catch {
      // Clipboard indisponível (ex.: contexto não seguro) — o texto continua selecionável manualmente.
    }
  }

  return (
    <button
      type="button"
      onClick={copiar}
      aria-label="Copiar"
      title="Copiar"
      className="inline-flex shrink-0 items-center text-zinc-400 transition-colors hover:text-brand print:hidden dark:text-zinc-500 dark:hover:text-link"
    >
      {copiado ? <Check size={14} weight="bold" /> : <Copy size={14} weight="bold" />}
    </button>
  );
}
