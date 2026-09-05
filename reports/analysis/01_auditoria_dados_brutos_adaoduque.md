# Relatório Técnico 01: Ingestão e Auditoria dos Dados Brutos (Adão Duque)

**Data:** 2026-09-05  
**Autor:** Antigravity (Data Analysis Partner)  
**Objetivo:** Ingestão, validação de integridade e auditoria temporal e de completude do dataset do Brasileirão Série A (Adão Duque).  
**Fonte:** `https://github.com/adaoduque/Brasileirao_Dataset`  
**Localização dos Arquivos:** `data/raw/adaoduque/`

---

## 1. Arquivos Ingeridos e Hashes de Integridade (SHA-256)

| Arquivo | Tamanho | SHA-256 (Truncado) | Formato |
| :--- | :--- | :--- | :--- |
| `campeonato-brasileiro-full.csv` | 1,187,343 bytes | `c09d03d36deb...` | 8,785 linhas x 16 colunas |
| `campeonato-brasileiro-estatisticas-full.csv` | 1,158,368 bytes | `f6b9a1198fbc...` | 17,570 linhas x 13 colunas |
| `campeonato-brasileiro-cartoes.csv` | 1,550,718 bytes | `4376ed95901b...` | 20,953 linhas x 8 colunas |
| `campeonato-brasileiro-gols.csv` | 509,564 bytes | `625262ca9e73...` | 9,861 linhas x 6 colunas |
| `Legenda.txt` | 2,113 bytes | `dfedf5fb55d9...` | Metadados descritivos |

---

## 2. Achados da Auditoria Estatística

### 2.1 Cobertura de Cartões Individuais (`campeonato-brasileiro-cartoes.csv`)
* **Período Coberto:** 2014 a 2024 (11 temporadas).
* **Granularidade:** Registros por cartão com atleta, time, número de camisa, posição em campo e minuto exato da advertência (incluindo acréscimos, ex.: `90+4'`).
* **Taxa de Cobertura:** ~98% a 99% das partidas da Série A possuem todos os cartões cadastrados.
* **Volume Anual:** Média de ~1.950 cartões amarelos e vermelhos por ano. Em 2024, constam 2.096 cartões em 379 partidas.
* **Avaliação:** **Excelente**. Atende com perfeição à necessidade do MVP 1 e MVP 4 (Integridade e Anomalias em Cartões) para a Série A.

### 2.2 Cobertura de Scouts por Partida (`campeonato-brasileiro-estatisticas-full.csv`)
* **Período 2003–2013:** Valores nulos/zerados para faltas, escanteios, chutes e posse (o Google não registrava widgets de scout nesses anos).
* **Período 2015–2023:** Dados íntegros de faltas cometidas, escanteios e chutes a gol por time e partida.
* **Ano 2024:** **Atenção crítica identificada.** O scraper do repositório capturou `0` para faltas, chutes e escanteios ao longo de todo o ano de 2024 (o array `stats` veio vazio da raspagem do Google).
* **Impacto:** A análise de tendências de faltas e escanteios da Série A está sólida de 2015 a 2023, mas para 2024 precisaremos complementar esses 3 indicadores agregados de outra fonte (ex.: súmulas CBF ou scraper auxiliar).

### 2.3 Efeito Calendário COVID-19 (2020 vs. 2021)
* Na agregação direta por ano civil:
  * 2020: 268 partidas
  * 2021: 492 partidas
* **Diagnóstico:** A temporada 2020 foi postergada e terminou em fevereiro de 2021.
* **Diretriz de Tratamento:** É imperativo que as métricas sejam calculadas pela variável `temporada`/`edicao`, e não por ano civil simples de data da partida, evitando distorções severas de volume.

---

## 3. Próximos Passos Recomendados

1. **Camada de Limpeza e Padronização (`src/cleaning/`):**
   * Padronizar nomes de clubes (ex.: "Athletico-PR" vs "Atlético-PR", "São Paulo" vs "Sao Paulo").
   * Tratar a coluna `minuto` dos cartões (limpar apóstrofos e somar acréscimos, ex.: `45+2'` -> 47).
   * Criar a variável `temporada` associada à rodada para corrigir o efeito COVID.
2. **Complemento de 2024 e Mapeamento Séries B, C e D:**
   * Desenvolver a rotina de coleta das súmulas oficiais da CBF para cobrir as divisões de acesso e preencher as lacunas de 2024.
