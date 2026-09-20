# components/busca-atleta

Componentes da tela de atletas (`app/atletas/page.tsx`). Adaptados a partir
da T2 do `03_telas.md`, §3 — ver
[`docs/passo-05-tabela-completa-atletas.md`](../../docs/passo-05-tabela-completa-atletas.md)
sobre como isso diverge do doc original (que descrevia só busca, sem
listagem prévia).

| Componente | Para quê |
| :--- | :--- |
| `BuscaAtletaForm` | Campo + botão de busca. Botão de buscar inativo com menos de 3 caracteres; submissão explícita (não busca a cada tecla), navegando para `/atletas?q=...`. Um "x" aparece dentro do campo sempre que há texto digitado e limpa a busca (volta para `/atletas`, mostrando todos os atletas de novo). |
| `ResultadoBuscaTabela` | Tabela (Atleta / Clubes / Até) da página atual — nunca escore ou tier. `app/atletas/page.tsx` decide qual fatia de 10 mostrar. |
| `Pager` | Botões com ícones `CaretDoubleLeft`/`CaretDoubleRight` (phosphor-icons, via `/dist/ssr` por ser componente de servidor) para trocar de página, mantendo a consulta (`q`) e a página (`pagina`) na URL. Ver [`docs/passo-06-paginacao-classica-atletas.md`](../../docs/passo-06-paginacao-classica-atletas.md). |

A ficha em si (rota `/atletas/[id]`) usa os componentes de
[`components/ficha-atleta`](../ficha-atleta/README.md).
