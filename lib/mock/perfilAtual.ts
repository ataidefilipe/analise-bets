import { cookies } from "next/headers";
import type { Perfil } from "@/lib/types/perfil";
import { getMe } from "@/lib/mock/me";
import { PERSONA_COOKIE, parsePersonaCookie } from "@/lib/mock/personaCookie";

/**
 * Lê o perfil ativo (cookie de demonstração + mock de `/v1/me`). Centraliza
 * aqui para que cada página não repita a leitura do cookie.
 */
export async function getPerfilAtual(): Promise<Perfil> {
  const cookieStore = await cookies();
  const persona = parsePersonaCookie(cookieStore.get(PERSONA_COOKIE)?.value);
  return getMe(persona);
}
