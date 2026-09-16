# F2-05 — Estender a tipologia de infrações a toda a base

**Fase:** 2 — Ativo de dados
**Responsável sugerido:** Rebeka Lemos
**Tamanho:** P
**Depende de:** F2-01, F2-02
**Status:** Backlog

---

## Descrição

A classificação de motivos de cartão (`categorize_card_reason`, em
`src/cleaning/cbf_delta_processor.py:48`) foi desenvolvida e validada sobre a Série B de
2022–2023. Com a conclusão da F2-01 e da F2-02, o motivo passa a existir também para a
Série A (2026 em diante), para a Série B 2024 e para as duas séries em 2025.

Revalidar a taxonomia sobre o corpus ampliado, medir sua cobertura e produzir a análise
tipológica consolidada.

## Objetivo

Transformar a tipologia de infrações de achado pontual da Série B em dimensão analítica
transversal da base, e verificar se a assinatura comportamental identificada se mantém fora
da amostra original.

## Contexto

A tipologia sustenta um dos argumentos centrais do produto: cartões por infração
comportamental não-física (reclamação, cera, conduta antidesportiva) são estruturalmente
mais fáceis de encomendar, porque não dependem de disputa de bola. Na Série B 2022–2023 essa
categoria representa **28,9% dos 3.671 cartões** — reclamação 15,8%, cera 8,4%, conduta
antidesportiva não-física 4,8%, toque intencional de mão 0,9%.

Duas perguntas em aberto que esta tarefa responde:

1. A proporção de infrações não-físicas se mantém na Série A, ou é característica da Série B?
2. A taxonomia construída sobre 2022–2023 cobre bem os motivos redigidos em 2025 e 2026, ou
   há padrões textuais novos caindo em "não classificado"?

A segunda pergunta é operacional: uma taxonomia que degrada com o tempo compromete o produto,
porque a classificação alimenta tanto o relatório entregue ao cliente quanto a priorização.

## Definition of Done

- [ ] `categorize_card_reason` executada sobre toda a base com motivo disponível.
- [ ] **Taxa de não classificados** reportada por temporada e série; amostra dos textos não
      classificados inspecionada manualmente.
- [ ] Taxonomia ajustada se houver categoria relevante emergente, com registro do que mudou e
      por quê.
- [ ] Tabela consolidada de tipologia por temporada, série e categoria.
- [ ] Comparação Série A × Série B da proporção de infrações não-físicas, com teste
      estatístico da diferença.
- [ ] Figura de composição tipológica por série e temporada.
- [ ] Relatório 05 (`reports/analysis/05_*.md`) atualizado com o corpus ampliado.
- [ ] Testes unitários cobrindo as categorias novas ou alteradas.
- [ ] Suíte `pytest` passando.

## Riscos e observações

* Se a proporção de infrações não-físicas divergir bastante entre as séries, isso é achado e
  não problema — alimenta diretamente a discussão sobre onde o risco de integridade se
  concentra, e o argumento de que a Série B merece cobertura própria no produto.
