"use client";

import { useRouter } from "next/navigation";
import type { Perfil, PersonaCodigo } from "@/lib/types/perfil";
import { PERSONA_COOKIE } from "@/lib/mock/personaCookie";

interface PersonaSwitcherProps {
  personas: Perfil[];
  ativa: PersonaCodigo;
}

/**
 * Ferramenta de demonstração/QA: troca o perfil mock ativo (cookie) e
 * recarrega os componentes de servidor para provar que o menu muda
 * conforme a permissão (doc 03, §0). Não existe caminho equivalente em
 * produção — lá o perfil vem da sessão autenticada (doc 01), sem escolha.
 */
export function PersonaSwitcher({ personas, ativa }: PersonaSwitcherProps) {
  const router = useRouter();

  function trocarPersona(persona: string) {
    document.cookie = `${PERSONA_COOKIE}=${persona}; path=/; max-age=31536000`;
    router.refresh();
  }

  return (
    <label className="flex items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400">
      <span className="hidden sm:inline">Perfil (demo)</span>
      <select
        value={ativa}
        onChange={(e) => trocarPersona(e.target.value)}
        className="rounded border border-zinc-300 bg-white px-2 py-1 text-zinc-700 focus-visible:border-brand focus-visible:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:focus-visible:border-link"
      >
        {personas.map((perfil) => (
          <option key={perfil.persona} value={perfil.persona}>
            {perfil.persona} — {perfil.nome}
          </option>
        ))}
      </select>
    </label>
  );
}
