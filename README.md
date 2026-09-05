# Impacto das Apostas Esportivas no Futebol Brasileiro

## 1. Visão geral

Este projeto tem como objetivo investigar, por meio de análise exploratória e estatística, os efeitos associados à expansão das apostas esportivas no futebol brasileiro.

A pesquisa será estruturada em dois grandes eixos:

1. **Impacto econômico e esportivo**

   * expansão das bets;
   * patrocínios;
   * receitas dos clubes;
   * público;
   * desempenho esportivo;
   * competitividade;
   * diferenças entre as Séries A, B, C e D.

2. **Integridade esportiva**

   * expansão dos mercados de apostas sobre eventos específicos;
   * evolução de faltas, cartões, pênaltis, escanteios e outros eventos;
   * identificação de padrões estatísticos anormais;
   * comparação entre eventos de jogo;
   * comparação com casos conhecidos de suspeita ou investigação de manipulação.

O projeto **não deve assumir inicialmente que as bets causaram alterações no futebol**. O objetivo é identificar associações, padrões e anomalias e, somente posteriormente, avaliar quais relações possuem evidência suficiente para análises causais.

---

# 2. Pergunta de pesquisa

## Pergunta principal

> Em que medida a expansão das apostas esportivas esteve associada a mudanças econômicas, esportivas e de integridade no futebol brasileiro, e esses efeitos foram diferentes entre as Séries A, B, C e D?

## Perguntas secundárias

### Mercado

1. Quando ocorreu a expansão mais significativa das apostas esportivas no Brasil?
2. Como evoluiu o número de operadores e marcas?
3. Como evoluiu o interesse do público por apostas esportivas?
4. Quando as bets passaram a ocupar espaço relevante no futebol brasileiro?

### Economia dos clubes

5. A presença das bets aumentou as receitas dos clubes?
6. O crescimento dos patrocínios de bets foi diferente entre as Séries A, B, C e D?
7. Clubes patrocinados por bets apresentaram evolução financeira diferente dos clubes sem esse tipo de patrocínio?

### Desempenho esportivo

8. O crescimento das bets esteve associado a mudanças no desempenho dos clubes?
9. Houve alteração na competitividade das competições?
10. A desigualdade esportiva aumentou ou diminuiu?
11. O comportamento foi diferente entre as quatro divisões?

### Integridade

12. Eventos específicos das partidas apresentaram mudanças durante a expansão das apostas?
13. Faltas, cartões, pênaltis e escanteios apresentaram alterações diferentes?
14. Jogadores específicos apresentam comportamentos estatisticamente anômalos?
15. Existem padrões temporais ou estatísticos semelhantes aos observados em casos conhecidos de manipulação?
16. A maior exposição às bets está associada a maior frequência de eventos potencialmente manipuláveis?

---

# 3. Hipóteses

As hipóteses serão tratadas como hipóteses testáveis, não como conclusões prévias.

## H1 — Expansão do mercado

A expansão das apostas esportivas no Brasil aumentou significativamente a exposição econômica do futebol às empresas de apostas.

Indicadores:

* número de operadores;
* número de marcas;
* interesse no Google Trends;
* número de clubes patrocinados;
* valor dos patrocínios;
* participação das bets como patrocinadoras master.

---

## H2 — Impacto econômico

Clubes com maior exposição às bets apresentaram evolução diferente de receitas, patrocínios e capacidade de investimento em comparação com clubes menos expostos.

---

## H3 — Diferença entre divisões

O efeito econômico e esportivo associado às bets não é homogêneo entre as Séries A, B, C e D.

A hipótese é que clubes da Série A apresentem maior exposição devido a:

* maior audiência;
* maior valor comercial;
* maior capacidade de atração de patrocinadores;
* maior presença em mercados de apostas;
* maior cobertura da mídia.

---

## H4 — Eventos específicos

A expansão das apostas está associada a alterações na frequência de determinados eventos estatísticos das partidas.

