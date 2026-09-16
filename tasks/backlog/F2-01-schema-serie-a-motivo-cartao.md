# F2-01 — Migrar o schema da Série A para carregar o motivo do cartão

**Fase:** 2 — Ativo de dados
**Responsável sugerido:** Filipe Ataíde
**Tamanho:** M
**Depende de:** —
**Status:** Backlog

---

## Descrição

O parser de súmulas extrai corretamente o motivo textual digitado pelo árbitro e sua
categorização (`src/cleaning/cbf_delta_processor.py:339-340`):

```python
"motivo_completo": motivo_full,
"categoria_infracao": categorize_card_reason(motivo_full),
```

Porém, a função `align_schema` (`:355-362`) força o DataFrame novo a adotar exatamente as
colunas da base existente. Como `data/processed/serie_a/cartoes.csv` foi originado da base
histórica do Kaggle (Adão Duque), que não possui essas colunas, **o motivo é descartado
silenciosamente para a Série A**.

Efeito concreto e já materializado: os **1.370 cartões da Série A 2026**, obtidos das
súmulas oficiais da CBF, estão na base sem motivo.

Migrar o schema da Série A para incluir `motivo_completo` e `categoria_infracao`, nulos
para o período histórico (2003–2024) e preenchidos de 2026 em diante, e reprocessar as
súmulas 2026 já baixadas.

## Objetivo

Recuperar, para a Série A, o atributo de maior valor competitivo do projeto, e impedir que
ele continue sendo perdido a cada execução do pipeline delta.

## Contexto

O motivo textual do árbitro é o diferencial mais forte do produto. A análise da Série B já
demonstrou o valor: dos 3.671 cartões de 2022–2023, **28,9% decorrem de infrações
comportamentais não-físicas** — reclamação (15,8%), cera (8,4%), conduta antidesportiva
não-física (4,8%), toque de mão (0,9%).

Essa é precisamente a categoria mais fácil de encomendar, porque **não depende de disputa
de bola**: o atleta não precisa de uma jogada específica para reclamar com o árbitro ou
retardar o reinício. Um cartão por falta temerária exige que o lance aconteça; um cartão por
reclamação, não.

Nenhum provedor de dados esportivos comerciais disponibiliza esse campo estruturado. É a
base do argumento de diferenciação frente a Sportradar, Genius, Sofascore e Opta — e hoje
só existe para a Série B, a divisão de menor visibilidade comercial.

## Definition of Done

- [ ] `data/processed/serie_a/cartoes.csv` e `.parquet` migrados com as colunas
      `motivo_completo` e `categoria_infracao`, nulas para 2003–2024.
- [ ] `align_schema` ajustada para **unir** schemas (preservando colunas novas) em vez de
      truncar para o schema antigo; comportamento coberto por teste.
- [ ] Súmulas da Série A 2026 já baixadas reprocessadas, com o motivo preenchido.
- [ ] Taxa de preenchimento do motivo reportada por temporada e por série (quantos cartões
      têm motivo recuperado com sucesso).
- [ ] `docs/data_dictionary.md` atualizado com as colunas novas e sua cobertura temporal.
- [ ] Manifesto de processados (`manifest_processed.json`) refletindo o schema novo.
- [ ] Teste de regressão garantindo que uma coluna presente no dado novo e ausente no
      histórico não é descartada.
- [ ] Suíte `pytest` passando.

## Riscos e observações

* Verificar se o layout da súmula da Série A 2026 é idêntico ao da Série B 2022–2023, para o
  qual o parser foi calibrado. Se divergir, a extração do motivo pode exigir ajuste de
  tokenização.
* A perda é retroativa apenas até onde há súmula oficial disponível. Para 2003–2024 na Série
  A, o motivo **não existe na fonte** (Kaggle) e permanecerá nulo — isso é esperado e deve
  ser documentado, não tratado como falha.
