import { BuscaAtletaForm } from "@/components/busca-atleta/BuscaAtletaForm";
import { Pager } from "@/components/busca-atleta/Pager";
import { ResultadoBuscaLista } from "@/components/busca-atleta/ResultadoBuscaLista";
import { EmptyState } from "@/components/ui/EmptyState";
import { buscarAtletas } from "@/lib/mock/buscaAtletas";

const POR_PAGINA = 10;

function primeiro(valor: string | string[] | undefined): string | undefined {
  return Array.isArray(valor) ? valor[0] : valor;
}

function lerPagina(valor: string | string[] | undefined): number {
  const n = Number(primeiro(valor));
  return Number.isInteger(n) && n >= 1 ? n : 1;
}

export default async function AtletasPage({ searchParams }: PageProps<"/atletas">) {
  const sp = await searchParams;
  const consulta = (primeiro(sp.q) ?? "").trim();
  const pagina = lerPagina(sp.pagina);

  const resultado =
    consulta.length >= 3
      ? await buscarAtletas(consulta, pagina, POR_PAGINA)
      : { itens: [], total: 0, pagina: 1, porPagina: POR_PAGINA };
  const totalPaginas = Math.max(1, Math.ceil(resultado.total / POR_PAGINA));

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4">
      <div className="flex flex-col gap-2">
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Consulta de atleta</h1>
        <BuscaAtletaForm valorInicial={consulta} />
      </div>

      {consulta.length === 0 ? null : consulta.length < 3 ? (
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Digite ao menos 3 caracteres para buscar.</p>
      ) : resultado.itens.length === 0 ? (
        <EmptyState
          titulo="Nenhum atleta encontrado."
          descricao="A base cobre Série A desde 2003 e Série B desde 2022."
        />
      ) : (
        <>
          <ResultadoBuscaLista itens={resultado.itens} />
          <Pager consulta={consulta} pagina={resultado.pagina} totalPaginas={totalPaginas} />
        </>
      )}
    </div>
  );
}
