# components/fila-triagem

Componentes específicos da T1 — Fila de triagem da rodada (`03_telas.md`,
§2). Usados só em `app/triagem/page.tsx`.

| Componente | Para quê |
| :--- | :--- |
| `RodadaFiltros` | Selects de competição/ano/rodada. Cada troca navega para a mesma rota com a query atualizada — o servidor busca a nova fila, sem estado de formulário duplicado no cliente. |
| `FilaTriagemPainel` | Dono do estado do corte de percentil. Filtra a lista já carregada no cliente (sem round-trip por arraste) para dar a resposta em tempo real que o doc pede, e decide entre mostrar a tabela ou o estado vazio. |
| `FilaTriagemTabela` | Tabela em si — atleta (com a linha de justificativa obrigatória e o link "ver ficha"), clube, confronto, condição e tier. |

Formatação da linha de justificativa e do tier vive em
[`lib/format/fila.ts`](../../lib/format/fila.ts), não aqui, para poder ser
reusada por outra tela sem importar componente de UI.
