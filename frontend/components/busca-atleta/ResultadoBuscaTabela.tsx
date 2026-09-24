import Link from "next/link";
import type { AtletaResumo } from "@/lib/types/atleta";

interface ResultadoBuscaTabelaProps {
  itens: AtletaResumo[];
}

/**
 * Resultado da busca, na ordem da API (atuação mais recente primeiro), no
 * máximo 20 itens. Só identificação e clubes — nunca escore ou tier (doc 03, §3).
 */
export function ResultadoBuscaTabela({ itens }: ResultadoBuscaTabelaProps) {
  return (
    <div className="overflow-x-auto rounded-2xl border border-line bg-surface shadow-card">
      <table className="w-full min-w-120 text-sm">
        <thead>
          <tr className="border-b border-line text-left text-xs tracking-wide text-muted uppercase bg-surface-muted">
            <th className="px-4 py-2 font-medium">Atleta</th>
            <th className="px-4 py-2 font-medium">Clubes</th>
            <th className="px-4 py-2 font-medium">Até</th>
          </tr>
        </thead>
        <tbody>
          {itens.map((atleta) => (
            <tr key={atleta.atletaId} className="border-b border-line-soft last:border-0">
              <td className="px-4 py-2">
                <Link
                  href={`/atletas/${atleta.atletaId}`}
                  className="font-medium text-ink hover:text-link"
                >
                  {atleta.nome}
                </Link>
              </td>
              <td className="px-4 py-2 text-body">
                {atleta.clubes.map((clube) => clube.nome).join(", ")}
              </td>
              <td className="px-4 py-2 text-muted">{atleta.ultimoAno}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
