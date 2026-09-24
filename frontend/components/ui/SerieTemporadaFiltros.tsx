"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { SERIES, type Serie } from "@/lib/opcoes";

interface SerieTemporadaFiltrosProps {
  serie: Serie;
  ano: number | undefined;
  /** Temporadas disponíveis por série, vindas de `/v1/cobertura`. */
  anosPorSerie: Record<Serie, number[]>;
  /** Mostra "Todas as temporadas" como primeira opção. */
  permitirTodas?: boolean;
  /** Parâmetros da URL que devem sobreviver à troca (ex.: `modo`). O resto é descartado. */
  manter?: string[];
}

const CAMPO_SELECT_CLASSE =
  "rounded-full border border-line-strong bg-surface px-3 py-1.5 text-sm text-body focus-visible:border-link focus-visible:outline-none";

/**
 * Par série + temporada, genérico (partidas e panorama). Trocar a série
 * descarta a temporada, que pode não existir na outra série. Busca e página
 * são descartadas sempre, para não cair numa página que não existe mais.
 */
export function SerieTemporadaFiltros({ serie, ano, anosPorSerie, permitirTodas = false, manter = [] }: SerieTemporadaFiltrosProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  function navegar(proximaSerie: Serie, proximoAno: string) {
    const params = new URLSearchParams();
    for (const chave of manter) {
      const valor = searchParams.get(chave);
      if (valor) params.set(chave, valor);
    }
    params.set("serie", proximaSerie);
    if (proximoAno) params.set("ano", proximoAno);
    router.push(`${pathname}?${params.toString()}`);
  }

  return (
    <div className="flex flex-wrap gap-2">
      <select
        value={serie}
        onChange={(e) => navegar(e.target.value as Serie, "")}
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
        value={ano ?? ""}
        onChange={(e) => navegar(serie, e.target.value)}
        className={CAMPO_SELECT_CLASSE}
        aria-label="Temporada"
      >
        {permitirTodas && <option value="">Todas as temporadas</option>}
        {anosPorSerie[serie].map((a) => (
          <option key={a} value={a}>
            {a}
          </option>
        ))}
      </select>
    </div>
  );
}
