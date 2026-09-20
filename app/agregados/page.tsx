import { EmptyState } from "@/components/ui/EmptyState";
import { FiltrosAgregado } from "@/components/panorama-agregado/FiltrosAgregado";
import { AgregadoTabela, type LinhaAgregado } from "@/components/panorama-agregado/AgregadoTabela";
import { ProporcaoPorClubeChart } from "@/components/panorama-agregado/ProporcaoPorClubeChart";
import { getAgregadoPorClube, getAgregadoPorRodada } from "@/lib/mock/agregados";
import { COMPETICOES } from "@/lib/mock/opcoesRodada";
import type { ModoAgregacao } from "@/lib/types/agregado";

function primeiro(valor: string | string[] | undefined): string | undefined {
  return Array.isArray(valor) ? valor[0] : valor;
}

function nomeCompeticao(slug: string): string {
  return COMPETICOES.find((c) => c.slug === slug)?.nome ?? slug;
}

export default async function AgregadosPage({ searchParams }: PageProps<"/agregados">) {
  const sp = await searchParams;
  const modo: ModoAgregacao = primeiro(sp.modo) === "rodada" ? "rodada" : "clube";
  const competicaoParam = primeiro(sp.competicao);
  const competicao = COMPETICOES.some((c) => c.slug === competicaoParam) ? (competicaoParam as string) : "";

  let linhas: LinhaAgregado[];
  let rotuloColuna: string;
  let dadosGrafico: { clubeNome: string; cartoesTotais: number; cartoes1T: number }[];

  if (modo === "clube") {
    const agregados = await getAgregadoPorClube(competicao || undefined);
    linhas = agregados.map((a) => ({
      chave: a.clubeNome,
      rotulo: a.clubeNome,
      partidas: a.partidas,
      cartoesTotais: a.cartoesTotais,
      cartoes1T: a.cartoes1T,
    }));
    rotuloColuna = "Clube";
    dadosGrafico = agregados;
  } else {
    const [agregados, porClube] = await Promise.all([
      getAgregadoPorRodada(competicao || undefined),
      getAgregadoPorClube(competicao || undefined),
    ]);
    linhas = agregados.map((a) => ({
      chave: `${a.competicao}-${a.ano}-${a.rodada}`,
      rotulo: `Rodada ${a.rodada} · ${nomeCompeticao(a.competicao)}/${a.ano}`,
      partidas: a.partidas,
      cartoesTotais: a.cartoesTotais,
      cartoes1T: a.cartoes1T,
    }));
    rotuloColuna = "Rodada";
    dadosGrafico = porClube;
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Panorama agregado</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          Cartões agregados por clube ou por rodada — camada aberta, sem nenhum atleta.
        </p>
      </div>

      <FiltrosAgregado modo={modo} competicao={competicao} />

      {linhas.length === 0 ? (
        <EmptyState titulo="Nenhum dado agregado disponível." descricao="Tente outra competição." />
      ) : (
        <>
          <AgregadoTabela linhas={linhas} rotuloColuna={rotuloColuna} />
          <ProporcaoPorClubeChart dados={dadosGrafico} />
        </>
      )}
    </div>
  );
}
