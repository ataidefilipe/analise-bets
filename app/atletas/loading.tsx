/**
 * Esqueleto exibido enquanto a navegação entre páginas de resultado busca os
 * novos dados (Next usa este arquivo como fallback de Suspense da rota).
 */
export default function CarregandoAtletas() {
  return (
    <div className="mx-auto flex max-w-2xl animate-pulse flex-col gap-4">
      <div className="flex flex-col gap-2">
        <div className="h-5 w-40 rounded bg-zinc-200 dark:bg-zinc-800" />
        <div className="h-10 w-full rounded bg-zinc-200 dark:bg-zinc-800" />
      </div>
      <div className="flex flex-col divide-y divide-zinc-200 rounded-md border border-zinc-200 dark:divide-zinc-800 dark:border-zinc-800">
        {Array.from({ length: 4 }, (_, i) => (
          <div key={i} className="h-12 bg-zinc-100 dark:bg-zinc-900" />
        ))}
      </div>
    </div>
  );
}
