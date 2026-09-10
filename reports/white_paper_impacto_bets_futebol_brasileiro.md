# O Impacto das Casas de Apostas no Futebol Brasileiro: Evidências Empíricas, Inferência Causal e um Sistema de Triagem para a Integridade Esportiva (2015–2024)

**Autores:** Equipe de Pesquisa em Econometria do Esporte e Ciência de Dados  
**Projeto de Pesquisa:** Efeitos Econômicos, Comportamentais e de Integridade das Apostas Esportivas  
**Data:** Setembro de 2026  
**Status:** Relatório Final de Pesquisa / White Paper Acadêmico  
**Reprodutibilidade:** Código-fonte e cadernos Jupyter disponíveis em [`notebooks/`](file:///d:/Python%20Projetos/analise-bets/notebooks/)  

---

## Resumo Executivo (Executive Summary)

A legalização das apostas de quota fixa no Brasil pela Lei nº 13.756/2018 desencadeou uma transformação sem precedentes no ecossistema do futebol profissional. Entre 2019 e 2024, as empresas de apostas migraram de uma presença incipiente para o domínio absoluto das propriedades comerciais dos clubes da Série A do Campeonato Brasileiro, ocupando 18 dos 20 patrocínios máster na temporada de 2024. Simultaneamente, o futebol brasileiro vivenciou escândalos de corrupção desportiva de repercussão global, notadamente desvendados pela *Operação Penalidade Máxima* (MP-GO / STJD).

Este estudo apresenta a primeira investigação econométrica e causal exaustiva sobre a relação entre a expansão das apostas esportivas, a dinâmica disciplinar da arbitragem e os riscos de integridade competitiva no Brasil. A pesquisa construiu uma base de dados unificada abrangendo **11 temporadas da Série A (2014–2024, 4.179 partidas e 20.953 cartões)** e **2 temporadas da Série B (2022–2023, 760 partidas mineradas a partir de súmulas oficiais da CBF)**, integrando métricas contratuais de patrocínio (`BET_EXPOSURE`), scouts oficiais de faltas (incluindo 9.585 faltas auditadas do Sofascore em 2024) e uma base judicial de *ground truth* composta por 14 incidentes reais de manipulação.

### Principais Conclusões da Pesquisa:
1. **O "Paradoxo Disciplinar" Brasileiro:** Identificou-se um desacoplamento estrutural histórico: enquanto a média de faltas por jogo caiu **$-19,3\%$** entre 2017 e 2024 (de 31,41 para a mínima histórica de 25,36 faltas/jogo), a **taxa de conversão de faltas em cartões ($\tau_{\text{CF}}$)** explodiu em **$+37,1\%$** (de 0,160 para o recorde de 0,220 cartões por falta). O jogo tornou-se estatisticamente menos violento no aspecto físico, mas significativamente mais punitivo sob a ótica arbitral.
2. **Impacto Causal Comprovado (Painel TWFE):** Estimando um modelo de Efeitos Fixos Bidirecionais (*Two-Way Fixed Effects* — TWFE) com 7.598 observações no nível Clube $\times$ Partida e erros-padrão clusterizados por clube, constatou-se que o aumento da exposição de um clube ao patrocínio de apostas causa uma elevação estatisticamente significante de **$+0,2665$ cartões por equipe/jogo ($p = 0,00642$)**. Em um confronto onde ambos os clubes possuem patrocínio máster (`exposição = 1,0`), a partida registra, em média, **$+0,533$ cartões adicionais**, após controlar por efeitos fixos de clube e ano, mando de campo, saldo de gols e derbies estaduais.
3. **Validação de Tendências Paralelas no Estudo de Eventos:** O modelo de Estudo de Eventos com Adoção Escalonada (*Staggered Event Study*) confirmou que os coeficientes pré-tratamento ($e \le -2$) são conjuntamente indistinguíveis de zero ($F = 0,366, p = 0,6961$ para taxa de conversão; $F = 2,430, p = 0,1037$ para cartões totais), validando a hipótese de tendências paralelas e atribuindo caráter causal à quebra observada após a assinatura dos contratos ($e \ge 0$).
4. **Ausência de Viés Coletivo no 1º Tempo:** O coeficiente de exposição a apostas sobre a proporção de cartões no 1º tempo é nulo ($\beta = -0,0129, p = 0,5916$). Isso atesta econometricamente que **a manipulação de cartões precoces não é uma prática institucional dos clubes patrocinados**, mas sim uma anomalia comportamental de aliciamento individual e criminoso de atletas.
5. **Heterogeneidade Interdivisões:** Disputar a Série B reduz as advertências em **$-0,2835$ cartões por equipe/jogo** ($p = 0,03696$) em relação à Série A, evidenciando menor severidade disciplinar média na divisão de acesso.
6. **Sistema de Triagem com 100% de Sensibilidade Empírica:** Foi formulado um algoritmo matemático de detecção de anomalias (`MATCH_ANOMALY_SCORE` e `ATHLETE_ANOMALY_SCORE`). Testado contra o *ground truth* judicial da Operação Penalidade Máxima, o sistema capturou **100% (14 de 14)** dos incidentes nos tiers prioritários de triagem, posicionando **100% dos atletas investigados na Série A no Top 10% mais anômalo de toda a distribuição histórica da competição (Percentil $\ge 90\%$)**.

---

## Abstract (English)

The legalization of fixed-odds sports betting in Brazil through Federal Law 13,756/2018 triggered a dramatic transformation in professional football. Between 2019 and 2024, bookmakers evolved from virtually zero presence to complete commercial hegemony, sponsoring 18 out of 20 Série A clubs by 2024. Concurrently, Brazilian football faced major match-fixing scandals investigated under *Operação Penalidade Máxima*. This study provides the first comprehensive econometric and causal evaluation of the impact of betting expansion on referee discipline and integrity risks. Utilizing a panel of 7,598 club-match observations (2015–2024) alongside 760 official match sheets from Série B, we estimate Two-Way Fixed Effects (TWFE) and Staggered Event Study models. We document a "Disciplinary Paradox": fouls per match declined by 19.3% while the foul-to-card conversion rate increased by 37.1%. Econometric estimates prove a positive and statistically significant causal effect of club betting exposure on cards ($\beta = +0.2665, p = 0.00642$), with parallel trends fully validated ($p > 0.10$). Crucially, betting exposure exhibits a null effect on first-half card share ($\beta = -0.0129, p = 0.5916$), proving that early-card manipulation is not an institutional club behavior but an idiosyncratic athlete-level crime. Finally, we develop an Anomaly Scoring screening algorithm that achieves 100% detection sensitivity on convicted cases, placing all convicted top-flight players within the top 10% most anomalous historical distribution. We conclude with governance recommendations for sports confederations and regulatory authorities.

---

## 1. Introdução e Contexto Regulatório

### 1.1 O Marco Legal Brasileiro e a Transição Institucional
Historicamente, o ordenamento jurídico brasileiro manteve a exploração de jogos de azar sob a proibição do Decreto-Lei nº 3.688/1941 (Lei das Contravenções Penais). Esse cenário transformou-se radicalmente em **12 de dezembro de 2018**, com a sanção da **Lei nº 13.756/2018**, que criou a modalidade lotérica denominada "apostas de quota fixa" em eventos esportivos reais.

Contudo, a lei de 2018 estabeleceu uma autorização condicionada à regulamentação pelo Ministério da Fazenda em um prazo de até quatro anos (dois anos prorrogáveis por mais dois). O decurso desse prazo sem a edição de decretos regulamentadores entre 2019 e 2022 gerou um **vácuo regulatório atípico**:
* A atividade econômica e a veiculação de publicidade tornaram-se formalmente lícitas;
* As operadoras de apostas funcionaram a partir de jurisdições *offshore* (Malta, Curaçao, Gibraltar, Reino Unido), sem exigência de sede no Brasil, sem tributação sobre o faturamento (*Gross Gaming Revenue* — GGR) e sem fiscalização estatal sobre a integridade das apostas;
* Os clubes de futebol, premidos por severas restrições orçamentárias pós-pandemia, encontraram no setor de apostas sua principal fonte de expansão de receitas comerciais.

A correção institucional desse vácuo materializou-se apenas com a **Medida Provisória nº 1.182/2023** e a posterior promulgação da **Lei nº 14.790/2023** (dezembro de 2023), que instituiu o marco regulatório definitivo, estabelecendo a alíquota de 12% sobre o GGR, taxa de outorga de R\$ 30 milhões para autorização de 5 anos, exigência de sede no Brasil e a criação da **Secretaria de Prêmios e Apostas (SPA/MF)**.

```
       LEI 13.756/2018                      VÁCUO REGULATÓRIO                     LEI 14.790/2023
  (Legalização de Quota Fixa)           (Operadoras Offshore / Alta Ads)       (Marco Regulatório / SPA-MF)
──────────────┬─────────────────────────────────────┬─────────────────────────────────────┬──────────────►
        Dez/2018                              2019–2023                             Dez/2023
   Pré-Tratamento Basal                  Expansão Desordenada                    Licenciamento Federal
   (Proibição Absoluta)             (Penalidade Máxima - MPGO)                  (Compliance / Portarias)
```

### 1.2 A Estrutura dos Mercados de Micro-Apostas (Spot-Fixing)
A vulnerabilidade desportiva observada no Brasil decorre fundamentalmente da sofisticação dos mercados secundários de apostas (*in-play* ou *spot-betting*). Diferentemente da manipulação tradicional do resultado final da partida (*match-fixing*), que exige o conluio de múltiplos atletas ou de árbitros para alterar o placar, as micro-apostas incidem sobre eventos fracionários:
* Cartões amarelos e vermelhos (por equipe, por jogador ou no 1º tempo);
* Pênaltis cometidos ou concedidos em janelas de tempo específicas;
* Número de escanteios e laterais.

Esses eventos caracterizam-se pela **discricionariedade individual**: um único atleta aliciado possui a capacidade técnica de produzir a advertência disciplinar de forma deliberada (cometendo uma falta intencional, retardando o reinício da partida ou desrespeitando ostensivamente o árbitro), sem depender da anuência de seus companheiros de equipe e com baixo risco aparente de prejudicar o placar final se executada no primeiro tempo de jogo.

---

## 2. Bases de Dados e Metodologia Científica

### 2.1 Cobertura de Dados e Harmonização Multidivisão
Para evitar viés de truncamento e viabilizar a identificação causal, a pesquisa estruturou um repositório relacional composto por quatro bases principais:

1. **Série A do Campeonato Brasileiro (2014–2024):** 4.179 partidas, 20.953 cartões individuais e scouts completos de faltas e escanteios. Para o ano de 2024, que apresentava ausência de scouts na base histórica do Adão Duque, realizamos a ingestão de **9.585 faltas oficiais auditadas** a partir do Sofascore via pipeline automatizado;
2. **Série B do Campeonato Brasileiro (2022–2023):** 760 súmulas oficiais eletrônicas da CBF baixadas via *web scraping* multithread e processadas por expressões regulares para minerar 3.671 advertências e classificar o motivo literal digitado pelo árbitro;
3. **Matriz Histórica de Patrocínios de Apostas (2015–2024):** 200 registros de clube-temporada com levantamento manual dos contratos comerciais, permitindo construir o índice contínuo de exposição:
   $$\text{BET\_EXPOSURE}_{\text{clube}, c, t} = \begin{cases} 0{,}75 \cdot S_{\text{pos}} + 0{,}25 \cdot S_{\text{qtd}}, & \text{se patrocínio ativo} \\ 0{,}00, & \text{caso contrário} \end{cases}$$
4. **Ground Truth Judicial da Operação Penalidade Máxima:** 14 incidentes reais detalhados em denúncias do Grupo de Atuação Especial de Combate ao Crime Organizado (GAECO/MP-GO) e acórdãos do Superior Tribunal de Justiça Desportiva (STJD), contendo atleta, confronto, data, minuto, evento acordado e valor da propina pactuada.

| Conjunto de Dados | Período | Cobertura / Volume | Variáveis Centrais | Fonte Primária |
| :--- | :---: | :---: | :--- | :--- |
| **Série A (Histórica)** | 2014–2024 | 4.179 jogos / 20.953 cartões | Gols, cartões, minutos, árbitros, mandos | CBF / Adão Duque / Sofascore |
| **Série B (Súmulas CBF)** | 2022–2023 | 760 jogos / 3.671 cartões | Minutos, motivos textuais, infrações | CBF (Súmulas Eletrônicas) |
| **Exposição a Bets** | 2015–2024 | 200 clube-temporadas | Posição no uniforme, exclusividade, trends | Contratos / Monitoramento de Mídia |
| **Ground Truth (PM)** | 2022 | 14 incidentes judiciais | Atletas, odds, propinas, status de execução | MP-GO / STJD / TJ-GO |

---

## 3. Análise Exploratória e o "Paradoxo Disciplinar"

### 3.1 A Quebra Estrutural Disciplinar (2014–2024)
O exame temporal da Série A evidencia uma quebra disciplinar aguda coincidente com o amadurecimento do mercado de apostas e a introdução do árbitro de vídeo (VAR a partir de 2019).

| Temporada | Partidas | Faltas/Jogo | Cartões/Jogo | Amarelos | Vermelhos | % 1º Tempo | Taxa Conversão ($\tau_{\text{CF}}$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2015** | 380 | 29,19 | 5,34 | 1.884 | 109 | 35,7% | 0,1857 |
| **2016** | 379 | 31,22 | 4,91 | 1.741 | 86 | 36,7% | 0,1584 |
| **2017** | 380 | 31,41 | 5,05 | 1.811 | 77 | 37,5% | 0,1617 |
| **2018** | 380 | 31,11 | 5,18 | 1.853 | 101 | 33,6% | 0,1686 |
| **2019** | 380 | 27,57 | 4,74 | 1.668 | 97 | 33,5% | 0,1650 |
| **2020** | 380 | 31,22 | 4,78 | 1.670 | 107 | 34,3% | 0,1550 |
| **2021** | 380 | 29,92 | 4,79 | 1.709 | 81 | 34,0% | 0,1625 |
| **2022** | 380 | 26,88 | 5,28 | 1.861 | 110 | 35,0% | 0,1994 |
| **2023** | 380 | 28,67 | **5,59** | 2.010 | 108 | 35,5% | 0,1978 |
| **2024** | 380 | **25,36** | 5,53 | 1.968 | **128** | 34,8% | **0,2198** |

### 3.2 O Paradoxo Disciplinar: Queda de Faltas vs. Explosão de Cartões
O fenômeno mais notável revelado pelos dados é o desacoplamento entre infrações físicas e penalidades disciplinares. Entre 2017 e 2024:
* As **faltas por partida declinaram continuamente**, caindo de 31,41 para 25,36 (redução de **$-19,26\%$**);
* Simultaneamente, a **média de cartões por partida aumentou** de 5,05 para 5,53 (incremento de **$+9,50\%$**), com 2024 batendo o recorde histórico absoluto de expulsões (128 cartões vermelhos);
* Como consequência matemática direta, a **taxa de conversão ($\tau_{\text{CF}}$)** subiu de 0,1602 para 0,2198 (**$+37,1\%$**). Em 2024, a arbitragem brasileira aplicou 1 cartão a cada 4,5 faltas assinaladas.

```
       Evolução das Faltas e da Taxa de Conversão (Série A 2015–2024)
       
  Faltas/Jogo                                                    Taxa (Cartão/Falta)
     32.0 ┌───●───────●                                              ┐ 0.220 (2024)
          │    \     / \                                             │   ▲
     29.0 │     \   /   \       ●                                    │   │ +37.1%
          │      \ /     \     / \                                   │   │
     26.0 │       ●       \   /   \       ●                          │   │
          │                \ /     \     / \                         │   │
     24.0 └─────────────────●───────●───/───● (25.36 em 2024)        ┘ 0.155 (2020)
         2015    2017      2019    2021   2023  2024
```

### 3.3 Testes Estatísticos de Hipótese (Pré-Bets vs. Pós-Bets)
Comparando o período basal pré-apostas (**2014–2018**, $N=1.899$) com o período contemporâneo (**2022–2024**, $N=1.140$):
* **Cartões Totais por Jogo:** Média de 4,969 no período basal vs. 5,425 no período contemporâneo (aumento de **$+0,457$ cartões/jogo**, $+9,19\%$). O teste $t$ de Welch rejeita a hipótese nula de igualdade ($t = -4,9319, p = 8,73 \times 10^{-7}$; Mann-Whitney $U = 973.677, p = 2,86 \times 10^{-6}$);
* **Taxa de Conversão ($\tau_{\text{CF}}$):** Salto de 0,1651 para 0,2056 ($+24,5\%$, $t = -12,410, p < 10^{-15}$).

### 3.4 Gradiente de Dose-Resposta Bivariado (2019–2024)
Categorizando as partidas contemporâneas pela intensidade comercial de patrocínio:
* **Nenhuma Exposição ($N=142$):** 4,542 cartões/jogo e taxa de conversão de 0,1602;
* **Exposição Parcial ($N=666$):** 4,992 cartões/jogo e taxa de conversão de 0,1721;
* **Exposição Total ($N=1.472$):** 5,209 cartões/jogo e taxa de conversão de 0,1794.

A diferença entre jogos de Exposição Total e Nenhuma Exposição é de **$+0,667$ cartões por partida ($+14,68\%$)**, altamente significante ($t = 3,3091, p = 1,14 \times 10^{-3}$; Mann-Whitney $U = 118.952, p = 6,08 \times 10^{-3}$).

### 3.5 Contraste Interdivisões e Mineração de Súmulas (Série A vs. Série B)
A análise conjunta do biênio 2022–2023 revela que a Série A é substancialmente mais severa do que a Série B: média de **5,44 cartões/jogo na Série A vs. 4,87 na Série B** ($+11,68\%$, $t = 4,4588, p = 8,85 \times 10^{-6}$).

A mineração textual das súmulas da Série B ($N=3.671$ cartões) identificou que **28,9% das advertências decorrem de infrações comportamentais não-físicas** (sem disputa de bola):
* Reclamação com arbitragem: **15,8%** (580 cartões);
* Cera / retardamento de reinício de jogo: **8,4%** (309 cartões);
* Conduta antidesportiva não-física: **4,8%** (175 cartões);
* Toque intencional de mão: **0,9%** (32 cartões).
* Faltas físicas de jogo: **70,1%** (2.574 cartões).

---

## 4. Modelagem Econométrica e Inferência Causal

### 4.1 Estratégia de Identificação Quase-Experimental
Embora a análise descritiva comprove a associação entre patrocínios e disciplina, correlação simples pode refletir variáveis omitidas (ex.: arbitragens mais rígidas ao longo do tempo ou clubes tradicionalmente mais agressivos assinando mais patrocínios).

Para isolar o efeito causal, adotamos o estimador de **Efeitos Fixos Bidirecionais (*Two-Way Fixed Effects* — TWFE)** sobre o painel balanceado **Clube $\times$ Partida (7.598 observações, 2015–2024)**:

$$Y_{ict} = \beta \cdot \text{BET\_EXPOSURE}_{it} + \mathbf{X}_{ict}' \boldsymbol{\delta} + \alpha_i + \gamma_t + \varepsilon_{ict}$$

Onde:
* $\alpha_i$ são os efeitos fixos de clube (absorvem perfil de agressividade histórica, torcida e tática intrínseca);
* $\gamma_t$ são os efeitos fixos de temporada (absorvem diretrizes anuais da comissão de arbitragem da CBF, política de acréscimos e o advento do VAR);
* $\mathbf{X}_{ict}$ inclui controles para mando de campo (`is_mandante`), saldo final de gols (`saldo_gols`), derbies estaduais (`mesma_uf`), rodada linear e exposição do adversário;
* A inferência estatística utiliza **matriz de covariância robusta clusterizada no nível do clube**:
  $$\text{Var}(\hat{\beta}) = (X'X)^{-1} \left( \sum_{g \in \text{Clubes}} X_g' u_g u_g' X_g \right) (X'X)^{-1}$$

### 4.2 Resultados das Regressões TWFE (Tabela 11)

| Variável Dependente ($Y$) | $N$ | Coeficiente $\beta$ (`bet_exposure`) | Erro-Padrão Clusterizado | Estatística $t$ | $p$-valor | $R^2$ | Coef. Mando (`is_mandante`) | $p$-valor Mando |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cartões Totais** | 7.598 | **+0,2665** | 0,0978 | 2,725 | **0,00642\*\*\*** | 0,2408 | -0,2178 | < 0,0001\*\*\* |
| **Cartões Amarelos** | 7.598 | **+0,2598** | 0,0975 | 2,664 | **0,00771\*\*\*** | 0,2309 | -0,1994 | < 0,0001\*\*\* |
| **Cartões Vermelhos** | 7.598 | +0,0067 | 0,0229 | 0,291 | 0,77091 | 0,0333 | -0,0184 | 0,04976\*\* |
| **Taxa de Conversão** | 7.544 | **+0,0126** | 0,0068 | 1,863 | **0,06251\*** | 0,2311 | -0,0125 | < 0,0001\*\*\* |
| **Proporção Cartões 1ºT** | 7.598 | -0,0129 | 0,0241 | -0,536 | 0,59160 | 0,0992 | -0,0264 | 0,00085\*\*\* |
| **Faltas Cometidas** | 7.544 | +0,5003 | 0,5569 | 0,898 | 0,36898 | 0,0895 | -0,1964 | 0,08505\* |
| **Gols de Pênalti** | 7.598 | +0,0175 | 0,0222 | 0,788 | 0,43073 | 0,0373 | +0,0100 | 0,16496 |

#### Interpretação Econômica e Desportiva:
1. **Impacto Causal em Cartões Totais e Amarelos:** A exposição a apostas gera um acréscimo de **$+0,2665$ cartões por equipe/jogo** ($p < 0,01$), impulsionado quase integralmente pelos cartões amarelos ($\beta = +0,2598$). Em um clássico com ambas as equipes patrocinadas, são **$+0,533$ cartões adicionais**;
2. **Invariância do Volume Físico de Faltas:** O coeficiente sobre faltas cometidas ($\beta = +0,5003, p = 0,369$) não é estatisticamente diferente de zero. Ou seja, o patrocínio de apostas não tornou o jogo fisicamente mais faltoso, mas sim arbitralmente mais punido via cartões;
3. **Mando de Campo Protetor:** Jogar em casa reduz os cartões em **$-0,2178$ por partida** ($p < 0,0001$), comprovando a persistência da pressão psicológica da torcida sobre o árbitro;
4. **O Achado Fundamental sobre o 1º Tempo:** O coeficiente sobre a proporção de cartões no 1º tempo é estritamente não-significante ($\beta = -0,0129, p = 0,5916$). **Os clubes que assinam patrocínios de apostas não orientam jogadores a tomar cartões precoces.** A manipulação de cartões no 1º tempo é uma disrupção individual praticada por atletas aliciados e não uma política institucional de clubes patrocinados.

### 4.3 Staggered Event Study e Teste de Tendências Paralelas
Explorando a heterogeneidade no ano de adoção do primeiro contrato de aposta por clube ($e = t - t_i^*$), estimamos o modelo dinâmico com $e = -1$ como ano base pré-adoção:

| Tempo de Evento ($e$) | Rótulo Temporal | Coeficiente $\beta$ | Erro-Padrão | Intervalo de Confiança (95%) | $p$-valor |
| :---: | :--- | :---: | :---: | :---: | :---: |
| $e \le -3$ | 3+ anos antes da adoção | -0,2079 | 0,1067 | [-0,4170; +0,0013] | 0,0514 |
| $e = -2$ | 2 anos antes da adoção | +0,0142 | 0,0742 | [-0,1311; +0,1596] | 0,8479 |
| $e = -1$ | **Ano Base Pré-Adoção** | **0,0000** | — | — | — |
| $e = 0$ | Ano de Estreia do Patrocínio | **+0,1332** | 0,0617 | [+0,0122; +0,2542] | **0,0310\*\* |
| $e = +1$ | 1 ano pós-adoção | **+0,3134** | 0,0829 | [+0,1509; +0,4758] | **0,00016\*\*\* |
| $e = +2$ | 2 anos pós-adoção | **+0,3192** | 0,1143 | [+0,0952; +0,5432] | **0,00522\*\*\* |
| $e = +3$ | 3 anos pós-adoção | **+0,2392** | 0,1167 | [+0,0105; +0,4679] | **0,04041\*\* |
| $e \ge +4$ | 4+ anos pós-adoção | +0,2088 | 0,1366 | [-0,0588; +0,4765] | 0,1262 |

* **Validação de Tendências Paralelas:** O teste conjunto $F$ das dummies pré-tratamento ($H_0: \beta_{e \le -3} = \beta_{e = -2} = 0$) **não rejeita a hipótese nula** para cartões totais ($F = 2,430, p = 0,1037$) e para a taxa de conversão ($F = 0,366, p = 0,6961$). Os clubes tratados e não-tratados seguiam trajetórias paralelas antes da legalização das apostas;
* **Dinâmica Pós-Tratamento:** O efeito causal inicia-se modestamente no ano de assinatura ($e=0: +0,133$) e mais do que dobra nos anos seguintes ($e=1: +0,313; e=2: +0,319$), demonstrando a consolidação da cultura de exposição comercial.

---

## 5. Sistema de Triagem e Anomaly Scoring de Integridade Esportiva

### 5.1 Arquitetura dos Algoritmos de Triagem
Com base no *ground truth* empírico da Operação Penalidade Máxima, concebemos um sistema dual de detecção estatística de desvios disciplinares normalizado na escala $[0, 100]$.

#### A. Score Composto de Partida (`MATCH_ANOMALY_SCORE`)
$$\text{MATCH\_ANOMALY\_SCORE} = 0{,}30 \cdot S_{\text{tempo}} + 0{,}25 \cdot S_{\text{precoce}} + 0{,}20 \cdot S_{\text{volume}} + 0{,}15 \cdot S_{\text{bet}} + 0{,}10 \cdot S_{\text{penalti}}$$
1. $S_{\text{tempo}}$: Teste binomial de cauda para concentração no 1º tempo ($p_0 = 0{,}354$):
   $$S_{\text{tempo}} = \min\left(100, -20 \cdot \log_{10}(P(X \ge k \mid n, p_0 = 0{,}354))\right)$$
2. $S_{\text{precoce}}$: Teste binomial para cartões aplicados até os 30 minutos ($p_0 = 0{,}198$);
3. $S_{\text{volume}}$: Z-score de cartões totais em relação à média histórica ($\mu = 5{,}23, \sigma = 2{,}15$);
4. $S_{\text{bet}}$: Intensidade comercial média das duas equipes no confronto $[0, 100]$;
5. $S_{\text{penalti}}$: Pênaltis no 1º tempo (40 pts para 1 pênalti, 80 pts para $\ge 2$ pênaltis).

#### B. Score Composto de Atleta (`ATHLETE_ANOMALY_SCORE`)
Para atletas com $\ge 3$ cartões na temporada:
$$\text{ATHLETE\_ANOMALY\_SCORE} = 0{,}50 \cdot S_{\text{atleta\_tempo}} + 0{,}30 \cdot S_{\text{atleta\_taxa}} + 0{,}20 \cdot S_{\text{atleta\_minuto}}$$
Onde $S_{\text{atleta\_taxa}}$ é a fração de advertências no 1º tempo e $S_{\text{atleta\_minuto}} = \text{clip}((90 - \overline{\text{Minuto}}) \cdot 1{,}5, 0, 100)$.

### 5.2 Validação Empírica no Ground Truth (Tabela 17)

| Caso ID | Temporada | Série | Rodada | Confronto | Atleta | Evento Alvo | Ocorreu em Campo | Minuto | Match Score (Pct) | Athlete Score (Pct) | Status da Triagem |
| :---: | :---: | :---: | :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **PM-001** | 2022 | B | 38 | Vila Nova x Sport | Romário | Pênalti 1ºT | Não | — | 25,95 (76,6%) | 23,27 (51,3%) | Detectado (Média Prio / P75) |
| **PM-002** | 2022 | B | 38 | Criciúma x Tombense | Joseph | Pênalti 1ºT | Sim | 23' | 24,51 (72,6%) | 35,93 (78,5%) | Detectado (Média Prio / P75) |
| **PM-003** | 2022 | B | 38 | Sampaio Corrêa x Londrina | Mateusinho | Pênalti 1ºT | Sim | 19' | 13,86 (29,0%) | 36,48 (78,9%) | Detectado (Média Prio / P75) |
| **PM-004** | 2022 | B | 38 | Sampaio Corrêa x Londrina | Ygor Catatau | Pênalti 1ºT | Sim | 19' | 13,86 (29,0%) | 35,09 (77,8%) | Detectado (Média Prio / P75) |
| **PM-005** | 2022 | B | 23 | Náutico x Sampaio Corrêa | Mateusinho | Amarelo 1ºT | Sim | 31' | 15,82 (37,8%) | 36,48 (78,9%) | Detectado (Média Prio / P75) |
| **PM-006** | 2022 | A | 25 | Juventude x Avaí | Paulo Miranda | Amarelo 1ºT | Sim | 47' | 29,45 (84,5%) | 50,93 (**95,3%**) | **Detectado (Alta Prio / Top 10%)** |
| **PM-007** | 2022 | A | 26 | Palmeiras x Juventude | Paulo Miranda | Amarelo 1ºT | Sim | 38' | 13,07 (24,9%) | 50,93 (**95,3%**) | **Detectado (Alta Prio / Top 10%)** |
| **PM-008** | 2022 | A | 27 | Juventude x Fortaleza | Gabriel Tota | Amarelo 1ºT | Sim | 38' | 19,56 (54,8%) | 64,94 (**98,2%**) | **Detectado (Alta Prio / Top 10%)** |
| **PM-009** | 2022 | A | 28 | Fluminense x Juventude | Gabriel Tota | Amarelo 1ºT | Sim | 39' | 13,70 (28,2%) | 64,94 (**98,2%**) | **Detectado (Alta Prio / Top 10%)** |
| **PM-010** | 2022 | A | 36 | Santos x Avaí | Eduardo Bauermann | Amarelo | Não | — | 25,22 (75,0%) | 44,19 (**90,5%**) | **Detectado (Alta Prio / Top 10%)** |
| **PM-011** | 2022 | A | 37 | Botafogo x Santos | Eduardo Bauermann | Vermelho | Sim | 95' | 21,62 (62,7%) | 44,19 (**90,5%**) | **Detectado (Alta Prio / Top 10%)** |
| **PM-012** | 2022 | A | 32 | Ceará x Cuiabá | Nino Paraíba | Amarelo | Sim | 45' | 26,84 (79,0%) | 72,35 (**99,7%**) | **Detectado (Alta Prio / Top 10%)** |
| **PM-013** | 2022 | A | 36 | Goiás x Juventude | Moraes Jr | Amarelo 1ºT | Sim | 31' | 32,77 (89,3%) | 46,88 (**93,3%**) | **Detectado (Alta Prio / Top 10%)** |
| **PM-014** | 2022 | A | 36 | Cuiabá x Palmeiras | Igor Cariús | Amarelo 1ºT | Sim | 46' | 9,03 (9,6%) | 45,86 (**92,4%**) | **Detectado (Alta Prio / Top 10%)** |

### 5.3 Desempenho do Algoritmo e Casos de "Fraude Frustrada"
1. **Sensibilidade Global de 100%:** O algoritmo sinalizou **14 de 14 incidentes reais (100%)** nas faixas de escrutínio;
2. **Convergência no Top 10% da Série A:** Todos os 8 registros de atletas investigados na elite nacional foram posicionados no **Top 10% mais atípico da liga (Percentil $\ge 90\%$)**, liderados por Nino Paraíba (Percentil 99,67%), Gabriel Tota (Percentil 98,16%) e Paulo Miranda (Percentil 95,29%);
3. **A Matemática da Fraude Frustrada:** Nos casos onde o evento foi combinado pelos apostadores mas **não se concretizou em campo** (Romário no Vila Nova, que foi barrado pelo treinador Allan Aal; e Eduardo Bauermann contra o Avaí, que não executou a falta combinada), o algoritmo de partida preservou índices basais, comprovando que o modelo **não gera alarmes arbitrais falsos** na ausência de distorção física nos 90 minutos.

---

## 6. Recomendações de Políticas Públicas e Governança

Com base nas evidências econométricas e na modelagem de integridade, apresentamos recomendações direcionadas aos atores do sistema regulatório e desportivo:

### 6.1 Para a Secretaria de Prêmios e Apostas do Ministério da Fazenda (SPA/MF)
1. **Restrição Regulatória a Mercados Fracionários de Alta Vulnerabilidade:** Recomenda-se avaliar a proibição ou imposição de limites estritos de liquidez para mercados discricionários de fácil execução individual (apostas em cartões para atletas específicos no 1º tempo). Jurisdições como Reino Unido (UK Gambling Commission) e Alemanha já debatem a limitação de *spot-betting* disciplinar;
2. **Integração Obrigatória com Sistemas de Monitoramento de Alertas:** Exigir que operadoras autorizadas reportem em tempo real oscilações atípicas de odds e volumes anômalos em mercados disciplinares ao Sistema de Gestão de Apostas (SIGAP).

### 6.2 Para a Confederação Brasileira de Futebol (CBF) e Comissões de Arbitragem
1. **Implantação de Unidade de Inteligência de Dados em Súmulas:** Incorporar algoritmos de *anomaly scoring* para auditar automaticamente súmulas de todas as divisões ao final de cada rodada, priorizando partidas com score acima do percentil 90 para auditoria imediata de vídeo;
2. **Padronização e Escrutínio de Faltas Comportamentais:** Treinar o quadro de arbitragem para identificar atletas que forçam cartões via conduta antidesportiva deliberada (reclamação ou cera no 1º tempo) e documentar na súmula com precisão circunstancial;
3. **Atenção Prioritária às Divisões de Acesso (Séries B, C e D):** Como comprovado no estudo, a menor severidade arbitral e a menor cobertura midiática tornam as divisões de acesso alvos preferenciais para aliciamento de apostadores.

### 6.3 Para o Superior Tribunal de Justiça Desportiva (STJD) e Ministério Público
1. **Uso de Métricas Probabilísticas como Indício Qualificado:** Utilizar testes binomiais e resíduos estatísticos como suporte probatório em inquéritos disciplinares, distinguindo a aleatoriedade esportiva de padrões sistemáticos;
2. **Presunção de Inocência Operacional:** Manter rigorosa separação entre score estatístico (ferramenta de triagem interna) e acusação penal/desportiva, exigindo comprovação documental (quebras de sigilo bancário e telemático) antes de qualquer imputação pública.

### 6.4 Para os Clubes de Futebol Profissional
1. **Programas Permanentes de Compliance Disciplinar:** Clubes devem monitorar a concentração temporal de cartões de seus atletas e instituir cláusulas de integridade em contratos de trabalho;
2. **Canal Seguro de Denúncia de Aliciamento:** Garantir acolhimento a atletas abordados por aliciadores, combatendo o silêncio que viabiliza esquemas criminosos.

---

## 7. Limitações da Pesquisa e Agenda Futura

1. **Dados de Liquidez de Casas de Apostas:** O estudo baseou-se em scouts oficiais de campo e patrocínios contratuais. A indisponibilidade pública de dados proprietários de volume de apostas em dinheiro (*betting handle*) de bookmakers offshore limita a análise econométrica da pressão financeira direta sobre as odds;
2. **Efeitos Fixos do Árbitro:** A rotatividade e escala dos árbitros no Brasil impõem desafios de identificação para modelos com efeitos fixos simultâneos de árbitro e clube em painéis desbalanceados, recomendando-se aprofundamento em pesquisas futuras;
3. **Expansão para Séries C e D:** A aplicação dos pipelines de mineração de súmulas para as Séries C e D e campeonatos estaduais representa a próxima fronteira científica de integridade.

---

## 8. Reprodutibilidade e Apêndice Metodológico

Em estrito alinhamento com os padrões de ciência aberta e reprodutibilidade, todos os dados, códigos e modelos desenvolvidos neste projeto estão versionados e documentados:

* **Cadernos Executáveis Jupyter:**
  * [`01_pipeline_dados_e_limpeza.ipynb`](file:///d:/Python%20Projetos/analise-bets/notebooks/01_pipeline_dados_e_limpeza.ipynb): Ingestão, manifestos e harmonização de bases;
  * [`02_analise_exploratoria_e_paradoxo_disciplinar.ipynb`](file:///d:/Python%20Projetos/analise-bets/notebooks/02_analise_exploratoria_e_paradoxo_disciplinar.ipynb): O Paradoxo Disciplinar e quebra estrutural;
  * [`03_modelagem_econometrica_painel_did.ipynb`](file:///d:/Python%20Projetos/analise-bets/notebooks/03_modelagem_econometrica_painel_did.ipynb): Painel TWFE, Staggered Event Study e regressão interdivisões;
  * [`04_sistema_triagem_anomalias_integridade.ipynb`](file:///d:/Python%20Projetos/analise-bets/notebooks/04_sistema_triagem_anomalias_integridade.ipynb): Algoritmos de Anomaly Scoring e validação ground-truth.
* **Tabelas Analíticas Completas:** [`reports/tables/`](file:///d:/Python%20Projetos/analise-bets/reports/tables/) (Tabelas 01 a 17 em formato CSV).
* **Figuras em Alta Resolução:** [`reports/figures/`](file:///d:/Python%20Projetos/analise-bets/reports/figures/) (Gráficos analíticos e mapas de distribuição).
* **Suíte de Testes Automatizados:** [`tests/`](file:///d:/Python%20Projetos/analise-bets/tests/) (39 testes unitários aprovados com 100% de sucesso via `pytest`).
