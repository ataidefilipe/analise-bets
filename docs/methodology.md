# Metodologia e Modelagem Estatística

**Projeto:** Impacto das Apostas Esportivas no Futebol Brasileiro  
**Documento de Referência Metodológica:** `docs/methodology.md`  
**Última Atualização:** 2026-09-05  

---

## 1. Princípios Metodológicos Fundamentais

1. **Separação entre Associação e Causalidade:**
   * Nenhuma correlação estatística observada ($X \leftrightarrow Y$) é tratada automaticamente como relação causal ($X \rightarrow Y$). Mudanças em regras de jogo, diretrizes de arbitragem (ex.: tempo de acréscimo, combate a reclamações), táticas de equipe e o advento do VAR atuam como potenciais variáveis de confusão (*confounders*).
2. **Taxonomia de Evidências:**
   * **Associação:** Covariação empírica documentada entre duas variáveis.
   * **Quebra de Regime / Estrutural:** Alteração estatisticamente significativa na média, variância ou distribuição temporal de uma variável entre dois períodos definidos.
   * **Evidência de Anomalia:** Comportamento de uma partida ou atleta que desvia significativamente da distribuição esperada (ex.: resíduo padronizado $|z| > 2,5$ ou probabilidade empírica $< 1\%$).
   * **Evidência de Manipulação:** Classificação reservada exclusivamente para eventos confirmados por autoridades policiais, Ministério Público ou tribunais de justiça desportiva.
3. **Anomaly Score como Triagem Investigativa:**
   * Índices de anomalia não constituem prova de má conduta; sua utilidade científica reside em priorizar eventos e indivíduos para escrutínio aprofundado.

---

## 2. Métricas Derivadas e Variáveis Construídas

### 2.1 Minutagem Contínua ($\text{Minuto}_{\text{cont}}$)
Para análises de sobrevivência e densidade temporal ao longo dos 90 minutos de jogo, a minutagem que contém acréscimos foi linearizada:
$$\text{Minuto}_{\text{cont}} = \text{Minuto}_{\text{nominal}} + \text{Acréscimo}$$
* Exemplos:
  * Cartão aos $45+2'$ do 1º Tempo: $\text{Minuto}_{\text{cont}} = 45 + 2 = 47'$ (Período: `1T`).
  * Cartão aos $90+4'$ do 2º Tempo: $\text{Minuto}_{\text{cont}} = 90 + 4 = 94'$ (Período: `2T`).

### 2.2 Taxa de Conversão Faltas $\rightarrow$ Cartões ($\tau_{\text{CF}}$)
Mede a severidade relativa da arbitragem por partida $i$ no ano $t$, isolando a propensão de uma falta gerar punição disciplinar:
$$\tau_{\text{CF}, i} = \frac{\text{Cartões Totais}_i}{\text{Faltas Cometidas}_i}$$
Se o volume de faltas diminui enquanto o volume de cartões se mantém ou sobe, $\tau_{\text{CF}}$ cresce, sinalizando mudança no critério arbitral ou na natureza das infrações.

---

## 3. Testes Estatísticos de Hipótese

Para avaliar as quebras de tendência entre o período basal (**Pré-Bets: 2014–2018**) e o período de **Alta Exposição (2022–2024)**, são empregados três testes complementares:

### 3.1 Teste $t$ de Student para Duas Amostras Independentes
Testa a igualdade das médias entre o grupo controle ($0$) e o grupo tratamento ($1$):
$$t = \frac{\bar{X}_1 - \bar{X}_0}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_0^2}{n_0}}}$$

### 3.2 Teste de Mann-Whitney $U$ (Não-Paramétrico)
Avalia a probabilidade de um valor selecionado ao acaso do grupo $1$ ser superior a um valor do grupo $0$, sem assumir normalidade nas distribuições:
$$U = n_0 n_1 + \frac{n_0 (n_0 + 1)}{2} - R_0$$
Onde $R_0$ é a soma dos postos do grupo controle.

### 3.3 Tamanho de Efeito (*Cohen's d*)
Quantifica a magnitude prática da diferença em unidades de desvio-padrão conjunto ($s_{\text{pooled}}$):
$$d = \frac{\bar{X}_1 - \bar{X}_0}{s_{\text{pooled}}}, \quad \text{onde } s_{\text{pooled}} = \sqrt{\frac{(n_0 - 1)s_0^2 + (n_1 - 1)s_1^2}{n_0 + n_1 - 2}}$$
* Convenção de interpretação:
  * $|d| < 0,2$: efeito negligenciável.
  * $0,2 \le |d| < 0,5$: efeito pequeno a moderado.
  * $|d| \ge 0,8$: efeito grande.

