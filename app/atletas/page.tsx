import { BuscaForm } from "@/components/ui/BuscaForm";
import { ResultadoBuscaTabela } from "@/components/busca-atleta/ResultadoBuscaTabela";
import { EmptyState } from "@/components/ui/EmptyState";
import { exigirAcessoTela } from "@/lib/api/sessao";
import { LIMITE_BUSCA, buscarAtletas } from "@/lib/api/atletas";
import { primeiroParam } from "@/lib/opcoes";

/**
 * T2, busca (doc 03, §3). Não há listagem prévia de atletas: a API só
 * responde a uma busca de 3+ caracteres, com até 20 resultados e sem escore
 * — a busca acha uma pessoa, não percorre a base (doc 01, §5). Por isso a
 * tabela completa com paginação dos passos 5 e 6 foi retirada.
 */
export default async function AtletasPage({ searchParams }: PageProps<"/atletas">) {
  await exigirAcessoTela("busca-atleta");
  const sp = await searchParams;
  const consulta = (primeiroParam(sp.q) ?? "").trim();
  const buscaCurta = consulta.length > 0 && consulta.length < 3;
  const resultados = consulta.length >= 3 ? await buscarAtletas(consulta) : [];

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4">
      <div className="flex flex-col gap-2">
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Consulta de atleta</h1>
        <BuscaForm basePath="/atletas" valorInicial={consulta} placeholder="nome ou apelido..." />
      </div>

      {consulta.length === 0 ? (
        <EmptyState
          titulo="Busque um atleta pelo nome ou apelido."
          descricao="Digite ao menos 3 caracteres. A busca cobre atletas com súmula eletrônica: Série A desde 2025 e Série B desde 2022."
        />
      ) : buscaCurta ? (
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Digite ao menos 3 caracteres para buscar.</p>
      ) : resultados.length === 0 ? (
        <EmptyState
          titulo="Nenhum atleta encontrado."
          descricao="A busca cobre atletas com súmula eletrônica: Série A desde 2025 e Série B desde 2022."
        />
      ) : (
        <>
          <ResultadoBuscaTabela itens={resultados} />
          {resultados.length >= LIMITE_BUSCA && (
            <p className="text-sm text-zinc-500 dark:text-zinc-400">
              Mostrando os {LIMITE_BUSCA} primeiros resultados. Refine a busca para encontrar outro atleta.
            </p>
          )}
        </>
      )}
    </div>
  );
}