Eventos prioritários:

* cartões;
* faltas;
* pênaltis;
* escanteios;
* impedimentos;
* eventos envolvendo jogadores específicos.

---

## H5 — Granularidade do mercado

Mercados mais específicos podem apresentar maior risco potencial de manipulação porque determinados eventos individuais são mais controláveis por um único jogador do que o resultado final de uma partida.

Exemplo conceitual:

```text
Resultado da partida
    ↓
difícil de controlar individualmente

Número de gols
    ↓
mais controlável, mas ainda complexo

Cartões
    ↓
mais específico

Cartão de determinado jogador
    ↓
evento individual

Falta cometida por determinado jogador
    ↓
evento altamente granular
```

Essa hipótese deverá ser tratada como hipótese de risco, não como afirmação de que eventos granulares são necessariamente manipulados.

---

## H6 — Anomalias

Jogadores ou partidas associadas a casos conhecidos de manipulação apresentam padrões estatísticos que podem ser utilizados como referência para identificar partidas potencialmente anômalas.

O objetivo não é classificar automaticamente um jogador como manipulador.

O resultado esperado é:

> **identificação de partidas, jogadores ou eventos que merecem investigação adicional.**

---

# 4. Delimitação temporal

A janela principal proposta é:

**2015–2025**

Podendo ser estendida até 2026 quando os dados estiverem disponíveis e consolidados.

A divisão temporal inicial será:

```text
2015–2017
Pré-expansão

2018–2022
Legalização e expansão do mercado

2023–2024
Regulamentação

2025–2026
Mercado regulado
```

## Justificativa

As apostas de quota fixa foram legalizadas no Brasil em 2018.

A regulamentação posterior criou uma segunda mudança estrutural.

A partir de 1º de janeiro de 2025, somente empresas autorizadas passaram a poder operar nacionalmente no mercado regulado.

Isso permite estudar diferentes fases da evolução do mercado.

---

# 5. Unidade de análise

O projeto utilizará diferentes unidades de análise.

## Nível 1 — Mercado

```text
ano/mês
```

Exemplos:

* número de operadores;
* número de marcas;
* Google Trends;
* tamanho do mercado.

---

## Nível 2 — Clube

```text
clube × temporada
```

Exemplos:

* receita;
* patrocínio;
* série;
* posição;
* pontos;
* público.

---

## Nível 3 — Partida

```text
partida
```

Exemplos:

* gols;
* faltas;
* cartões;
* escanteios;
* árbitro.

---

## Nível 4 — Jogador

```text
jogador × partida
```

Exemplos:

* cartão;
* minuto do cartão;
* posição;
* faltas individuais, caso a fonte seja encontrada.

---

## Nível 5 — Mercado de apostas

Idealmente:

```text
partida × mercado × seleção × timestamp
```

Exemplos:

* resultado;
* gols;
* cartões;
* cartão de jogador;
* faltas;
* escanteios.

---

# 6. Arquitetura conceitual

O projeto será estruturado da seguinte maneira:

```text
                 EXPANSÃO DAS BETS
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
      IMPACTO ECONÔMICO         INTEGRIDADE
             │                       │
       ┌─────┼─────┐           ┌─────┼─────┐
       ▼     ▼     ▼           ▼     ▼     ▼
    Receita Público Desempenho Faltas Cartões Pênaltis
       │                       │
       │                       ▼
       │                   Anomalias
       │                       │
       └───────────┬───────────┘
                   ▼
             ANÁLISE POR SÉRIE
             A / B / C / D
                   │
                   ▼
            MODELOS ESTATÍSTICOS
                   │
                   ▼
        CASOS CONHECIDOS / INVESTIGAÇÕES
```

---

# 7. Dataset principal

A base principal deverá utilizar como unidade:

```text
clube × temporada
```

Estrutura inicial:

