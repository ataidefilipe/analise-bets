import Link from "next/link";
import type { AtletaResumo } from "@/lib/types/atleta";

interface ResultadoBuscaListaProps {
  itens: AtletaResumo[];
}

/**
 * Lista de resultados (doc 03, §3): só identificação e clubes — nunca
 * escore ou tier. Isso não é cerimônia; evita que uma busca ampla devolva
 * um ranking de atipicidade pronto para varredura. O perfil disciplinar só
 * aparece ao abrir a ficha.
 */
export function ResultadoBuscaLista({ itens }: ResultadoBuscaListaProps) {
  return (
    <ul className="divide-y divide-zinc-200 rounded-md border border-zinc-200 dark:divide-zinc-800 dark:border-zinc-800">
      {itens.map((atleta) => (
        <li key={atleta.atletaId}>
          <Link
            href={`/atletas/${atleta.atletaId}`}
            className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 px-4 py-3 text-sm hover:bg-zinc-50 dark:hover:bg-zinc-900"
          >
            <span className="font-medium text-zinc-900 dark:text-zinc-50">{atleta.nome}</span>
            <span className="text-zinc-500 dark:text-zinc-400">
              {atleta.clubes.map((clube) => clube.nome).join(", ")}
            </span>
            <span className="text-zinc-400 dark:text-zinc-500">até {atleta.ultimoAno}</span>
          </Link>
        </li>
      ))}
    </ul>
  );
}
