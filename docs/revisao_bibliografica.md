# Revisão Bibliográfica e Fundamentação Teórica

**Projeto:** Impacto das Apostas Esportivas no Futebol Brasileiro (2015–2024)  
**Documento de Governança Acadêmica:** `docs/revisao_bibliografica.md`  
**Última Atualização:** 2026-09-11  

---

## 1. Visão Geral e Estrutura da Fundamentação

Para fundamentar as análises estatísticas, a modelagem econométrica causal (TWFE / *Staggered Event Study*) e o algoritmo de triagem de integridade (*Anomaly Scoring*) desenvolvidos no projeto, realizou-se uma revisão sistemática da literatura acadêmica e institucional.

A fundamentação teórica organiza-se em **seis eixos epistemológicos**:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           EIXOS DA FUNDAMENTAÇÃO TEÓRICA                         │
├────────────────────────────────────────┬─────────────────────────────────────────┤
│ 1. ECONOMETRIA FORENSE NO ESPORTE      │ 2. MICRO-APOSTAS E SPOT-FIXING          │
│ • Detecção estatística de fraude       │ • Assimetria de incentivos individuais  │
│ • Desvios comportamentais e incentivos │ • Vulnerabilidade de cartões e escanteios│
├────────────────────────────────────────┼─────────────────────────────────────────┤
│ 3. ECONOMIA E PATROCÍNIO DE BETS       │ 4. MARCO REGULATÓRIO & GOVERNANÇA       │
│ • Dependência orçamentária dos clubes  │ • Transição institucional brasileira    │
│ • Saturação comercial de uniformes     │ • Diretrizes globais (Macolin / UNODC)  │
├────────────────────────────────────────┼─────────────────────────────────────────┤
│ 5. PRESSÃO ARBITRAL E O JOGO           │ 6. INFERÊNCIA CAUSAL E EVENT STUDY      │
│ • "Paradoxo Disciplinar" e critérios   │ • Tendências paralelas e TWFE           │
│ • Sensibilidade punitiva dos árbitros  │ • Variância no tempo de adoção          │
└────────────────────────────────────────┴─────────────────────────────────────────┘
```

---

## 2. Eixo 1: Econometria Forense e Detecção Estatística de Fraude no Esporte

A identificação de manipulações esportivas por meio de dados observacionais apoia-se no campo da **Econometria Forense** (*Forensic Economics*), que utiliza desvios de distribuições teóricas esperadas para identificar comportamentos estratégicos ou ilícitos.

### Artigos de Referência

1. **DUGGAN, Mark; LEVITT, Steven D. (2002). "Winning Isn't Everything: Corruption in Sumo Wrestling." *American Economic Review*, 92(5), 1594–1605.**
   * *Contribuição Teórica:* Demonstrou que agentes alteram seu comportamento de forma não aleatória quando os incentivos marginais são fortemente assimétricos (lutadores de sumô à beira da eliminação vencem com probabilidade desproporcional contra adversários já qualificados).
   * *Conexão com o Projeto:* Fundamenta a premissa de que a fraude esportiva deixa **pegadas estatísticas detectáveis** na frequência e no momento dos eventos, validando o uso de desvios empíricos em relação à distribuição teórica basal.

2. **WOLFERS, Justin (2006). "Point Shaving: Corruption in NCAA Basketball." *American Economic Review*, 96(2), 279–283.**
   * *Contribuição Teórica:* Analisou a distribuição das margens de vitória no basquete universitário americano frente aos spreads das casas de apostas, identificando acúmulo anormal de vitórias por margem inferior ao handicap (*point shaving*).
   * *Conexão com o Projeto:* Demonstra como testar anomalias em distribuições contínuas de jogo e como agentes minimizam o risco de detecção alterando eventos de baixa visibilidade coletiva.

3. **PRESTON, Ian; SZYMANSKI, Stefan (2003). "Cheating in Contests." *Oxford Review of Economic Policy*, 19(4), 612–624.**
   * *Contribuição Teórica:* Modela formalmente a microeconomia da trapaça em competições, contrastando o doping (que visa vencer) com a manipulação de apostas (que explora o subdesempenho deliberado ou a execução de eventos pontuais).
   * *Conexão com o Projeto:* Fornece a base teórica para o conflito de agência entre o atleta aliciado e o clube empregador.

---

## 3. Eixo 2: A Mecânica das Micro-Apostas e o *Spot-Fixing*

A migração das apostas de resultado final (*match-fixing*) para eventos pontuais fracionários (*spot-fixing* ou *micro-betting*) alterou radicalmente a natureza da corrupção desportiva.

### Artigos e Obras de Referência

1. **CARPENTER, Kevin (2012). "Match-Fixing — The Biggest Threat to Sport in the 21st Century?" *International Sports Law Review*, 2, 13–24.**
   * *Contribuição Teórica:* Define a taxonomia moderna da corrupção esportiva, distinguindo o *match-fixing* (manipulação do resultado ou placar final) do *spot-fixing* (manipulação de frações ou eventos isolados do jogo, como faltas, advertências ou laterais).
   * *Conexão com o Projeto:* É o fundamento conceitual direto para explicar por que os esquemas desvendados na *Operação Penalidade Máxima* concentraram-se em **cartões amarelos no 1º tempo** e não na derrota deliberada das equipes.

2. **FORREST, David (2012). "The Threat to Football from Match-Fixing." *Trends in Organized Crime*, 15(2-3), 99–116.**
   * *Contribuição Teórica:* Examina a economia dos mercados de apostas asiáticos e *in-play*, demonstrando que a liquidez global permitiu apostas elevadas em eventos específicos sem alterar drasticamente as cotações de vitória/empate.
   * *Conexão com o Projeto:* Explica a viabilidade econômica do aliciamento de jogadores na Série B e em jogos de meio de tabela da Série A, onde a vigilância de liquidez global era menor.

3. **HILL, Declan (2010). "A Good Match to Fix: The New Face of Football Corruption." *Global Crime*, 11(2), 173–184.**
   * *Contribuição Teórica:* Detalha o modus operandi de intermediários (*fixers*) e redes criminosas que recrutam atletas com remuneração instável ou em ligas secundárias através de ofertas desproporcionais aos seus salários correntes.
   * *Conexão com o Projeto:* Alinha-se diretamente com os achados empíricos dos autos do MP-GO na Operação Penalidade Máxima (propina média de R$ 50 mil a R$ 100 mil por cartão amarelo, equivalente a vários meses de salário de atletas da Série B ou divisões de base).

4. **HABERFELD, M. R.; SHEEHAN, Kevin M. (Eds.) (2013). *Match-Fixing in International Sports: Existing Processes, Law Enforcement, and Prevention Strategies*. New York: Springer.**
   * *Contribuição Teórica:* Analisa as lacunas de persecução criminal e a necessidade de cooperação entre operadoras de apostas, confederações e autoridades policiais para monitorar padrões incomuns de apostas.

---

## 4. Eixo 3: Economia das Apostas e Patrocínio no Futebol Profissional

A presença ostensiva de casas de apostas como patrocinadoras master do futebol brasileiro espelha dinâmicas observadas na Europa na década anterior.

### Artigos de Referência

1. **LOPEZ-GONZALEZ, Hibai; GRIFFITHS, Mark D. (2018). "Catering, Escorting and Promoting: Latent Modes of Sports Sponsorship by Gambling Operators." *International Review for the Sociology of Sport*, 53(8), 903–921.**
   * *Contribuição Teórica:* Analisa as estratégias de marketing agressivo de bookmakers no futebol europeu, categorizando como as empresas de apostas normalizam sua marca ao se vincularem à identidade visual e afetiva dos clubes.
   * *Conexão com o Projeto:* Fundamenta a construção da nossa variável `BET_EXPOSURE` (Seção 4 da metodologia), capturando a centralidade do patrocínio máster frente a propriedades secundárias (mangas, calção).

2. **BUNING, Richard J.; PALMER, Catherine (2020). "The Normalization of Sports Wagering Among College Students and Young Adults." *Journal of Gambling Studies*, 36(3), 855–870.**
   * *Contribuição Teórica:* Demonstra a correlação direta entre o volume de publicidade esportiva em uniformes e placas de campo e a explosão de buscas digitais e engajamento em apostas esportivas.
   * *Conexão com o Projeto:* Justifica o uso do **Google Trends Brasil** como *proxy* contínua de transbordamento macroeconômico (`S_macro`) no índice de exposição combinada (`bet_exposure_total`).

3. **SZYMANSKI, Stefan (2003). "The Economic Design of Sporting Contests." *Journal of Economic Literature*, 41(4), 1137–1187.**
   * *Contribuição Teórica:* Modelo seminal de economia do esporte sobre equilíbrio competitivo (*competitive balance*), assimetria de receitas e incentivos financeiros em torneios esportivos abertos.
   * *Conexão com o Projeto:* Alinha-se à hipótese H3 do projeto, que investiga como a injeção assimétrica de patrocínios de bets afeta a desigualdade entre as Séries A, B, C e D.

---

## 5. Eixo 4: Comportamento Arbitral, Critérios Punitivos e o "Paradoxo Disciplinar"

Um dos achados centrais do projeto é o **Paradoxo Disciplinar**: a queda contínua no número de faltas por partida (de 31,41 em 2017 para 25,36 em 2024) acompanhada pela máxima histórica na taxa de conversão em cartões ($\tau_{\text{CF}} = 0,220$). A literatura internacional fornece suporte analítico para explicar o comportamento dos árbitros.

### Artigos de Referência

1. **GARICANO, Luis; PALACIOS-HUERTA, Ignacio; PRENDERGAST, Canice (2005). "Favoritism Under Social Pressure." *Journal of Labor Economics*, 23(2), 235–263.**
   * *Contribuição Teórica:* Artigo clássico que demonstrou empiricamente o viés de arbitragem (tempo de acréscimo assimétrico em favor do mandante em função da pressão do público na La Liga).
   * *Conexão com o Projeto:* Valida o controle de **mando de campo** em nossos modelos econométricos (que confirmou que jogar em casa reduz cartões em $\beta = -0,2178, p < 10^{-9}$) e estabelece a sensibilidade arbitral a pressões institucionais e regulatórias.

2. **BURAIMO, Babatunde; FORREST, David; SIMMONS, Robert (2010). "The 12th Man? Refereeing Bias in English and German Soccer." *Journal of the Royal Statistical Society: Series A (Statistics in Society)*, 173(2), 431–449.**
   * *Contribuição Teórica:* Analisa a aplicação de cartões amarelos e vermelhos na Premier League e Bundesliga, testando hipóteses de favoritismo, rigor disciplinar e variância entre árbitros.
   * *Conexão com o Projeto:* Fornece a base econométrica para modelar a contagem de cartões e a probabilidade de penalização disciplinar condicionada ao perfil da partida.

3. **PETTERSSON-LIDBOM, Per; PRIKS, Mikael (2010). "Behavior under Social Pressure: Empty Italian Stadiums and Referee Bias." *Economics Letters*, 108(2), 212–214.**
   * *Contribuição Teórica:* Explora partidas com portões fechados na Itália para mensurar a resposta punitiva do árbitro na ausência de ruído e pressão física da torcida.
   * *Conexão com o Projeto:* Complementa nossa análise da temporada pandêmica de 2020 e a evolução dos critérios disciplinares pós-VAR.

---

## 6. Eixo 5: Arcabouço Regulatório e Relatórios Institucionais Globais

### Documentos e Tratados Internacionais

1. **UNODC — United Nations Office on Drugs and Crime (2021). *Global Report on Corruption in Sport*. Viena: Nações Unidas.**
   * *Destaques:* O relatório global dedica capítulos substanciais à manipulação de apostas esportivas, apontando que ligas inferiores e divisões de acesso são os elos mais vulneráveis do futebol internacional devido à disparidade salarial e menor cobertura televisiva.
   * *Conexão com o Projeto:* Sustenta teoricamente nossa constatação empírica de que os esquemas da Penalidade Máxima originaram-se na Série B de 2022 e corrobora nossas recomendações para a Secretaria de Prêmios e Apostas (SPA/MF) e CBF.

2. **CONSELHO DA EUROPA (2014). *Convenção do Conselho da Europa sobre a Manipulação de Competições Desportivas (Convenção de Macolin)*. Série de Tratados do Conselho da Europa, nº 215.**
   * *Destaques:* Estabelece os parâmetros legais internacionais para cooperação entre autoridades públicas, organizações esportivas e operadores de apostas, definindo o conceito de apostas esportivas ilegais e apostas esportivas suspeitas.
   * *Conexão com o Projeto:* Serve de baliza normativa para as recomendações de governança e integridade propostas na Seção 6 do nosso White Paper.

3. **SPORTRADAR INTEGRITY SERVICES (2023, 2024). *Betting Corruption and Match-Fixing Annual Report*. St. Gallen: Sportradar.**
   * *Destaques:* Catalogou o Brasil consecutivamente como um dos países com maior número absoluto de alertas de jogos suspeitos no mundo, concentrados majoritariamente em torneios estaduais e divisões nacionais de acesso (Séries C e D).
   * *Conexão com o Projeto:* Fornece o contexto de integridade no qual a Operação Penalidade Máxima se insere e justifica a priorização da triagem automatizada de súmulas.

4. **IBIA — International Betting Integrity Association (2023, 2024). *Integrity Reports (Quarterly & Annual)*. Bruxelas: IBIA.**
   * *Destaques:* Documenta que o futebol e o tênis representam mais de 75% dos alertas globais de integridade, com destaque para a crescente incidência de alertas em mercados específicos de atletas (*spot-betting*).

---

## 7. Eixo 6: Metodologia Econométrica de Painel, TWFE e Identificação Causal

A fundamentação econométrica da Fase 7 do projeto (modelos TWFE e *Staggered Event Study*) apoia-se nos desenvolvimentos recentes da econometria de avaliação de impacto:

1. **ANGRIST, Joshua D.; PISCHKE, Jörn-Steffen (2009). *Mostly Harmless Econometrics: An Empiricist's Companion*. Princeton: Princeton University Press.**
   * *Aplicação no Projeto:* Princípios de delineamento de quase-experimentos, controle de fatores não observados via efeitos fixos e regressão com dados em painel.

2. **CALLAWAY, Brantly; SANT'ANNA, Pedro H. C. (2021). "Difference-in-Differences with Multiple Time Periods." *Journal of Econometrics*, 225(2), 200–230.**
   * *Aplicação no Projeto:* Fundamenta a necessidade do nosso *Staggered Event Study* (Estudo de Eventos com Adoção Escalonada), considerando que os clubes de futebol brasileiro não assinaram contratos de patrocínio com casas de apostas todos no mesmo ano (adoção gradual entre 2019 e 2024).

3. **GOODMAN-BACON, Andrew (2021). "Difference-in-Differences with Variation in Treatment Timing." *Journal of Econometrics*, 225(2), 254–277.**
   * *Aplicação no Projeto:* Explica a decomposição do estimador TWFE padrão quando há tratamento escalonado no tempo e a importância do teste formal de tendências paralelas nos períodos pré-tratamento ($e \le -2$).

4. **CAMERON, A. Colin; MILLER, Douglas L. (2015). "A Practitioner’s Guide to Cluster-Robust Inference." *Journal of Human Resources*, 50(2), 317–372.**
   * *Aplicação no Projeto:* Justifica teoricamente o agrupamento dos erros-padrão (*cluster-robust standard errors*) no nível do clube adotado em nossas regressões, corrigindo correlação serial intraclube e heterocedasticidade.

---

## 8. Matriz de Vinculação: Literatura vs. Módulos do Projeto

A tabela abaixo resume como cada corpo teórico fundamenta as decisões analíticas e empíricas adotadas no código-fonte e relatórios:

| Módulo / Decisão do Projeto | Base Empírica no Projeto | Artigos e Referências Norteadoras | Justificativa Teórica |
| :--- | :--- | :--- | :--- |
| **Índice `BET_EXPOSURE`** (`src/cleaning/clean_betting.py`) | Matriz de 200 registros de patrocínio (2015–2024) + Google Trends | Lopez-Gonzalez & Griffiths (2018); Buning & Palmer (2020) | Distinção entre exposição de marca contratual e transbordamento macroeconômico digital. |
| **O Paradoxo Disciplinar** (`src/analysis/eda_serie_a.py`) | Série A (2014–2024): faltas em queda ($-19\%$) e cartões em alta ($+8\%$) | Garicano et al. (2005); Buraimo et al. (2010); Pettersson-Lidbom & Priks (2010) | Ocorrência de severidade punitiva descolada do contato físico puro; efeito de diretrizes de arbitragem e pressão de visibilidade. |
| **Modelagem Causal TWFE** (`src/models/econometric_models.py`) | Painel de 7.598 obs. com efeitos fixos de clube e ano | Callaway & Sant'Anna (2021); Goodman-Bacon (2021); Cameron & Miller (2015) | Isolamento de características fixas de clubes e choques temporais; teste formal de tendências paralelas pré-adoção. |
| **Ground Truth da Penalidade Máxima** (`data/processed/integrity/`) | 14 incidentes judiciais (MP-GO / STJD) de cartões encomendados no 1º tempo | Carpenter (2012); Forrest (2012); Hill (2010); UNODC (2021) | *Spot-fixing* focado em eventos discricionários individuais executados precocemente (1º tempo) com baixo risco esportivo. |
| **Anomaly Scoring Dual** (`src/models/anomaly_detection.py`) | Algoritmo de triagem ($S_{\text{tempo}}$, $S_{\text{precoce}}$, etc.) calibrado em percentis | Duggan & Levitt (2002); Wolfers (2006); Preston & Szymanski (2003) | Econometria forense: detecção de caudas anômalas em distribuições de Poisson/Binomiais como indicador de escrutínio. |
| **Comparação Séries A vs. B/C/D** (`src/analysis/eda_series_comparison.py`) | 760 súmulas mineradas da Série B vs. Série A | UNODC (2021); Sportradar (2023, 2024); Szymanski (2003) | Maior vulnerabilidade em divisões de acesso decorrente de menor monitoramento e disparidade de remuneração. |

---

## 9. Lista Consolidada de Referências em Formato ABNT / APA

```text
ANGRIST, Joshua D.; PISCHKE, Jörn-Steffen. Mostly harmless econometrics: an empiricist's companion. Princeton: Princeton University Press, 2009.