| Campo                  | Descrição                                         |
| ---------------------- | ------------------------------------------------- |
| `ano`                  | temporada                                         |
| `clube`                | clube                                             |
| `serie`                | Série A/B/C/D                                     |
| `uf`                   | estado                                            |
| `posicao`              | posição final                                     |
| `pontos`               | pontos                                            |
| `vitorias`             | vitórias                                          |
| `empates`              | empates                                           |
| `derrotas`             | derrotas                                          |
| `gols_marcados`        | gols marcados                                     |
| `gols_sofridos`        | gols sofridos                                     |
| `saldo_gols`           | saldo                                             |
| `publico_medio`        | público médio                                     |
| `receita_total`        | receita total                                     |
| `receita_patrocinio`   | receita de patrocínios                            |
| `folha_salarial`       | folha salarial                                    |
| `divida`               | dívida                                            |
| `bet_patron`           | existência de patrocinador bet                    |
| `bet_master`           | bet como patrocinador master                      |
| `numero_bets`          | número de empresas de apostas associadas ao clube |
| `valor_patrocinio_bet` | valor conhecido do patrocínio                     |
| `bet_exposure`         | índice de exposição às bets                       |

---

# 8. Dataset de partidas

Estrutura:

```text
match_id
date
competition
serie
season
home_team
away_team
home_score
away_score
referee
```

Estatísticas:

```text
home_fouls
away_fouls

home_yellow_cards
away_yellow_cards

home_red_cards
away_red_cards

home_corners
away_corners

home_offsides
away_offsides

home_shots
away_shots

home_shots_on_target
away_shots_on_target

home_possession
away_possession
```

---

# 9. Dataset de eventos de jogadores

Estrutura:

```text
match_id
date
player
team
position
event
minute
```

Eventos prioritários:

```text
yellow_card
red_card
penalty
goal
own_goal
```

Quando disponível:

```text
foul_committed
foul_suffered
```

---

# 10. Dataset do mercado de apostas

Idealmente:

```text
match_id
timestamp
bookmaker
market
selection
line
odds
```

Exemplos:

```text
market = match_result
market = goals
market = corners
market = cards
market = player_cards
market = player_fouls
```

Essa camada será considerada opcional caso os dados históricos não sejam obtidos.

---

# 11. Dataset de volume de apostas

Idealmente:

```text
match_id
timestamp
market
selection
volume
number_of_bets
```

Exemplo:

```text
Flamengo x Palmeiras
Mercado: cartão do jogador X
Volume: R$ 50.000
```

Essa é uma das partes mais difíceis do projeto.

Os operadores possuem dados detalhados das apostas e devem armazenar determinadas informações, mas esses dados não estão necessariamente disponíveis publicamente no nível necessário para pesquisa.

Portanto:

**o projeto não deve depender da obtenção desses dados.**

---

# 12. Dataset de integridade

Estrutura:

```text
case_id
match_id
date
competition
serie
club
player
market
event
source
alert_type
investigation
outcome
```

Fontes potenciais:

* CBF;
* Ministério Público;
* GAECO;
* Polícia Civil;
* tribunais;
* IBIA;
* Sportradar;
* imprensa especializada.

---

# 13. Fontes de dados identificadas

## 13.1 CBF

Fonte primária para:

* competições;
* resultados;
* classificação;
* estatísticas oficiais;
* informações dos clubes.

Uso:

**validação e fonte oficial de referência.**

---

## 13.2 Dataset Adão Duque

Repositório:

`github.com/adaoduque/Brasileirao_Dataset`

Cobertura identificada:

**2003–2024**

Dados relevantes:

* partidas;
* estatísticas;
* faltas;
* cartões;
* escanteios;
* posse;
* chutes;
* passes.

Arquivo particularmente relevante:

```text
campeonato-brasileiro-estatisticas-full.csv
```

Também há dados de cartões individuais.

---

## 13.3 Dataset estendido

Repositório:

`github.com/leeofernandes1980/brasileirao-dataset`

