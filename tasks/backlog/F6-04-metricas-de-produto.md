# F6-04 — Definição e instrumentação de métricas de produto

**Fase:** 6 — Entregáveis
**Responsável sugerido:** Lacê Rene
**Tamanho:** M
**Depende de:** F1-04
**Status:** Backlog

---

## Descrição

Definir o conjunto de métricas pelas quais o produto é avaliado, e instrumentar o pipeline
para que sejam calculadas e registradas automaticamente a cada execução.

Métricas propostas:

**Qualidade do sinal**
* Precisão@k por rodada (k = 1, 3, 5)
* Sensibilidade out-of-sample no ground truth, com intervalo de confiança
* Carga de alerta: itens sinalizados por rodada, por nível e por tier

**Qualidade do dado**
* Taxa de parsing bem-sucedido de súmulas
* Completude por temporada: partidas, gols e cartões efetivamente ingeridos frente ao esperado
* Taxa de preenchimento do motivo do cartão
* Taxa de não classificados na tipologia de infrações

**Operação**
* Latência D+1: horas entre o fim da partida e a disponibilidade do dado processado
* Taxa de sucesso das execuções do pipeline
* Súmulas indisponíveis, com o motivo

## Objetivo

Tornar a saúde do produto mensurável e visível, em vez de inferida da última execução
bem-sucedida.

## Contexto

O pipeline já produz um relatório de auditoria por execução
(`data/processed/delta_pipeline_last_run.json`), com contagens de downloads e registros
inseridos. Falta a camada de métricas de **qualidade** — a que mostraria, por exemplo, que a
Série B 2024 entrou na base com 27 cartões, quando o esperado eram cerca de 1.900, e que isso
passou sem alerta.

A distinção é relevante: o relatório atual mede o que o pipeline **fez**; as métricas medem
se o que ele fez está **correto e útil**. Só o segundo conjunto detecta falhas silenciosas.

As métricas também são entregável acadêmico. A pergunta "como vocês sabem que o produto está
funcionando?" tem resposta fraca se for a última execução sem erro, e forte se for um painel
histórico de qualidade.

## Definition of Done

- [ ] Conjunto de métricas definido e documentado, com fórmula, fonte e limiar de alerta para
      cada uma.
- [ ] Cálculo automático incorporado ao fim de cada execução do pipeline.
- [ ] Histórico de métricas persistido, permitindo comparar execuções ao longo do tempo.
- [ ] Alertas explícitos quando uma métrica cruzar seu limiar — em especial completude e taxa
      de parsing, que são as que capturariam falhas como a da Série B 2024.
- [ ] Painel ou relatório simples exibindo a série histórica das métricas.
- [ ] Métricas citadas no documento de visão de produto (F6-01) e no white paper (F6-03).
- [ ] Testes unitários do cálculo das métricas.
- [ ] Suíte `pytest` passando.

## Riscos e observações

* Sobreposição parcial com a checagem de completude da F2-03. Coordenar para que a checagem
  seja implementada uma vez e consumida pelas duas tarefas.
* Definir limiares realistas. Um limiar excessivamente sensível gera ruído e passa a ser
  ignorado — o mesmo problema que a F1-04 identifica na fila de triagem.
