import type { FichaAtleta } from "@/lib/types/atleta";

interface FichaCabecalhoProps {
  ficha: Pick<FichaAtleta, "nome" | "clubes" | "atletaId">;
}

/**
 * Enquadramento neutro e factual (doc 03, §3 "Cuidado de design"): uma ficha
 * de dados disciplinares, não um dossiê de investigação. Sem vermelho, sem
 * ícone de alerta, sem selo — percentil alto é informação estatística, não
 * acusação.
 */
export function FichaCabecalho({ ficha }: FichaCabecalhoProps) {
  return (
    <div className="flex flex-col gap-1">
      <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">{ficha.nome}</h1>
      <p className="text-sm text-zinc-500 dark:text-zinc-400">
        {ficha.clubes.map((clube) => clube.nome).join(" · ")}
      </p>
      <p className="font-mono text-xs text-zinc-400 dark:text-zinc-600">{ficha.atletaId}</p>
    </div>
  );
}