Cobertura informada:

**2003–2026**

Utiliza dados históricos do dataset original e dados posteriores provenientes do Sofascore.

Dados relevantes:

* partidas;
* estatísticas;
* gols;
* cartões;
* faltas;
* jogadores;
* minuto dos cartões.

Esse dataset é candidato a ser a principal fonte de dados de partidas para a primeira EDA.

---

## 13.4 Sofascore

Possível fonte para:

* partidas;
* jogadores;
* eventos;
* estatísticas;
* cartões;
* faltas;
* escanteios.

O uso de APIs não oficiais deverá ser documentado e validado.

A fonte não deve ser tratada automaticamente como equivalente a uma fonte oficial.

---

## 13.5 Kaggle

Possíveis datasets:

* Brazilian Football Matches;
* datasets de Brasileirão;
* datasets históricos de resultados.

Uso:

**fonte complementar e comparação entre datasets.**

---

## 13.6 Ministério da Fazenda / Secretaria de Prêmios e Apostas

Fonte oficial para:

* operadores autorizados;
* marcas;
* situação das empresas;
* regulamentação;
* informações agregadas do mercado;
* dados institucionais.

Sistema relevante:

**SIGAP — Sistema de Gestão de Apostas.**

O sistema recebe informações dos operadores.

---

## 13.7 Google Trends

Uso:

construção de proxies de interesse por apostas.

Termos potenciais:

```text
bet
bets
apostas esportivas
apostas futebol
casa de apostas
bet365
Betano
Sportingbet
```

Variáveis:

```text
google_trends_bets
google_trends_apostas
google_trends_apostas_futebol
```

O Google Trends deve ser interpretado como indicador de interesse/pesquisa, não como tamanho financeiro do mercado.

---

## 13.8 IBIA

A International Betting Integrity Association possui sistemas de monitoramento de apostas suspeitas.

Uso:

* contexto;
* número de alertas;
* casos;
* comparação temporal;
* validação externa de eventos.

A IBIA informou 68 alertas de apostas suspeitas no Brasil entre 2021 e 2025.

Os dados detalhados de apostas utilizados pelo sistema não são integralmente públicos.

---

## 13.9 Sportradar

Fonte comercial especializada em:

* odds;
* monitoramento;
* integridade;
* comportamento de apostas;
* detecção de padrões suspeitos.

O sistema UFDS monitora partidas e mercados em larga escala.

Uso potencial:

**referência metodológica e eventual fonte de dados caso acesso acadêmico/comercial seja obtido.**

O projeto não deve depender dessa fonte.

---

# 14. Variáveis do mercado de bets

Será construída uma série temporal agregada:

```text
ano
numero_operadores
numero_marcas
google_trends
ggr
numero_apostadores
investimento_publicitario
numero_clubes_patrocinados
valor_patrocinios
```

Nem todas estarão disponíveis para todo o período.

A ausência de uma variável não deverá impedir a construção do projeto.

---

# 15. Índice de exposição às bets

Para permitir comparações entre clubes, será criado um indicador de exposição.

Uma versão inicial:

```text
BET_EXPOSURE =
    presença de patrocinador
    +
    posição do patrocínio
    +
    quantidade de patrocinadores
    +
    valor do patrocínio
```

Uma versão normalizada poderá variar de:

```text
0 = nenhuma exposição
1 = exposição máxima
```

O método definitivo de construção será decidido após inspeção dos dados.

Não criar pesos arbitrários antes de analisar a distribuição das variáveis.

---

# 16. Análise exploratória

A primeira etapa será puramente exploratória.

## 16.1 Expansão das bets

Gráficos:

* Google Trends ao longo do tempo;
* número de operadores;
* número de marcas;
* número de clubes patrocinados;
* valor dos patrocínios.

---

## 16.2 Economia

Comparar ao longo do tempo:

* receita média;
* receita de patrocínio;
* folha salarial;
* dívida;
* valor dos elencos.

