import Link from "next/link";
import type { AtletaResumo } from "@/lib/types/atleta";

interface ResultadoBuscaTabelaProps {
  itens: AtletaResumo[];
}

/**
 * Tabela de atletas em ordem alfabética (já vem ordenada de
 * `listarAtletas`) — só a página atual (10 itens), decidida pelo servidor.
 * Só identificação e clubes — nunca escore ou tier (doc 03, §3).
 */
export function ResultadoBuscaTabela({ itens }: ResultadoBuscaTabelaProps) {
  return (
    <div className="overflow-x-auto rounded-md border border-zinc-200 dark:border-zinc-800">
      <table className="w-full min-w-120 text-sm">
        <thead>
          <tr className="border-b border-zinc-200 text-left text-xs tracking-wide text-zinc-500 uppercase dark:border-zinc-800 dark:text-zinc-400">
            <th className="px-4 py-2 font-medium">Atleta</th>
            <th className="px-4 py-2 font-medium">Clubes</th>
            <th className="px-4 py-2 font-medium">Até</th>
          </tr>
        </thead>
        <tbody>
          {itens.map((atleta) => (
            <tr key={atleta.atletaId} className="border-b border-zinc-100 last:border-0 dark:border-zinc-900">
              <td className="px-4 py-2">
                <Link
                  href={`/atletas/${atleta.atletaId}`}
                  className="font-medium text-zinc-900 hover:text-brand dark:text-zinc-50 dark:hover:text-link"
                >
                  {atleta.nome}
                </Link>
              </td>
              <td className="px-4 py-2 text-zinc-700 dark:text-zinc-300">
                {atleta.clubes.map((clube) => clube.nome).join(", ")}
              </td>
              <td className="px-4 py-2 text-zinc-500 dark:text-zinc-400">{atleta.ultimoAno}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
