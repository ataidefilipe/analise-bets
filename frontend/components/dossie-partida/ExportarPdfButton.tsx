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
      className="flex shrink-0 items-center gap-2 rounded-full border border-line-strong px-3 py-1.5 text-sm text-body transition-colors hover:border-link hover:text-link print:hidden"
    >
      <FilePdf size={16} weight="bold" />
      Exportar PDF
    </button>
  );
}