Comparação:

```text
Série A
Série B
Série C
Série D
```

---

## 16.3 Público

Variáveis:

* público médio;
* público total;
* taxa de ocupação, quando disponível.

Pergunta:

> A expansão das bets ocorreu junto com aumento ou redução da presença do público?

---

## 16.4 Desempenho

Variáveis:

* pontos;
* vitórias;
* derrotas;
* gols;
* saldo;
* posição;
* acesso;
* rebaixamento.

---

## 16.5 Competitividade

Possíveis indicadores:

### Desvio-padrão dos pontos

Medir dispersão dos resultados dentro da competição.

### Concentração

Avaliar concentração de:

* pontos;
* receita;
* patrocínios;
* títulos;
* classificação.

Objetivo:

> verificar se a expansão das bets esteve associada a aumento ou redução da desigualdade esportiva.

---

# 17. Análise de integridade

Essa será uma seção independente.

## 17.1 Eventos analisados

Prioridade:

1. cartões;
2. cartões por jogador;
3. faltas;
4. faltas por jogador;
5. pênaltis;
6. escanteios;
7. impedimentos.

---

# 18. Comparação entre eventos

Classificar eventos pela possibilidade teórica de influência individual.

### Baixa granularidade

* resultado;
* pontos;
* gols.

### Média granularidade

* escanteios;
* número total de cartões;
* número total de faltas.

### Alta granularidade

* cartão de determinado jogador;
* falta de determinado jogador;
* primeiro cartão;
* cartão em determinado intervalo;
* próximo cartão.

Essa classificação será usada para formular hipóteses, não para afirmar que determinados mercados são manipulados.

---

# 19. Análise temporal dos eventos

Não analisar apenas o total.

Dividir partidas em intervalos:

```text
0–15
15–30
30–45
45–60
60–75
75–90+
```

Perguntas:

* existem concentrações anormais?
* determinados eventos aumentam em momentos específicos?
* determinados jogadores apresentam comportamento diferente?
* a distribuição mudou após a expansão dos mercados?

---

# 20. Modelo de comportamento esperado

Para cada jogador, tentar estimar:

```text
evento esperado =
f(
    posição,
    minutos jogados,
    faltas,
    adversário,
    árbitro,
    competição,
    temporada,
    mando de campo
)
```

Exemplo:

```text
probabilidade esperada de cartão = 8%
probabilidade observada = evento ocorrido
```

Ao longo de muitas partidas, podem ser calculados:

* eventos esperados;
* eventos observados;
* resíduos;
* frequência de desvios;
* persistência da anomalia.

---

# 21. Anomaly Score

Criar um indicador exploratório:

```text
ANOMALY_SCORE
```

Ele poderá considerar:

* desvio em relação ao comportamento histórico;
* frequência do evento;
* contexto da partida;
* comportamento do árbitro;
* adversário;
* minuto;
* posição do jogador;
* Série;
* exposição às bets.

Exemplo conceitual:

```text
comportamento histórico
        ↓
comportamento esperado
        ↓
evento observado
        ↓
desvio
        ↓
Anomaly Score
```

O score **não será um indicador de culpa**.

Sua finalidade será priorizar observações para investigação.

---

# 22. Casos conhecidos

Criar uma base específica com casos públicos de:

* manipulação;
* investigação;
* denúncia;
* punição;
* alerta de integridade.

Estrutura:

```text
caso
ano
competição
série
partida
jogador
evento
mercado
tipo
fonte
situação
resultado
```

Essa base será utilizada para validar se os indicadores estatísticos identificam padrões semelhantes aos encontrados em casos conhecidos.

---

# 23. Estratégia de comparação

Uma das análises principais será:

```text
CASOS CONHECIDOS
        vs
PARTIDAS NÃO INVESTIGADAS
```

Objetivo:

> identificar características estatísticas que diferenciem eventos conhecidos de manipulação de partidas normais.

