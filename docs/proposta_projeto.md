# Proposta de Projeto: Impacto das Apostas Esportivas no Futebol Brasileiro

**Projeto de Pesquisa Aplicada e Ciência de Dados**  
**Data:** Setembro de 2026  
**Repositório:** [`analise-bets`](file:///d:/Python%20Projetos/analise-bets)  

---

## 1. Integrantes e Título Provisório

### Integrantes da Equipe
* **Filipe Ataíde**
* **Rebeka Lemos**
* **Nickolas Gomes**

### Título Provisório
> **"O Impacto da Expansão das Casas de Apostas no Futebol Brasileiro: Evidências Empíricas, Inferência Causal e um Sistema de Triagem para a Integridade Esportiva (2015–2024)"**

*Título Alternativo / Sintético:*  
> *"Apostas Esportivas e Dinâmica Disciplinar no Futebol Brasileiro: Econometria e Detecção de Anomalias"*

---

## 2. Formato Escolhido: A, B ou C

### Contexto dos Formatos
* **Formato A — Artigo Acadêmico / Paper Científico:** Estrutura metodológica e econométrica clássica, revisão bibliográfica, testes formais de hipóteses e inferência causal.
* **Formato B — Relatório Técnico / White Paper Governamental/Setorial:** Foco em impacto regulatório, diagnóstico do mercado para entidades esportivas (CBF, clubes) e reguladores (Secretaria de Prêmios e Apostas - SPA/MF).
* **Formato C — Produto de Dados / Ferramenta Aplicada:** Foco em engenharia de software de dados, pipeline de dados automatizada e sistema de detecção e triagem algorítmica de anomalias (*Screening Tool*).

### Escolha e Posicionamento do Projeto
* **Formato Primário:** **Formato A (Artigo Acadêmico / Paper Científico)** ou **Formato B (Relatório Técnico / White Paper Aplicado)**.
* **Diferencial:** A pesquisa une a solidez econométrica com identificação causal do **Formato A**, o diagnóstico regulatório do **Formato B** e a entrega de um algoritmo operacional de integridade desportiva do **Formato C**.

---

## 3. Problema que Será Investigado

A legalização das apostas de quota fixa no Brasil (Lei nº 13.756/2018) desencadeou um crescimento comercial sem precedentes no futebol profissional: entre 2019 e 2024, as empresas de apostas assumiram a hegemonia dos patrocínios máster dos clubes de elite (atingindo 18 dos 20 clubes da Série A em 2024).

Em paralelo, a consolidação dos mercados de **micro-apostas (*spot-betting*)** — focados em cartões, faltas, pênaltis e escanteios — ampliou a vulnerabilidade da integridade esportiva. Diferente do *match-fixing* tradicional sobre o resultado final da partida, o *spot-fixing* depende de atos isolados de um único atleta, com baixo impacto perceptível no placar, mas com alto retorno financeiro ilegal em apostas combinadas (como revelado pela *Operação Penalidade Máxima* do MP-GO).

O projeto investiga se a penetração maciça das bets provocou alterações observáveis no padrão de arbitragem e disciplina do jogo, avaliando se essas mudanças decorrem de um comportamento sistêmico e institucional dos clubes ou de distorções comportamentais e aliciamentos individuais isolados.

---

## 4. Pergunta e Objetivos do Projeto

### Pergunta Principal de Pesquisa
> **"Em que medida a expansão e a exposição comercial às casas de apostas esportivas estiveram associadas e causaram alterações na dinâmica disciplinar (faltas, cartões) e nos riscos de integridade desportiva no futebol brasileiro entre 2015 e 2024?"**

### Perguntas Secundárias
1. Como se comportou o chamado "Paradoxo Disciplinar" (relação entre volume de faltas e taxa de conversão em cartões)?
2. A exposição ao patrocínio de apostas altera o número de cartões recebidos por um clube de forma estatisticamente significante?
3. O efeito sobre cartões precoces (1º tempo) reflete uma postura institucional do clube ou ações pontuais e criminosas de atletas aliciados?
4. É possível formular um índice algorítmico baseado em dados públicos de partidas e atletas capaz de identificar partidas e jogadores com alto desvio estatístico associado a manipulações comprovadas?

### Objetivo Geral
Mensurar com rigor empírico e econométrico os efeitos da expansão das apostas esportivas sobre a disciplina em campo no futebol brasileiro e implementar um sistema algorítmico de triagem (*screening*) para preservação da integridade esportiva.

### Objetivos Específicos
1. **Estruturar e Auditar:** Compilar bases de dados relacionais das Séries A e B (2014–2024) com garantia de reprodutibilidade via hashes SHA-256.
2. **Construir Métricas:** Desenvolver o índice `BET_EXPOSURE` para mensurar a exposição contratual de cada clube-temporada às operadoras de apostas.
3. **Modelar Causalidade:** Estimar modelos econométricos de Efeitos Fixos Bidirecionais (TWFE) e Estudo de Eventos (*Staggered Event Study*), testando a hipótese de tendências paralelas pré-tratamento.
4. **Validar Hipótese de Integridade:** Analisar o comportamento no 1º tempo vs. jogo completo para isolar comportamentos institucionais de aliciamentos individuais.
5. **Calibrar Algoritmo de Triagem:** Construir e validar os escores `MATCH_ANOMALY_SCORE` e `ATHLETE_ANOMALY_SCORE` utilizando o *ground truth* judicial da Operação Penalidade Máxima.

---

## 5. Dados que Serão Utilizados

O repositório do projeto organiza dados brutos e tratados com rastreabilidade auditável:

| Conjunto de Dados | Janela Temporal | Escopo / Volume | Principais Variáveis | Fonte Primária |
| :--- | :---: | :---: | :--- | :--- |
| **Série A (Histórica)** | 2014–2024 | 4.179 partidas / 20.953 cartões | Gols, cartões (minuto e tipo), mandos, público | CBF / Adão Duque |
| **Série A (Scouts 2024)** | 2024 | 380 partidas / 9.585 faltas | Faltas cometidas, escanteios, finalizações | Sofascore (via pipeline) |
| **Série B (Súmulas CBF)** | 2022–2023 | 760 partidas / 3.671 cartões | Minutagem exata, motivos textuais digitados pelo árbitro | CBF (Súmulas Eletrônicas) |
| **Matriz de Patrocínios** | 2015–2024 | 200 clube-temporadas | Marcas, posição no uniforme, valores, exclusividade | IBOPE Repucom / Imprensa de Negócios / Balanços |
| **Interesse Digital (Trends)** | 2015–2025 | 120 meses / 10 anos | Volume relativo de busca por apostas esportivas | Google Trends Brasil |
| **Ground Truth Judicial** | 2022 | 14 incidentes com condenação | Atleta, jogo, minuto da infração, propina pactuada | MP-GO (GAECO) / STJD |

---

## 6. Entregável e Resultados Esperados

### Entregáveis
1. **White Paper / Artigo Completo:** Relatório analítico detalhado ([`reports/white_paper_impacto_bets_futebol_brasileiro.md`](file:///d:/Python%20Projetos/analise-bets/reports/white_paper_impacto_bets_futebol_brasileiro.md)) contendo fundamentação teórica, formulações matemáticas, metodologia causal e recomendações de políticas públicas.
2. **Quatro Cadernos Jupyter Reprodutíveis:**
   * `01_pipeline_dados_e_limpeza.ipynb`: Ingestão, auditoria e validação de hashes.
   * `02_analise_exploratoria_e_paradoxo_disciplinar.ipynb`: Séries temporais e decomposição do paradoxo disciplinar.
   * `03_modelagem_econometrica_painel_did.ipynb`: Modelos TWFE, controle de covariáveis e gráficos de Event Study.
   * `04_sistema_triagem_anomalias_integridade.ipynb`: Calibração do algoritmo de *Anomaly Scoring* e validação com ground truth.
3. **Pacote de Figuras e Tabelas:** Mais de 15 figuras analíticas em alta resolução e 17 tabelas consolidadas em CSV.
4. **Código-Fonte e Suíte de Testes:** Módulos em Python estruturados em `src/` com suíte de testes unitários automatizados (`pytest`).

### Resultados Empíricos Obtidos / Esperados
* **O Paradoxo Disciplinar:** Queda física das faltas em $-19,3\%$ (31,4 $\to$ 25,4 faltas/jogo) acompanhada por uma elevação de $+37,1\%$ na taxa de conversão em cartões (recorde de 0,220 cartões por falta em 2024).
* **Efeito Causal Identificado:** Clubes com exposição máster a bets recebem em média $+0,2665$ cartões a mais por jogo ($p = 0,00642$), com tendências paralelas validadas nos períodos pré-tratamento ($p > 0,10$).
* **Ausência de Viés Institucional nos Cartões Precoces:** O coeficiente sobre cartões no 1º tempo é estatisticamente nulo ($\beta = -0,0129, p = 0,5916$), demonstrando que a manipulação precoce é uma ação individual e não uma estratégia tática do clube.
* **Alta Eficácia de Triagem:** O algoritmo de *Anomaly Scoring* classificou 100% dos casos reais da Operação Penalidade Máxima nos tiers prioritários de investigação (todos os atletas condenados da Série A ficaram no Top 10% mais anômalos da história da competição).

---

## 7. Próximas Atividades do Grupo

| Atividade | Descrição / Escopo | Prazo Estimado |
| :--- | :--- | :---: |
| **Atividade 1: Revisão e Formatação Final do Texto** | Adequação da redação às normas acadêmicas (ABNT/APA), consolidação das referências bibliográficas e alinhamento da introdução e conclusões. | Semana 1 |
| **Atividade 2: Refinamento Visual das Evidências** | Harmonização dos gráficos de estudo de eventos, densidade temporal (KDE) e tabelas resumo para inclusão no documento e nos slides. | Semana 1 |
| **Atividade 3: Testes de Robustez no Algoritmo de Triagem** | Avaliação do comportamento do algoritmo em cenários de clássicos estaduais (derbies) para calibrar a taxa de falsos positivos. | Semana 2 |
| **Atividade 4: Elaboração da Apresentação Executiva** | Criação do deck de slides focado nos tomadores de decisão (reguladores, clubes e federações), destacando a causalidade e o sistema de triagem. | Semana 2 |

---

## 8. Responsabilidade de Cada Integrante

* **Filipe Ataíde:**
  * **Engenharia de Dados e Modelagem Econométrica Causal:** Coordenação técnica dos pipelines de dados, estruturação do painel relacional no nível de clube-partida, concepção e cálculo da métrica contínua `BET_EXPOSURE`, especificação e estimação dos modelos de Efeitos Fixos Bidirecionais (TWFE) e do *Staggered Event Study*, além da validação das premissas de identificação causal.
* **Rebeka Lemos:**
  * **Análise Exploratória de Dados (EDA), Visualizações e Redação Científica:** Condução das análises estatísticas descritivas sobre o Paradoxo Disciplinar, criação das rotinas de visualização gráfica de alta resolução (séries temporais, quebras estruturais e testes de hipóteses), levantamento e síntese da revisão bibliográfica e redação dos capítulos do relatório final e do paper acadêmico.
* **Nickolas Gomes:**
  * **Integridade Esportiva, Algoritmos de Detecção de Anomalias e Validação Factual:** Desenvolvimento da esteira de ingestão e parsing das súmulas oficiais da Série B da CBF, compilação e validação do *ground truth* judicial da *Operação Penalidade Máxima*, formulação matemática dos índices multidimensionais `MATCH_ANOMALY_SCORE` e `ATHLETE_ANOMALY_SCORE` e realização dos testes empíricos de sensibilidade.

---

## Extras: 1. Draft do Projeto (Protótipo e Visão Inicial)

### Diagrama Arquitetural do Sistema

```
                                      FLUXO INTEGRADO DO PROJETO
                                      
  ┌─────────────────────────────┐        ┌─────────────────────────────┐        ┌─────────────────────────────┐
  │      FONTES PRIMÁRIAS       │        │   TRATAMENTO & ENGENHARIA   │        │     MODELAGEM & PRODUTO     │
  │                             │        │                             │        │                             │
  │ • CBF / Adão Duque          │ ─────► │ • Normalização UTF-8        │ ─────► │ • Painel TWFE & Event Study │
  │   (Série A: 2014–2024)      │        │ • Minutagem Decomposta      │        │   (Inferência Causal)       │
  │                             │        │ • Taxa de Conversão F/C     │        │                             │
  │ • Súmulas Oficiais CBF      │ ─────► │ • Parsing de PDFs           │ ─────► │ • Anomaly Scoring Engine    │
  │   (Série B: 2022–2023)      │        │ • Classificação de Motivos  │        │   - Match Anomaly Score     │
  │                             │        │                             │        │   - Athlete Anomaly Score   │
  │ • Matriz Bets & Trends      │ ─────► │ • Métrica BET_EXPOSURE      │ ─────► │                             │
  │   (2015–2024)               │        │   (Contratual e Macro)      │        │ • White Paper & Cadernos    │
  │                             │        │                             │        │   (Reprodutibilidade Total) │
  │ • Ground Truth MP-GO / STJD │ ─────► │ • Validação Judicial        │ ─────► │ • Recomendações Regulatórias│
  │   (Penalidade Máxima)       │        │                             │        │   (SPA/MF, CBF e Clubes)    │
  └─────────────────────────────┘        └─────────────────────────────┘        └─────────────────────────────┘
```

### Descrição do Protótipo Funcional
O protótipo consiste em uma esteira analítica dividida em dois motores:
1. **Motor Causal Econométrico:** avalia se choques exógenos contratuais alteram parâmetros de advertências arbitrais a nível de equipe-jogo.
2. **Motor de Triagem de Integridade (*Screening Engine*):** algoritmo em Python com scoring ponderado de 0 a 100:
   * **Nível Partida:** Avalia a concentração de cartões no 1º tempo, desvios da taxa de conversão esperada e ocorrência de pênaltis precoces em jogos de alta exposição.
   * **Nível Atleta:** Calcula o desvio probabilístico binomial de advertências precoces com base na minutagem histórica de cada jogador, gerando uma lista priorizada para auditoria independente.