---

## 4. Modelagem da Exposição às Bets (`BET_EXPOSURE`)

Para quantificar o grau de exposição econômica de cada clube $c$ na temporada $t$, desenvolvemos uma formulação aditiva e normalizada decomposta em três dimensões:

### 4.1 Dimensões Componentes

1. **Relevância Contratual da Propriedade ($S_{\text{pos}}$):**
   $$S_{\text{pos}} = \begin{cases} 1,00, & \text{se patrocínio master (espaço nobre da camisa)} \\ 0,50, & \text{se mangas / omoplata / costas} \\ 0,30, & \text{se propriedades secundárias (shorts/barra)} \\ 0,00, & \text{se ausente} \end{cases}$$

2. **Multiplicidade de Marcas Parceiras ($S_{\text{qtd}}$):**
   $$S_{\text{qtd}} = \min\left(1,0, \; \frac{N_{\text{marcas}}}{2}\right)$$

3. **Ambiente Macro e Demanda Digital ($S_{\text{macro}}$):**
   $$S_{\text{macro}, t} = \frac{\text{Trends}_t}{\text{Trends}_{\max}} \in [0,0, \; 1,0]$$
   Onde $\text{Trends}_t$ é a média anual de buscas no Google Trends Brasil para termos de apostas esportivas e $\text{Trends}_{\max} = 100$.

### 4.2 Índices no Nível do Clube

Conforme diretriz analítica `D-ANA-07`, foram computadas duas variáveis complementares:
1. **Exposição Contratual Estrita (`bet_exposure_clube`):**
   $$\text{BET\_EXPOSURE}_{\text{clube}, c, t} = \begin{cases} 0,75 \cdot S_{\text{pos}} + 0,25 \cdot S_{\text{qtd}}, & \text{se clube possui patrocínio de bet} \\ 0,00, & \text{caso contrário} \end{cases}$$
2. **Exposição Combinada com Transbordamento Macro (`bet_exposure_total`):**
   $$\text{BET\_EXPOSURE}_{\text{total}, c, t} = 0,60 \cdot S_{\text{pos}} + 0,15 \cdot S_{\text{qtd}} + 0,25 \cdot S_{\text{macro}, t}$$

### 4.3 Agregação no Nível da Partida

Para cada partida $i$ entre o mandante $M$ e o visitante $V$ na edição $t$:
$$\text{Exposure}_{\text{partida}, i} = \frac{\text{BET\_EXPOSURE}_{M, t} + \text{BET\_EXPOSURE}_{V, t}}{2}$$

Categorização das partidas contemporâneas (2019–2024):
* **Nenhuma:** Nem mandante nem visitante possuem patrocínio de apostas.
* **Parcial (1 clube):** Exatamente uma das equipes possui patrocínio ativo.
* **Total (2 clubes):** Ambas as equipes possuem patrocínio ativo no uniforme.

---

## 5. Análise Comparativa Entre Divisões (Série A vs. Série B) e Assinatura de Manipulação

### 5.1 Comparação Transversal Interdivisões (Série A vs. Série B)
Para testar se o comportamento disciplinar difere sistematicamente entre a elite nacional e a divisão de acesso (onde a pressão de visibilidade da mídia e VAR é historicamente distinta), contrasta-se as temporadas 2022 e 2023 sob hipótese nula de igualdade de médias disciplinares ($H_0: \mu_A = \mu_B$):

1. **Testes Paramétricos e Não-Paramétricos:** Teste $t$ de Welch (variâncias desiguais) e teste de postos de Mann-Whitney $U$.
2. **Tamanho do Efeito:** $d$ de Cohen entre $\text{Cartões}_{\text{Série A}}$ e $\text{Cartões}_{\text{Série B}}$.

### 5.2 Tipologia Textual de Infrações via Mineração de Súmulas
A extração do texto literal do árbitro nas súmulas oficiais da CBF permitiu categorizar as advertências em duas macroclasses conceituais:

1. **Infrações Físicas de Disputa de Bola:**
   * *Falta Temerária / Entrada Dura:* Disputa direta pelo controle da bola (`falta_temeraria`). Depende da dinâmica e da imprevisibilidade do adversário.
