# Relatório Técnico 04: Complemento dos Scouts 2024 (Série A) e Piloto das Súmulas CBF (Série B)

**Data:** 2026-09-10  
**Autor:** Antigravity (Data Analysis Partner)  
**Objetivo:** Integrar os scouts da temporada 2024 da Série A via Sofascore para calcular a taxa de conversão faltas $\rightarrow$ cartões definitiva e estabelecer o pipeline automatizado de download e extração de Súmulas Eletrônicas da CBF para divisões de acesso (Série B).  
**Bases de Dados Atualizadas:**
* `data/processed/serie_a/estatisticas.parquet`: 17.570 scouts (2003–2024), agora com 756 registros válidos de 2024 preenchidos com faltas, escanteios e finalizações.
* `data/processed/serie_b/`: 20 partidas piloto, 86 cartões categorizados por motivo e 36 gols extraídos de PDFs oficiais da CBF.

---

## 1. Sumário Executivo

O **Passo 1** do projeto alcançou dois marcos analíticos fundamentais:

1. **Fechamento Definitivo da Série Temporal da Série A (2014–2024):**
   * A integração dos scouts de 2024 comprovou que o "paradoxo disciplinar" atingiu seu ápice histórico em 2024.
   * Enquanto a média de faltas por partida caiu para o menor nível de toda a história dos pontos corridos (**25,36 faltas por jogo**, contra 31,41 em 2017), a severidade disciplinar atingiu o **recorde histórico absoluto**, com uma taxa de conversão de **0,2198 cartões por falta** (quase 1 cartão a cada 4,5 faltas cometidas).
   * O ano de 2024 também consolidou o recorde de cartões vermelhos da liga (**128 expulsões**, 6,11% de todas as advertências).

2. **Fortalecimento do Efeito Dose-Resposta da Exposição a Bets (2019–2024):**
   * Com o ano de 2024 completo, a propensão de uma falta gerar cartão em jogos com **Exposição Total** (ambos os clubes com patrocínio de aposta) é de **0,1877**, contra **0,1603** em jogos **Sem Exposição**.
   * O teste de hipótese tornou-se ainda mais contundente: $t = 3,9207$, com $p = 1,30 \times 10^{-4}$ (rejeição de $H_0$ com nível de significância extremo).

3. **Arquitetura Oficial de Súmulas da CBF Estabelecida (Série B):**
   * Mapeamos os endpoints canônicos da CDN da CBF (`142` Série A, `242` Série B, `342` Série C, `542` Série D).
   * O parser nativo em Python (sem dependências externas) extraiu com 100% de sucesso as primeiras 20 partidas da Série B de 2022, permitindo categorizar os cartões pelo **texto literal do motivo** anotado pelo árbitro (faltas temerárias, reclamações, cera, conduta antidesportiva).

---

## 2. Série Histórica Consolidada da Disciplina na Série A (2014–2024)

Com a incorporação dos scouts de 2024 auditados do Sofascore, a tabela oficial da Série A consolida a seguinte trajetória:

| Temporada | Total Jogos | Cartões / Jogo | Faltas / Jogo | Taxa Cartão / Falta ($\tau_{\text{CF}}$) | Expulsões (Vermelhos) | Taxa Vermelhos (%) | Gols Pênalti |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2014** | 380 | 4,78 | — | — | 82 | 4,62% | 62 |
| **2015** | 380 | 5,34 | 29,19 | 0,1857 | 109 | 5,47% | 73 |
| **2016** | 379 | 4,91 | 31,22 | 0,1584 | 86 | 4,71% | 79 |
| **2017** | 380 | 5,05 | 31,41 | 0,1617 | 77 | 4,08% | 89 |
| **2018** | 380 | 5,18 | 31,11 | 0,1686 | 101 | 5,17% | 72 |
| **2019** | 380 | 4,74 | 27,57 | 0,1650 | 97 | 5,50% | 94 |
| **2020** | 380 | 4,78 | 31,22 | 0,1550 | 107 | 6,02% | 111 |
| **2021** | 380 | 4,79 | 29,92 | 0,1625 | 81 | 4,53% | 86 |
| **2022** | 380 | 5,28 | 26,88 | 0,1994 | 110 | 5,58% | 98 |
| **2023** | 380 | **5,59** | 28,67 | 0,1978 | 108 | 5,10% | 95 |
| **2024** | 380 | 5,53 | **25,36** | **0,2198** | **128** | **6,11%** | 76 |

---

## 3. Resultados do Piloto de Súmulas CBF (Série B)

Nas 20 partidas iniciais da Série B de 2022 processadas pelo novo parser:
* **Média de Cartões:** 4,30 cartões por partida.
* **Distribuição Temática dos Motivos dos Cartões:**
  1. *Falta Temerária / Disputa de Bola:* 45,3% (39 advertências)
  2. *Outros Motivos Gerais:* 30,2% (26 advertências)
  3. *Reclamação com Palavras / Gestos:* 10,5% (9 advertências)
  4. *Cera / Retardar o Reinício de Jogo:* 8,1% (7 advertências)
  5. *Conduta Antidesportiva / Discussões:* 4,7% (4 advertências)
  6. *Toque de Mão Deliberado:* 1,2% (1 advertência)

Essa categorização textual comprova que mais de **23% dos cartões aplicados decorrem de atitudes disciplinares e protelação de jogo** (reclamação, cera e conduta antidesportiva), e não de faltas físicas.

---

## 4. Garantia de Qualidade e Testes Automatizados

A suíte de testes unitários foi executada via `pytest`, registrando **20 testes aprovados com 100% de sucesso**:
* `tests/test_scouts_2024.py` (5 testes): Cobertura de 380 jogos, limites físicos de faltas e escanteios, integridade de chaves primárias e taxa de conversão.
* `tests/test_parse_cbf.py` (4 testes): Robustez do parser de PDFs da CBF, validação de categorias de infração e consistência dos datasets relacionais da Série B.
* `tests/test_clean_serie_a.py` (5 testes) e `tests/test_clean_betting.py` (6 testes): Garantia de não-regressão nas camadas anteriores.
