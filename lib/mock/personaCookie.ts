import type { PersonaCodigo } from "@/lib/types/perfil";
import { PERFIL_PADRAO } from "@/lib/mock/me";

/**
 * Nome do cookie usado só para a demonstração/QA do menu dinâmico
 * (ver `getMe` em `lib/mock/me.ts`). Não existe em produção — a persona virá
 * da sessão autenticada (doc 01).
 */
export const PERSONA_COOKIE = "mock_persona";

const PERSONAS_VALIDAS: readonly PersonaCodigo[] = ["P1", "P2", "P3", "P4", "P5"];

export function parsePersonaCookie(valor: string | undefined): PersonaCodigo {
  if (valor && (PERSONAS_VALIDAS as readonly string[]).includes(valor)) {
    return valor as PersonaCodigo;
  }
  return PERFIL_PADRAO;
}