2. **Infrações Comportamentais / Não-Físicas (Discricionárias do Atleta):**
   * *Reclamação com Arbitragem (`reclamacao`):* Gestos ostensivos ou palavras desrespeitosas.
   * *Cera / Retardamento de Reinício (`cera_retardar`):* Demorar para repor a bola em jogo, chutar bola longe após apito, simular lesão.
   * *Conduta Antidesportiva Não-Física (`conduta_antidesportiva`):* Provocações, puxões de camisa fora da disputa, tumultos.
   * *Mão Intencional (`mao_intencional`):* Toque deliberado na bola.

> **Importância para Modelos de Integridade:** Atletas aliciados para receber cartão amarelo sob encomenda têm incentivo econômico direto para forçar cartões em infrações comportamentais não-físicas (reclamação, cera ou agressão verbal), pois essas ações eliminam o risco de lesão física e não dependem do posicionamento de adversários em campo.

### 5.3 Teste Binomial e Assinatura Temporal de Manipulação (*Ground Truth*)
A análise dos casos confessados e condenados da *Operação Penalidade Máxima* (MP-GO/STJD) revelou uma regularidade matemática notável:

1. **Distribuição Basal Populacional:**
   No histórico do Campeonato Brasileiro (Séries A e B), a probabilidade empírica de um cartão ocorrer no 1º tempo é de:
   $$p = P(\text{Cartão no 1T}) \approx 0,345 \text{ a } 0,354$$
   Com 64,5% a 65,5% ocorrendo no 2º tempo (fadiga física, pressão do placar, faltas táticas de transição).

2. **Modelo Binomial de Triagem:**
   Seja $X \sim \text{Binomial}(n, p)$ o número de cartões de um atleta ou amostra ocorridos no 1º tempo. A probabilidade de observar $k$ ou mais sucessos por mero acaso é dada por:
   $$P(X \ge k) = \sum_{j=k}^{n} \binom{n}{j} p^j (1-p)^{n-j}$$

   * **Aplicação aos Casos Comprovados:** Entre os casos judiciais de cartão amarelo encomendado na Penalidade Máxima (Paulo Miranda, Gabriel Tota, Nino Paraíba, Moraes Jr, Igor Cariús, Mateusinho), $k = 7$ em $n = 7$ casos ($100\%$) ocorreram no 1º tempo:
     $$P(X = 7 \mid n=7, p=0,35) = (0,35)^7 = 0,000643 \quad (p < 0,001)$$
   * Rejeita-se categoricamente $H_0$ de aleatoriedade temporal.

3. **Racional Econômico da Manipulação no 1º Tempo:**
   * **Mitigação de Risco Tático:** Caso o atleta aliciado espere o 2º tempo, ele corre o risco de ser substituído no intervalo por decisão técnica, lesionar-se ou ser expulso diretamente, inviabilizando a aposta combinada da quadrilha.
   * **Convergência de Horário:** Apostas casadas múltiplas exigiam liquidação síncrona nos primeiros tempos para maximizar retorno em mercados ao vivo.

---

## 6. Modelagem Econométrica e Inferência Causal (Fase 7)

### 6.1 Efeitos Fixos Bidirecionais (Two-Way Fixed Effects — TWFE)
Para estimar a relação entre a intensidade da exposição (`BET_EXPOSURE`) e os desfechos esportivos sem incorrer em viés de variáveis omitidas, adota-se o estimador TWFE no nível Clube $\times$ Partida:
$$Y_{ict} = \beta \cdot \text{BET\_EXPOSURE}_{it} + \mathbf{X}_{ict}' \boldsymbol{\delta} + \alpha_i + \gamma_t + \varepsilon_{ict}$$
* $\alpha_i$ (Efeito Fixo de Clube): Controla por características invariantes no tempo de cada clube (ex.: tradição tática, perfil de torcida, pressão de mídia local, agressividade histórica);
* $\gamma_t$ (Efeito Fixo de Temporada): Absorve choques anuais agregados de toda a liga (ex.: diretrizes anuais da comissão de arbitragem da CBF, política de tempo de acréscimo e o advento do VAR a partir de 2019);
* $\mathbf{X}_{ict}$ (Controles Exógenos): Mando de campo (`is_mandante`), derbies estaduais (`mesma_uf`), saldo final de gols (`saldo_gols`), rodada linear e exposição da equipe adversária (`exposure_adversario`).

