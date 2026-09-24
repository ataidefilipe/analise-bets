"use client";

/**
 * Erro inesperado (doc 03, §6: "Mensagem genérica. Nunca stack trace").
 * Inclui a API fora do ar — o detalhe técnico fica no log do servidor.
 */
export default function Erro({ retry }: { error: Error & { digest?: string }; retry: () => void }) {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center gap-3 rounded-3xl border border-dashed border-line-strong px-6 py-10 text-center">
      <p className="font-medium text-body">Não foi possível carregar esta tela.</p>
      <p className="text-sm text-muted">
        O serviço de dados pode estar indisponível. Tente novamente em instantes.
      </p>
      <button
        type="button"
        onClick={() => retry()}
        className="rounded-full border border-line-strong px-3 py-1.5 text-sm text-body hover:border-link hover:text-link"
      >
        Tentar de novo
      </button>
    </div>
  );
}
