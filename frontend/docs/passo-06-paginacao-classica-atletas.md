# Passo 6 — Paginação clássica na tabela de atletas

Status: pronto para avaliação.

Substitui o "carregar mais" do [passo 5](./passo-05-tabela-completa-atletas.md)
por paginação Anterior/Próxima de 10 em 10, a pedido do usuário. A tabela
continua mostrando todos os atletas por padrão (sem busca) e filtrando pelo
que foi buscado — isso não muda, só a forma de navegar entre os resultados.

## O que mudou

- `Pager` (`components/busca-atleta/Pager.tsx`) volta a existir:
  Anterior/Próxima, mantendo a consulta atual (`q`) e a página (`pagina`) na
  URL.
- `ResultadoBuscaTabela` volta a ser um componente de servidor simples —
  recebe só os 10 itens da página atual, sem estado de "carregar mais".
- `app/atletas/page.tsx` agora faz a paginação: busca/lista a base inteira
  (já filtrada e ordenada por `listarAtletas`), calcula o total de páginas e
  corta a fatia da página pedida.
- Texto "N atletas no total" fica visível acima da tabela, junto do texto
  "Página X de Y" do paginador.

## Como conferir

1. `pnpm dev`, ir em "Busca e ficha do atleta" sem digitar nada: tabela com
   10 dos 60 atletas, "Página 1 de 6".
2. Clicar em "Próxima": mostra os próximos 10, sem duplicar os anteriores.
3. Buscar "Silva": "22 atletas no total", "Página 1 de 3"; navegar até a
   página 3 mostra só os 2 últimos.
4. Limpar a busca: volta para a base inteira paginada.

## Nota

Isso não muda a divergência já registrada em relação ao doc 03 §3 (que
descreve só busca, sem listagem prévia, e "sem paginação") — só troca a
mecânica de paginação usada. Ver
[`docs/passo-05-tabela-completa-atletas.md`](./passo-05-tabela-completa-atletas.md)
para o registro completo dessa divergência.
