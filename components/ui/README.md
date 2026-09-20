# components/ui

Primitivos genéricos, sem conhecimento de qual tela os usa.

| Componente | Para quê | Doc |
| :--- | :--- | :--- |
| `Callout` | Caixa de aviso interpretativo, sempre visível junto ao escore. | `03_telas.md` §1.1 |
| `EmptyState` | Estado vazio explicativo (fila vazia, sem escalação etc.), nunca uma lista em branco. | `03_telas.md` §1.6 e §6 |

Regra para esta pasta: um componente só entra aqui se nenhuma tela específica
for pré-requisito para entendê-lo. Componente que só faz sentido numa tela
(ex.: a linha de justificativa da fila de triagem) vai para
`components/<tela>/`, não aqui.
