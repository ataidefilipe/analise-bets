interface TelaPendenteProps {
  rotulo: string;
  descricaoCurta: string;
}

/**
 * Stub usado pelas 4 rotas antes de cada tela ser implementada (uma por
 * passo, ver docs/passo-01-base-do-projeto.md). Existe só para provar que a
 * navegação e a permissão por perfil já funcionam de ponta a ponta.
 */
export function TelaPendente({ rotulo, descricaoCurta }: TelaPendenteProps) {
  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-2">
      <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">{rotulo}</h1>
      <p className="text-sm text-zinc-500 dark:text-zinc-400">{descricaoCurta}</p>
      <p className="mt-4 text-sm text-zinc-400 dark:text-zinc-500">
        Tela ainda não implementada — será construída em um passo dedicado.
      </p>
    </div>
  );
}
