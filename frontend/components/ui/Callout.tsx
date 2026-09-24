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
    <div className="flex gap-3 rounded-xl border border-line border-l-4 border-l-accent bg-surface-muted px-4 py-3 text-sm text-body">
      <span aria-hidden className="select-none text-accent">
        ⓘ
      </span>
      <p>{children}</p>
    </div>
  );
}
