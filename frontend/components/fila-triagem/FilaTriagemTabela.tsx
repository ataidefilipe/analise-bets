import Link from "next/link";
import type { Condicao, FilaTriagemItem } from "@/lib/types/fila-triagem";
import { formatarJustificativa } from "@/lib/format/fila";
import { formatarTier } from "@/lib/format/tier";

interface FilaTriagemTabelaProps {
  itens: FilaTriagemItem[];
}

const ROTULO_CONDICAO: Record<Condicao, string> = {
  titular: "Titular",
  reserva: "Reserva",
};

const CELULA_CLASSE = "px-4 py-3 align-top text-body";

/**
 * Tabela da fila (doc 03, §2). A linha de justificativa embaixo do nome não
 * é decorativa — é o que permite a P2 fundamentar em despacho por que um
 * caso foi aberto ou arquivado.
 */
export function FilaTriagemTabela({ itens }: FilaTriagemTabelaProps) {
  return (
    <div className="overflow-x-auto rounded-2xl border border-line bg-surface shadow-card">
      <table className="w-full min-w-[720px] text-sm">
        <thead>
          <tr className="border-b border-line text-left text-xs tracking-wide text-muted uppercase bg-surface-muted">
            <th className="px-4 py-2 font-medium">Atleta</th>
            <th className="px-4 py-2 font-medium">Clube</th>
            <th className="px-4 py-2 font-medium">Confronto</th>
            <th className="px-4 py-2 font-medium">Condição</th>
            <th className="px-4 py-2 font-medium">Tier</th>
          </tr>
        </thead>
        <tbody>
          {itens.map((item) => (
            <tr key={item.atletaId} className="border-b border-line-soft last:border-0">
              <td className="px-4 py-3 align-top">
                <div className="flex flex-col gap-0.5">
                  <span className="font-medium text-ink">
                    {item.atleta ?? "Identificação não disponível"}
                    {item.numCamisa ? ` · #${item.numCamisa}` : ""}
                  </span>
                  <span className="text-xs text-muted">
                    {formatarJustificativa(item)} ·{" "}
                    <Link href={`/atletas/${item.atletaId}`} className="text-link hover:underline">
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
