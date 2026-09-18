# F2-03 — Corrigir a ingestão parcial da Série B 2024

**Fase:** 2 — Ativo de dados
**Responsável sugerido:** Filipe Ataíde
**Tamanho:** P
**Depende de:** —
**Status:** Concluído (2026-09-18) — pendência da F2-01 fechada em 16/09; ingestão da Série B 2024 concluída em 18/09, junto com a F2-02

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


---

## Herdado da F2-01 (2026-09-16)

O parser de súmulas atribuía a seção do documento como nome do clube nas expulsões (o clube
vem embutido no nome do atleta na seção de vermelhos). A correção foi aplicada e as súmulas de
2026 das duas séries foram reprocessadas, mas **restam 101 cartões da Série B 2022–2023 com o
clube errado** — 44 em 2022 e 57 em 2023, todos vermelhos ou segundos amarelos.

Reprocessar essas súmulas corrige o problema, mas altera a base sobre a qual os artefatos da
Fase 1 foram gerados: o `ATHLETE_ANOMALY_SCORE` agrupa por `clube_slug`, então um atleta
expulso aparece hoje partido em duas linhas de atleta-temporada, e uma delas pode cair abaixo
do mínimo de 3 cartões. Ao reprocessar, é preciso regenerar as Tabelas 15 a 22 e conferir se
algum número da Fase 1 muda.


---

## Fechamento da pendência herdada da F2-01 (2026-09-16)

Ao reprocessar a Série B 2022–2023 para corrigir a atribuição de clube nas expulsões, o
reparse devolveu **519 cartões a mais** do que a base continha. A investigação encontrou um
segundo defeito, maior:

`parse_cbf_sumulas.py` localizava as seções da súmula **sem guarda de primeira ocorrência**. O
token `2º Cartão Amarelo` — subtipo de expulsão, que aparece dentro da seção de vermelhos —
sobrescrevia o índice da seção de amarelos com uma posição posterior à dos vermelhos, e o
recorte `tokens[idx_amarelo:idx_vermelho]` virava vazio. **Toda partida com expulsão por
segundo amarelo perdia todos os seus cartões amarelos.**

Efeito: a Série B 2022–2023 estava sem 14% dos seus cartões (1.698 → 1.942 em 2022;
1.973 → 2.248 em 2023). O parser do pipeline delta já tinha a guarda e estava correto — por
isso as duas implementações divergiam.

Corrigido, reprocessado e com toda a cadeia de artefatos regenerada. As probabilidades basais
do índice foram reestimadas sobre a base completa. Impacto nos números da Fase 1 registrado no
relatório 07.

**Segue em aberto:** a ingestão da Série B 2024, objeto original desta tarefa (27 cartões em
5 partidas, contra 380 partidas esperadas).

---

## Fechamento (2026-09-18)

A ingestão faltante foi executada junto com a F2-02: **380 de 380 partidas** da Série B 2024,
824 gols e 2.220 cartões, sem nenhum 404. A base da Série B passa a cobrir 2022 a 2025
integralmente.

Foi nessa temporada que apareceu a súmula malformada da partida 181 (Vila Nova), que revelou
os três defeitos encadeados descritos no registro de execução da F2-02.
