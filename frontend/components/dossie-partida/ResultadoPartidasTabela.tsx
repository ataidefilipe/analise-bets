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
    <div className="overflow-x-auto rounded-2xl border border-line bg-surface shadow-card">
      <table className="w-full min-w-120 text-sm">
        <thead>
          <tr className="border-b border-line text-left text-xs tracking-wide text-muted uppercase bg-surface-muted">
            <th className="px-4 py-2 font-medium">Partida</th>
            <th className="px-4 py-2 font-medium">Competição</th>
            <th className="px-4 py-2 font-medium">Data</th>
          </tr>
        </thead>
        <tbody>
          {itens.map((partida) => (
            <tr
              key={`${partida.serie}-${partida.ano}-${partida.partidaId}`}
              className="border-b border-line-soft last:border-0"
            >
              <td className="px-4 py-2">
                <Link
                  href={hrefDossie(partida)}
                  className="font-medium text-ink hover:text-link"
                >
                  {partida.clubeMandante} {formatarPlacar(partida.placar)} {partida.clubeVisitante}
                </Link>
                {!partida.temProcedencia && (
                  <span className="block text-xs text-subtle">sem procedência documental</span>
                )}
              </td>
              <td className="px-4 py-2 text-body">
                {nomeSerie(partida.serie)} {partida.ano} · Rodada {partida.rodada}
              </td>
              <td className="px-4 py-2 text-muted">{formatarData(partida.data)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
