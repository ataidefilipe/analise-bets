import type { Perfil } from "@/lib/types/perfil";
import { sair } from "@/lib/api/acoes";
import { HomeButton } from "@/components/layout/HomeButton";
import { NavMenu } from "@/components/layout/NavMenu";
import { ThemeToggle } from "@/components/layout/ThemeToggle";

interface AppShellProps {
  perfil: Perfil;
  children: React.ReactNode;
}

/**
 * Casca visual comum a todas as telas: cabeçalho com identificação do perfil
 * ativo e menu já filtrado por permissão. Layout neutro e factual (doc 03,
 * §3 "Cuidado de design") — sem cor de alerta, ícones de alarme ou selo.
 */
export function AppShell({ perfil, children }: AppShellProps) {
  return (
    <div className="flex min-h-full flex-col">
      <header className="border-b border-zinc-200 print:hidden dark:border-zinc-800">
        <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-3">
          <div className="flex items-center gap-2">
            <span aria-hidden className="size-2 rounded-full bg-brand" />
            <div>
              <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                Análise de integridade
              </p>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">
                {perfil.nome} · {perfil.camada === "identificada" ? "dados identificados" : "dados agregados"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <form action={sair}>
              <button
                type="submit"
                className="rounded border border-zinc-300 px-3 py-1 text-xs text-zinc-600 transition-colors hover:border-brand hover:text-brand dark:border-zinc-700 dark:text-zinc-400 dark:hover:border-link dark:hover:text-link"
              >
                Sair
              </button>
            </form>
          </div>
        </div>
        <NavMenu perfil={perfil} />
      </header>
      <main className="flex-1 px-4 py-6">
        <HomeButton />
        {children}
      </main>
    </div>
  );
}
