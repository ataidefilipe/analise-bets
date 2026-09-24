# components/ficha-atleta

Componentes da ficha da T2 (`03_telas.md`, §3), usados em `app/atletas/[id]/page.tsx`.

| Componente | Para quê |
| :--- | :--- |
| `FichaCabecalho` | Nome, clubes por onde passou e o identificador (`atletaId`). Enquadramento deliberadamente neutro — ver "Cuidado de design" abaixo. |
| `HistoricoTemporadas` | Uma linha por temporada: partidas, minutos, cartões, proporção de 1º tempo e tier. |
| `LinhaDoTempoCartoes` | Cartões agrupados por temporada, com minuto/período/tipo/categoria e o motivo — ou a nota de que a súmula não registrou o motivo, quando for o caso. |

O aviso interpretativo usa o `Callout` genérico de `components/ui`, não um
componente próprio desta pasta.

## Cuidado de design (doc 03, §3)

Esta é a tela com maior potencial de dano do sistema: uma ficha individual,
nominada, num produto sobre integridade. Por isso nenhum componente aqui usa
vermelho, ícone de alerta ou selo — percentil alto é informação estatística,
não acusação. Antes de adicionar qualquer destaque visual novo nesta pasta,
reler esse trecho do doc.