### 6.2 Erros-Padrão Clusterizados por Clube
Dada a presença de correlação serial temporal e dependência espacial entre partidas disputadas pelo mesmo clube ao longo de 10 anos, a inferência estatística utiliza matriz de covariância robusta clusterizada por clube:
$$\text{Var}(\hat{\beta}) = (X'X)^{-1} \left( \sum_{g \in \text{Clubes}} X_g' u_g u_g' X_g \right) (X'X)^{-1}$$
Garantindo que os testes de hipótese ($t$ e $F$) sejam assintoticamente válidos e conservadores.

### 6.3 Estudo de Eventos com Adoção Escalonada (Staggered Event Study)
Como os clubes assinaram contratos de apostas em anos distintos entre 2019 e 2024 (e um grupo de controle nunca adotou, liderado pelo Palmeiras), define-se o tempo relativo $e = t - t_i^*$:
$$Y_{ict} = \alpha_i + \gamma_t + \sum_{k \in \{-3, -2, 0, 1, 2, 3, \ge 4\}} \beta_k \cdot \mathbb{I}(t - t_i^* = k) + \mathbf{X}_{ict}' \boldsymbol{\delta} + \varepsilon_{ict}$$
Com $e = -1$ (ano base pré-adoção) omitido como referência ($\beta_{-1} \equiv 0$).

### 6.4 Teste Formal de Tendências Paralelas (Parallel Trends Test)
A validade da inferência causal em modelos quase-experimentais repousa na hipótese de que, na ausência do tratamento, o grupo tratado teria seguido a mesma trajetória do grupo de controle. Testa-se formalmente via teste $F$ conjunto das dummies pré-tratamento:
$$H_0: \beta_{e \le -3} = \beta_{e = -2} = 0$$
* A não-rejeição de $H_0$ ($p > 0,05$) atesta econometricamente que os grupos já não estavam divergindo antes da entrada das bets, sustentando a plausibilidade de atribuição causal para os coeficientes pós-adoção ($\beta_{e \ge 0}$).

---

## 7. Sistema de Triagem e Anomaly Scoring de Integridade Esportiva (Fase 8)

### 7.1 Arquitetura Conceitual e Escopo
A Fase 8 estruturou um framework algorítmico de detecção de anomalias disciplinares para servir como camada de conformidade (*compliance*) e triagem preliminar (*screening*) de integridade esportiva. O sistema processa súmulas oficiais da CBF e avalia simultaneamente a dimensão do confronto coletivo e o histórico disciplinar longitudinal dos atletas.

### 7.2 Formulação do Match Anomaly Score (`MATCH_ANOMALY_SCORE`)

> **Revisão de 2026-09-16 (tarefas F1-01 / F1-02).** A especificação canônica vive nas
> constantes do topo de `src/models/anomaly_detection.py` e é fixada por teste automatizado.
> O subscore de exposição comercial ($S_{\text{bet}}$) foi **removido** do índice; a
> justificativa está na seção 2.1 do relatório técnico 07.

Para cada partida $i \in \{1, \dots, 4.559\}$, calcula-se uma pontuação ponderada $[0, 100]$:
$$\text{MATCH\_ANOMALY\_SCORE} = 0{,}39 \cdot S_{\text{tempo}} + 0{,}28 \cdot S_{\text{precoce}} + 0{,}22 \cdot S_{\text{volume}} + 0{,}11 \cdot S_{\text{penalti}}$$

Onde:
1. **$S_{\text{tempo}}$ (Concentração no 1º Tempo):** Teste de cauda binomial com probabilidade basal estimada na própria base, $p_0 = 0{,}353$:
   $$S_{\text{tempo}} = \text{clip}\left(-25 \cdot \log_{10}(P(X \ge k \mid n, p_0)), 0, 100\right)$$
2. **$S_{\text{precoce}}$ (Cartões até 30 Minutos de jogo corrido):** Teste de cauda binomial com $p_0 = 0{,}156$:
   $$S_{\text{precoce}} = \text{clip}\left(-25 \cdot \log_{10}(P(X \ge k \mid n, p_0)), 0, 100\right)$$
3. **$S_{\text{volume}}$ (Z-Score de Cartões Totais dentro de temporada e série):**
   $$S_{\text{volume}} = \text{clip}\left(25{,}0 \cdot \frac{\text{Cartões} - \mu_{\text{temporada, série}}}{\sigma_{\text{temporada, série}}}, 0{,}0, 100{,}0\right)$$
