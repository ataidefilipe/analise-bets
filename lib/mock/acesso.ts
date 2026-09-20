import { redirect } from "next/navigation";
import type { Perfil, TelaId } from "@/lib/types/perfil";
import { getPerfilAtual } from "@/lib/mock/perfilAtual";

/**
 * Aplica em cada rota a mesma regra do menu (doc 03, §0: uma tela fora de
 * `telasPermitidas` "não aparece"): se o perfil ativo não tem acesso, a
 * página nem chega a renderizar — redireciona para "/". Cobre tanto quem
 * digita a URL direto quanto quem já está na tela e troca de perfil no
 * seletor de demonstração.
 *
 * Chamar no topo de cada `page.tsx` protegida, antes de buscar dados —
 * devolve o perfil para a página não precisar buscá-lo de novo.
 */
export async function exigirAcessoTela(tela: TelaId): Promise<Perfil> {
  const perfil = await getPerfilAtual();
  if (!perfil.telasPermitidas.includes(tela)) {
    redirect("/");
  }
  return perfil;
}
