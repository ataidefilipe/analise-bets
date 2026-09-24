import { redirect } from "next/navigation";
import { EntrarForm } from "@/components/layout/EntrarForm";
import { getPerfilAtual } from "@/lib/api/sessao";

/**
 * Entrada por chave de API (doc 01, §2). Não há cadastro nem recuperação: as
 * chaves são emitidas manualmente pelo backend.
 */
export default async function EntrarPage() {
  if (await getPerfilAtual()) redirect("/");

  return (
    <div className="flex w-full max-w-sm flex-col gap-4">
      <div>
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Análise de integridade</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          Informe a chave de acesso fornecida pela equipe do projeto. O perfil e o que você pode ver vêm dela.
        </p>
      </div>
      <EntrarForm />
    </div>
  );
}
