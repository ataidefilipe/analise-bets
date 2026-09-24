import Link from "next/link";
import type { PartidaResumo } from "@/lib/types/partida";
import { formatarData, formatarPlacar } from "@/lib/format/partida";
import { nomeSerie } from "@/lib/opcoes";

interface ResultadoPartidasTabelaProps {
  itens: PartidaResumo[];
}

/** Rota do dossiê: a chave da partida é série + temporada + id, não o id sozinho. */
export function hrefDossie(p: { serie: string; ano: number; partidaId: number }): string {
  return `/partidas/${p.serie}/${p.ano}/${p.partidaId}`;
}

/** Tabela de partidas (mais recentes primeiro) — só a página atual, decidida pelo backend. */
export function ResultadoPartidasTabela({ itens }: ResultadoPartidasTabelaProps) {
  return (
    <div className="overflow-x-auto rounded-md border border-zinc-200 dark:border-zinc-800">
      <table className="w-full min-w-120 text-sm">
        <thead>
          <tr className="border-b border-zinc-200 text-left text-xs tracking-wide text-zinc-500 uppercase dark:border-zinc-800 dark:text-zinc-400">
            <th className="px-4 py-2 font-medium">Partida</th>
            <th className="px-4 py-2 font-medium">Competição</th>
            <th className="px-4 py-2 font-medium">Data</th>
          </tr>
        </thead>
        <tbody>
          {itens.map((partida) => (
            <tr
              key={`${partida.serie}-${partida.ano}-${partida.partidaId}`}
              className="border-b border-zinc-100 last:border-0 dark:border-zinc-900"
            >
              <td className="px-4 py-2">
                <Link
                  href={hrefDossie(partida)}
                  className="font-medium text-zinc-900 hover:text-brand dark:text-zinc-50 dark:hover:text-link"
                >
                  {partida.clubeMandante} {formatarPlacar(partida.placar)} {partida.clubeVisitante}
                </Link>
                {!partida.temProcedencia && (
                  <span className="block text-xs text-zinc-400 dark:text-zinc-500">sem procedência documental</span>
                )}
              </td>
              <td className="px-4 py-2 text-zinc-700 dark:text-zinc-300">
                {nomeSerie(partida.serie)} {partida.ano} · Rodada {partida.rodada}
              </td>
              <td className="px-4 py-2 text-zinc-500 dark:text-zinc-400">{formatarData(partida.data)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
