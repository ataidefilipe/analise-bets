interface ProporcaoPorClubeChartProps {
  dados: { clubeNome: string; cartoesTotais: number; cartoes1T: number }[];
}

/**
 * Gráfico de barras de proporção de cartões no 1º tempo por clube (doc 03,
 * §5) — sempre por clube, mesmo quando a tabela acima está agregada por
 * rodada. Série única (magnitude por categoria): uma cor só (o acento da
 * marca), sem legenda — o título já diz o que é — com o valor direto na
 * ponta de cada barra em vez de eixo/grade, já que todo valor está
 * rotulado.
 */
export function ProporcaoPorClubeChart({ dados }: ProporcaoPorClubeChartProps) {
  const linhas = dados
    .map((item) => ({
      clubeNome: item.clubeNome,
      proporcao: item.cartoesTotais === 0 ? 0 : Math.round((item.cartoes1T / item.cartoesTotais) * 100),
    }))
    .sort((a, b) => b.proporcao - a.proporcao);

  if (linhas.length === 0) {
    return null;
  }

  return (
    <div className="rounded-3xl border border-line bg-surface shadow-card p-4">
      <h2 className="text-sm font-semibold text-ink">
        Proporção de cartões no 1º tempo por clube
      </h2>
      <p className="mb-3 text-xs text-muted">
        Percentual dos cartões de cada clube que aconteceram até o intervalo.
      </p>
      <div className="flex flex-col gap-1.5">
        {linhas.map((item) => (
          <div key={item.clubeNome} className="flex items-center gap-2">
            <span
              className="w-28 shrink-0 truncate text-xs text-muted"
              title={item.clubeNome}
            >
              {item.clubeNome}
            </span>
            <div className="h-4 min-w-0 flex-1">
              <div
                className="h-4 rounded-r bg-accent"
                style={{ width: `${item.proporcao}%` }}
                title={`${item.clubeNome}: ${item.proporcao}%`}
              />
            </div>
            <span className="w-10 shrink-0 text-right text-xs text-body tabular-nums">
              {item.proporcao}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
