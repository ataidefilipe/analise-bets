# Passo 4 — Paginação na busca de atleta

Status: **superado pelo passo 5** — [`passo-05-tabela-completa-atletas.md`](./passo-05-tabela-completa-atletas.md).
O padrão Anterior/Próxima descrito aqui foi substituído por "carregar mais"
sobre uma tabela que já lista todos os atletas por padrão. Mantido como
registro histórico da decisão, não como comportamento atual.

## Atenção: isto diverge do doc 03

O doc 03, §3, pede explicitamente **"Mínimo 3 caracteres, 20 resultados,
sem paginação"** para a busca de atleta. A pedido do usuário, este passo
substitui isso por **10 resultados por página, com paginação** — uma
decisão de produto que sobrepõe o que o documento original especifica.
Registrando aqui para não parecer um desvio acidental depois.

## O que foi entregue

- `buscarAtletas` (`lib/mock/buscaAtletas.ts`) agora aceita `pagina` e
  `porPagina` (padrão 10) e devolve `{ itens, total, pagina, porPagina }`
  em vez de uma lista já cortada em 20 — o filtro por nome roda sobre o
  pool inteiro, a paginação só decide qual fatia mostrar.
- `Pager` (`components/busca-atleta/Pager.tsx`): Anterior/Próxima, mantendo
  a consulta atual (`q`) na URL — trocar de página nunca perde o que foi
  buscado, como pedido.
- `app/atletas/loading.tsx`: esqueleto exibido enquanto a próxima página
  carrega (Next usa esse arquivo como fallback automático da navegação).
- Pool de atletas mock aumentado de 40 para 60, para a paginação ter mais
  de uma página em buscas comuns (ex.: "Silva" agora dá 22 resultados, 3
  páginas).

## Como conferir

1. `pnpm dev`, ir em "Busca e ficha do atleta".
2. Buscar "Silva" (sobrenome comum no pool mock): ver 10 resultados e
   "Página 1 de 3".
3. Clicar em "Próxima": ver o esqueleto de carregamento e depois os
   próximos 10, com a busca "Silva" ainda no campo.
4. Chegar na última página: "Próxima" fica desativado.

## O que fica para os próximos passos

- T3 (dossiê de partida) e T4 (panorama agregado).
