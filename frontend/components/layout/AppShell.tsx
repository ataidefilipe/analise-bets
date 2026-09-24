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
      <header className="sticky top-0 z-20 border-b border-line bg-background/80 backdrop-blur-xl print:hidden">
        <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-3">
          <div className="flex items-center gap-3">
            {/* Marca no estilo Astrolus: círculo + barra na cor de marca. */}
            <span aria-hidden className="flex items-center gap-0.5">
              <span className="size-4 rounded-full bg-ink" />
              <span className="h-6 w-1.5 rounded-full bg-brand" />
            </span>
            <div>
              <p className="text-sm font-bold tracking-tight text-ink">
                Análise de integridade
              </p>
              <p className="text-xs text-muted">
                {perfil.nome} · {perfil.camada === "identificada" ? "dados identificados" : "dados agregados"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <form action={sair}>
              <button
                type="submit"
                className="rounded-full border border-line-strong px-3 py-1 text-xs text-muted transition-colors hover:border-link hover:text-link"
              >
                Sair
              </button>
            </form>
          </div>
        </div>
        <NavMenu perfil={perfil} />
      </header>
      <main className="relative isolate flex-1 px-4 py-6">
        <HomeButton />
        {children}
      </main>
    </div>
  );
}
