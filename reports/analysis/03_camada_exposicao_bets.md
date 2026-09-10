# Relatório Técnico 03: Camada de Exposição às Bets e Cruzamento com a Série A (MVP 2)

**Data:** 2026-09-06  
**Autor:** Antigravity (Data Analysis Partner)  
**Objetivo:** Mensurar a expansão da demanda e a penetração econômica dos patrocínios de apostas esportivas no futebol brasileiro (2015–2025) e avaliar sua associação empírica com métricas de integridade disciplinar na Série A.  
**Bases de Dados:**
* Google Trends Brasil (2015–2025): Séries mensal (132 registros) e anual (11 registros).
* Matriz Histórica de Patrocínios da Série A (2015–2024): 200 registros clube $\times$ temporada em 34 clubes distintos.
* Partidas Enriquecidas da Série A: 8.785 partidas (2003–2024) $\times$ 39 colunas em [`data/processed/serie_a/partidas_com_exposure.parquet`](file:///d:/Python%20Projetos/analise-bets/data/processed/serie_a/partidas_com_exposure.parquet).

---

## 1. Sumário Executivo

O MVP 2 concluiu a modelagem empírica da exposição do futebol brasileiro às casas de apostas, integrando com sucesso a dimensão macro (Google Trends) e micro (contratos de patrocínio clube a clube) aos dados esportivos da Série A.

Os principais achados estatísticos e econômicos são:

1. **Hiper-Expansão e Saturação dos Patrocínios na Elite (0% $\rightarrow$ 90%):**
   * Até 2018 (ano da Lei 13.756/2018), **nenhum clube** da Série A possuía patrocínio de apostas na camisa.
   * Em 2019, ano de entrada inicial, **45%** dos clubes fecharam acordos (20% com bet master).
   * Em 2024, atingiu-se a saturação com **90% dos clubes patrocinados** e **80% estampando bet master**, tornando o segmento o maior investidor individual do futebol nacional.
2. **Efeito Dose-Resposta Estatisticamente Robusto nos Cartões por Partida:**
   * No período contemporâneo (2019–2024), jogos entre equipes com **Exposição Total** (ambos os clubes com patrocínio de bet, $N=1.472$) registraram média de **5,209 cartões por partida**, contra **4,542 cartões** em jogos **Sem Exposição** ($N=142$).
   * A diferença de **+0,667 cartões/jogo (+14,68%)** é altamente significativa tanto no teste paramétrico ($t = 3,3091, p = 1,14 \times 10^{-3}$) quanto no não-paramétrico (Mann-Whitney $U = 118.952, p = 6,08 \times 10^{-3}$).
3. **Disparada na Taxa de Conversão de Faltas em Cartões:**
   * A propensão de uma falta cometida resultar em punição disciplinar é **+11,98% maior** em jogos de Exposição Total (0,1794 cartões/falta $\approx$ 1 a cada 5,5 faltas) comparada a jogos Sem Exposição (0,1602 cartões/falta $\approx$ 1 a cada 6,2 faltas), com significância estatística ($t = 2,6967, p = 7,73 \times 10^{-3}$).
4. **Ausência de Viés Intrajogo Estrutural Agregado:**
   * A proporção média de cartões no 1º tempo manteve-se estável entre as faixas de exposição (33,90% em Sem Exposição vs. 34,47% em Exposição Total, $p = 0,798$), evidenciando que anomalias de cartões precoces observadas na Série A concentram-se em atletas e partidas atípicas específicas (outliers), e não em um deslocamento da média global da liga.

---

## 2. Metodologia do Índice `BET_EXPOSURE`

O índice foi estruturado de forma aditiva e normalizada na escala contínua $[0.0, 1.0]$:

$$\text{BET\_EXPOSURE}_{\text{clube}, c, t} = 0,75 \cdot S_{\text{pos}} + 0,25 \cdot S_{\text{qtd}}$$
$$\text{BET\_EXPOSURE}_{\text{total}, c, t} = 0,60 \cdot S_{\text{pos}} + 0,15 \cdot S_{\text{qtd}} + 0,25 \cdot S_{\text{macro}, t}$$

Onde:
* $S_{\text{pos}} \in \{1,00 \text{ (Master)}, 0,50 \text{ (Mangas)}, 0,30 \text{ (Secundário)}, 0,00 \text{ (Nenhum)}\}$
* $S_{\text{qtd}} = \min(1,0, \; N_{\text{marcas}} / 2)$
* $S_{\text{macro}, t} = \text{Google Trends Anualizado}_t / 100$

Para partidas $i$:
$$\text{Exposure}_{\text{partida}, i} = \frac{\text{Exposure}_{\text{mandante}} + \text{Exposure}_{\text{visitante}}}{2}$$

---

## 3. Dinâmica Temporal do Mercado e Patrocínios (2015–2025)

Os dados anuais consolidados em [`reports/tables/tabela_04_metricas_mercado_bets_anual.csv`](file:///d:/Python%20Projetos/analise-bets/reports/tables/tabela_04_metricas_mercado_bets_anual.csv) documentam a evolução das fases de mercado:

| Temporada | Fase Regulatória | Google Trends Médio | % Clubes com Bet | % Clubes Bet Master | % Jogos Ambos com Bet | Índice Exposição Médio |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **2015** | Pré-Legalização | 2,44 | 0,0% | 0,0% | 0,0% | 0,000 |
| **2016** | Pré-Legalização | 2,33 | 0,0% | 0,0% | 0,0% | 0,000 |
| **2017** | Pré-Legalização | 3,35 | 0,0% | 0,0% | 0,0% | 0,000 |
| **2018** | Legalização / Expansão | 6,95 | 0,0% | 0,0% | 0,0% | 0,000 |
| **2019** | Legalização / Expansão | 14,24 | 45,0% | 20,0% | 18,9% | 0,270 |
| **2020** | Legalização / Expansão | 22,62 | 75,0% | 15,0% | 55,3% | 0,349 |
| **2021** | Legalização / Expansão | 41,91 | 85,0% | 50,0% | 71,6% | 0,575 |
| **2022** | Legalização / Expansão | 72,49 | 90,0% | 50,0% | 80,5% | 0,608 |
| **2023** | Regulamentação | 87,97 | 90,0% | 60,0% | 80,5% | 0,638 |
| **2024** | Regulamentação | 94,58 | 90,0% | **80,0%** | **80,5%** | **0,741** |
| **2025** | Mercado Regulado | 91,73 | — | — | — | — |

---

## 4. Testes de Hipótese e Efeito Dose-Resposta na Partida

Ao estratificar todas as partidas disputadas entre 2019 e 2024 ($N=2.280$) de acordo com a categoria de patrocínio das equipes em campo, observa-se uma progressão monotônica (*dose-response*):

| Categoria da Partida | Total Partidas | Cartões Média $\pm$ DP | Cartões 1T (%) | Faltas Média | Taxa Cartão / Falta |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Nenhuma (0 clubes com bet)** | 142 | 4,542 $\pm$ 2,271 | 33,90% | 26,11 | 0,1602 |
| **Parcial (1 clube com bet)** | 666 | 4,812 $\pm$ 2,337 | 34,17% | 29,05 | 0,1641 |
| **Total (2 clubes com bet)** | 1.472 | **5,209 $\pm$ 2,493** | 34,47% | 29,08 | **0,1794** |

### Testes Formais de Significância (Total vs. Nenhuma):
* **Cartões por Jogo:**
  * Teste $t$ de Welch: $t = 3,3091$, $p = 1,14 \times 10^{-3}$ (Rejeita $H_0$ com alta significância).
  * Mann-Whitney $U$: $U = 118.952,0$, $p = 6,08 \times 10^{-3}$.
* **Taxa de Conversão Faltas $\rightarrow$ Cartões:**
  * Teste $t$: $t = 2,6967$, $p = 7,73 \times 10^{-3}$ (Rejeita $H_0$ a $p < 0,01$).

> [!IMPORTANT]
> **Interpretação Cautelosa:**
> A associação positiva entre a presença de patrocinadores de apostas e o aumento no volume e na severidade disciplinar das partidas é estatisticamente inequívoca. Contudo, em conformidade com o princípio de governança do projeto, **não se conclui causalidade direta imediata**. Fatores como a evolução temporal coincidente (as partidas com Total Exposição concentram-se nos anos mais recentes de 2022–2024, quando diretrizes contra reclamações e acréscimos aumentaram a severidade geral) operam como variáveis de confusão que serão isoladas nos modelos de painel com efeitos fixos (MVP 6).

---

## 5. Ranking dos Clubes por Exposição Acumulada (2019–2024)

Conforme consolidado em [`reports/tables/tabela_06_top_clubes_exposicao_acumulada.csv`](file:///d:/Python%20Projetos/analise-bets/reports/tables/tabela_06_top_clubes_exposicao_acumulada.csv):

* **Clubes de Máxima Exposição Contratual (Média $\ge 0,80$):**
  * América-MG, Vasco da Gama, Goiás, Juventude e Chapecoense (clubes que mantiveram patrocínio master de apostas em 100% de suas participações na Série A).
* **Grandes Clubes com Adoção Precoce e Contínua (Média $0,60$ a $0,70$):**
  * Atlético-MG (Betano), São Paulo (Sportsbet.io / Superbet), Fluminense (Betano / Superbet), Fortaleza (NetBet / Novibet) e Bahia (Casa de Apostas / Esportes da Sorte).
* **Clubes Tradicionais Resistentes a Bets na Camisa:**
  * Palmeiras (manteve contrato exclusivo com Crefisa/FAM até o final de 2024, com exposição contratual direta igual a $0,00$).
  * Cuiabá (manteve patrocinador local tradicional Drebor).

---

## 6. Figuras Analíticas Geradas

As seguintes figuras em resolução 300 DPI estão disponíveis em [`reports/figures/eda_bets/`](file:///d:/Python%20Projetos/analise-bets/reports/figures/eda_bets/):

1. **`01_evolucao_google_trends_e_marcos.png`:** Curva temporal de buscas e marcos regulatórios (Lei 13.756/2018, Copa 2022, MP 1.182/2023, Vigência 2025).
2. **`02_penetracao_patrocinios_serie_a.png`:** Curva de adoção dos patrocínios master e secundários de 2015 a 2024.
3. **`03_distribuicao_bet_exposure_clubes.png`:** Boxplots contrastando a distribuição de `bet_exposure_clube` e `bet_exposure_total`.
4. **`04_associacao_exposicao_vs_cartoes_faltas.png`:** Painel quádruplo ilustrando a curva dose-resposta entre categoria de exposição da partida e indicadores de jogo.
5. **`05_heatmap_marcas_bets_clubes.png`:** Ranking de contratos-ano das marcas de apostas na Série A.

---

## 7. Próximos Passos (Transição para o MVP 3 / MVP 4)

Com a base histórica de futebol (MVP 1) e a camada de exposição a bets (MVP 2) plenamente operacionais e integradas:
1. **Coleta e Ingestão das Súmulas CBF:** Preenchimento de faltas da Série A em 2024 e extensão para Séries B, C e D.
2. **Modelagem Econométrica de Painel (MVP 6):** Estimar regressões em painel com efeitos fixos por clube e temporada controlando por rodada, arbitragem e variáveis táticas.
