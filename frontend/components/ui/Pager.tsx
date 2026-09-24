import Link from "next/link";
import { CaretDoubleLeft, CaretDoubleRight } from "@phosphor-icons/react/dist/ssr";

interface PagerProps {
  basePath: string;
  consulta: string;
  pagina: number;
  totalPaginas: number;
  /** Outros filtros da tela, mantidos ao trocar de página (ex.: série e temporada). */
  parametros?: Record<string, string>;
}

const BOTAO_CLASSE =
  "flex size-8 items-center justify-center rounded-full border border-line-strong text-muted transition-colors hover:border-link hover:text-link";
const BOTAO_DESATIVADO_CLASSE =
  "flex size-8 items-center justify-center rounded-full border border-line text-faint";

function href(basePath: string, consulta: string, pagina: number, parametros: Record<string, string> = {}): string {
  const params = new URLSearchParams(parametros);
  if (consulta) params.set("q", consulta);
  params.set("pagina", String(pagina));
  return `${basePath}?${params.toString()}`;
}

/** Pagina uma tabela mantendo a consulta e os filtros atuais na URL. Genérico, sem conhecimento de domínio. */
export function Pager({ basePath, consulta, pagina, totalPaginas, parametros }: PagerProps) {
  if (totalPaginas <= 1) return null;

  return (
    <div className="flex items-center justify-between gap-4">
      {pagina > 1 ? (
        <Link
          href={href(basePath, consulta, pagina - 1, parametros)}
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
      <span className="text-sm text-muted">
        Página {pagina} de {totalPaginas}
      </span>
      {pagina < totalPaginas ? (
        <Link
          href={href(basePath, consulta, pagina + 1, parametros)}
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