BUNING, Richard J.; PALMER, Catherine. The normalization of sports wagering among college students and young adults. Journal of Gambling Studies, v. 36, n. 3, p. 855-870, 2020.

BURAIMO, Babatunde; FORREST, David; SIMMONS, Robert. The 12th man? Refereeing bias in English and German soccer. Journal of the Royal Statistical Society: Series A (Statistics in Society), v. 173, n. 2, p. 431-449, 2010.

CALLAWAY, Brantly; SANT'ANNA, Pedro H. C. Difference-in-differences with multiple time periods. Journal of Econometrics, v. 225, n. 2, p. 200-230, 2021.

CAMERON, A. Colin; MILLER, Douglas L. A practitioner’s guide to cluster-robust inference. Journal of Human Resources, v. 50, n. 2, p. 317-372, 2015.

CARPENTER, Kevin. Match-fixing — the biggest threat to sport in the 21st century?. International Sports Law Review, v. 2, p. 13-24, 2012.

CONSELHO DA EUROPA. Convenção sobre a manipulação de competições desportivas (Convenção de Macolin). Série de Tratados do Conselho da Europa, nº 215, 2014.

DUGGAN, Mark; LEVITT, Steven D. Winning isn't everything: corruption in sumo wrestling. American Economic Review, v. 92, n. 5, p. 1594-1605, 2002.

