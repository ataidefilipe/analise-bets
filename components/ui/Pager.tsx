import Link from "next/link";
import { CaretDoubleLeft, CaretDoubleRight } from "@phosphor-icons/react/dist/ssr";

interface PagerProps {
  basePath: string;
  consulta: string;
  pagina: number;
  totalPaginas: number;
}

const BOTAO_CLASSE =
  "flex size-8 items-center justify-center rounded border border-zinc-300 text-zinc-500 transition-colors hover:border-brand hover:text-brand dark:border-zinc-700 dark:text-zinc-400 dark:hover:border-link dark:hover:text-link";
const BOTAO_DESATIVADO_CLASSE =
  "flex size-8 items-center justify-center rounded border border-zinc-200 text-zinc-300 dark:border-zinc-800 dark:text-zinc-700";

function href(basePath: string, consulta: string, pagina: number): string {
  const params = new URLSearchParams();
  if (consulta) params.set("q", consulta);
  params.set("pagina", String(pagina));
  return `${basePath}?${params.toString()}`;
}

/** Pagina uma tabela (10 por página) mantendo a consulta atual na URL. Genérico — usado por atletas e partidas. */
export function Pager({ basePath, consulta, pagina, totalPaginas }: PagerProps) {
  if (totalPaginas <= 1) return null;

  return (
    <div className="flex items-center justify-between gap-4">
      {pagina > 1 ? (
        <Link
          href={href(basePath, consulta, pagina - 1)}
          aria-label="Página anterior"
          title="Página anterior"
          className={BOTAO_CLASSE}
        >
          <CaretDoubleLeft size={16} weight="bold" />
        </Link>
      ) : (
        <span aria-hidden className={BOTAO_DESATIVADO_CLASSE}>
          <CaretDoubleLeft size={16} weight="bold" />
        </span>
      )}
      <span className="text-sm text-zinc-500 dark:text-zinc-400">
        Página {pagina} de {totalPaginas}
      </span>
      {pagina < totalPaginas ? (
        <Link
          href={href(basePath, consulta, pagina + 1)}
          aria-label="Próxima página"
          title="Próxima página"
          className={BOTAO_CLASSE}
        >
          <CaretDoubleRight size={16} weight="bold" />
        </Link>
      ) : (
        <span aria-hidden className={BOTAO_DESATIVADO_CLASSE}>
          <CaretDoubleRight size={16} weight="bold" />
        </span>
      )}
    </div>
  );
}
