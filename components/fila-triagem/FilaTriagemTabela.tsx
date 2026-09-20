import Link from "next/link";
import type { Condicao, FilaTriagemItem } from "@/lib/types/fila-triagem";
import { formatarJustificativa, formatarTier } from "@/lib/format/fila";

interface FilaTriagemTabelaProps {
  itens: FilaTriagemItem[];
}

const ROTULO_CONDICAO: Record<Condicao, string> = {
  titular: "Titular",
  reserva: "Reserva",
};

const CELULA_CLASSE = "px-4 py-3 align-top text-zinc-700 dark:text-zinc-300";

/**
 * Tabela da fila (doc 03, §2). A linha de justificativa embaixo do nome não
 * é decorativa — é o que permite a P2 fundamentar em despacho por que um
 * caso foi aberto ou arquivado.
 */
export function FilaTriagemTabela({ itens }: FilaTriagemTabelaProps) {
  return (
    <div className="overflow-x-auto rounded-md border border-zinc-200 dark:border-zinc-800">
      <table className="w-full min-w-[720px] text-sm">
        <thead>
          <tr className="border-b border-zinc-200 text-left text-xs tracking-wide text-zinc-500 uppercase dark:border-zinc-800 dark:text-zinc-400">
            <th className="px-4 py-2 font-medium">Atleta</th>
            <th className="px-4 py-2 font-medium">Clube</th>
            <th className="px-4 py-2 font-medium">Confronto</th>
            <th className="px-4 py-2 font-medium">Condição</th>
            <th className="px-4 py-2 font-medium">Tier</th>
          </tr>
        </thead>
        <tbody>
          {itens.map((item) => (
            <tr key={item.atletaId} className="border-b border-zinc-100 last:border-0 dark:border-zinc-900">
              <td className="px-4 py-3 align-top">
                <div className="flex flex-col gap-0.5">
                  <span className="font-medium text-zinc-900 dark:text-zinc-50">
                    {item.atleta ?? "Identificação não disponível"}
                    {item.numCamisa ? ` · #${item.numCamisa}` : ""}
                  </span>
                  <span className="text-xs text-zinc-500 dark:text-zinc-400">
                    {formatarJustificativa(item)} ·{" "}
                    <Link href={`/atletas?atletaId=${item.atletaId}`} className="text-link hover:underline">
                      ver ficha
                    </Link>
                  </span>
                </div>
              </td>
              <td className={CELULA_CLASSE}>{item.clubeNome}</td>
              <td className={CELULA_CLASSE}>{item.confronto}</td>
              <td className={CELULA_CLASSE}>{ROTULO_CONDICAO[item.condicao]}</td>
              <td className={CELULA_CLASSE}>{formatarTier(item)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
