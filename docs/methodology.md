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
