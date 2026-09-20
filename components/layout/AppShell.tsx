import type { Perfil } from "@/lib/types/perfil";
import { listarPersonasMock } from "@/lib/mock/me";
import { BackButton } from "@/components/layout/BackButton";
import { NavMenu } from "@/components/layout/NavMenu";
import { PersonaSwitcher } from "@/components/layout/PersonaSwitcher";
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
      <header className="border-b border-zinc-200 dark:border-zinc-800">
        <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-3">
          <div className="flex items-center gap-2">
            <span aria-hidden className="size-2 rounded-full bg-brand" />
            <div>
              <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                Análise de integridade
              </p>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">
                {perfil.nome} · {perfil.granularidade === "identificada" ? "dados identificados" : "dados agregados"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <PersonaSwitcher personas={listarPersonasMock()} ativa={perfil.persona} />
            <ThemeToggle />
          </div>
        </div>
        <NavMenu perfil={perfil} />
      </header>
      <main className="flex-1 px-4 py-6">
        <BackButton />
        {children}
      </main>
    </div>
  );
}
