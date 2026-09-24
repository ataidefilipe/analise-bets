# components/busca-atleta

Componentes da tela de atletas (`app/atletas/page.tsx`). Adaptados a partir
da T2 do `03_telas.md`, §3 — ver
[`docs/passo-05-tabela-completa-atletas.md`](../../docs/passo-05-tabela-completa-atletas.md)
sobre como isso diverge do doc original (que descrevia só busca, sem
listagem prévia).

| Componente | Para quê |
| :--- | :--- |
| `ResultadoBuscaTabela` | Tabela (Atleta / Clubes / Até) da página atual — nunca escore ou tier. `app/atletas/page.tsx` decide qual fatia de 10 mostrar. |

O campo de busca (`BuscaForm`) e a paginação (`Pager`) são genéricos —
ver [`components/ui`](../ui/README.md) — e reusados pela T3 (dossiê de
partida). Ver
[`docs/passo-08-busca-e-paginacao-partidas.md`](../../docs/passo-08-busca-e-paginacao-partidas.md)
sobre essa generalização.

A ficha em si (rota `/atletas/[id]`) usa os componentes de
[`components/ficha-atleta`](../ficha-atleta/README.md).
