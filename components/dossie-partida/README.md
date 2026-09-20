# components/dossie-partida

Componentes da T3 (`03_telas.md`, §4). `ResultadoPartidasTabela` é usada em
`app/partidas/page.tsx` (listagem, com busca e paginação genéricas — ver
[`docs/passo-08-busca-e-paginacao-partidas.md`](../../docs/passo-08-busca-e-paginacao-partidas.md));
as demais são usadas em `app/partidas/[id]/page.tsx` (o dossiê).

| Componente | Para quê |
| :--- | :--- |
| `ResultadoPartidasTabela` | Tabela (Partida / Competição / Data) da página atual, mais recentes primeiro. Não existe no doc 03 — ver nota sobre a listagem de partidas ser uma adição do projeto. |
| `IdentificacaoPartida` | Seção 1: confronto, placar, data, arena, árbitro, competição/rodada. |
| `ProcedenciaPartida` | Seção 2, "o coração da tela": fonte, URL da súmula, SHA-256, datas de download/processamento. URL e hash têm botão de copiar (`components/ui/CopiarTexto`). |
| `EventosPartida` | Seção 3: cartões com minuto, período, tipo e motivo (ou a nota de que a súmula não registrou). |
| `EscoreAnomaliaPartida` | Seção 4: percentil da partida + a ressalva obrigatória de que, neste nível, o escore não discrimina melhor que sorteio. |
| `AtletasSinalizados` | Seção 5, só camada identificada — quem chama (`app/partidas/[id]/page.tsx`) decide se renderiza, checando `perfil.granularidade`. Linka para a ficha do atleta (T2). |
| `ExportarPdfButton` | Botão "Exportar PDF" = `window.print()` (doc 03, §4, "[MVP] Dívida": não é um registro auditável assinado). |

## Impressão

`AppShell` (cabeçalho/menu) e `BackButton` ficam ocultos com `print:hidden`
para que a impressão mostre só o conteúdo do dossiê. Qualquer componente
novo que só faz sentido na tela (não no papel) deve usar a mesma classe.
