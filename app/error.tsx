"use client";

/**
 * Erro inesperado (doc 03, §6: "Mensagem genérica. Nunca stack trace").
 * Inclui a API fora do ar — o detalhe técnico fica no log do servidor.
 */
export default function Erro({ retry }: { error: Error & { digest?: string }; retry: () => void }) {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center gap-3 rounded-md border border-dashed border-zinc-300 px-6 py-10 text-center dark:border-zinc-700">
      <p className="font-medium text-zinc-700 dark:text-zinc-300">Não foi possível carregar esta tela.</p>
      <p className="text-sm text-zinc-500 dark:text-zinc-400">
        O serviço de dados pode estar indisponível. Tente novamente em instantes.
      </p>
      <button
        type="button"
        onClick={() => retry()}
        className="rounded border border-zinc-300 px-3 py-1.5 text-sm text-zinc-700 hover:border-brand hover:text-brand dark:border-zinc-700 dark:text-zinc-300 dark:hover:border-link dark:hover:text-link"
      >
        Tentar de novo
      </button>
    </div>
  );
}
