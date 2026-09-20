# Passo 10 — Controle de acesso por rota

Status: pronto para avaliação.

Até aqui, `perfil.telasPermitidas` só controlava o que aparecia no menu
(doc 03, §0: "não aparece"). Nada impedia abrir a URL de uma tela
diretamente, ou trocar de perfil pelo seletor de demonstração enquanto já
está numa tela à qual o novo perfil não tem acesso. A pedido do usuário,
isso agora é bloqueado na própria rota.

## O que foi entregue

- `lib/mock/acesso.ts` — `exigirAcessoTela(tela)`: lê o perfil ativo e
  chama `redirect("/")` (de `next/navigation`) se a tela não estiver em
  `telasPermitidas`. Também devolve o perfil, para a página não precisar
  buscá-lo de novo.
- Aplicado no topo das 6 páginas protegidas, antes de qualquer busca de
  dado: `/triagem`, `/atletas`, `/atletas/[id]`, `/partidas`,
  `/partidas/[id]`, `/agregados`.
- Cobre os dois casos pedidos: acesso direto pela URL sem permissão, e
  trocar de perfil (seletor de demonstração) enquanto já está numa tela à
  qual o perfil novo não tem acesso — o `PersonaSwitcher` já chama
  `router.refresh()`, que reexecuta a checagem com o perfil atualizado.

## Nota técnica: por que `/atletas` não mostra um 307 puro

`/atletas` e `/atletas/[id]` têm `loading.tsx`, o que faz o Next.js
envolver a página num limite de Suspense e fazer streaming da resposta.
Quando isso acontece, `redirect()` não sai mais como um cabeçalho HTTP
307 — o Next já comprometeu o `200` inicial do streaming, então o
redirecionamento vira uma instrução (`NEXT_REDIRECT`) embutida no próprio
stream, que o roteador do navegador executa no cliente. Isso funciona
normalmente em qualquer navegador com JavaScript (é o mecanismo padrão do
App Router), mas ferramentas sem JS como `curl` não o seguem — por isso a
verificação abaixo usa dois métodos diferentes conforme a rota.

## Como conferir

1. `pnpm dev`.
2. Trocar o perfil para P5 (Imprensa — só tem Panorama agregado) e tentar
   abrir `/triagem` direto pela URL: volta para a home.
3. Ficar em "Panorama agregado" com o perfil P5 e trocar para P1 (Clube) no
   seletor: como P1 não tem acesso a "Panorama agregado", a página
   redireciona para a home assim que o perfil muda.
4. Testado via `curl`: `/triagem`, `/partidas` e `/agregados` devolvem
   `307` puro para perfil sem acesso; `/atletas` e `/atletas/[id]` (que têm
   `loading.tsx`) devolvem `200` mas o corpo da resposta contém a
   instrução `NEXT_REDIRECT` — confirmando que o redirecionamento foi
   corretamente disparado, só que por streaming em vez de um cabeçalho
   HTTP direto.

## O que fica para os próximos passos

Nenhum passo do MVP pendente — isso é um reforço de segurança/UX sobre as
4 telas já entregues.