Caso seja possível identificar padrões robustos, esses padrões poderão posteriormente alimentar um modelo de classificação ou scoring.

---

# 24. Diferença entre correlação e causalidade

Este é um princípio obrigatório do projeto.

Não será permitido concluir:

```text
bets ↑
faltas ↑

logo:

bets causaram aumento das faltas
```

Existem variáveis de confusão:

* mudança nas regras;
* mudança de arbitragem;
* mudança tática;
* mudança na qualidade dos dados;
* pandemia;
* mudança no perfil dos jogadores;
* mudanças nas competições;
* mudanças regulatórias;
* mudança na quantidade de jogos.

Os modelos deverão controlar essas variáveis quando possível.

---

# 25. Modelo estatístico futuro

Depois da EDA, poderão ser utilizados modelos de painel.

Estrutura conceitual:

```text
Y = β0
  + β1 BET
  + β2 SERIE
  + β3 BET × SERIE
  + controles
  + efeitos fixos
  + erro
```

Onde `Y` pode ser:

* receita;
* público;
* pontos;
* gols;
* cartões;
* faltas;
* probabilidade de acesso;
* desempenho.

O termo:

```text
BET × SERIE
```

será especialmente importante.

Ele permite testar se o efeito associado à exposição às bets é diferente entre A, B, C e D.

---

# 26. Diferença-em-diferenças

Caso a qualidade dos dados permita, utilizar:

### Grupo tratado

Clubes que passaram a ter patrocínio de bets.

### Grupo controle

Clubes semelhantes que não tiveram patrocínio de bets.

Comparar:

```text
ANTES
vs
DEPOIS
```

e:

```text
TRATADO
vs
CONTROLE
```

Possíveis resultados:

* receita;
* patrocínio;
* público;
* desempenho.

---

# 27. Estrutura esperada do artigo

## 1. Introdução

* crescimento das apostas;
* transformação do mercado;
* presença das bets no futebol;
* problema de integridade;
* pergunta de pesquisa.

## 2. Contexto

* evolução das apostas no Brasil;
* legislação de 2018;
* regulamentação;
* mercado regulado de 2025;
* entrada das bets no futebol.

## 3. Revisão da literatura

Temas:

* sports betting;
* match fixing;
* sports integrity;
* gambling markets;
* football economics;
* sponsorship;
* behavioral economics;
* anomaly detection.

## 4. Dados

Descrever:

* fontes;
* período;
* variáveis;
* tratamento;
* limitações.

## 5. Metodologia

* EDA;
* estatística descritiva;
* correlação;
* painel;
* diferença-em-diferenças;
* análise de anomalias.

## 6. Resultados

Separar:

### 6.1 Mercado

### 6.2 Economia

### 6.3 Desempenho

### 6.4 Séries A/B/C/D

### 6.5 Eventos de jogo

### 6.6 Anomalias

### 6.7 Casos conhecidos

## 7. Discussão

Interpretar resultados sem extrapolar causalidade.

## 8. Limitações

* disponibilidade de dados;
* ausência de volume real de apostas;
* qualidade das bases;
* mudanças metodológicas dos fornecedores;
* viés de seleção;
* causalidade.

## 9. Conclusão

Responder às perguntas de pesquisa.

---

# 28. Estrutura do projeto de software

Proposta inicial:

```text
bet-football-impact/
│
├── README.md
│
├── data/
│   ├── raw/
│   │   ├── cbf/
│   │   ├── sofascore/
│   │   ├── betting/
│   │   ├── clubs/
│   │   └── integrity/
│   │
│   ├── processed/
│   │
│   └── final/
│
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_bets.ipynb
│   ├── 04_eda_football.ipynb
│   ├── 05_series_comparison.ipynb
│   ├── 06_integrity.ipynb
│   └── 07_statistical_models.ipynb
│
├── src/
│   ├── ingestion/
│   ├── cleaning/
│   ├── features/
│   ├── analysis/
│   ├── models/
│   └── visualization/
│
├── reports/
│   ├── figures/
│   ├── tables/
│   └── drafts/
│
├── docs/
│   ├── data_dictionary.md
│   ├── methodology.md
│   └── sources.md
│
├── tests/
│
└── requirements.txt
```

