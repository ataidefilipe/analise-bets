# Passo 3 — T2: Busca e ficha do atleta

Status: pronto para avaliação.

## O que foi entregue

- Rota `/atletas` (busca), substituindo o placeholder do passo 1: campo +
  botão de busca desativado com menos de 3 caracteres, submissão explícita
  (não busca a cada tecla, como o mockup do doc mostra), sem paginação, até
  20 resultados.
- Estados da busca: "digite ao menos 3 caracteres", "nenhum atleta
  encontrado" (com o texto exato do doc sobre a cobertura da base) e a
  lista de resultados — **só nome, clubes e último ano, nunca escore ou
  tier**, exatamente como o doc exige para não virar um ranking de
  atipicidade disfarçado de busca.
- Rota dinâmica `/atletas/[id]` (ficha), nova — antes a T1 linkava para
  `/atletas?atletaId=...`; migrei para `/atletas/{id}`, espelhando o
  formato do endpoint do doc 01 (`/atletas/{id}`) e dando à ficha uma URL
  própria, compartilhável e com histórico de navegação real (o botão
  "Voltar" agora volta de fato para a busca, não só para a home).
- Ficha com as 4 seções do doc: cabeçalho (nome, clubes, identificador),
  histórico por temporada (partidas, minutos, cartões, proporção de 1º
  tempo, tier), linha do tempo de cartões (agrupada por temporada, com
  minuto/período/tipo/categoria) e o aviso interpretativo.
- Onde o motivo do cartão não está registrado (~86% dos casos simulados,
  seguindo a estatística do doc para a Série A), aparece "Motivo não
  registrado na súmula desta temporada" em vez de um campo vazio.
- Enquadramento visual neutro em toda a ficha — sem vermelho, ícone de
  alerta ou selo (doc 03, §3, "Cuidado de design"). Documentei essa regra
  no README de `components/ficha-atleta` para não se perder em telas
  futuras.
- Refactor de apoio: o vocabulário de tier (antes só dentro de
  `filaTriagem.ts`) virou `lib/mock/tier.ts`, e o formatador
  correspondente virou `lib/format/tier.ts` — T1 e T2 agora reusam o mesmo
  código em vez de ter cada um a sua cópia.

## Como conferir

1. `pnpm dev`, entrar em "Busca e ficha do atleta" pelo menu.
2. Digitar 1–2 letras: botão de busca continua inativo.
3. Buscar por "Silva" (nome comum no pool de mock): ver a lista de
   resultados sem nenhum escore/tier.
4. Buscar por algo sem correspondência (ex.: "zzzzz"): ver o estado vazio.
5. Abrir uma ficha pela lista de resultados e conferir as 4 seções.
6. Voltar para a T1 (Triagem) e clicar em "ver ficha" numa linha da fila —
   deve abrir a ficha do mesmo atleta, com dados consistentes ao recarregar.
7. Clicar no botão de voltar (círculo com seta) na ficha: deve retornar à
   busca ou à triagem, dependendo de onde você veio.

## Assunções registradas (a confirmar quando os docs 01/02 chegarem)

- **Categorias do motivo do cartão** ("Reclamação", "Falta tática" etc.) são
  inventadas para o mock — o doc só diz que existe uma "categoria", sem
  definir o vocabulário.
- **Tipo de cartão** simplificado para amarelo/vermelho binário; o doc não
  detalha se "segundo amarelo" é um tipo à parte.
- Continuam valendo as assunções do passo 2 sobre o vocabulário de tier.

## O que fica para os próximos passos

- T3 (dossiê de partida) e T4 (panorama agregado).
- Trocar `buscarAtletas`/`getFichaAtleta` por chamadas reais quando o doc 01
  chegar.
