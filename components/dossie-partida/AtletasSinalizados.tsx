import Link from "next/link";
import type { AtletaSinalizado } from "@/lib/types/partida";
import { formatarTier } from "@/lib/format/tier";

interface AtletasSinalizadosProps {
  atletas: AtletaSinalizado[];
}

/** Seção 5 do dossiê (doc 03, §4) — só camada identificada; quem chama decide se renderiza, via `perfil.granularidade`. */
export function AtletasSinalizados({ atletas }: AtletasSinalizadosProps) {
  if (atletas.length === 0) {
    return (
      <p className="text-sm text-zinc-500 dark:text-zinc-400">
        Nenhum atleta desta partida acima do corte de atenção.
      </p>
    );
  }

  return (
    <div>
      <h2 className="mb-2 text-sm font-semibold text-zinc-900 dark:text-zinc-50">Atletas sinalizados</h2>
      <ul className="divide-y divide-zinc-200 rounded-md border border-zinc-200 dark:divide-zinc-800 dark:border-zinc-800">
        {atletas.map((atleta) => (
          <li key={atleta.atletaId} className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 px-4 py-2 text-sm">
            <Link
              href={`/atletas/${atleta.atletaId}`}
              className="font-medium text-zinc-900 hover:text-brand dark:text-zinc-50 dark:hover:text-link"
            >
              {atleta.atleta}
            </Link>
            <span className="text-zinc-500 dark:text-zinc-400">{atleta.clubeNome}</span>
            <span className="text-zinc-700 dark:text-zinc-300">{formatarTier(atleta)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
