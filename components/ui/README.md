# components/ui

Primitivos genéricos, sem conhecimento de qual tela os usa.

| Componente | Para quê | Doc |
| :--- | :--- | :--- |
| `Callout` | Caixa de aviso interpretativo, sempre visível junto ao escore. | `03_telas.md` §1.1 |
| `EmptyState` | Estado vazio explicativo (fila vazia, sem escalação etc.), nunca uma lista em branco. | `03_telas.md` §1.6 e §6 |
| `CopiarTexto` | Botão de copiar genérico (usado na procedência do dossiê de partida). | `03_telas.md` §4 |
| `BuscaForm` | Campo + botão de busca genérico (nome/apelido de atleta, nome de clube em partidas) — mínimo 3 caracteres, "x" para limpar. Recebe `basePath`, `placeholder` e `parametros` (filtros a manter na URL). | `03_telas.md` §3 |
| `Pager` | Paginação genérica, com ícones `CaretDoubleLeft`/`CaretDoubleRight`. Recebe `basePath` e `parametros`; mantém a consulta e os filtros na URL. | — |
| `SerieTemporadaFiltros` | Par de selects série + temporada (listagem de partidas e panorama). Temporadas vêm de `/v1/cobertura`. | — |

Regra para esta pasta: um componente só entra aqui se nenhuma tela específica
for pré-requisito para entendê-lo. Componente que só faz sentido numa tela
(ex.: a linha de justificativa da fila de triagem) vai para
`components/<tela>/`, não aqui.
