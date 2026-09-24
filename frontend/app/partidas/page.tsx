import { BuscaForm } from "@/components/ui/BuscaForm";
import { Pager } from "@/components/ui/Pager";
import { SerieTemporadaFiltros } from "@/components/ui/SerieTemporadaFiltros";
import { ResultadoPartidasTabela } from "@/components/dossie-partida/ResultadoPartidasTabela";
import { EmptyState } from "@/components/ui/EmptyState";
import { exigirAcessoTela } from "@/lib/api/sessao";
import { getCobertura } from "@/lib/api/cobertura";
import { listarPartidas } from "@/lib/api/partidas";
import { lerInteiro, lerSerie, primeiroParam } from "@/lib/opcoes";

/**
 * O doc 03 não descreve uma tela de listagem para a T3 — assume que P3
 * chega numa partida específica por referência externa. Esta lista existe
 * para navegar até um dossiê, agora sobre `GET /v1/partidas`: busca por nome
 * de clube e paginação feitas no backend.
 */
export default async function PartidasPage({ searchParams }: PageProps<"/partidas">) {
  await exigirAcessoTela("dossie-partida");
  const [sp, cobertura] = await Promise.all([searchParams, getCobertura()]);
  const serie = lerSerie(sp.serie);
  const anoPedido = lerInteiro(sp.ano);
  const ano = anoPedido && cobertura[serie].temporadas.includes(anoPedido) ? anoPedido : undefined;
  const consulta = (primeiroParam(sp.q) ?? "").trim();
  const buscaCurta = consulta.length > 0 && consulta.length < 3;

  const pagina = buscaCurta
    ? null
    : await listarPartidas({ serie, ano, consulta: consulta || undefined, pagina: lerInteiro(sp.pagina) });

  const filtros: Record<string, string> = ano ? { serie, ano: String(ano) } : { serie };

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4">
      <div className="flex flex-col gap-2">
        <h1 className="text-lg font-semibold text-ink">Partidas monitoradas</h1>
        <SerieTemporadaFiltros
          serie={serie}
          ano={ano}
          anosPorSerie={{ A: cobertura.A.temporadas, B: cobertura.B.temporadas }}
          permitirTodas
        />
        <BuscaForm basePath="/partidas" valorInicial={consulta} placeholder="nome de um dos clubes..." parametros={filtros} />
      </div>

      {buscaCurta || !pagina ? (
        <p className="text-sm text-muted">Digite ao menos 3 caracteres para buscar.</p>
      ) : pagina.itens.length === 0 ? (
        <EmptyState titulo="Nenhuma partida encontrada." descricao="Tente buscar pelo nome de um dos clubes ou mudar a temporada." />
      ) : (
        <>
          <p className="text-sm text-muted">
            {pagina.totalItens.toLocaleString("pt-BR")} partidas no total
          </p>
          <ResultadoPartidasTabela itens={pagina.itens} />
          <Pager
            basePath="/partidas"
            consulta={consulta}
            pagina={pagina.pagina}
            totalPaginas={pagina.totalPaginas}
            parametros={filtros}
          />
        </>
      )}
    </div>
  );
}
