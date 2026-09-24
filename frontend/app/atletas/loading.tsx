/**
 * Esqueleto exibido enquanto a navegação entre páginas de resultado busca os
 * novos dados (Next usa este arquivo como fallback de Suspense da rota).
 */
export default function CarregandoAtletas() {
  return (
    <div className="mx-auto flex max-w-2xl animate-pulse flex-col gap-4">
      <div className="flex flex-col gap-2">
        <div className="h-5 w-40 rounded bg-track" />
        <div className="h-10 w-full rounded-full bg-track" />
      </div>
      <div className="flex flex-col divide-y divide-line overflow-hidden rounded-2xl border border-line bg-surface shadow-card">
        {Array.from({ length: 4 }, (_, i) => (
          <div key={i} className="h-12 bg-surface-muted" />
        ))}
      </div>
    </div>
  );
}
