# Passo 8 — Busca e paginação na listagem de partidas

Status: pronto para avaliação.

A pedido do usuário, a listagem de partidas (`/partidas`, criada no
[passo 7](./passo-07-dossie-partida.md) só para navegar até um dossiê)
passa a funcionar como a tabela de atletas da T2: busca + paginação de 10
em 10, mostrando o total.

## O que mudou

- `listarPartidas` (`lib/mock/partidas.ts`) agora aceita `consulta`: sem
  ela (ou com menos de 3 caracteres) devolve as 24 partidas do mock; com 3+
  caracteres, filtra por nome de qualquer um dos dois clubes — mesma regra
  de 3 caracteres da T2, mesma ordenação por data (mais recentes primeiro)
  de antes.
- `ResultadoPartidasTabela` (`components/dossie-partida/`): tabela
  (Partida / Competição / Data) da página atual, no mesmo estilo da
  `ResultadoBuscaTabela` da T2.
- **Generalização**: o formulário de busca e o paginador, que antes eram
  específicos de atleta (`components/busca-atleta/BuscaAtletaForm.tsx` e
  `Pager.tsx`), viraram `components/ui/BuscaForm.tsx` e
  `components/ui/Pager.tsx` — genéricos, recebendo `basePath` (e
  `placeholder`, no caso do formulário). `/atletas` e `/partidas` agora
  usam os dois mesmos componentes.

## Como conferir

1. `pnpm dev`, ir em "Dossiê de partida": tabela com 10 das 24 partidas,
   mais recentes primeiro, "24 partidas no total".
2. Buscar o nome de um clube (ex.: "Exemplo A"): a tabela filtra para as
   partidas desse clube.
3. Paginar (ícones «/»): mantém a busca atual, se houver.
4. Limpar a busca ("x" no campo): volta a mostrar todas as 24.

## Nota

A listagem em si continua sendo uma adição do projeto, não do doc 03 (ver
passo 7) — este passo só alinha a interação dela com a da T2.
