# F2-03 — Corrigir a ingestão parcial da Série B 2024

**Fase:** 2 — Ativo de dados
**Responsável sugerido:** Filipe Ataíde
**Tamanho:** P
**Depende de:** —
**Status:** Backlog

---

## Descrição

A Série B de 2024 está presente na base, mas com volume incompatível com uma temporada
completa. Em `data/processed/serie_b/cartoes.csv`, a distribuição por temporada é:

| Temporada | Cartões |
| :---: | ---: |
| 2022 | 1.698 |
| 2023 | 1.973 |
| **2024** | **27** |
| 2026 | 1.383 |

Vinte e sete cartões em uma temporada de 380 partidas indica ingestão interrompida ou
parcial — o esperado, pela média das temporadas vizinhas, é da ordem de 1.800 a 1.900.

Diagnosticar a causa, completar a ingestão e validar.

## Objetivo

Fechar a cobertura da Série B e garantir que o pipeline não produza temporadas parciais
silenciosamente.

## Contexto

O problema não é apenas o dado faltante — é que **ele passou despercebido**. O pipeline
concluiu com sucesso, gerou manifesto e alimentou o feed de produto com uma temporada 93%
vazia, sem disparar alerta.

Para um produto vendido sobre a promessa de base auditável e rastreável, uma ingestão
parcial silenciosa é uma falha mais grave que o dado ausente em si. A correção deve incluir
uma **checagem de completude** que torne esse tipo de falha visível.

A Série B tem relevância desproporcional para o produto: foi onde a Operação Penalidade
Máxima começou, é a divisão de maior vulnerabilidade e a de menor cobertura pelos provedores
globais de dados esportivos.

## Definition of Done

- [ ] Causa raiz identificada e registrada (súmulas não baixadas, falha de parsing, filtro de
      rodada, ou outra).
- [ ] Temporada 2024 da Série B ingerida integralmente; contagem de partidas, gols e cartões
      compatível com a magnitude de 2022, 2023 e 2026.
- [ ] **Checagem de completude** adicionada ao pipeline: ao final da execução, comparar o
      número de partidas e cartões por temporada contra o esperado e emitir aviso explícito
      no relatório de auditoria quando a divergência ultrapassar um limiar definido.
- [ ] Relatório de auditoria do pipeline (`delta_pipeline_last_run.json`) passa a conter a
      seção de completude.
- [ ] Verificação equivalente aplicada a **todas** as temporadas já ingeridas, para descobrir
      se há outras lacunas parciais não detectadas.
- [ ] Teste unitário da checagem de completude.
- [ ] Suíte `pytest` passando.

## Riscos e observações

* Executar a verificação retroativa antes de assumir que 2024 é o único caso. A Série A 2026
  registra 114 súmulas com HTTP 404 na última execução — confirmar se são partidas ainda não
  realizadas (esperado, temporada em curso) ou indisponibilidade real da fonte.
