import { Callout } from "@/components/ui/Callout";
import { EmptyState } from "@/components/ui/EmptyState";
import { RodadaFiltros } from "@/components/fila-triagem/RodadaFiltros";
import { FilaTriagemPainel } from "@/components/fila-triagem/FilaTriagemPainel";
import { getFilaTriagem } from "@/lib/mock/filaTriagem";
import { ANOS_DISPONIVEIS, COMPETICOES, TOTAL_RODADAS } from "@/lib/mock/opcoesRodada";
import { exigirAcessoTela } from "@/lib/mock/acesso";

type ValorParam = string | string[] | undefined;

function primeiro(valor: ValorParam): string | undefined {
  return Array.isArray(valor) ? valor[0] : valor;
}

function lerCompeticao(valor: ValorParam): string {
  const v = primeiro(valor);
  return COMPETICOES.some((c) => c.slug === v) ? (v as string) : COMPETICOES[0].slug;
}

function lerAno(valor: ValorParam): number {
  const n = Number(primeiro(valor));
  return (ANOS_DISPONIVEIS as readonly number[]).includes(n) ? n : ANOS_DISPONIVEIS[0];
}

function lerRodada(valor: ValorParam): number {
  const n = Number(primeiro(valor));
  return Number.isInteger(n) && n >= 1 && n <= TOTAL_RODADAS ? n : 1;
}

export default async function TriagemPage({ searchParams }: PageProps<"/triagem">) {
  const sp = await searchParams;
  const competicao = lerCompeticao(sp.competicao);
  const ano = lerAno(sp.ano);
  const rodada = lerRodada(sp.rodada);

  const perfil = await exigirAcessoTela("fila-triagem");
  const fila = await getFilaTriagem({ competicao, ano, rodada, clubeSlug: perfil.clube?.slug });

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-4">
      <div className="flex flex-col gap-2">
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          Triagem da rodada
          {fila.clubeEscopo ? ` — Elenco do ${fila.clubeEscopo.nome}` : ""}
        </h1>
        <RodadaFiltros competicao={competicao} ano={ano} rodada={rodada} />
      </div>

      {!fila.escalacaoPublicada ? (
        <EmptyState
          titulo="Escalação ainda não publicada"
          descricao="A escalação desta rodada ainda não foi publicada pela CBF. A fila fica disponível após a publicação da súmula."
        />
      ) : (
        <>
          <Callout>{fila.avisoInterpretativo}</Callout>
          {fila.baseRasa && (
            <Callout>
              Histórico insuficiente nas primeiras rodadas; os escores são dominados pela média da liga.
            </Callout>
          )}
          <FilaTriagemPainel
            itens={fila.itens}
            totalRelacionados={fila.totalRelacionados}
            percentilInicial={perfil.limiarPadrao}
          />
        </>
      )}
    </div>
  );
}
