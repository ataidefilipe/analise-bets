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
Para cada partida $i \in \{1, \dots, 4.559\}$, calcula-se uma pontuação ponderada $[0, 100]$:
$$\text{MATCH\_ANOMALY\_SCORE} = 0{,}30 \cdot S_{\text{tempo}} + 0{,}25 \cdot S_{\text{precoce}} + 0{,}20 \cdot S_{\text{volume}} + 0{,}15 \cdot S_{\text{bet}} + 0{,}10 \cdot S_{\text{penalti}}$$

Onde:
1. **$S_{\text{tempo}}$ (Concentração no 1º Tempo):** Teste de cauda binomial com probabilidade basal da liga $p_0 = 0{,}354$:
   $$S_{\text{tempo}} = \min\left(100, -20 \cdot \log_{10}(P(X \ge k \mid n, p_0 = 0{,}354))\right) \quad \text{se } k/n > 0{,}354 \text{ senão } 0{,}0$$
2. **$S_{\text{precoce}}$ (Cartões até 30 Minutos):** Teste de cauda binomial com probabilidade basal $p_0 = 0{,}198$:
   $$S_{\text{precoce}} = \min\left(100, -20 \cdot \log_{10}(P(X \ge k \mid n, p_0 = 0{,}198))\right) \quad \text{se } k/n > 0{,}198 \text{ senão } 0{,}0$$
3. **$S_{\text{volume}}$ (Z-Score de Cartões Totais):**
   $$S_{\text{volume}} = \text{clip}\left(\frac{\text{Cartões} - \mu_{\text{liga}}}{\sigma_{\text{liga}}} \cdot 25{,}0, 0{,}0, 100{,}0\right)$$
4. **$S_{\text{bet}}$ (Intensidade Comercial das Equipes):**
   $$S_{\text{bet}} = \frac{\text{Exposure}_{\text{mandante}} + \text{Exposure}_{\text{visitante}}}{2} \cdot 100$$
5. **$S_{\text{penalti}}$ (Penalidades no 1º Tempo):**
   $$S_{\text{penalti}} = \begin{cases} 80{,}0, & \ge 2 \text{ pênaltis no 1ºT} \\ 40{,}0, & 1 \text{ pênalti no 1ºT} \\ 0{,}0, & 0 \text{ pênaltis no 1ºT} \end{cases}$$

### 7.3 Formulação do Athlete Anomaly Score (`ATHLETE_ANOMALY_SCORE`)
Para cada atleta-temporada com $\ge 3$ cartões recebidos:
$$\text{ATHLETE\_ANOMALY\_SCORE} = 0{,}50 \cdot S_{\text{atleta\_tempo}} + 0{,}30 \cdot S_{\text{atleta\_taxa}} + 0{,}20 \cdot S_{\text{atleta\_minuto}}$$

Onde:
* $S_{\text{atleta\_tempo}} = \min(100, -25 \cdot \log_{10}(p_{\text{binom}}))$;
* $S_{\text{atleta\_taxa}} = \text{prop\_cartoes\_1t} \cdot 100$;
* $S_{\text{atleta\_minuto}} = \text{clip}((90{,}0 - \overline{\text{Minuto}}) \cdot 1{,}5, 0{,}0, 100{,}0)$.

### 7.4 Calibração Empírica por Percentis e Validação Ground-Truth
Os thresholds de alerta foram calibrados empiricamente na distribuição histórica:
* **Alta Prioridade de Escrutínio:** Top 10% da liga (Percentil $\ge 90\%$);
* **Média Prioridade de Escrutínio:** Top 25% da liga (Percentil $\ge 75\%$);
* **Linha de Base / Típico:** Abaixo do Percentil 75%.

**Sensibilidade Empírica no Ground Truth (Operação Penalidade Máxima):**
* $100\%$ dos 14 casos reais investigados e condenados foram classificados em *Alta* ou *Média Prioridade*;
* $100\%$ dos atletas confessos/condenados da Série A (8/8 registros) foram posicionados no **Top 10% (Percentil $\ge 90\%$)** da distribuição histórica;
* Nino Paraíba (Percentil 99,7%), Gabriel Tota (Percentil 98,2%), Paulo Miranda (Percentil 95,3%), Moraes Jr (Percentil 93,3%), Igor Cariús (Percentil 92,4%), Eduardo Bauermann (Percentil 90,5%).

### 7.5 Governança Ética e Presunção de Inocência
A metodologia estabelece formalmente que scores elevados representam **anomalias estatísticas sob escrutínio probabilístico**, e **não prova penal de manipulação de resultados**. Fatores desportivos legítimos (estratégia tática agressiva, arbitragem rígida, faltas de contenção) podem gerar scores atípicos, devendo o sistema ser empregado como ferramenta de triagem para auditoria humana por federações e unidades de integridade.



