import Link from "next/link";
import type { AtletaSinalizado } from "@/lib/types/partida";
import { formatarTier } from "@/lib/format/tier";

interface AtletasSinalizadosProps {
  atletas: AtletaSinalizado[];
}

/**
 * Seção 5 do dossiê (doc 03, §4) — só camada identificada; quem chama decide
 * se renderiza, via `perfil.camada`. O corte é o limiar padrão do perfil, e
 * para o perfil clube o backend já restringe ao próprio elenco.
 */
export function AtletasSinalizados({ atletas }: AtletasSinalizadosProps) {
  if (atletas.length === 0) {
    return (
      <p className="text-sm text-muted">
        Nenhum atleta desta partida acima do corte de atenção.
      </p>
    );
  }

  return (
    <div>
      <h2 className="mb-2 text-sm font-semibold text-ink">Atletas sinalizados</h2>
      <ul className="divide-y divide-line overflow-hidden rounded-2xl border border-line bg-surface shadow-card">
        {atletas.map((atleta) => (
          <li key={atleta.atletaId} className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 px-4 py-2 text-sm">
            <Link
              href={`/atletas/${atleta.atletaId}`}
              className="font-medium text-ink hover:text-link"
            >
              {atleta.atleta}
            </Link>
            <span className="text-muted">{atleta.clubeNome}</span>
            <span className="text-body">{formatarTier(atleta)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
