/**
 * Manchas desfocadas em degradê atrás do conteúdo, no estilo do template
 * Astrolus. Só na home e na entrada — nas telas de dados competiriam com as
 * tabelas. Puramente decorativo: fora da árvore de acessibilidade, não recebe
 * clique e some na impressão.
 */
export function FundoDecorativo() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden print:hidden">
      <div className="absolute inset-x-0 top-24 m-auto grid max-w-5xl grid-cols-2 -space-x-52 opacity-(--glow-opacity)">
        <div className="h-56 bg-linear-to-br from-(--glow-a-from) to-(--glow-a-to) blur-[106px]" />
        <div className="h-32 bg-linear-to-r from-(--glow-b-from) to-(--glow-b-to) blur-[106px]" />
      </div>
    </div>
  );
}
