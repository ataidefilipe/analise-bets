# Passo 9 — T4: Panorama agregado

Status: pronto para avaliação. **Fecha as 4 telas do MVP do doc 03.**

## O que foi entregue

- Rota `/agregados` com:
  - Alternância "por clube" / "por rodada" (`FiltrosAgregado`) — doc 03,
    §5: "Agregados por clube ou por rodada".
  - Filtro por competição (Série A / Série B / todas).
  - Tabela ordenável (`AgregadoTabela`): partidas, cartões, cartões no 1º
    tempo, proporção e média por partida. Clicar num cabeçalho alterna a
    ordenação (crescente/decrescente) por aquela coluna.
  - Gráfico de barras da proporção de cartões no 1º tempo por clube
    (`ProporcaoPorClubeChart`) — sempre por clube, mesmo com a tabela em
    modo "por rodada", exatamente como o doc descreve.
- `lib/mock/agregados.ts` reaproveita os mocks de partida/dossiê da T3
  (`listarPartidas` + `getDossiePartida`) em vez de manter um terceiro
  dataset paralelo — os números desta tela batem com os da T3.
- **Regra inegociável do doc 03, §5 seguida à risca**: nenhum tipo, mock ou
  componente desta tela tem (ou pode ganhar) um campo de atleta. Documentei
  isso explicitamente no README de `components/panorama-agregado` como
  aviso para qualquer alteração futura.
- Gráfico construído seguindo a skill de dataviz do projeto: como é uma
  única série (mesma métrica, várias categorias — magnitude, não
  identidade), usei uma cor só (`bg-accent`, já validada com o script da
  skill para contraste), sem legenda, com o valor direto na ponta de cada
  barra em vez de eixo/grade. A tabela ordenável ao lado cobre a exigência
  de ter uma visão em tabela como alternativa ao gráfico.

## Como conferir

1. `pnpm dev`, ir em "Panorama agregado" pelo menu (perfis P3 ou P5 têm
   acesso; P5 só tem acesso a esta tela).
2. Alternar entre "Por clube" e "Por rodada": a tabela muda de colunas
   pertinentes; o gráfico continua sempre por clube.
3. Filtrar por Série A ou Série B: tabela e gráfico atualizam juntos.
4. Clicar nos cabeçalhos da tabela para reordenar por qualquer coluna.
5. Inspecionar a página (view-source): não deve haver nenhum campo de
   atleta em lugar nenhum — nem nos dados, nem na tela.

## Assunções registradas (a confirmar quando os docs 01/02 chegarem)

- Filtro por competição é uma adição prática (o doc não detalha os filtros
  desta tela além de "por clube ou por rodada").
- O gráfico usa os mesmos ~20 clubes fictícios das outras telas; como a
  base de partidas mock tem só 24 jogos, é possível (e aconteceu no teste)
  que algum clube fique de fora por não ter sido sorteado em nenhuma
  partida — comportamento correto do agregado, não um bug.

## Isso fecha o MVP

Com T1 (fila de triagem), T2 (busca e ficha do atleta), T3 (dossiê de
partida) e T4 (panorama agregado) implementadas, as 4 telas do doc 03 estão
todas de pé sobre a mesma base (perfil/menu dinâmico, paleta de marca, tema
claro/escuro). O que resta é o que o próprio doc já registra como fora do
MVP (§7) e as pendências acumuladas nos passos anteriores — sobretudo
trocar a camada `lib/mock/*` por chamadas reais assim que os docs 01 e 02
chegarem.
