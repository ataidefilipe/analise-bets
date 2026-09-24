interface EmptyStateProps {
  titulo: string;
  descricao: string;
}

/**
 * Estado vazio explicativo (doc 03, §1.6 e §6): toda tela que lista escore
 * precisa de um deles em vez de uma lista em branco. A maioria dos casos
 * listados no doc 03 §6 (sem escalação, fila vazia, base rasa, busca curta,
 * sem permissão) não são erros — por isso o tom é informativo, não de alerta.
 */
export function EmptyState({ titulo, descricao }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-1 rounded-md border border-dashed border-zinc-300 px-6 py-10 text-center dark:border-zinc-700">
      <p className="font-medium text-zinc-700 dark:text-zinc-300">{titulo}</p>
      <p className="max-w-md text-sm text-zinc-500 dark:text-zinc-400">{descricao}</p>
    </div>
  );
}
