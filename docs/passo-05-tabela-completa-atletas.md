# Passo 5 — Tabela completa de atletas, ordenada e com "carregar mais"

Status: pronto para avaliação.

Supera o [passo 4](./passo-04-paginacao-busca.md): troca a paginação
Anterior/Próxima por uma tabela que já lista todos os atletas por padrão.

## Atenção: isto continua divergindo do doc 03

O doc 03, §3, descreve uma tela de **busca** — sem resultado nenhum até o
usuário digitar algo. A pedido do usuário, a tela agora é uma **tabela
navegável**: mostra todos os atletas em ordem alfabética já de cara, e a
busca apenas filtra essa tabela. Mantendo o registro para não parecer
esquecimento.

## O que foi entregue

- `listarAtletas` (`lib/mock/buscaAtletas.ts`) substitui `buscarAtletas`:
  sem consulta (ou com menos de 3 caracteres), devolve a base inteira
  ordenada por nome (`localeCompare` com locale `pt-BR`, então acentos
  ordenam corretamente); com consulta de 3+ caracteres, filtra antes de
  ordenar.
- `ResultadoBuscaTabela` (`components/busca-atleta/ResultadoBuscaTabela.tsx`)
  substitui `ResultadoBuscaLista`: agora é uma tabela (Atleta / Clubes /
  Até) em vez de uma lista simples, com um texto "Mostrando X de Y
  atletas" e um botão "Carregar mais 10" que soma 10 aos já exibidos — sem
  navegação, sem perder o que já estava na tela.
- Removido: `Pager` (Anterior/Próxima) e o tipo `ResultadoBusca` do passo 4,
  ambos superados por este passo.
- A busca continua funcionando como filtro: o mesmo texto digitado decide
  o que a tabela mostra, sem sair da mesma tela.

## Como conferir

1. `pnpm dev`, ir em "Busca e ficha do atleta" **sem digitar nada**: a
   tabela já aparece, em ordem alfabética, "Mostrando 10 de 60 atletas".
2. Clicar em "Carregar mais 10": vira "Mostrando 20 de 60 atletas", sem
   recarregar a página.
3. Buscar "Silva": a tabela passa a mostrar só os atletas com esse nome
   ("Mostrando 10 de 22 atletas"), ainda em ordem alfabética e com
   "carregar mais".
4. Apagar a busca: volta a mostrar a base inteira.

## O que fica para os próximos passos

- T3 (dossiê de partida) e T4 (panorama agregado).
