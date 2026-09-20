import { BuscaAtletaForm } from "@/components/busca-atleta/BuscaAtletaForm";
import { ResultadoBuscaTabela } from "@/components/busca-atleta/ResultadoBuscaTabela";
import { EmptyState } from "@/components/ui/EmptyState";
import { listarAtletas } from "@/lib/mock/buscaAtletas";

function primeiro(valor: string | string[] | undefined): string | undefined {
  return Array.isArray(valor) ? valor[0] : valor;
}

export default async function AtletasPage({ searchParams }: PageProps<"/atletas">) {
  const sp = await searchParams;
  const consulta = (primeiro(sp.q) ?? "").trim();
  const buscaCurta = consulta.length > 0 && consulta.length < 3;

  const itens = buscaCurta ? [] : await listarAtletas(consulta);

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4">
      <div className="flex flex-col gap-2">
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Consulta de atleta</h1>
        <BuscaAtletaForm valorInicial={consulta} />
      </div>

      {buscaCurta ? (
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Digite ao menos 3 caracteres para buscar.</p>
      ) : itens.length === 0 ? (
        <EmptyState
          titulo="Nenhum atleta encontrado."
          descricao="A base cobre Série A desde 2003 e Série B desde 2022."
        />
      ) : (
        <ResultadoBuscaTabela itens={itens} />
      )}
    </div>
  );
}
