import Link from "next/link";
import { EmptyState } from "@/components/ui/EmptyState";

/** 404 da API ou rota inexistente (doc 03, §6): partida ou atleta que não está na base. */
export default function NaoEncontrado() {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center gap-3">
      <EmptyState titulo="Não encontrado." descricao="A partida ou o atleta procurado não está na base." />
      <Link href="/" className="text-sm text-link hover:underline">
        Voltar para o início
      </Link>
    </div>
  );
}
