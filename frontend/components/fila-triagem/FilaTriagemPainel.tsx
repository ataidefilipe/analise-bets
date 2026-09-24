"use client";

import { useEffect, useRef, useState, useTransition } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import type { FilaTriagemItem } from "@/lib/types/fila-triagem";
import { EmptyState } from "@/components/ui/EmptyState";
import { FilaTriagemTabela } from "@/components/fila-triagem/FilaTriagemTabela";

interface FilaTriagemPainelProps {
  itens: FilaTriagemItem[];
  totalRelacionados: number;
  totalSinalizados: number;
  /** Corte que o backend aplicou nesta resposta — ponto de partida do slider. */
  percentilAplicado: number;
}

/** Espera o usuário parar de arrastar antes de pedir a fila de novo. */
const ESPERA_MS = 350;

/**
 * O controle de corte (doc 03, §2): "a funcionalidade mais importante desta
 * tela, porque a decisão de produto é a carga de alerta, não o algoritmo".
 *
 * O corte é aplicado no backend (a API devolve no máximo 200 itens e uma
 * rodada tem ~450 relacionados, então filtrar no navegador perderia gente).
 * O slider grava `?percentil=` na URL e a página de servidor busca a fila de
 * novo; o contador vem de `totalSinalizados`, não do tamanho da lista.
 */
export function FilaTriagemPainel({ itens, totalRelacionados, totalSinalizados, percentilAplicado }: FilaTriagemPainelProps) {
  const [percentil, setPercentil] = useState(Math.round(percentilAplicado));
  const [carregando, iniciarTransicao] = useTransition();
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const espera = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => () => clearTimeout(espera.current), []);

  function mudarCorte(valor: number) {
    setPercentil(valor);
    clearTimeout(espera.current);
    espera.current = setTimeout(() => {
      const params = new URLSearchParams(searchParams.toString());
      params.set("percentil", String(valor));
      iniciarTransicao(() => router.replace(`${pathname}?${params.toString()}`, { scroll: false }));
    }, ESPERA_MS);
  }

  const truncada = totalSinalizados > itens.length;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-2 rounded-3xl border border-line bg-surface shadow-card px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <label htmlFor="corte-percentil" className="text-sm font-medium text-body">
            Corte: percentil {percentil}
          </label>
          <span className="text-sm text-muted" aria-live="polite">
            {carregando ? "atualizando..." : `${totalSinalizados} de ${totalRelacionados} relacionados`}
          </span>
        </div>
        <input
          id="corte-percentil"
          type="range"
          min={0}
          max={99}
          value={percentil}
          onChange={(e) => mudarCorte(Number(e.target.value))}
          className="accent-brand"
        />
        <p className="text-xs text-muted">
          Baixar o corte captura mais casos conhecidos e também mais alarme falso.
        </p>
      </div>

      {itens.length === 0 ? (
        <EmptyState
          titulo="Nenhum atleta acima do corte atual."
          descricao="Reduza o percentil para ampliar a fila."
        />
      ) : (
        <>
          {truncada && (
            <p className="text-xs text-muted">
              Exibindo os {itens.length} de maior percentil. Suba o corte para ver uma fila completa.
            </p>
          )}
          <div className={carregando ? "opacity-60 transition-opacity" : undefined}>
            <FilaTriagemTabela itens={itens} />
          </div>
        </>
      )}
    </div>
  );
}
