import type { IdentificacaoPartida as IdentificacaoPartidaType } from "@/lib/types/partida";
import { formatarData, formatarPlacar } from "@/lib/format/partida";
import { nomeSerie } from "@/lib/opcoes";

interface IdentificacaoPartidaProps {
  identificacao: IdentificacaoPartidaType;
}

/** Seção 1 do dossiê (doc 03, §4): partida, data, arena, árbitro, placar. */
export function IdentificacaoPartida({ identificacao }: IdentificacaoPartidaProps) {
  return (
    <div className="flex flex-col gap-1">
      <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        {identificacao.clubeMandante} {formatarPlacar(identificacao.placar)} {identificacao.clubeVisitante}
      </h1>
      <p className="text-sm text-zinc-500 dark:text-zinc-400">
        {[
          formatarData(identificacao.data),
          identificacao.arena,
          identificacao.arbitro ? `Árbitro: ${identificacao.arbitro}` : null,
        ]
          .filter(Boolean)
          .join(" · ")}
      </p>
      <p className="text-xs text-zinc-400 dark:text-zinc-600">
        {nomeSerie(identificacao.serie)} · Rodada {identificacao.rodada}/{identificacao.ano}
      </p>
    </div>
  );
}
