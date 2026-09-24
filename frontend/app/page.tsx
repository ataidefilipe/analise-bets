import Link from "next/link";
import { redirect } from "next/navigation";
import { getPerfilAtual } from "@/lib/api/sessao";
import { TELAS } from "@/lib/telas";
import { EmptyState } from "@/components/ui/EmptyState";
import { FundoDecorativo } from "@/components/ui/FundoDecorativo";

export default async function Home() {
  const perfil = await getPerfilAtual();
  if (!perfil) redirect("/entrar");
  const telasVisiveis = TELAS.filter((tela) => perfil.telasPermitidas.includes(tela.id));

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-8 pt-6">
      <FundoDecorativo />
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight text-ink sm:text-4xl">
          Olá, {perfil.nome}
        </h1>
        <p className="text-base text-muted">
          Estas são as telas disponíveis para o seu perfil.
        </p>
      </div>

      {telasVisiveis.length === 0 ? (
        <EmptyState
          titulo="Nenhuma tela disponível"
          descricao="Este perfil ainda não tem acesso a nenhuma das telas do MVP."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {telasVisiveis.map((tela) => (
            <Link
              key={tela.id}
              href={tela.rota}
              className="group flex flex-col gap-2 rounded-3xl border border-line bg-surface p-6 shadow-card transition hover:-translate-y-0.5 hover:border-link"
            >
              <span className="text-lg font-semibold text-ink transition-colors group-hover:text-link">{tela.rotulo}</span>
              <span className="text-sm text-muted">{tela.descricaoCurta}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
