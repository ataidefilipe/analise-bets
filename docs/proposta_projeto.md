# Proposta de Projeto: Impacto das Apostas Esportivas no Futebol Brasileiro

**Projeto de Pesquisa Aplicada e Ciência de Dados**  
**Data:** Setembro de 2026  
**Repositório:** [`analise-bets`](file:///d:/Python%20Projetos/analise-bets)  

---

## 1. Integrantes e Título Provisório

### Integrantes da Equipe
* **Filipe Ataide**
* **Rebeka Lemos**
* **Nickolas Gomes**
* **Lacê Rene**
* **Luan de Oliveira**

### Título Provisório
> **"O Impacto da Expansão das Casas de Apostas no Futebol Brasileiro: Evidências Empíricas, Inferência Causal e um Sistema de Triagem para a Integridade Esportiva (2015–2024)"**

*Título Alternativo / Sintético:*  
> *"Apostas Esportivas e Dinâmica Disciplinar no Futebol Brasileiro: Econometria e Detecção de Anomalias"*

---

## 2. Formato Escolhido: A, B ou C

### Contexto dos Formatos
* **Formato C — Artigo Acadêmico / Paper Científico:** Estrutura metodológica e econométrica clássica, revisão bibliográfica, testes formais de hipóteses e inferência causal.

---

## 3. Problema que Será Investigado

A legalização das apostas de quota fixa no Brasil (Lei nº 13.756/2018) desencadeou um crescimento comercial sem precedentes no futebol profissional: entre 2019 e 2024, as empresas de apostas assumiram a hegemonia dos patrocínios master dos clubes de elite (atingindo 18 dos 20 clubes da Série A em 2024).

Em paralelo, a consolidação dos mercados de **micro-apostas (*spot-betting*)** — focados em cartões, faltas, pênaltis e escanteios — ampliou a vulnerabilidade da integridade esportiva. Diferente do *match-fixing* tradicional sobre o resultado final da partida, o *spot-fixing* depende de atos isolados de um único atleta, com baixo impacto perceptível no placar, mas com alto retorno financeiro ilegal em apostas combinadas (como revelado pela *Operação Penalidade Máxima* do MP-GO).

O projeto investiga se a penetração maciça das bets provocou alterações observáveis no padrão de arbitragem e disciplina do jogo, avaliando se essas mudanças decorrem de um comportamento sistêmico e institucional dos clubes ou de distorções comportamentais e aliciamentos individuais isolados.

---

## 4. Pergunta e Objetivos do Projeto

### Pergunta Principal de Pesquisa
> **"Em que medida a expansão e a exposição comercial às casas de apostas esportivas estiveram associadas e causaram alterações na dinâmica disciplinar (faltas, cartões) e nos riscos de integridade desportiva no futebol brasileiro entre 2015 e 2024?"**

### Perguntas Secundárias
1. A exposição ao patrocínio de apostas altera o número de cartões recebidos por um clube de forma estatisticamente significante?
2. O efeito sobre cartões precoces (1º tempo) reflete uma postura institucional do clube ou ações pontuais e criminosas de atletas aliciados?
3. É possível formular um índice algorítmico baseado em dados públicos de partidas e atletas capaz de identificar partidas e jogadores com alto desvio estatístico associado a manipulações comprovadas?

### Objetivo Geral
Mensurar com rigor empírico e econométrico os efeitos da expansão das apostas esportivas sobre a disciplina em campo no futebol brasileiro e implementar um sistema algorítmico de triagem (*screening*) para preservação da integridade esportiva.

### Objetivos Específicos
1. **Estruturar e Auditar:** Compilar bases de dados relacionais das Séries A e B (2014–2024) com garantia de reprodutibilidade via hashes SHA-256.
2. **Construir Métricas:** Desenvolver o índice `BET_EXPOSURE` para mensurar a exposição contratual de cada clube-temporada às operadoras de apostas.
3. **Modelar Causalidade:** Estimar modelos econométricos de Efeitos Fixos Bidirecionais (TWFE), Estudo de Eventos (*Staggered Event Study*), Callaway–Sant'Anna ou Sun–Abraham, testando a hipótese de tendências paralelas pré-tratamento.
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

As atividades finais e revisões do projeto foram estruturadas em três níveis de prioridade, distribuindo as entregas e responsabilidades de forma balanceada entre os integrantes da equipe:

### Prioridade 1 — Bloqueadores (Ajustes Críticos de Dados e Modelagem)
| Ref. | Tarefa | Escopo e Detalhamento | Responsável |
| :---: | :--- | :--- | :---: |
| **4.2** | **Google Trends** | Baixar a série temporal real de buscas ou remover/renomear referências no projeto. | **Filipe Ataíde** |
| **4.3** | **Reescrita dos §3.2–3.4** | Atualizar e reescrever as seções §3.2 a §3.4 diretamente a partir dos CSVs consolidados da base. | **Luan de Oliveira** |
| **4.1** | **Documentação dos Patrocínios** | Documentar detalhadamente as fontes primárias e secundárias da matriz de patrocínios dos clubes. | **Nickolas Gomes** |
| **3.3** | **Modelagem Causal Avançada** | Rodar e consolidar as estimativas via estimadores robustos de Callaway–Sant'Anna ou Sun–Abraham. | **Lacê Rene** |
| **2.2** | **Autoria Real** | Ajustar metadados e autoria real de todos os integrantes no documento e entregáveis. | **Rebeka Lemos** |

### Prioridade 2 — Estrutura Acadêmica (Rigor Metodológico e Teórico)
| Ref. | Tarefa | Escopo e Detalhamento | Responsável |
| :---: | :--- | :--- | :---: |
| **3.4** | **Seção de Discussão** | Criar seção aprofundada de Discussão confrontando os resultados obtidos com a literatura empírica e teórica. | **Filipe Ataíde** |
| **2.9 / 2.8** | **Hipóteses e Objetivos** | Formalizar matematicamente as hipóteses H1–H4 (§2.9) e migrar/alinhar a redação dos objetivos (§2.8). | **Luan de Oliveira** |
| **2.10 / 2.15** | **Referencial Teórico e Conclusão** | Criar o Referencial Teórico estruturado no corpo (§2.10) e elaborar a seção de Conclusão (§2.15). | **Nickolas Gomes** |
| **3.5** | **Ampliação das Limitações** | Expandir a análise crítica de limitações metodológicas, escopo amostral e vieses potenciais (§3.5). | **Lacê Rene** |
| **2.5** | **Palavras-Chave** | Definir e padronizar palavras-chave acadêmicas em português e inglês (§2.5). | **Rebeka Lemos** |

### Prioridade 3 — Polimento (Robustez, Compliance e Formatação)
| Ref. | Tarefa | Escopo e Detalhamento | Responsável |
| :---: | :--- | :--- | :---: |
| **3.7** | **Robustez Poisson / Binomial Negativa** | Estimar modelos de contagem (Poisson e Binomial Negativa) para validar a robustez das especificações OLS/TWFE. | **Filipe Ataíde** |
| **5.1** | **Anonimização de Atletas** | Anonimizar dados de atletas investigados que não tenham sido condenados judicialmente, garantindo compliance ético e LGPD (§5.1). | **Luan de Oliveira** |
| **2.17** | **Padronização ABNT** | Padronizar rigorosamente todas as citações e referências no corpo do texto conforme as normas da ABNT (§2.17). | **Nickolas Gomes** |
| **4.6 / 4.9 / 5.3** | **Revisão Técnica e Links** | Corrigir contagem de testes unitários (§4.6), checar e corrigir links internos/externos (§4.9) e alinhar a numeração dos formatos A/B/C (§5.3). | **Lacê Rene** |
| **3.8** | **Sensibilidade dos Pesos do Índice** | Conduzir análise de sensibilidade variando os pesos dos componentes dos escores de anomalia (§3.8). | **Rebeka Lemos** |

---

## 8. Responsabilidade de Cada Integrante

* **Filipe Ataíde:**
  * **Foco de Atuação:** Engenharia de Dados, Modelagem Econométrica Causal e Discussão Teórica.
  * **Atribuições Gerais:** Coordenação técnica dos pipelines de dados, estruturação do painel relacional no nível de clube-partida, concepção e cálculo da métrica contínua `BET_EXPOSURE`, especificação e estimação dos modelos de Efeitos Fixos Bidirecionais (TWFE) e do *Staggered Event Study*, além da validação das premissas de identificação causal.
  * **Tarefas Prioritárias Atribuídas:**
    * `[Prioridade 1 — 4.2]` Google Trends — baixar série real ou remover/renomear.
    * `[Prioridade 2 — 3.4]` Criar seção de Discussão confrontando a literatura.
    * `[Prioridade 3 — 3.7]` Testes de robustez com regressão Poisson / binomial negativa.

* **Luan de Oliveira:**
  * **Foco de Atuação:** Consolidação Empírica, Formalização de Hipóteses e Compliance Ético/LGPD.
  * **Atribuições Gerais:** Consolidação de dados tabulares a partir das bases processadas, formalização e especificação empírica de hipóteses e objetivos de pesquisa, e implementação de diretrizes de conformidade ética e proteção de dados na manipulação de registros de atletas.
  * **Tarefas Prioritárias Atribuídas:**
    * `[Prioridade 1 — 4.3]` Reescrever §3.2–3.4 a partir dos CSVs consolidados.
    * `[Prioridade 2 — 2.9 / 2.8]` Formalizar hipóteses H1–H4 e migrar/alinhar objetivos.
    * `[Prioridade 3 — 5.1]` Anonimizar atletas investigados não condenados.

* **Nickolas Gomes:**
  * **Foco de Atuação:** Fontes de Patrocínio, Integridade Esportiva, Referencial Teórico e Normatização.
  * **Atribuições Gerais:** Rastreamento e documentação de fontes de patrocínios, ingestão e validação do *ground truth* judicial da *Operação Penalidade Máxima*, desenvolvimento da esteira de súmulas da Série B, elaboração do referencial teórico e padronização ABNT.
  * **Tarefas Prioritárias Atribuídas:**
    * `[Prioridade 1 — 4.1]` Documentar fontes da matriz de patrocínios.
    * `[Prioridade 2 — 2.10 / 2.15]` Criar Referencial Teórico no corpo e seção de Conclusão.
    * `[Prioridade 3 — 2.17]` Padronizar citações ABNT no corpo do texto.

* **Lacê Rene:**
  * **Foco de Atuação:** Inferência Causal Avançada, Validação Metodológica e Auditoria Técnica.
  * **Atribuições Gerais:** Implementação e diagnóstico de estimadores causais heterogêneos (*staggered DiD*), análise crítica e aprofundamento das limitações empíricas do estudo, e revisão técnica da suíte de testes, hiperlinks e taxonomia de formatos.
  * **Tarefas Prioritárias Atribuídas:**
    * `[Prioridade 1 — 3.3]` Rodar Callaway–Sant'Anna ou Sun–Abraham.
    * `[Prioridade 2 — 3.5]` Ampliar a seção de Limitações.
    * `[Prioridade 3 — 4.6 / 4.9 / 5.3]` Corrigir contagem de testes, links e numeração A/B/C.

* **Rebeka Lemos:**
  * **Foco de Atuação:** Análise Exploratória de Dados (EDA), Metadados e Sensibilidade do Índice.
  * **Atribuições Gerais:** Condução das análises estatísticas descritivas sobre o Paradoxo Disciplinar, criação das rotinas de visualização gráfica de alta resolução, padronização de metadados de autoria e palavras-chave, e validação de robustez dos pesos dos algoritmos de triagem.
  * **Tarefas Prioritárias Atribuídas:**
    * `[Prioridade 1 — 2.2]` Autoria real e identificação institucional da equipe.
    * `[Prioridade 2 — 2.5]` Definir e padronizar palavras-chave.
    * `[Prioridade 3 — 3.8]` Análise de sensibilidade dos pesos do índice de anomalia.

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
