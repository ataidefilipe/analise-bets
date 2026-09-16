# F1-02 — Remover `score_bet` do índice de suspeição

**Fase:** 1 — Credibilidade
**Responsável sugerido:** Filipe Ataíde
**Tamanho:** P
**Depende de:** —
**Status:** Backlog

---

## Descrição

O `MATCH_ANOMALY_SCORE` embute um subscore derivado da exposição comercial das equipes a
casas de apostas (`anomaly_detection.py:144` e `:154`):

```python
matches["score_bet"] = np.clip(matches["exposure_total_partida"] * 100.0, 0.0, 100.0)
...
+ 0.10 * matches["score_bet"]
```

Remover este componente do índice composto e redistribuir seu peso entre os subscores de
campo (`S_tempo`, `S_precoce`, `S_volume`, `S_penalti`). A variável `exposure_total_partida`
permanece na base como **coluna de contexto e estratificação**, apenas deixa de compor o
escore de suspeição.

## Objetivo

Eliminar a circularidade metodológica e a indefensabilidade comercial do índice, sem perder
a informação de exposição comercial como dimensão analítica.

## Contexto

Dois problemas distintos justificam a remoção:

1. **Circularidade.** O projeto usa a econometria (TWFE / Event Study) para *estimar* a
   associação entre exposição a bets e cartões. Usar a mesma exposição como *feature* de
   suspeição faz o índice confirmar a hipótese por construção.

2. **Indefensabilidade comercial.** Com o componente ativo, um clube recebe escore de
   suspeição mais alto por causa do patrocinador estampado na camisa — independentemente do
   que aconteceu em campo. Nenhum clube compra um produto que o penaliza por uma decisão
   comercial lícita, e nenhuma federação instrui um procedimento sobre essa base.

O próprio relatório 07 já registra, na observação técnica da seção 4.1, que partidas
anteriores a 2018 (com `S_bet = 0`) disparam alerta apenas pela anomalia de campo — o que
indica que o componente não é necessário para a sensibilidade do sistema.

## Definition of Done

- [ ] `score_bet` removido do cálculo de `match_anomaly_score`; pesos redistribuídos e
      somando 1,0.
- [ ] `exposure_total_partida` preservada como coluna nas bases e nos relatórios de saída,
      sinalizada como **contexto, não componente**.
- [ ] Relatório 07 atualizado: fórmula nova e parágrafo explicando por que a exposição foi
      retirada do escore (a justificativa é um argumento de produto, vale documentar).
- [ ] Comparação antes/depois registrada: quantas partidas mudam de tier de prioridade, e se
      algum dos 14 casos de ground truth muda de classificação.
- [ ] Tabelas 15–17 e figuras de integridade regeradas.
- [ ] Teste unitário garantindo que `exposure` não participa do escore composto.
- [ ] Suíte `pytest` passando.

## Riscos e observações

* Se a sensibilidade no ground truth cair após a remoção, **registrar o número real**. Uma
  queda indicaria que parte da detecção vinha do patrocínio e não do comportamento em campo —
  achado relevante por si só, e material honesto para a seção de limitações.
* Executar junto com F1-01 para uma única regeração de artefatos.
