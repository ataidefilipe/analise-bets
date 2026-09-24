import { redirect } from "next/navigation";
import { EntrarForm } from "@/components/layout/EntrarForm";
import { FundoDecorativo } from "@/components/ui/FundoDecorativo";
import { getPerfilAtual } from "@/lib/api/sessao";

/**
 * Entrada por chave de API (doc 01, §2). Não há cadastro nem recuperação: as
 * chaves são emitidas manualmente pelo backend.
 */
export default async function EntrarPage() {
  if (await getPerfilAtual()) redirect("/");

  return (
    <>
      <FundoDecorativo />
      <div className="flex w-full max-w-sm flex-col gap-6 rounded-3xl border border-line bg-surface/80 p-8 shadow-card backdrop-blur-sm">
        <div className="flex flex-col gap-2">
          <h1 className="text-2xl font-bold tracking-tight text-ink">Análise de integridade</h1>
          <p className="text-sm text-muted">
            Informe a chave de acesso fornecida pela equipe do projeto. O perfil e o que você pode ver vêm dela.
          </p>
        </div>
        <EntrarForm />
      </div>
    </>
  );
}
