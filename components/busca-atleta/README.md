# components/busca-atleta

Componentes da busca da T2 (`03_telas.md`, §3), usados em `app/atletas/page.tsx`.

| Componente | Para quê |
| :--- | :--- |
| `BuscaAtletaForm` | Campo + botão de busca. Botão inativo com menos de 3 caracteres; submissão explícita (não busca a cada tecla), navegando para `/atletas?q=...` — o servidor busca e re-renderiza. |
| `ResultadoBuscaLista` | Lista de resultados: só nome, clubes e último ano — **nunca escore ou tier**. Cada linha linka para `/atletas/{id}` (a ficha). |
| `Pager` | Anterior/Próxima entre páginas de resultado (10 por página), mantendo a consulta atual na URL. Ver [`docs/passo-04-paginacao-busca.md`](../../docs/passo-04-paginacao-busca.md) — isso substitui o "sem paginação" do doc 03 §3 por pedido explícito do usuário. |

A ficha em si (rota `/atletas/[id]`) usa os componentes de
[`components/ficha-atleta`](../ficha-atleta/README.md).
