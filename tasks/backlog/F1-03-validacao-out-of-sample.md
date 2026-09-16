# F1-03 — Validação out-of-sample do classificador de integridade

**Fase:** 1 — Credibilidade
**Responsável sugerido:** Lacê Rene
**Tamanho:** M
**Depende de:** F1-01, F1-02
**Status:** Backlog

---

## Descrição

O classificador híbrido (`IsolationForest` + `BaggingPUClassifier`) é treinado e avaliado
sobre o mesmo conjunto de casos. Em `src/models/integrity_classifier.py`:

* `train_match_classifiers(df_matches, df_pm)` — linha 105
* `train_athlete_classifiers(df_athletes, df_pm)` — linha 174
* `evaluate_ground_truth_ml(df_matches, df_athletes, df_pm)` — linha 240

`df_pm` é o ground truth da Operação Penalidade Máxima e é usado para construir `y_pu` no
treino (linhas 153 e 220) **e** para avaliar o resultado. A sensibilidade reportada de
100% (14/14) é, portanto, medida **dentro da amostra de treino**.

Implementar um protocolo de validação fora da amostra e reportar a sensibilidade real.

## Objetivo

Produzir uma estimativa honesta do poder de generalização do classificador, substituindo a
métrica in-sample que hoje sustenta a principal afirmação do projeto.

## Contexto

Com 14 positivos conhecidos, qualquer classificador supervisionado ou semi-supervisionado
consegue 100% de sensibilidade in-sample — o número não carrega informação. A afirmação
"100% de sensibilidade" aparece hoje no relatório 07, em `docs/decisoes_e_progresso.md`, na
proposta de projeto e no white paper, e é o principal argumento de eficácia do sistema.
Se ela cair em avaliação honesta, todos esses documentos precisam ser ajustados.

Há duas estratégias viáveis, não excludentes:

1. **Leave-one-out sobre os positivos** — para cada um dos 14 incidentes, retreinar sem ele
   e verificar se ainda é capturado no tier prioritário.
2. **Separação por série** — treinar apenas com os casos da Série B (Fase 1 da operação) e
   testar nos casos da Série A, ou vice-versa. Mais próximo do uso real: detectar um esquema
   novo com um modelo calibrado em esquemas anteriores.

Observação importante: o `MATCH_ANOMALY_SCORE` e o `ATHLETE_ANOMALY_SCORE` estatísticos
(binomiais) **não** são treinados no ground truth — são fórmulas fechadas calibradas em
distribuição basal. Eles não sofrem deste problema e podem ser reportados separadamente,
com sua sensibilidade original preservada. Essa distinção deve ficar explícita.

## Definition of Done

- [ ] Protocolo leave-one-out implementado para os 14 positivos, nos dois níveis (partida e
      atleta).
- [ ] Protocolo de separação por série implementado como validação complementar.
- [ ] Sensibilidade out-of-sample reportada em tabela nova, lado a lado com a in-sample.
- [ ] Distinção explícita, no código e no relatório, entre os escores estatísticos fechados
      (não treinados no ground truth) e o classificador de ML (treinado).
- [ ] `reports/analysis/07_*.md` e `docs/decisoes_e_progresso.md` atualizados com os números
      reais; a afirmação "100% de sensibilidade" qualificada ou substituída.
- [ ] Testes unitários cobrindo o novo protocolo em `tests/test_integrity_classifier.py`.
- [ ] Suíte `pytest` passando.

## Riscos e observações

* **Esta é a tarefa de maior risco narrativo do backlog.** É provável que a sensibilidade
  caia. Tratar a queda como resultado, não como falha: um sistema de triagem com
  sensibilidade honesta declarada é vendável; um com 100% in-sample não sobrevive à primeira
  diligência técnica.
* Com N = 14, qualquer estimativa terá intervalo de confiança largo. Reportar o intervalo,
  não só o ponto.
