"use client";

import { FilePdf } from "@phosphor-icons/react";

/**
 * Exportação [MVP] (doc 03, §4): impressão da própria página via
 * `window.print()`, com folha de estilo de impressão. O dossiê em PDF
 * assinado e arquivável (tarefa F3-03) fica como dívida registrada — isto
 * não é um registro auditável.
 */
export function ExportarPdfButton() {
  return (
    <button
      type="button"
      onClick={() => window.print()}
      className="flex shrink-0 items-center gap-2 rounded border border-zinc-300 px-3 py-1.5 text-sm text-zinc-700 transition-colors hover:border-brand hover:text-brand print:hidden dark:border-zinc-700 dark:text-zinc-300 dark:hover:border-link dark:hover:text-link"
    >
      <FilePdf size={16} weight="bold" />
      Exportar PDF
    </button>
  );
}
