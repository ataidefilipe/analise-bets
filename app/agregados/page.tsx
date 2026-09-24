import { EmptyState } from "@/components/ui/EmptyState";
import { SerieTemporadaFiltros } from "@/components/ui/SerieTemporadaFiltros";
import { FiltrosAgregado } from "@/components/panorama-agregado/FiltrosAgregado";
import { AgregadoTabela, type LinhaAgregado } from "@/components/panorama-agregado/AgregadoTabela";
import { ProporcaoPorClubeChart } from "@/components/panorama-agregado/ProporcaoPorClubeChart";
import { exigirAcessoTela } from "@/lib/api/sessao";
import { getCobertura } from "@/lib/api/cobertura";
import { getAgregadoPorClube, getAgregadoPorRodada } from "@/lib/api/agregados";
import type { ModoAgregacao } from "@/lib/types/agregado";
import { lerInteiro, lerSerie, nomeSerie, primeiroParam } from "@/lib/opcoes";

export default async function AgregadosPage({ searchParams }: PageProps<"/agregados">) {
  await exigirAcessoTela("panorama-agregado");
  const [sp, cobertura] = await Promise.all([searchParams, getCobertura()]);
  const modo: ModoAgregacao = primeiroParam(sp.modo) === "rodada" ? "rodada" : "clube";

  // A API agrega uma série e uma temporada por vez; sem filtro, abre na mais recente.
  const serie = lerSerie(sp.serie);
  const temporadas = cobertura[serie].temporadas;
  const anoPedido = lerInteiro(sp.ano);
  const ano = anoPedido && temporadas.includes(anoPedido) ? anoPedido : temporadas[0];

  const filtros = (
    <div className="flex flex-wrap items-center gap-4">
      <FiltrosAgregado modo={modo} />
      <SerieTemporadaFiltros
        serie={serie}
        ano={ano}
        anosPorSerie={{ A: cobertura.A.temporadas, B: cobertura.B.temporadas }}
        manter={["modo"]}
      />
    </div>
  );

  let linhas: LinhaAgregado[] = [];
  let dadosGrafico: { clubeNome: string; cartoesTotais: number; cartoes1T: number }[] = [];

  if (ano) {
    // O gráfico é sempre por clube, mesmo com a tabela agregada por rodada.
    const [porClube, porRodada] = await Promise.all([
      getAgregadoPorClube(serie, ano),
      modo === "rodada" ? getAgregadoPorRodada(serie, ano) : Promise.resolve([]),
    ]);
    dadosGrafico = porClube;
    linhas =
      modo === "clube"
        ? porClube.map((a) => ({ chave: a.clubeNome, rotulo: a.clubeNome, ...a }))
        : porRodada.map((a) => ({
            chave: String(a.rodada),
            rotulo: `Rodada ${a.rodada}`,
            partidas: a.partidas,
            cartoesTotais: a.cartoesTotais,
            cartoes1T: a.cartoes1T,
          }));
  }

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Panorama agregado</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          Cartões agregados por clube ou por rodada — camada aberta, sem nenhum atleta.
          {ano ? ` ${nomeSerie(serie)} ${ano}.` : ""}
        </p>
      </div>

      {filtros}

      {linhas.length === 0 ? (
        <EmptyState titulo="Nenhum dado agregado disponível." descricao="Tente outra série ou temporada." />
      ) : (
        <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-2">
          <AgregadoTabela linhas={linhas} rotuloColuna={modo === "clube" ? "Clube" : "Rodada"} />
          <ProporcaoPorClubeChart dados={dadosGrafico} />
        </div>
      )}
    </div>
  );
}
