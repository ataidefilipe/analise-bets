import Link from "next/link";
import { getPerfilAtual } from "@/lib/mock/perfilAtual";
import { TELAS } from "@/lib/mock/telas";
import { EmptyState } from "@/components/ui/EmptyState";

export default async function Home() {
  const perfil = await getPerfilAtual();
  const telasVisiveis = TELAS.filter((tela) => perfil.telasPermitidas.includes(tela.id));

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
          Olá, {perfil.nome}
        </h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          Estas são as telas disponíveis para o seu perfil.
        </p>
      </div>

      {telasVisiveis.length === 0 ? (
        <EmptyState
          titulo="Nenhuma tela disponível"
          descricao="Este perfil ainda não tem acesso a nenhuma das telas do MVP."
        />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {telasVisiveis.map((tela) => (
            <Link
              key={tela.id}
              href={tela.rota}
              className="flex flex-col gap-1 rounded-md border border-zinc-200 px-4 py-3 hover:border-zinc-400 dark:border-zinc-800 dark:hover:border-zinc-600"
            >
              <span className="font-medium text-zinc-900 dark:text-zinc-50">{tela.rotulo}</span>
              <span className="text-sm text-zinc-500 dark:text-zinc-400">{tela.descricaoCurta}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
