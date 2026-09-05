# Registro de Decisões, Progresso e Próximos Passos

**Projeto:** Impacto das Apostas Esportivas no Futebol Brasileiro  
**Documento Vivo de Governança:** Conforme seções 16 e 17 do [.agent.md](file:///c:/Users/filipe.barbosa/OneDrive%20-%20ICAL%20PARTICIPA%C3%87%C3%95ES%20S%20A/Desktop/Filipe/Python%20Proj/analise-bets/.agent.md)  
**Última Atualização:** 2026-09-05  

---

## 1. Síntese do Progresso até o Momento

* **Alinhamento Metodológico:** Definido o [.agent.md](file:///c:/Users/filipe.barbosa/OneDrive%20-%20ICAL%20PARTICIPA%C3%87%C3%95ES%20S%20A/Desktop/Filipe/Python%20Proj/analise-bets/.agent.md) como constituição do projeto (parceiro analítico, dados primeiro, pushback técnico, separação de fatos/hipóteses/análises/decisões, reprodutibilidade).
* **Auditoria de Fontes:** Realizada a matriz comparativa de fontes (Adão Duque, Súmulas CBF, Football-Data.co.uk, Sofascore, SPA/MF, Google Trends, Balanços de Clubes, Operação Penalidade Máxima).
* **Fase 1 Concluída (Ingestão Série A):**
  * Desenvolvido o pipeline automatizado [`src/ingestion/download_adaoduque.py`](file:///c:/Users/filipe.barbosa/OneDrive%20-%20ICAL%20PARTICIPA%C3%87%C3%95ES%20S%20A/Desktop/Filipe/Python%20Proj/analise-bets/src/ingestion/download_adaoduque.py).
  * Dados brutos baixados e salvos intactos em [`data/raw/adaoduque/`](file:///c:/Users/filipe.barbosa/OneDrive%20-%20ICAL%20PARTICIPA%C3%87%C3%95ES%20S%20A/Desktop/Filipe/Python%20Proj/analise-bets/data/raw/adaoduque/).
  * Gerado manifesto criptográfico com hashes SHA-256 (`manifest.json`) garantindo rastreabilidade e integridade.
  * Emitido o Relatório Técnico de Auditoria: [`reports/analysis/01_auditoria_dados_brutos_adaoduque.md`](file:///c:/Users/filipe.barbosa/OneDrive%20-%20ICAL%20PARTICIPA%C3%87%C3%95ES%20S%20A/Desktop/Filipe/Python%20Proj/analise-bets/reports/analysis/01_auditoria_dados_brutos_adaoduque.md).

---

## 2. Registro de Decisões Tomadas

Classificadas conforme a taxonomia da Seção 17 do `.agent.md`:

### 2.1 Decisões Estratégicas e de Negócio (Decididas pelo Usuário)
* **D-EST-01: Priorização da Ingestão Série A (Adão Duque):**
  * *Decisão:* Iniciar imediatamente a Fase 1 pela ingestão e inspeção dos dados de partidas e cartões da Série A via repositório Adão Duque, antes de modelar ou avançar para etapas posteriores.
  * *Justificativa:* Viabiliza rapidamente o MVP 1 e MVP 4 para a divisão principal, permitindo inspecionar dados empíricos reais.
* **D-EST-02: Dados de Volume de Apostas Fora do Caminho Crítico:**
  * *Decisão:* Não travar a pesquisa buscando dados privados de faturamento/volume financeiro por aposta granular, que são comercialmente sigilosos. Tratar essa camada como estritamente opcional.

### 2.2 Decisões Analíticas (Recomendadas pelo Agente e Validadas pelo Impacto)
* **D-ANA-01: Temporalidade por "Temporada / Edição" e não "Ano Civil":**
  * *Decisão:* As métricas temporais devem ser agrupadas pela edição da competição (`temporada`), e não pela data civil pura.
  * *Impacto:* Corrige a anomalia do calendário da pandemia de COVID-19 (Brasileirão 2020 foi concluído em fevereiro de 2021, gerando 268 jogos em 2020 e 492 jogos em 2021 na data calendário).
* **D-ANA-02: Diagnóstico e Tratamento da Lacuna de Faltas/Scouts de 2024:**
  * *Decisão:* Não descartar a temporada de 2024. Manter o arquivo de cartões individuais (`cartoes.csv`), que está 100% íntegro (2.096 cartões em 379 partidas em 2024), e preencher as faltas/escanteios totais de 2024 através de fonte complementar (súmulas CBF).
* **D-ANA-03: Estratégia Híbrida para Séries B, C e D:**
  * *Decisão:* Adotar as Súmulas Eletrônicas da CBF como a única fonte oficial, gratuita e unificada para cobrir as divisões de acesso e atender à pergunta central de pesquisa (comparação Séries A vs. B/C/D).

### 2.3 Decisões Técnicas (Decididas pelo Agente)
* **D-TEC-01: Governança do Diretório de Dados Brutos:**
  * *Decisão:* Criação de `data/raw/adaoduque/` como área de dados imutáveis (read-only em análises). Qualquer transformação gerará dados derivados em `data/processed/`.
* **D-TEC-02: Rastreabilidade via Checksums SHA-256:**
  * *Decisão:* Implementação de `manifest.json` com hash de cada arquivo baixado na ingestão para garantir reproducibilidade exata.
* **D-TEC-03: Modularização do Código em `src/`:**
  * *Decisão:* Divisão do código em pacotes bem delineados: `src/ingestion`, `src/cleaning`, `src/analysis`, `src/modeling`, `src/visualization`.

---

## 3. Fatos e Evidências Auditadas

1. **Cartões com Minuto e Atleta (Série A):**
   * Cobertura histórica total entre **2014 e 2024** (11 anos), com mais de 20.950 cartões cadastrados com minuto, jogador, clube e camisa.
2. **Scouts Agregados por Clube (Faltas, Chutes, Escanteios):**
   * Cobertura completa entre **2015 e 2023**. 
   * Anos de 2003 a 2013 e o ano de 2024 vieram com valores zerados no scraper do Adão Duque.
3. **Casos Conhecidos (Ground Truth):**
   * A Operação Penalidade Máxima (2022–2023) fornece um conjunto com jogadores e partidas investigadas com eventos pré-definidos (ex.: cartões encomendados no 1º tempo), servindo como grupo de teste supervisionado.

---

## 4. Questões em Aberto e Pontos de Controle

* **Q1 (CBF Scraping):** Qual a estratégia e escopo de amostragem ideal para as Séries B, C e D? (Coletar 100% das partidas ou uma janela focada 2018–2025?).
* **Q2 (Scouts de 2024):** Para a Série A de 2024, priorizaremos o complemento de faltas totais via súmulas CBF ou via API pública pontual de scout?
* **Q3 (Patrocínios de Casas de Apostas):** Estruturação da planilha histórica de mapeamento de patrocínios (Master vs. Mangas/Outros) clube a clube.

---

## 5. Próximos Passos Detalhados

1. **Pipeline de Limpeza e Normalização da Série A (`src/cleaning/clean_matches_and_cards.py`):**
   * Criar chaves padronizadas para nomes de clubes e atletas.
   * Converter a coluna `minuto` dos cartões para formato numérico contínuo (ex.: `45+2'` $\rightarrow$ 47).
   * Atribuir a coluna canônica `temporada`.
   * Salvar os dados processados em `data/processed/serie_a/`.
2. **Coleta e Amostragem das Súmulas CBF (Séries B, C e D):**
   * Construir extrator em Python para o portal de competições da CBF (focado em cartões, árbitros e borderôs).
3. **Construção da Camada de Exposição às Bets:**
   * Extrair série histórica do Google Trends (2015–2025) para os termos `bet`, `aposta`, marcas principais.
   * Mapear patrocínios de bets nos clubes da Série A e B por temporada.
4. **Primeira Análise Exploratória (EDA):**
   * Gerar as primeiras curvas de tendência temporal: cartões por partida, faltas por partida e minuto médio dos cartões antes e depois de 2018.
