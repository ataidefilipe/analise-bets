# F6-01 — Documento de visão de produto

**Fase:** 6 — Entregáveis
**Responsável sugerido:** Filipe Ataíde
**Tamanho:** M
**Depende de:** —
**Status:** Backlog

---

## Descrição

Redigir o documento de visão de produto em `docs/visao_produto.md`, consolidando a definição
do que está sendo construído, para quem, por quê, e com quais limites.

Estrutura sugerida:

1. Problema e contexto regulatório
2. Definição do produto em três camadas (dado, triagem, risco pré-jogo)
3. Segmentação de clientes e definição do ICP
4. Personas, com a pergunta que cada uma faz e o formato em que quer a resposta
5. Proposta de valor por segmento
6. Vantagens competitivas e ativos defensáveis
7. Riscos: técnicos, jurídicos, éticos e comerciais
8. Modelo de receita
9. Métricas de produto
10. Roadmap e estado atual

## Objetivo

Dar ao orientador e à banca um documento único que responda ao redirecionamento solicitado, e
alinhar a equipe sobre o que está sendo construído antes que o trabalho técnico avance.

## Contexto

A análise de negócio já está registrada em [`docs/analise_negocio.md`](../../docs/analise_negocio.md)
— diagnóstico de mercado, inventário de ativos, segmentação, personas, vantagens, riscos e
concorrência. **Esta tarefa não a reescreve.**

A separação entre os dois documentos é deliberada:

| Documento | Papel | Base |
| :--- | :--- | :--- |
| `docs/analise_negocio.md` | **Análise** — o que o mercado parece ser | Hipóteses fundamentadas |
| `docs/visao_produto.md` (esta tarefa) | **Decisão** — o que será construído | Evidência da Fase 5 |

O trabalho aqui é converter hipótese em decisão: revisar cada afirmação da análise à luz do
que a F5-03 encontrou, descartar o que foi refutado, e comprometer o projeto com um escopo.

Pontos que o documento precisa tratar de frente, porque são as perguntas que a banca fará:

* **Por que não as bets como cliente primário.** Três razões: timing (mercados de cartão
  liquidam no apito final, e um alerta D+1 chega depois do pagamento), sinal inferior
  (operadoras já têm dado transacional de odds e apostas, que antecede o evento), e conflito
  de interesse (o mesmo escore serve para proteger e para precificar).
* **Por que o pipeline é o ativo, e não o modelo.** O diferencial defensável é a base oficial
  auditável com minuto e motivo do árbitro, não a fórmula de scoring.
* **Qual é a resposta à concorrência.** Sportradar, Genius Sports e IBIA operam com dado de
  mercado em tempo real. O posicionamento do projeto é complementar e de nicho: fonte oficial,
  explicável, com cobertura de Série B e admissibilidade para instrução de procedimento.

O documento deve ser escrito como hipótese declarada enquanto a F5-03 não estiver pronta, e
revisado com a evidência quando estiver.

## Definition of Done

- [ ] `docs/visao_produto.md` redigido com as dez seções, **derivado** de
      `docs/analise_negocio.md` e não duplicando seu conteúdo.
- [ ] Cada hipótese da análise de negócio marcada como **confirmada, refutada ou ainda em
      aberto**, com a referência à entrevista que a sustenta.
- [ ] Definição do ICP explícita, com justificativa e com as alternativas descartadas e o
      motivo do descarte.
- [ ] Personas descritas com a pergunta que fazem e o formato de entrega que esperam,
      atualizadas com a linguagem real dos entrevistados.
- [ ] Escopo comprometido: o que **será** e o que **não será** construído até a entrega.
- [ ] Seção de riscos incluindo os achados técnicos da Fase 1 (precisão indeterminada,
      validação in-sample, circularidade do `S_bet`) — declarados, não omitidos.
- [ ] Seção de concorrência com posicionamento explícito.
- [ ] Seção de ética e conflito de interesse, remetendo à F4-03.
- [ ] Ambos os documentos referenciados no `README.md` do repositório.
- [ ] Revisado pelos cinco integrantes antes de ser apresentado ao orientador.

## Riscos e observações

* O risco principal é o documento virar cópia da análise de negócio com outro título. A prova
  de que não virou é a presença de decisões: escopo fechado, segmento recusado, hipótese
  descartada.
* Se a F5-03 refutar hipóteses centrais, este documento deve registrar a mudança de rumo
  abertamente. Um projeto que corrige o curso com evidência é avaliado acima de um que
  sustenta a hipótese inicial por inércia.
