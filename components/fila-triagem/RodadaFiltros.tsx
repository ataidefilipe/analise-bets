"use client";

import { usePathname, useRouter } from "next/navigation";
import { SERIES, TOTAL_RODADAS, type Serie } from "@/lib/opcoes";

interface RodadaFiltrosProps {
  serie: Serie;
  ano: number;
  rodada: number;
  /** Temporadas com escore pré-jogo na série, vindas de `/v1/cobertura`. */
  anos: number[];
}

const RODADAS = Array.from({ length: TOTAL_RODADAS }, (_, i) => i + 1);

const CAMPO_SELECT_CLASSE =
  "rounded border border-zinc-300 bg-white px-2 py-1 text-sm text-zinc-700 focus-visible:border-brand focus-visible:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:focus-visible:border-link";

/**
 * Filtros de série/ano/rodada (doc 03, §2). Cada troca navega para a mesma
 * rota com a query atualizada, deixando o servidor buscar a nova fila. Trocar
 * série ou ano limpa a rodada e o corte, para abrir na última rodada disponível.
 */
export function RodadaFiltros({ serie, ano, rodada, anos }: RodadaFiltrosProps) {
  const router = useRouter();
  const pathname = usePathname();

  function atualizar(campo: "serie" | "ano" | "rodada", valor: string) {
    const params = new URLSearchParams({ serie: campo === "serie" ? valor : serie });
    if (campo !== "serie") params.set("ano", campo === "ano" ? valor : String(ano));
    if (campo === "rodada") params.set("rodada", valor);
    router.push(`${pathname}?${params.toString()}`);
  }

  return (
    <div className="flex flex-wrap gap-2">
      <select
        value={serie}
        onChange={(e) => atualizar("serie", e.target.value)}
        className={CAMPO_SELECT_CLASSE}
        aria-label="Série"
      >
        {SERIES.map((s) => (
          <option key={s.codigo} value={s.codigo}>
            {s.nome}
          </option>
        ))}
      </select>
      <select
        value={ano}
        onChange={(e) => atualizar("ano", e.target.value)}
        className={CAMPO_SELECT_CLASSE}
        aria-label="Ano"
      >
        {anos.map((a) => (
          <option key={a} value={a}>
            {a}
          </option>
        ))}
      </select>
      <select
        value={rodada}
        onChange={(e) => atualizar("rodada", e.target.value)}
        className={CAMPO_SELECT_CLASSE}
        aria-label="Rodada"
      >
        {RODADAS.map((r) => (
          <option key={r} value={r}>
            Rodada {r}
          </option>
        ))}
      </select>
    </div>
  );
}
