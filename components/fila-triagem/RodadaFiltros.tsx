"use client";

import { usePathname, useRouter } from "next/navigation";
import { ANOS_DISPONIVEIS, COMPETICOES, TOTAL_RODADAS } from "@/lib/mock/opcoesRodada";

interface RodadaFiltrosProps {
  competicao: string;
  ano: number;
  rodada: number;
}

const RODADAS = Array.from({ length: TOTAL_RODADAS }, (_, i) => i + 1);

const CAMPO_SELECT_CLASSE =
  "rounded border border-zinc-300 bg-white px-2 py-1 text-sm text-zinc-700 focus-visible:border-brand focus-visible:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:focus-visible:border-link";

/** Filtros de competição/ano/rodada (doc 03, §2). Cada troca navega para a mesma rota com a query atualizada, deixando o servidor buscar a nova fila. */
export function RodadaFiltros({ competicao, ano, rodada }: RodadaFiltrosProps) {
  const router = useRouter();
  const pathname = usePathname();

  function atualizar(campo: "competicao" | "ano" | "rodada", valor: string) {
    const params = new URLSearchParams({
      competicao: campo === "competicao" ? valor : competicao,
      ano: campo === "ano" ? valor : String(ano),
      rodada: campo === "rodada" ? valor : String(rodada),
    });
    router.push(`${pathname}?${params.toString()}`);
  }

  return (
    <div className="flex flex-wrap gap-2">
      <select
        value={competicao}
        onChange={(e) => atualizar("competicao", e.target.value)}
        className={CAMPO_SELECT_CLASSE}
        aria-label="Competição"
      >
        {COMPETICOES.map((c) => (
          <option key={c.slug} value={c.slug}>
            {c.nome}
          </option>
        ))}
      </select>
      <select
        value={ano}
        onChange={(e) => atualizar("ano", e.target.value)}
        className={CAMPO_SELECT_CLASSE}
        aria-label="Ano"
      >
        {ANOS_DISPONIVEIS.map((a) => (
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
