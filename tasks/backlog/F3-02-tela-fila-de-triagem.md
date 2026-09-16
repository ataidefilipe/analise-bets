# F3-02 — Tela de fila de triagem da rodada

**Fase:** 3 — Produto
**Responsável sugerido:** Rebeka Lemos
**Tamanho:** M
**Depende de:** F1-04
**Status:** Backlog

---

## Descrição

Construir a interface do produto: uma tela única que apresenta, para a rodada mais recente,
uma fila curta e priorizada de partidas e atletas que merecem escrutínio — com a memória de
cálculo aberta para cada item.

Estrutura mínima:

* Fila com 3 a 5 itens por rodada, ordenada por prioridade.
* Ao abrir um item: subscores que dispararam, p-valor de cada teste, minutos dos eventos,
  motivo textual do árbitro e comparação contra a distribuição basal.
* Link para a súmula-fonte com o hash SHA-256 correspondente.
* Contexto da partida (exposição comercial, rodada, situação na tabela) apresentado como
  informação de apoio, explicitamente **fora** do escore.

## Objetivo

Dar forma de produto ao que hoje existe como notebook e CSV, e tornar o sistema
demonstrável a um cliente ou a uma banca.

## Contexto

Nenhuma das personas identificadas consome notebook. O analista de federação quer saber
quais jogos mandar para revisão de vídeo; o compliance de clube quer saber se algum atleta do
elenco está sinalizado; o integrity officer de operadora quer um registro auditável. Todos
querem uma lista curta com justificativa, e nenhum quer rodar Python.

O requisito central não é estética nem volume de informação — é **explicabilidade**. Um
analista de federação precisa poder fundamentar por que abriu ou arquivou um procedimento.
Um escore isolado não fundamenta nada; um escore acompanhado do teste binomial, do minuto e
do motivo digitado pelo árbitro, com link para a súmula original e hash de integridade,
fundamenta.

Essa exigência é também o diferencial frente a sistemas de caixa-preta: a fórmula fechada do
projeto é uma vantagem de produto, não uma limitação técnica.

O limiar de corte da fila vem da F1-04 — sem a curva de carga operacional, não há como
definir quantos itens exibir.

## Definition of Done

- [ ] Tela funcional exibindo a fila da rodada mais recente disponível na base.
- [ ] Cada item abre a memória de cálculo completa: subscores, p-valores, minutagem, motivo e
      comparação com a distribuição basal.
- [ ] Link para a súmula-fonte com hash exibido.
- [ ] Limiar de corte configurável, com o valor padrão derivado da F1-04.
- [ ] Aviso permanente e visível na interface: escore alto significa desvio estatístico da
      distribuição basal, **não** indício ou acusação de manipulação.
- [ ] Nomes de atletas tratados conforme a arquitetura definida na F4-02; se a F4-02 ainda não
      estiver concluída, a tela opera em modo agregado ou pseudonimizado.
- [ ] Funciona sobre os dados de 2026 já processados, sem preparação manual.
- [ ] Documentação de como subir e rodar a tela.

## Riscos e observações

* Escopo deve ficar deliberadamente pequeno: uma tela, uma fila, um detalhe. O objetivo é
  demonstrar o produto, não construir uma plataforma.
* Esta tela é o artefato central da demo da banca (F6-02). Priorizar clareza de leitura sobre
  quantidade de recursos.
