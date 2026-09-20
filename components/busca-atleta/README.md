# components/busca-atleta

Componentes da tela de atletas (`app/atletas/page.tsx`). Adaptados a partir
da T2 do `03_telas.md`, §3 — ver
[`docs/passo-05-tabela-completa-atletas.md`](../../docs/passo-05-tabela-completa-atletas.md)
sobre como isso diverge do doc original (que descrevia só busca, sem
listagem prévia).

| Componente | Para quê |
| :--- | :--- |
| `BuscaAtletaForm` | Campo + botão de busca. Botão inativo com menos de 3 caracteres; submissão explícita (não busca a cada tecla), navegando para `/atletas?q=...`. |
| `ResultadoBuscaTabela` | Tabela (Atleta / Clubes / Até) — nunca escore ou tier. Mostra todos os atletas por padrão (ordem alfabética) ou só os relacionados à busca; 10 por vez, com botão "Carregar mais 10" que soma ao que já está na tela, sem navegação. |

A ficha em si (rota `/atletas/[id]`) usa os componentes de
[`components/ficha-atleta`](../ficha-atleta/README.md).
