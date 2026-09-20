"use client";

import { usePathname, useRouter } from "next/navigation";
import { COMPETICOES } from "@/lib/mock/opcoesRodada";
import type { ModoAgregacao } from "@/lib/types/agregado";

interface FiltrosAgregadoProps {
  modo: ModoAgregacao;
  /** "" = todas as competições. */
  competicao: string;
}

const BOTAO_ATIVO = "rounded bg-brand px-3 py-1.5 text-sm font-medium text-brand-foreground";
const BOTAO_INATIVO =
  "rounded px-3 py-1.5 text-sm text-zinc-700 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800";

/** Alterna entre agregação por clube e por rodada (doc 03, §5), e filtra por competição. */
export function FiltrosAgregado({ modo, competicao }: FiltrosAgregadoProps) {
  const router = useRouter();
  const pathname = usePathname();

  function atualizar(campo: "modo" | "competicao", valor: string) {
    const params = new URLSearchParams();
    params.set("modo", campo === "modo" ? valor : modo);
    const proximaCompeticao = campo === "competicao" ? valor : competicao;
    if (proximaCompeticao) {
      params.set("competicao", proximaCompeticao);
    }
    router.push(`${pathname}?${params.toString()}`);
  }

  return (
    <div className="flex flex-wrap items-center gap-4">
      <div className="flex gap-1" role="group" aria-label="Agregar por">
        <button
          type="button"
          onClick={() => atualizar("modo", "clube")}
          className={modo === "clube" ? BOTAO_ATIVO : BOTAO_INATIVO}
        >
          Por clube
        </button>
        <button
          type="button"
          onClick={() => atualizar("modo", "rodada")}
          className={modo === "rodada" ? BOTAO_ATIVO : BOTAO_INATIVO}
        >
          Por rodada
        </button>
      </div>
      <select
        value={competicao}
        onChange={(e) => atualizar("competicao", e.target.value)}
        aria-label="Competição"
        className="rounded border border-zinc-300 bg-white px-2 py-1 text-sm text-zinc-700 focus-visible:border-brand focus-visible:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:focus-visible:border-link"
      >
        <option value="">Todas as competições</option>
        {COMPETICOES.map((c) => (
          <option key={c.slug} value={c.slug}>
            {c.nome}
          </option>
        ))}
      </select>
    </div>
  );
}
