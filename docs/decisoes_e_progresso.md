# Registro de Decisões, Progresso e Próximos Passos

**Projeto:** Impacto das Apostas Esportivas no Futebol Brasileiro  
**Documento Vivo de Governança:** Conforme seções 16 e 17 do `.agent.md`  
**Última Atualização:** 2026-09-10  

---

## 1. Síntese do Progresso até o Momento

* **Alinhamento Metodológico:**
  * Postura de parceiro analítico crítico e investigativo: primazia dos dados empíricos, separação rigorosa entre associação, quebra estrutural, anomalia e acusação de manipulação.
  * Estabelecido que o volume financeiro granular por aposta é dado sigiloso das operadoras e permanece fora do caminho crítico do projeto.
* **Auditoria de Fontes e Dados Brutos:**
  * Mapeamento comparativo das fontes primárias e secundárias (Adão Duque, Súmulas CBF, Sofascore, Football-Data.co.uk, SPA/MF, Google Trends).
* **Fase 1 Concluída (Ingestão Série A):**
  * Script automatizado: [`src/ingestion/download_adaoduque.py`](file:///d:/Python%20Projetos/analise-bets/src/ingestion/download_adaoduque.py).
  * Dados brutos preservados intactos em [`data/raw/adaoduque/`](file:///d:/Python%20Projetos/analise-bets/data/raw/adaoduque/) com manifesto de integridade criptográfica SHA-256 ([`manifest.json`](file:///d:/Python%20Projetos/analise-bets/data/raw/adaoduque/manifest.json)).
  * Relatório Técnico emitido: [`reports/analysis/01_auditoria_dados_brutos_adaoduque.md`](file:///d:/Python%20Projetos/analise-bets/reports/analysis/01_auditoria_dados_brutos_adaoduque.md).
* **Fase 2 Concluída (Limpeza e Normalização Série A):**
  * Script automatizado: [`src/cleaning/clean_serie_a.py`](file:///d:/Python%20Projetos/analise-bets/src/cleaning/clean_serie_a.py).
  * Suíte de testes unitários e de integração validada com 100% de aprovação ([`tests/test_clean_serie_a.py`](file:///d:/Python%20Projetos/analise-bets/tests/test_clean_serie_a.py)).
  * Particionamento temporal determinístico das 22 temporadas (2003 a 2024), corrigindo a distorção do calendário COVID-19 (todas as 380 partidas da edição de 2020 receberam canonicamente `temporada = 2020`, inclusive as 112 partidas disputadas em janeiro e fevereiro de 2021).
  * Decomposição da minutagem de cartões e gols (`minuto_continuo`, `minuto_nominal`, `acrescimo`, `periodo`).
  * Padronização de slugs para 45 clubes e para os atletas, preservando texto UTF-8 original.
  * Dados derivados gravados em formato duplo (CSV UTF-8 e Parquet) em [`data/processed/serie_a/`](file:///d:/Python%20Projetos/analise-bets/data/processed/serie_a/) com manifesto `manifest_processed.json`:
    * `partidas`: 8.785 partidas x 22 colunas.
    * `cartoes`: 20.953 registros x 14 colunas.
    * `estatisticas`: 17.570 registros x 16 colunas.
    * `gols`: 9.861 registros x 12 colunas.
* **Fase 3 Concluída (EDA Profunda Série A e Testes de Hipótese):**
  * Script analítico modular: [`src/analysis/eda_serie_a.py`](file:///d:/Python%20Projetos/analise-bets/src/analysis/eda_serie_a.py).
  * Relatório Técnico emitido: [`reports/analysis/02_eda_profunda_serie_a.md`](file:///d:/Python%20Projetos/analise-bets/reports/analysis/02_eda_profunda_serie_a.md).
  * Geradas 5 figuras analíticas em alta resolução em [`reports/figures/eda_serie_a/`](file:///d:/Python%20Projetos/analise-bets/reports/figures/eda_serie_a/).
  * Geradas 3 tabelas estatísticas em [`reports/tables/`](file:///d:/Python%20Projetos/analise-bets/reports/tables/).
  * Comprovação estatística rigorosa de quebras de tendência entre os períodos Pré-Bets (2014–2018) e Alta Exposição (2022–2024).
* **Fase 4 Concluída (Camada de Exposição às Bets e MVP 2):**
  * Script de ingestão: [`src/ingestion/build_betting_data.py`](file:///d:/Python%20Projetos/analise-bets/src/ingestion/build_betting_data.py).
  * Matriz histórica completa de patrocínios cobrindo 200 registros (20 clubes x 10 temporadas na Série A, 2015–2024) e série mensal/anual do Google Trends Brasil (2015–2025) armazenadas em `data/raw/betting/` com manifesto SHA-256.
  * Script de limpeza e cálculo do índice: [`src/cleaning/clean_betting.py`](file:///d:/Python%20Projetos/analise-bets/src/cleaning/clean_betting.py).
  * Implementação do índice contínuo `BET_EXPOSURE` em duas vertentes: `bet_exposure_clube` (estritamente contratual) e `bet_exposure_total` (contratual + transbordamento macro do Google Trends).
  * Enriquecimento da base consolidada de partidas (`data/processed/serie_a/partidas_com_exposure.parquet` com 8.785 jogos e 39 colunas).
  * Suíte de testes unitários com 11 testes aprovados com 100% de sucesso via pytest ([`tests/test_clean_betting.py`](file:///d:/Python%20Projetos/analise-bets/tests/test_clean_betting.py)).
  * Script analítico e visual: [`src/analysis/eda_bets.py`](file:///d:/Python%20Projetos/analise-bets/src/analysis/eda_bets.py).
  * Relatório Técnico emitido: [`reports/analysis/03_camada_exposicao_bets.md`](file:///d:/Python%20Projetos/analise-bets/reports/analysis/03_camada_exposicao_bets.md).
  * Geradas 5 figuras em alta resolução em [`reports/figures/eda_bets/`](file:///d:/Python%20Projetos/analise-bets/reports/figures/eda_bets/) e 3 tabelas consolidadas em [`reports/tables/`](file:///d:/Python%20Projetos/analise-bets/reports/tables/).

---

## 2. Registro de Decisões Tomadas

Classificadas conforme a taxonomia da Seção 17 do `.agent.md`:

### 2.1 Decisões Estratégicas e de Negócio (Decididas pelo Usuário)
* **D-EST-01: Priorização da Ingestão da Série A (Adão Duque):**
  * *Decisão:* Iniciar a coleta e limpeza pela Série A do Brasileirão utilizando o repositório consolidado do Adão Duque antes de avançar para as demais divisões ou modelagem econométrica.
  * *Justificativa:* Viabiliza rapidamente o MVP 1 (base histórica do futebol) e o MVP 4 (integridade e cartões na divisão principal) com dados auditáveis.
* **D-EST-02: Dados de Volume Financeiro de Apostas Fora do Caminho Crítico:**
  * *Decisão:* Não bloquear a pesquisa buscando dados privados de faturamento/volume apostado por mercado granular (sigilo comercial das casas). Tratar volume real como camada estritamente opcional e focar em proxies públicas (Google Trends, patrocínios e licenças oficiais SPA/MF).
  * *Justificativa:* Evita paralisia do projeto por indisponibilidade de dados proprietários não públicos.
* **D-EST-03: Sequenciamento Estrito de Fases (EDA Antes de Modelos):**
  * *Decisão:* Não estimar modelos de regressão, efeitos fixos ou diferença-em-diferenças antes de esgotar a análise exploratória profunda e os testes de quebra estrutural.
  * *Justificativa:* Evita especificação espúria de modelos sem conhecimento prévio da distribuição empírica das séries temporais.
* **D-EST-04: Matriz Histórica de Patrocínios Auditável (MVP 2):**
  * *Decisão:* Compilar a matriz de 200 registros clube $\times$ temporada da Série A (2015–2024) com base nos dados censitários do IBOPE Repucom (*Mapa do Patrocínio*), balanços patrimoniais oficiais dos clubes e imprensa de negócios esportivos, preservando rastreabilidade de marca, tipo de propriedade e fonte documental (`docs/sources.md`).
* **D-EST-05: Resolução da Dualidade Contratual vs. Transbordamento Macro (Questão 3.1):**
  * *Decisão:* O usuário aprovou a recomendação técnica de gerar duas métricas complementares no cálculo do `BET_EXPOSURE`: uma dimensão estritamente contratual (`bet_exposure_clube`), onde clubes sem patrocínio possuem índice zero absoluto, e uma dimensão combinada (`bet_exposure_total`), que incorpora o transbordamento macroeconômico do interesse digital nacional via Google Trends.

### 2.2 Decisões Analíticas (Recomendadas pelo Agente e Validadas pelo Impacto)
* **D-ANA-01: Temporalidade por "Temporada / Edição" e não "Ano Civil":**
  * *Decisão:* As métricas temporais devem ser agrupadas pela edição da competição (`temporada`), e não pela data civil pura de realização da partida.
  * *Impacto:* Corrige a anomalia do calendário da pandemia de COVID-19 (Brasileirão 2020 foi concluído em 25/02/2021). Uma divisão ingênua por ano civil geraria 268 jogos em 2020 e 492 jogos em 2021.
* **D-ANA-02: Diagnóstico e Tratamento da Lacuna de Faltas/Scouts de 2024:**
  * *Decisão:* Não descartar a temporada 2024 do Adão Duque. Manter a base de cartões individuais (`cartoes.csv`), que está 100% íntegra (2.096 cartões em 379 partidas em 2024), e complementar faltas e escanteios totais de 2024 via fonte secundária (súmulas CBF).
  * *Impacto:* Preserva a integridade de 2024 para análises de cartões e gols sem contaminar a série de scouts.
* **D-ANA-03: Estratégia Híbrida para Séries B, C e D:**
  * *Decisão:* Adotar as Súmulas Eletrônicas da CBF como fonte oficial, gratuita e unificada para cobrir as divisões de acesso e atender à pergunta central de pesquisa (comparação Séries A vs. B/C/D).
* **D-ANA-04: Minutagem Contínua e Decomposição de Acréscimos:**
  * *Decisão:* Para eventos de partida (cartões e gols), criar a variável `minuto_continuo` somando o minuto nominal aos acréscimos (ex.: `45+2'` $\rightarrow$ 47; `90+4'` $\rightarrow$ 94) para viabilizar curvas de sobrevivência e densidade contínua, preservando também `minuto_nominal`, `acrescimo` e `periodo` (`1T`/`2T`).
* **D-ANA-05: Janelas Temporais de Contraste para Testes de Hipótese:**
  * *Decisão:* Definir o período **2014–2018** como grupo de controle basal (**Pré-Bets**) e **2022–2024** como grupo de tratamento (**Alta Exposição e Escândalos**). O período intermediário 2019–2021 é tratado como janela de transição (introdução do VAR e pandemia).
  * *Impacto:* Permite isolar o efeito da maturidade do mercado de apostas com alto poder estatístico.
* **D-ANA-06: Métrica de Conversão Faltas $\rightarrow$ Cartões como Indicador de Severidade:**
  * *Decisão:* Adotar a razão $\text{Taxa} = \frac{\text{Cartões Totais}}{\text{Faltas Cometidas}}$ como métrica central para capturar se alterações disciplinares decorrem de violência de jogo ou de mudanças na sensibilidade arbitral.
* **D-ANA-07: Dualidade no Cálculo do Índice `BET_EXPOSURE` (Contratual vs. Total):**
  * *Decisão:* Implementar duas variáveis de exposição no nível do clube: `bet_exposure_clube` (estritamente contratual, $0.0$ para clubes sem bet) e `bet_exposure_total` (incluindo transbordamento macro do Google Trends), atendendo à sugestão validada pelo usuário.
* **D-ANA-08: Categorização das Partidas por Exposição:**
  * *Decisão:* Estratificar os jogos contemporâneos (2019–2024) em `Nenhuma` (0 clubes com bet), `Parcial` (1 clube com bet) e `Total` (ambos com bet) para viabilizar testes de dose-resposta.

### 2.3 Decisões Técnicas (Decididas pelo Agente)
* **D-TEC-01: Governança do Diretório de Dados Brutos:**
  * *Decisão:* Diretório `data/raw/adaoduque/` e `data/raw/betting/` mantidos em modo estritamente imutável (read-only). Toda e qualquer transformação deve gerar arquivos derivados em `data/processed/`.
* **D-TEC-02: Rastreabilidade via Checksums e Manifestos:**
  * *Decisão:* Geração de `manifest.json` com hashes SHA-256 na ingestão e `manifest_processed.json` no processamento (armazenando linhas, colunas e bytes exatos de cada arquivo gerado).
* **D-TEC-03: Modularização e Pacotes em `src/`:**
  * *Decisão:* Estruturar o projeto em pacotes Python bem delineados: `src/ingestion`, `src/cleaning`, `src/analysis`, `src/models`, `src/visualization`.
* **D-TEC-04: Persistência Dual em CSV e Apache Parquet:**
  * *Decisão:* Gravação dos dados processados simultaneamente em CSV (compatibilidade e inspeção rápida) e Parquet colunar via PyArrow (alta performance para consultas analíticas).
* **D-TEC-05: Automação de Figuras e Tabelas de Auditoria:**
  * *Decisão:* Os scripts de análise devem salvar tabelas descritivas em `reports/tables/` e figuras vetoriais/alta resolução em `reports/figures/`, garantindo reprodutibilidade de ponta a ponta.
* **D-TEC-06: Suíte de Testes Automatizada com Pytest:**
  * *Decisão:* Validação contínua com 11 testes unitários em `tests/` cobrindo consistência de limites matemáticos $[0.0, 1.0]$, integridade referencial relacional e regras de negócio.

---

## 3. Fatos e Evidências Auditadas

1. **Volume Histórico de Cartões (Série A 2014–2024):**
   * Cobertura de 11 temporadas completas com 20.953 cartões individuais cadastrados com atleta, clube, minuto e posição.
   * A média de cartões por jogo subiu de **5,054** (2014–2018) para **5,469** (2022–2024), uma quebra de **+8,20%** com significância extrema ($p = 4,01 \times 10^{-6}$, Mann-Whitney $p = 1,38 \times 10^{-5}$).
   * O ano de **2023** bateu o recorde absoluto de cartões totais (2.118 advertências) e **2024** bateu o recorde de expulsões (128 cartões vermelhos, 6,11% do total).
2. **O "Paradoxo Disciplinar" (Faltas vs. Cartões):**
   * As faltas por jogo declinaram significativamente de **30,73** (2015–2018) para **27,78** (2022–2023), uma queda de **-9,62%** ($p = 5,11 \times 10^{-22}$).
   * Simultaneamente, a taxa de conversão de faltas em cartões disparou **+17,79%** ($p = 1,14 \times 10^{-16}$), passando de 1 cartão a cada ~5,9 faltas para 1 a cada 5,0 faltas.
3. **Concentração Intrajogo (1º Tempo vs. 2º Tempo):**
   * Na média geral da liga, **34,5%** dos cartões saem no 1º tempo e **65,5%** no 2º tempo.
   * Foi identificado um cluster de atletas na era recente que acumulam entre **55% e 68,8%** de seus cartões no 1º tempo.
4. **Validação com Casos Conhecidos (Operação Penalidade Máxima 2022):**
   * Na nossa base de 2022, **Gabriel Tota** recebeu 2 cartões na Série A, ambos no 1º tempo (minuto médio 38,5').
   * **Paulo Miranda** recebeu 3 de seus 5 cartões na Série A de 2022 no 1º tempo (minuto médio 35,8').
   * Isso valida que o desvio temporal prematuro de cartões espelha o comportamento das fraudes confessadas e judicialmente investigadas.
5. **Efeito do Árbitro de Vídeo (VAR) sobre Pênaltis:**
   * Os gols de pênalti saltaram de uma média de ~75 por ano (0,19/jogo em 2014–2018) para picos de 111 (0,29/jogo em 2020) e 98 (0,26/jogo em 2022), coincidindo exatamente com a introdução do VAR no Brasil em maio de 2019.
6. **Efeito Dose-Resposta da Exposição a Bets sobre Cartões (2019–2024):**
   * Partidas com **Exposição Total** (ambas as equipes patrocinadas por bets, $N=1.472$) registraram **5,209** cartões por jogo contra **4,542** cartões em partidas **Sem Exposição** ($N=142$). A diferença de **+0,667 cartões/jogo (+14,68%)** é altamente significativa ($t = 3,3091, p = 1,14 \times 10^{-3}$; Mann-Whitney $U = 118.952, p = 6,08 \times 10^{-3}$).
   * A taxa de conversão faltas $\rightarrow$ cartões é de **0,1794** em jogos com Exposição Total contra **0,1602** em jogos Sem Exposição ($t = 2,6967, p = 7,73 \times 10^{-3}$).

---

## 4. Questões em Aberto e Pontos de Controle

* **Q1 (Complemento de Faltas 2024):** A coleta de faltas totais de 2024 deve ser extraída via súmulas CBF para estender a taxa de conversão faltas $\rightarrow$ cartões para o ano de 2024?
* **Q2 (Séries B, C e D):** Como estruturar o pipeline de download e parsing das súmulas da CBF para cobrir as divisões de acesso entre 2018 e 2024?
* **Q3 (Patrocínios de Bets):** **[CONCLUÍDO NO MVP 2]** Compilação histórica realizada e índice `BET_EXPOSURE` calculado e integrado com sucesso.

---

## 5. Próximos Passos Detalhados

1. **Coleta e Amostragem das Súmulas CBF (Séries B, C e D e Faltas 2024 Série A):**
   * Implementar crawler/parser para súmulas eletrônicas em PDF/HTML da CBF.
2. **Análise Comparativa de Integridade por Série (A vs. B/C/D):**
   * Contrastar a dispersão e as taxas de cartões precoces entre a Série A e a Série B (onde ocorreram os casos centrais da Penalidade Máxima).
3. **Modelagem Estatística de Painel (MVP 6):**
   * Especificar modelos com efeitos fixos de clube e tempo controlando pela interação $\text{BET} \times \text{SÉRIE}$.

