"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, COOKIE_CHAVE, apiGet } from "@/lib/api/cliente";

export interface EstadoEntrar {
  erro?: string;
}

/** Valida a chave em `GET /v1/me` antes de gravá-la; chave inválida não vira sessão. */
export async function entrar(_: EstadoEntrar, formData: FormData): Promise<EstadoEntrar> {
  const chave = String(formData.get("chave") ?? "").trim();
  if (!chave) return { erro: "Informe a chave de acesso." };

  try {
    await apiGet("/v1/me", {}, { chave, tratarNavegacao: false });
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) return { erro: "Chave não reconhecida ou desativada." };
    if (e instanceof ApiError && e.status === 403) return { erro: "Seu perfil não tem acesso a este sistema." };
    return { erro: "Não foi possível falar com a API. Tente novamente em instantes." };
  }

  (await cookies()).set(COOKIE_CHAVE, chave, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 8,
  });
  redirect("/");
}

export async function sair(): Promise<void> {
  (await cookies()).delete(COOKIE_CHAVE);
  redirect("/entrar");
}