4. **$S_{\text{penalti}}$ (Penalidades no 1º Tempo):**
   $$S_{\text{penalti}} = \begin{cases} 80{,}0, & \ge 2 \text{ pênaltis no 1ºT} \\ 40{,}0, & 1 \text{ pênalti no 1ºT} \\ 0{,}0, & 0 \text{ pênaltis no 1ºT} \end{cases}$$

A variável `exposure_total_partida` permanece na base como covariável de contexto e
estratificação, sem participar de nenhum escore.

### 7.3 Formulação do Athlete Anomaly Score (`ATHLETE_ANOMALY_SCORE`)
Para cada atleta-temporada com $\ge 3$ cartões recebidos:
$$\text{ATHLETE\_ANOMALY\_SCORE} = 0{,}50 \cdot S_{\text{atleta\_tempo}} + 0{,}30 \cdot S_{\text{atleta\_taxa}} + 0{,}20 \cdot S_{\text{atleta\_minuto}}$$

Onde:
* $S_{\text{atleta\_tempo}} = \text{clip}(-25 \cdot \log_{10}(p_{\text{binom}}), 0, 100)$, com $p_0 = 0{,}353$;
* $S_{\text{atleta\_taxa}} = \text{prop\_cartoes\_1t} \cdot 100$;
* $S_{\text{atleta\_minuto}} = \text{clip}((90{,}0 - \overline{\text{Minuto}}) \cdot 1{,}5, 0{,}0, 100{,}0)$, sobre o minuto de jogo corrido.

### 7.4 Calibração Empírica por Percentis e Validação Ground-Truth
Os tiers de alerta são definidos pelo percentil empírico da própria distribuição, o que torna a
carga operacional um parâmetro explícito:
* **Extrema Anomalia:** Top 1% (Percentil $\ge 99\%$);
* **Alta Prioridade de Escrutínio:** Top 5% (Percentil $\ge 95\%$);
* **Média Prioridade:** Top 10% (Percentil $\ge 90\%$);
* **Típico / Baixa Prioridade:** abaixo do Percentil 90%.

**Ancoragem do ground truth.** O cruzamento entre os 14 casos e a base é feito pelo mapa de
identidade explícito de `src/models/ground_truth_resolver.py`, com evidência e grau de confiança
por associação. Situação: 14 de 14 partidas resolvidas (1 com correção de rodada), 7 de 10
atletas resolvidos, 1 abaixo do mínimo de 3 cartões e 2 sem correspondente defensável.

**Sensibilidade dos escores estatísticos (fórmulas fechadas, não treinadas no ground truth):**
* **5 dos 14 casos (35,7%)** sinalizados em faixa prioritária de triagem;
* Dois dos nove não sinalizados são fraudes que não se consumaram em campo.

**Sensibilidade do classificador de ML (Tabela 22).** A distinção é essencial: apenas o
`BaggingPUClassifier` é treinado nos rótulos. Sob leave-one-out agrupado por entidade:

| Nível | Critério | In-sample | Leave-one-out | IC 95% (Wilson) |
| :--- | :--- | :---: | :---: | :---: |
| Partida | Classe 2 (Alto Risco) | 12/14 (85,7%) | **5/14 (35,7%)** | 16,3% – 61,2% |
| Partida | Classe 1 ou 2 | 14/14 (100%) | **10/14 (71,4%)** | 45,4% – 88,3% |
| Atleta | Classe 2 (Alto Risco) | 7/7 (100%) | **0/7 (0,0%)** | 0,0% – 35,4% |
| Atleta | Classe 1 ou 2 | 7/7 (100%) | **3/7 (42,9%)** | 15,8% – 75,0% |

Sob separação por série — treinar na Série B e avaliar na Série A, o cenário mais próximo do uso
real — a captura no tier de Alto Risco é de 1 em 9 partidas (11,1%).

**Limitação de fonte.** Os metadados por incidente do ground truth (rodada, minuto e, em alguns
casos, a atribuição do cartão) não reconciliam com os registros de súmula: de 14 casos, apenas 1
tem o evento confirmado na base. O rótulo positivo é, portanto, definido nos níveis agregados de
partida e de atleta-temporada, e não por evento individual.

### 7.5 Governança Ética e Presunção de Inocência
A metodologia estabelece formalmente que scores elevados representam **anomalias estatísticas sob escrutínio probabilístico**, e **não prova penal de manipulação de resultados**. Fatores desportivos legítimos (estratégia tática agressiva, arbitragem rígida, faltas de contenção) podem gerar scores atípicos, devendo o sistema ser empregado como ferramenta de triagem para auditoria humana por federações e unidades de integridade.

