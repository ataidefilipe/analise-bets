import { BuscaAtletaForm } from "@/components/busca-atleta/BuscaAtletaForm";
import { Pager } from "@/components/busca-atleta/Pager";
import { ResultadoBuscaTabela } from "@/components/busca-atleta/ResultadoBuscaTabela";
import { EmptyState } from "@/components/ui/EmptyState";
import { listarAtletas } from "@/lib/mock/buscaAtletas";

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
  const buscaCurta = consulta.length > 0 && consulta.length < 3;

  const todos = buscaCurta ? [] : await listarAtletas(consulta);
  const totalPaginas = Math.max(1, Math.ceil(todos.length / POR_PAGINA));
  const pagina = Math.min(lerPagina(sp.pagina), totalPaginas);
  const itensDaPagina = todos.slice((pagina - 1) * POR_PAGINA, pagina * POR_PAGINA);

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4">
      <div className="flex flex-col gap-2">
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Consulta de atleta</h1>
        <BuscaAtletaForm valorInicial={consulta} />
      </div>

      {buscaCurta ? (
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Digite ao menos 3 caracteres para buscar.</p>
      ) : todos.length === 0 ? (
        <EmptyState
          titulo="Nenhum atleta encontrado."
          descricao="A base cobre Série A desde 2003 e Série B desde 2022."
        />
      ) : (
        <>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">{todos.length} atletas no total</p>
          <ResultadoBuscaTabela itens={itensDaPagina} />
          <Pager consulta={consulta} pagina={pagina} totalPaginas={totalPaginas} />
        </>
      )}
    </div>
  );
}
