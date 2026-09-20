interface CalloutProps {
  children: React.ReactNode;
}

/**
 * Caixa de aviso interpretativo (doc 03, §1.1): sempre visível na mesma tela
 * onde um escore aparece, nunca em rodapé/tooltip/modal. O texto é sempre
 * passado pelo chamador (vindo de `aviso_interpretativo` na resposta da API)
 * — este componente não hard-coda nenhuma mensagem.
 */
export function Callout({ children }: CalloutProps) {
  return (
    <div className="flex gap-3 rounded-md border border-zinc-300 bg-zinc-50 px-4 py-3 text-sm text-zinc-700 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300">
      <span aria-hidden className="select-none text-zinc-500">
        ⓘ
      </span>
      <p>{children}</p>
    </div>
  );
}