---

## 8. Modelo de Classificação de Integridade e Suspeição por Machine Learning (Fase 12)

### 8.1 Motivação e Abordagem Híbrida
A Fase 12 expandiu a triagem de integridade para além das heurísticas probabilísticas univariadas, formulando um classificador de Machine Learning capaz de operar sob o desafio do **extremo desbalanceamento de classes** (apenas 14 casos confirmados no *ground truth* judicial em mais de 4.500 partidas) e o problema de instâncias não-rotuladas (*Positive-Unlabeled Learning*).

### 8.2 Componente 1: Isolation Forest Multidimensional
Para capturar anomalias estruturais multivariadas sem viés de supervisão humana, emprega-se o algoritmo `IsolationForest` no nível da partida e do atleta:
* **Espaço de Features (Partida):** Proporção de cartões no 1º tempo (`prop_cartoes_1t`), cartões precoces até 30' (`prop_cartoes_30m`), volume total de cartões (`total_cartoes`), $z$-score de volume na temporada (`z_cartoes`), cartões por cera/reclamação (`cartoes_reclamacao_cera`), pênaltis no 1ºT (`penaltis_1t`) e transformações log-binomiais (`score_tempo`, `score_precoce`).
* **Espaço de Features (Atleta):** `prop_cartoes_1t`, `cartoes_30m`, `minuto_medio_partida`, `total_cartoes`, `score_atleta_tempo`, `score_atleta_taxa` e `score_atleta_minuto`.
* **Calibração de Contaminação:** Fixada em $\alpha = 0{,}03$ (3% da cauda mais extrema da distribuição).
* **Score de Decisão Normalizado:**
  $$S_{\text{IForest}} = \frac{-d(\mathbf{x}) - \min(-d)}{\max(-d) - \min(-d)} \cdot 100 \in [0, 100]$$

### 8.3 Componente 2: Bagging PU-Learning (Positive and Unlabeled Learning)
Para estimar a probabilidade a posteriori calibrada de suspeição sem tratar partidas não-investigadas como garantidamente negativas:
1. Conjunto positivo ($P$): partidas e atletas com casos confirmados e executados da Operação Penalidade Máxima ($y=1$).
2. Conjunto não-rotulado ($U$): todo o restante da base histórica ($y=0$ provisório).
3. **Bagging PU Ensemble:** Treina um comitê de $B = 50$ estimadores base (`RandomForestClassifier` com pesos balanceados), onde cada estimador recebe todos os positivos e uma subamostra aleatória balanceada de não-rotulados ($|U_{\text{sub}}| = 4 \cdot |P|$).
4. **Probabilidade Calibrada de Suspeição:**
   $$\hat{P}(\text{Suspeito} = 1 \mid \mathbf{x}) = \frac{1}{B} \sum_{b=1}^{B} p_b(\mathbf{x}) \in [0, 1]$$

### 8.4 Tiers Operacionais de Decisão
As predições do Isolation Forest e da probabilidade PU são combinadas na seguinte matriz de decisão:
* **Classe 2 (Alto Risco / Alerta Investigativo):** $\hat{P} \ge 0{,}60$ OU ($\text{Outlier}_{\text{IF}} = 1$ E $\hat{P} \ge 0{,}45$);
* **Classe 1 (Monitoramento / Risco Moderado):** $\hat{P} \ge 0{,}35$ OU $\text{Outlier}_{\text{IF}} = 1$;
* **Classe 0 (Basal / Conforme):** Casos típicos em ambas as dimensões.

### 8.5 Desempenho e Validação Empírica
* **Sensibilidade no Ground Truth (Tabela 18):** métrica **in-sample** — os mesmos casos compõem o rótulo positivo do treino PU. A estimativa fora da amostra está na Tabela 22 e cai para 5/14 (partida) e 0/7 (atleta) no tier de Alto Risco.
* **Probabilidade Média de Suspeição:** $80{,}4\%$ nas partidas investigadas e $84{,}8\%$ nos atletas confessos/condenados.
* **Distribuição Populacional:** O modelo classifica apenas $8{,}93\%$ das partidas históricas no tier de Alto Risco, garantindo foco operacional e controle de falsos alarmes para unidades de auditoria desportiva.



