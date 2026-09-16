# F1-01 — Reconciliar pesos e subscore de pênalti entre código e documentação

**Fase:** 1 — Credibilidade
**Responsável sugerido:** Rebeka Lemos
**Tamanho:** P
**Depende de:** —
**Status:** Backlog

---

## Descrição

O `MATCH_ANOMALY_SCORE` está documentado de uma forma no relatório técnico e implementado
de outra no código. Há duas divergências:

**Pesos do índice composto**

| Componente | Relatório 07 | Código (`anomaly_detection.py:151-155`) |
| :--- | :---: | :---: |
| `S_tempo` | 0,30 | **0,35** |
| `S_precoce` | 0,25 | 0,25 |
| `S_volume` | 0,20 | 0,20 |
| `S_bet` | 0,15 | **0,10** |
| `S_penalti` | 0,10 | 0,10 |

**Subscore de pênalti no 1º tempo**

* Relatório 07: três faixas — `80,0` se ≥ 2 pênaltis, `40,0` se 1 pênalti, `0,0` se nenhum.
* Código (`anomaly_detection.py:147`): binário — `np.where(penaltis_1t > 0, 100.0, 0.0)`.

Também há divergência no `S_volume`: o relatório descreve `clip(Z · 25,0)`, enquanto o
código usa `clip(50,0 + 20,0 · Z)`. Verificar durante a execução da tarefa.

## Objetivo

Garantir que a fórmula publicada seja exatamente a fórmula executada, e que todos os
números derivados (tabelas, figuras, percentis) tenham sido gerados pela versão vigente.

## Contexto

O projeto se posiciona explicitamente sobre reprodutibilidade — hashes SHA-256, manifestos
de proveniência, suíte de testes. Uma divergência entre a fórmula publicada e a fórmula
executada invalida essa premissa e é o tipo de inconsistência que uma banca encontra em
poucos minutos. Como todos os resultados de triagem (Tabelas 15, 16 e 17) derivam deste
índice, a correção exige regeração dos artefatos.

Esta tarefa deve ser executada **em conjunto com a F1-02**, que altera os mesmos pesos, para
evitar duas regerações consecutivas das tabelas.

## Definition of Done

- [ ] Decidido e registrado qual é a especificação correta (código ou relatório), com
      justificativa metodológica de uma linha por componente divergente.
- [ ] `src/models/anomaly_detection.py` e `reports/analysis/07_sistema_triagem_anomalias_integridade.md`
      expressam a mesma fórmula, incluindo `S_volume` e `S_penalti`.
- [ ] Tabelas 15, 16 e 17 regeradas a partir do código corrigido.
- [ ] Figuras em `reports/figures/integrity/` regeradas.
- [ ] Números citados em `docs/decisoes_e_progresso.md` e no white paper conferidos contra
      as tabelas novas e corrigidos onde divergirem.
- [ ] Teste unitário em `tests/test_anomaly_detection.py` que fixa os pesos e falha se a
      soma dos coeficientes ≠ 1,0 ou se algum peso for alterado sem atualização do teste.
- [ ] Suíte `pytest` passando integralmente.

## Riscos e observações

* Se a alteração de peso mudar a classificação de algum dos 14 casos da Operação Penalidade
  Máxima, isso **deve ser reportado, não escondido**. É um resultado de sensibilidade
  legítimo e alimenta a F1-04.
