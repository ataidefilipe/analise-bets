import Link from "next/link";

interface PagerProps {
  consulta: string;
  pagina: number;
  totalPaginas: number;
}

const BOTAO_CLASSE =
  "rounded border border-zinc-300 px-3 py-1.5 text-sm text-zinc-700 hover:border-brand hover:text-brand dark:border-zinc-700 dark:text-zinc-300 dark:hover:border-link dark:hover:text-link";
const BOTAO_DESATIVADO_CLASSE =
  "rounded border border-zinc-200 px-3 py-1.5 text-sm text-zinc-300 dark:border-zinc-800 dark:text-zinc-700";

function href(consulta: string, pagina: number): string {
  return `/atletas?q=${encodeURIComponent(consulta)}&pagina=${pagina}`;
}

/**
 * Pagina os resultados da busca (10 por página, a pedido do usuário — o doc
 * 03 §3 originalmente pedia 20 resultados sem paginação, ver
 * docs/passo-04-paginacao-busca.md). Cada página mantém a consulta atual na
 * URL, então trocar de página nunca perde o que foi buscado.
 */
export function Pager({ consulta, pagina, totalPaginas }: PagerProps) {
  if (totalPaginas <= 1) return null;

  return (
    <div className="flex items-center justify-between gap-4">
      {pagina > 1 ? (
        <Link href={href(consulta, pagina - 1)} className={BOTAO_CLASSE}>
          Anterior
        </Link>
      ) : (
        <span className={BOTAO_DESATIVADO_CLASSE}>Anterior</span>
      )}
      <span className="text-sm text-zinc-500 dark:text-zinc-400">
        Página {pagina} de {totalPaginas}
      </span>
      {pagina < totalPaginas ? (
        <Link href={href(consulta, pagina + 1)} className={BOTAO_CLASSE}>
          Próxima
        </Link>
      ) : (
        <span className={BOTAO_DESATIVADO_CLASSE}>Próxima</span>
      )}
    </div>
  );
}