---

# 29. Regras de qualidade dos dados

Cada dataset deverá possuir:

* fonte;
* URL;
* data de coleta;
* período;
* licença, quando conhecida;
* metodologia de coleta;
* versão;
* nível de confiabilidade.

Nenhum dado deverá entrar na base final sem registrar sua origem.

---

# 30. Data Dictionary

Será obrigatório manter um dicionário de dados.

Exemplo:

| Campo          | Tipo    | Fonte     | Descrição                |
| -------------- | ------- | --------- | ------------------------ |
| `match_id`     | string  | Sofascore | identificador da partida |
| `season`       | integer | CBF       | temporada                |
| `serie`        | string  | CBF       | divisão                  |
| `fouls`        | integer | dataset   | faltas cometidas         |
| `yellow_cards` | integer | dataset   | cartões amarelos         |
| `player`       | string  | dataset   | jogador                  |
| `minute`       | integer | dataset   | minuto do evento         |

---

# 31. Validação cruzada

Sempre que possível:

```text
Dataset A
   ↓
Dataset B
   ↓
CBF
   ↓
amostra validada
```

Exemplo:

* selecionar 100 partidas;
* comparar gols;
* cartões;
* faltas;
* jogadores;
* datas.

Registrar divergências.

---

# 32. Limitações esperadas

## Principal limitação

O volume financeiro detalhado das apostas por mercado provavelmente não estará disponível publicamente.

Portanto, o projeto deverá diferenciar:

### Dados observados

* eventos da partida;
* resultados;
* estatísticas;
* patrocínios.

### Proxies

* Google Trends;
* número de operadores;
* exposição do clube.

### Dados restritos

* volume de apostas;
* contas;
* distribuição financeira;
* timestamps completos das apostas.

---

# 33. Princípio de interpretação

Os resultados deverão ser classificados como:

### Associação

```text
X está associado a Y.
```

### Evidência de alteração

```text
Y apresentou comportamento diferente após X.
```

### Evidência de anomalia

```text
Y apresentou comportamento estatisticamente incomum.
```

### Evidência de manipulação

Só utilizar quando houver confirmação independente por:

* investigação;
* decisão judicial;
* órgão de integridade;
* autoridade competente.

Um `Anomaly Score` nunca será tratado sozinho como prova de manipulação.

---

# 34. MVP da pesquisa

A primeira versão não precisa de todas as variáveis.

## MVP 1 — Futebol

Período:

**2015–2025**

Dados:

* Série;
* clube;
* partida;
* resultado;
* pontos;
* gols;
* faltas;
* cartões;
* escanteios;
* jogador;
* minuto do cartão.

Objetivo:

**construir a linha histórica do futebol.**

---

## MVP 2 — Bets

Adicionar:

* Google Trends;
* operadores;
* marcas;
* patrocínios;
* clubes patrocinados.

Objetivo:

**medir exposição às bets.**

---

## MVP 3 — EDA

Produzir:

* evolução temporal;
* A/B/C/D;
* correlações;
* distribuição;
* outliers.

---

## MVP 4 — Integridade

Adicionar:

* eventos individuais;
* análise de cartões;
* análise de faltas;
* timing;
* jogadores;
* Anomaly Score.

---

## MVP 5 — Validação

Adicionar:

* casos conhecidos;
* investigações;
* alertas de integridade.

---

## MVP 6 — Modelagem

Somente depois dos resultados exploratórios:

* painel;
* efeitos fixos;
* diferença-em-diferenças;
* interação BET × SÉRIE;
* modelos de anomalia.

---

