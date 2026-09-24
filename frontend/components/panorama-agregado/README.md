# components/panorama-agregado

Componentes da T4 (`03_telas.md`, §5), usados em `app/agregados/page.tsx`.

| Componente | Para quê |
| :--- | :--- |
| `FiltrosAgregado` | Alterna entre agregação "por clube" e "por rodada". Série e temporada ficam em `components/ui/SerieTemporadaFiltros` — a API agrega uma de cada vez. |
| `AgregadoTabela` | Tabela ordenável (clicar num cabeçalho alterna a ordenação) — partidas, cartões, cartões no 1º tempo, proporção e média por partida. |
| `ProporcaoPorClubeChart` | Gráfico de barras da proporção de cartões no 1º tempo por clube — sempre por clube, mesmo com a tabela em modo "por rodada". |

## Regra inegociável desta pasta (doc 03, §5)

> "Nenhum atleta, em nenhuma circunstância. Se um dia aparecer um campo de
> atleta nesta tela, é vazamento de camada e o backend está com defeito."

Nenhum tipo em `lib/types/agregado.ts` tem campo de atleta, e o adaptador
(`lib/api/agregados.ts`) só lê contagens por clube/rodada. Qualquer PR
que adicione um campo de atleta aqui deve ser tratado como bug de
segurança de camada, não como funcionalidade.

## Gráfico

Segue a skill de dataviz do projeto: série única (magnitude por categoria)
→ uma cor só (`bg-accent`), sem legenda (o título já diz o que é plotado),
valor direto na ponta de cada barra em vez de eixo/grade (já que todo valor
está rotulado). A tabela ordenável ao lado já cobre a "visão em tabela"
exigida como alternativa acessível ao gráfico.