FORREST, David. The threat to football from match-fixing. Trends in Organized Crime, v. 15, n. 2-3, p. 99-116, 2012.

GARICANO, Luis; PALACIOS-HUERTA, Ignacio; PRENDERGAST, Canice. Favoritism under social pressure. Journal of Labor Economics, v. 23, n. 2, p. 235-263, 2005.

GOODMAN-BACON, Andrew. Difference-in-differences with variation in treatment timing. Journal of Econometrics, v. 225, n. 2, p. 254-277, 2021.

HABERFELD, M. R.; SHEEHAN, Kevin M. (Eds.). Match-fixing in international sports: existing processes, law enforcement, and prevention strategies. New York: Springer, 2013.

HILL, Declan. A good match to fix: the new face of football corruption. Global Crime, v. 11, n. 2, p. 173-184, 2010.

IBIA — INTERNATIONAL BETTING INTEGRITY ASSOCIATION. Annual integrity report 2023. Bruxelas: IBIA, 2024.

LOPEZ-GONZALEZ, Hibai; GRIFFITHS, Mark D. Catering, escorting and promoting: latent modes of sports sponsorship by gambling operators. International Review for the Sociology of Sport, v. 53, n. 8, p. 903-921, 2018.

PETTERSSON-LIDBOM, Per; PRIKS, Mikael. Behavior under social pressure: empty Italian stadiums and referee bias. Economics Letters, v. 108, n. 2, p. 212-214, 2010.

PRESTON, Ian; SZYMANSKI, Stefan. Cheating in contests. Oxford Review of Economic Policy, v. 19, n. 4, p. 612-624, 2003.

SPORTRADAR INTEGRITY SERVICES. Betting corruption and match-fixing report 2023. St. Gallen: Sportradar, 2024.

SZYMANSKI, Stefan. The economic design of sporting contests. Journal of Economic Literature, v. 41, n. 4, p. 1137-1187, 2003.

UNODC — UNITED NATIONS OFFICE ON DRUGS AND CRIME. Global report on corruption in sport. Viena: Nações Unidas, 2021.

WOLFERS, Justin. Point shaving: corruption in NCAA basketball. American Economic Review, v. 96, n. 2, p. 279-283, 2006.
```
