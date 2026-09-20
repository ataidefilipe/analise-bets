import type { TemporadaResumo } from "@/lib/types/atleta";
import { formatarProporcao } from "@/lib/format/proporcao";
import { formatarTier } from "@/lib/format/tier";

interface HistoricoTemporadasProps {
  temporadas: TemporadaResumo[];
}

const TH_NUMERICO = "px-4 py-2 text-right font-medium";
const TD_NUMERICO = "px-4 py-2 text-right text-zinc-700 dark:text-zinc-300";

/**
 * Uma linha por temporada (doc 03, §3): "é onde o padrão aparece — proporção
 * de 1º tempo consistentemente alta ao longo de temporadas diz mais que um
 * escore isolado".
 */
export function HistoricoTemporadas({ temporadas }: HistoricoTemporadasProps) {
  if (temporadas.length === 0) {
    return <p className="text-sm text-zinc-500 dark:text-zinc-400">Sem temporadas registradas.</p>;
  }

  return (
    <div>
      <h2 className="mb-2 text-sm font-semibold text-zinc-900 dark:text-zinc-50">Histórico por temporada</h2>
      <div className="overflow-x-auto rounded-md border border-zinc-200 dark:border-zinc-800">
        <table className="w-full min-w-[600px] text-sm">
          <thead>
            <tr className="border-b border-zinc-200 text-xs tracking-wide text-zinc-500 uppercase dark:border-zinc-800 dark:text-zinc-400">
              <th className="px-4 py-2 text-left font-medium">Temporada</th>
              <th className="px-4 py-2 text-left font-medium">Clube</th>
              <th className={TH_NUMERICO}>Partidas</th>
              <th className={TH_NUMERICO}>Minutos</th>
              <th className={TH_NUMERICO}>Cartões</th>
              <th className={TH_NUMERICO}>1º tempo</th>
              <th className={TH_NUMERICO}>Proporção</th>
              <th className="px-4 py-2 text-left font-medium">Tier</th>
            </tr>
          </thead>
          <tbody>
            {temporadas.map((temporada) => (
              <tr key={temporada.ano} className="border-b border-zinc-100 last:border-0 dark:border-zinc-900">
                <td className="px-4 py-2 text-zinc-900 dark:text-zinc-50">{temporada.ano}</td>
                <td className="px-4 py-2 text-zinc-700 dark:text-zinc-300">{temporada.clubeNome}</td>
                <td className={TD_NUMERICO}>{temporada.partidasJogadas}</td>
                <td className={TD_NUMERICO}>{temporada.minutosJogados.toLocaleString("pt-BR")}</td>
                <td className={TD_NUMERICO}>{temporada.cartoesTotais}</td>
                <td className={TD_NUMERICO}>{temporada.cartoes1T}</td>
                <td className={TD_NUMERICO}>{formatarProporcao(temporada.cartoes1T, temporada.cartoesTotais)}</td>
                <td className="px-4 py-2 text-zinc-700 dark:text-zinc-300">{formatarTier(temporada)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
