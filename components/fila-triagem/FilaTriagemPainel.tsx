"use client";

import { useMemo, useState } from "react";
import type { FilaTriagemItem } from "@/lib/types/fila-triagem";
import { EmptyState } from "@/components/ui/EmptyState";
import { FilaTriagemTabela } from "@/components/fila-triagem/FilaTriagemTabela";

interface FilaTriagemPainelProps {
  itens: FilaTriagemItem[];
  totalRelacionados: number;
  percentilInicial: number;
}

/** Doc 03, §2: "sem paginação no MVP — o corte já limita a fila a poucas dezenas". */
const LIMITE_EXIBICAO = 200;

/**
 * O controle de corte (doc 03, §2): "a funcionalidade mais importante desta
 * tela, porque a decisão de produto é a carga de alerta, não o algoritmo".
 * Filtra no cliente a lista já carregada — sem round-trip ao servidor a
 * cada arraste — para dar a resposta "em tempo real" que o doc pede.
 */
export function FilaTriagemPainel({ itens, totalRelacionados, percentilInicial }: FilaTriagemPainelProps) {
  const [percentil, setPercentil] = useState(percentilInicial);

  const filtrados = useMemo(
    () => itens.filter((item) => item.percentil >= percentil).slice(0, LIMITE_EXIBICAO),
    [itens, percentil],
  );

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-2 rounded-md border border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <label htmlFor="corte-percentil" className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
            Corte: percentil {percentil}
          </label>
          <span className="text-sm text-zinc-500 dark:text-zinc-400">
            {filtrados.length} de {totalRelacionados} relacionados
          </span>
        </div>
        <input
          id="corte-percentil"
          type="range"
          min={0}
          max={99}
          value={percentil}
          onChange={(e) => setPercentil(Number(e.target.value))}
          className="accent-brand"
        />
        <p className="text-xs text-zinc-500 dark:text-zinc-400">
          Baixar o corte captura mais casos conhecidos e também mais alarme falso.
        </p>
      </div>

      {filtrados.length === 0 ? (
        <EmptyState
          titulo="Nenhum atleta acima do corte atual."
          descricao="Reduza o percentil para ampliar a fila."
        />
      ) : (
        <FilaTriagemTabela itens={filtrados} />
      )}
    </div>
  );
}
