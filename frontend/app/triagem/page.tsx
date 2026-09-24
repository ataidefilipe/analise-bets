import { Callout } from "@/components/ui/Callout";
import { EmptyState } from "@/components/ui/EmptyState";
import { RodadaFiltros } from "@/components/fila-triagem/RodadaFiltros";
import { FilaTriagemPainel } from "@/components/fila-triagem/FilaTriagemPainel";
import { exigirAcessoTela } from "@/lib/api/sessao";
import { getCobertura } from "@/lib/api/cobertura";
import { getFilaTriagem } from "@/lib/api/fila";
import { TOTAL_RODADAS, lerInteiro, lerSerie, primeiroParam } from "@/lib/opcoes";

function lerPercentil(valor: string | string[] | undefined): number | undefined {
  const n = Number(primeiroParam(valor));
  return primeiroParam(valor) !== undefined && Number.isFinite(n) && n >= 0 && n <= 100 ? n : undefined;
}

export default async function TriagemPage({ searchParams }: PageProps<"/triagem">) {
  const perfil = await exigirAcessoTela("fila-triagem");
  const [sp, cobertura] = await Promise.all([searchParams, getCobertura()]);

  // Sem filtro na URL, abre na temporada mais recente com escore, na última rodada com escalação.
  const serie = lerSerie(sp.serie);
  const temporadas = cobertura[serie].fila;
  const anoPedido = lerInteiro(sp.ano);
  const temporada = temporadas.find((t) => t.temporada === anoPedido) ?? temporadas[0];

  if (!temporada) {
    return (
      <EmptyState
        titulo="Sem escore pré-jogo para esta série."
        descricao="A fila de triagem depende da escalação publicada na súmula eletrônica."
      />
    );
  }

  const rodadaPedida = lerInteiro(sp.rodada);
  const rodada = rodadaPedida && rodadaPedida <= TOTAL_RODADAS ? rodadaPedida : temporada.ultima_rodada;

  const fila = await getFilaTriagem({
    serie,
    ano: temporada.temporada,
    rodada,
    percentil: lerPercentil(sp.percentil),
    avisoInterpretativo: perfil.avisoInterpretativo,
  });

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-4">
      <div className="flex flex-col gap-2">
        <h1 className="text-lg font-semibold text-ink">
          Triagem da rodada
          {fila.clubeEscopo ? ` — Elenco do ${fila.clubeEscopo.nome}` : ""}
        </h1>
        <RodadaFiltros
          serie={serie}
          ano={temporada.temporada}
          rodada={rodada}
          anos={temporadas.map((t) => t.temporada)}
        />
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
            // Remonta quando a rodada muda, para o slider voltar ao corte que o backend aplicou.
            key={`${serie}-${temporada.temporada}-${rodada}`}
            itens={fila.itens}
            totalRelacionados={fila.totalRelacionados}
            totalSinalizados={fila.totalSinalizados}
            percentilAplicado={fila.percentilAplicado}
          />
        </>
      )}
    </div>
  );
}
