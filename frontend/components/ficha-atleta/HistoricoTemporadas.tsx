import type { TemporadaResumo } from "@/lib/types/atleta";
import { formatarProporcao } from "@/lib/format/proporcao";
import { formatarTier } from "@/lib/format/tier";

interface HistoricoTemporadasProps {
  temporadas: TemporadaResumo[];
}

const TH_NUMERICO = "px-4 py-2 text-right font-medium";
const TD_NUMERICO = "px-4 py-2 text-right text-body";

/**
 * Uma linha por temporada (doc 03, §3): "é onde o padrão aparece — proporção
 * de 1º tempo consistentemente alta ao longo de temporadas diz mais que um
 * escore isolado".
 */
export function HistoricoTemporadas({ temporadas }: HistoricoTemporadasProps) {
  const semTier = temporadas.every((t) => t.tier === null);

  if (temporadas.length === 0) {
    return <p className="text-sm text-muted">Sem temporadas registradas.</p>;
  }

  return (
    <div>
      <h2 className="mb-2 text-sm font-semibold text-ink">Histórico por temporada</h2>
      <div className="overflow-x-auto rounded-2xl border border-line bg-surface shadow-card">
        <table className="w-full min-w-[600px] text-sm">
          <thead>
            <tr className="border-b border-line text-xs tracking-wide text-muted uppercase">
              <th className="px-4 py-2 text-left font-medium">Temporada</th>
              <th className="px-4 py-2 text-left font-medium">Série</th>
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
              <tr
                key={`${temporada.ano}-${temporada.serie}-${temporada.clubeNome}`}
                className="border-b border-line-soft last:border-0">
                <td className="px-4 py-2 text-ink">{temporada.ano}</td>
                <td className="px-4 py-2 text-body">{temporada.serie}</td>
                <td className="px-4 py-2 text-body">{temporada.clubeNome}</td>
                <td className={TD_NUMERICO}>{temporada.partidasJogadas}</td>
                <td className={TD_NUMERICO}>{temporada.minutosJogados.toLocaleString("pt-BR")}</td>
                <td className={TD_NUMERICO}>{temporada.cartoesTotais}</td>
                <td className={TD_NUMERICO}>{temporada.cartoes1T}</td>
                <td className={TD_NUMERICO}>{formatarProporcao(temporada.cartoes1T, temporada.cartoesTotais)}</td>
                <td className="px-4 py-2 text-body">{formatarTier(temporada)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {semTier && (
        <p className="mt-2 text-xs text-muted">
          Tier só existe na janela do escore retrospectivo (Série A 2015–2024, Série B 2022–2023).
        </p>
      )}
    </div>
  );
}
