"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import type { ModoAgregacao } from "@/lib/types/agregado";

interface FiltrosAgregadoProps {
  modo: ModoAgregacao;
}

const BOTAO_ATIVO = "rounded-full bg-brand px-4 py-1.5 text-sm font-medium text-brand-foreground shadow-sm";
const BOTAO_INATIVO =
  "rounded-full px-4 py-1.5 text-sm text-body hover:bg-surface-muted";

/**
 * Alterna entre agregação por clube e por rodada (doc 03, §5), mantendo a
 * série e a temporada escolhidas em `SerieTemporadaFiltros`.
 */
export function FiltrosAgregado({ modo }: FiltrosAgregadoProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  function atualizar(valor: ModoAgregacao) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("modo", valor);
    router.push(`${pathname}?${params.toString()}`);
  }

  return (
    <div className="flex gap-1" role="group" aria-label="Agregar por">
      <button type="button" onClick={() => atualizar("clube")} className={modo === "clube" ? BOTAO_ATIVO : BOTAO_INATIVO}>
        Por clube
      </button>
      <button
        type="button"
        onClick={() => atualizar("rodada")}
        className={modo === "rodada" ? BOTAO_ATIVO : BOTAO_INATIVO}
      >
        Por rodada
      </button>
    </div>
  );
}
