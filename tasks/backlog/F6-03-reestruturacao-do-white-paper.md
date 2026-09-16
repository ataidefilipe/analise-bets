# F6-03 — Reestruturação do white paper em dois braços

**Fase:** 6 — Entregáveis
**Responsável sugerido:** Luan de Oliveira e Nickolas Gomes
**Tamanho:** G
**Depende de:** F1-04, F5-03
**Status:** Backlog

---

## Descrição

Reorganizar `reports/white_paper_impacto_bets_futebol_brasileiro.md` em dois braços
articulados:

* **Braço A — Evidência.** O que já existe: contexto regulatório, paradoxo disciplinar,
  inferência causal (TWFE e Event Study), tipologia de infrações e validação com o ground
  truth judicial.
* **Braço B — Produto.** O que deriva da evidência: definição do produto, cliente, validação
  de mercado, governança e limitações operacionais.

## Objetivo

Adequar o entregável principal ao redirecionamento solicitado pelo orientador, sem descartar
o trabalho empírico já concluído.

## Contexto

O white paper foi escrito como artigo, com conclusão voltada a recomendações de política
pública para o Ministério da Fazenda, CBF e STJD. O redirecionamento não invalida esse
conteúdo — a evidência causal continua sendo a fundamentação do produto, e é o que distingue
o projeto de uma ideia de negócio sem base empírica.

A articulação entre os braços é o argumento central do trabalho: **o produto existe porque a
evidência mostrou onde está o risco.** A econometria estabeleceu a associação entre exposição
comercial e dinâmica disciplinar; a análise de tipologia mostrou que quase um terço dos
cartões independe de disputa de bola; o ground truth judicial mostrou que 100% dos eventos
manipulados confessados ocorreram no 1º tempo, com minutagem média de 38,2 minutos. O produto
é a operacionalização desses três achados.

Uma reescrita substantiva, não cosmética, precisa incorporar as correções da Fase 1:

* A afirmação de 100% de sensibilidade precisa ser qualificada com o resultado out-of-sample
  (F1-03) e acompanhada da carga de alerta (F1-04).
* A retirada do `S_bet` do índice (F1-02) precisa ser explicada, com a justificativa
  metodológica.
* A seção de limitações precisa absorver os achados da Fase 1 e as restrições declaradas na
  Fase 4.

## Definition of Done

- [ ] White paper reestruturado nos dois braços, com transição explícita entre evidência e
      produto.
- [ ] Todos os números conferidos contra as tabelas regeradas após a Fase 1.
- [ ] Afirmações de sensibilidade qualificadas e acompanhadas das métricas de precisão e
      carga.
- [ ] Seção de produto incorporando o ICP, as personas e a evidência de demanda da F5-03.
- [ ] Seção de governança e ética incorporando as decisões da Fase 4, incluindo a posição
      sobre o segmento de trading.
- [ ] Seção de limitações ampliada: precisão indeterminada, ground truth de uma operação e uma
      temporada, dependência de fonte única, ausência de dado de mercado de apostas.
- [ ] Recomendações regulatórias preservadas, realocadas para o fecho do Braço A.
- [ ] Links internos e referências conferidos; citações padronizadas.
- [ ] Revisão cruzada entre os cinco integrantes.

## Riscos e observações

* Tarefa de maior volume de escrita do backlog. Iniciar a estrutura cedo, mesmo com seções em
  aberto aguardando F1-04 e F5-03.
* Resistir à tentação de suavizar os achados da Fase 1. Um trabalho que declara suas
  limitações com precisão é avaliado acima de um que as omite e é confrontado na arguição.