# 35. Primeiro objetivo técnico

Antes de desenvolver qualquer modelo estatístico:

> **Construir uma base histórica confiável do Campeonato Brasileiro entre 2015 e 2025, com partidas, clubes, séries, faltas, cartões, jogadores e eventos.**

Depois:

> **Construir uma série histórica de exposição do futebol brasileiro às bets.**

Somente então:

> **Cruzar as duas bases.**

---

# 36. Primeiro conjunto de análises

A primeira EDA deverá responder:

1. Como evoluíram faltas por partida?
2. Como evoluíram cartões por partida?
3. Como evoluíram escanteios?
4. Como evoluíram pênaltis?
5. Como evoluiu a frequência de cartões por jogador?
6. As mudanças foram diferentes entre A/B/C/D?
7. Existe quebra de tendência após 2018?
8. Existe outra quebra após 2023?
9. Existe outra alteração após 2025?
10. A exposição às bets acompanha essas alterações?
11. Quais jogadores apresentam maiores desvios?
12. Quais partidas apresentam maiores anomalias?

---

# 37. Resultado esperado

O projeto não parte da premissa de que:

> "as bets estão manipulando o futebol".

O objetivo é determinar, com dados:

> **se a expansão das apostas esportivas esteve associada a transformações mensuráveis no futebol brasileiro e se determinados eventos de jogo apresentam padrões estatisticamente anormais compatíveis com maior risco de integridade.**

O resultado poderá apontar:

### Cenário A

Nenhuma associação relevante.

### Cenário B

Associação econômica, mas não esportiva.

### Cenário C

Alterações esportivas associadas à exposição.

### Cenário D

Alterações estatísticas em eventos específicos.

### Cenário E

Padrões anômalos concentrados em determinados mercados/jogadores.

### Cenário F

Padrões anômalos que coincidem com casos conhecidos de manipulação.

Cada cenário possui uma interpretação diferente.

---

# 38. Critério de sucesso

O projeto será considerado bem-sucedido se conseguir:

1. construir uma base histórica reproduzível;
2. documentar as fontes;
3. medir a expansão das bets;
4. medir a exposição dos clubes;
5. comparar A/B/C/D;
6. identificar alterações estatísticas;
7. detectar outliers;
8. comparar outliers com casos conhecidos;
9. separar correlação de causalidade;
10. produzir resultados reproduzíveis.

---

# 39. Ordem de execução

```text
FASE 1
Mapeamento de fontes
        ↓
FASE 2
Coleta dos dados
        ↓
FASE 3
Padronização
        ↓
FASE 4
Construção do dataset
        ↓
FASE 5
Validação
        ↓
FASE 6
EDA
        ↓
FASE 7
Análise por Série
        ↓
FASE 8
Análise de integridade
        ↓
FASE 9
Detecção de anomalias
        ↓
FASE 10
Comparação com casos conhecidos
        ↓
FASE 11
Modelagem estatística
        ↓
FASE 12
Redação do artigo
```

---

# 40. Próxima tarefa do projeto

A próxima tarefa é **não desenvolver modelos ainda**.

Deve ser realizada uma auditoria das fontes de dados para responder objetivamente:

```text
1. Quais bases possuem faltas por jogador?
2. Quais possuem cartões por jogador?
3. Quais possuem minuto do evento?
4. Quais possuem pênaltis?
5. Quais possuem escanteios?
6. Quais possuem odds históricas?
7. Quais possuem mercados de cartões?
8. Quais possuem mercados de faltas?
9. Quais possuem volume de apostas?
10. Quais possuem histórico suficiente entre 2015 e 2025?
11. Quais possuem API?
12. Quais são gratuitas?
13. Quais possuem restrições de uso?
14. Quais podem ser utilizadas academicamente?
```

O resultado dessa auditoria deverá produzir uma **matriz definitiva de fontes**, que será utilizada para decidir o desenho final da pesquisa.
