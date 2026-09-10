# Dicionário de Dados — Datasets Processados da Série A

**Projeto:** Impacto das Apostas Esportivas no Futebol Brasileiro  
**Localização dos Arquivos:** `data/processed/serie_a/`  
**Formatos Disponíveis:** CSV (UTF-8) e Apache Parquet (`pyarrow`)  
**Data da Versão:** 2026-09-05  

---

## 1. Visão Geral da Arquitetura de Dados

Os datasets da Série A foram normalizados a partir dos dados brutos do Adão Duque (2003–2024), estruturados em modelo relacional indexado por chaves primárias e estrangeiras:

```text
       ┌──────────────────────┐
       │       partidas       │
       │  (PK: partida_id)    │
       └──────────┬───────────┘
                  │ 1
                  │
        ┌─────────┼─────────┐
        │ N       │ N       │ N
        ▼         ▼         ▼
   ┌─────────┐┌─────────┐┌─────────┐
   │ cartoes ││estatist.││  gols   │
   └─────────┘└─────────┘└─────────┘
```

---

## 2. Dataset: `partidas` (`partidas.parquet` / `partidas.csv`)
* **Descrição:** Registros consolidados de cada partida disputada na Série A do Campeonato Brasileiro de 2003 a 2024.
* **Granularidade:** 1 linha por partida.
* **Volume:** 8.785 partidas.
* **Chave Primária:** `partida_id`.

| Campo | Tipo | Nulos | Descrição | Regras e Valores Válidos |
| :--- | :--- | :---: | :--- | :--- |
| `partida_id` | `int64` | Não | Identificador único numérico da partida | Sequencial de 1 a 8.785 |
| `temporada` | `int64` | Não | Ano oficial da edição da competição | 2003 a 2024 (ex.: jogos de fev/2021 são `2020`) |
| `rodada` | `int64` | Não | Número da rodada do campeonato | 1 a 38 (ou 42 em 2005, 46 em 2003/04) |
| `data` | `string` | Não | Data da realização da partida | Formato ISO 8601 (`YYYY-MM-DD`) |
| `horario` | `string` | Sim | Horário de início da partida | Formato `HH:MM` |
| `clube_mandante` | `string` | Não | Nome original do clube mandante | Ex.: "São Paulo", "Athletico-PR" |
| `clube_mandante_slug` | `string` | Não | Slug canônico do clube mandante | Ex.: `sao_paulo`, `athletico_pr` |
| `clube_visitante` | `string` | Não | Nome original do clube visitante | Ex.: "Palmeiras", "Flamengo" |
| `clube_visitante_slug` | `string` | Não | Slug canônico do clube visitante | Ex.: `palmeiras`, `flamengo` |
| `gols_mandante` | `int64` | Sim | Gols marcados pelo time mandante | Nulo apenas em partidas canceladas (W.O.) |
| `gols_visitante` | `int64` | Sim | Gols marcados pelo time visitante | Nulo apenas em partidas canceladas (W.O.) |
| `total_gols` | `int64` | Sim | Somatório de gols da partida | $\ge 0$ |
| `saldo_mandante` | `int64` | Sim | `gols_mandante - gols_visitante` | Positivo se mandante venceu |
| `resultado` | `string` | Não | Desfecho final da partida | `Vitoria Mandante`, `Empate`, `Vitoria Visitante` |
| `vencedor` | `string` | Não | Nome do time vencedor ou "Empate" | Ex.: "Flamengo" ou "-" |
| `arena` | `string` | Não | Nome do estádio onde ocorreu o jogo | Ex.: "Maracanã", "Allianz Parque" |
| `mandante_uf` | `string` | Não | Estado (UF) do clube mandante | Sigla com 2 caracteres (ex.: `SP`, `RJ`, `RS`) |
| `visitante_uf` | `string` | Não | Estado (UF) do clube visitante | Sigla com 2 caracteres |
| `formacao_mandante` | `string` | Sim | Esquema tático do clube mandante | Ex.: "4-2-3-1", "4-3-3" (disponível pós-2015) |
| `formacao_visitante`| `string` | Sim | Esquema tático do clube visitante | Ex.: "3-5-2", "4-4-2" |
| `tecnico_mandante` | `string` | Sim | Nome do treinador do mandante | Ex.: "Abel Ferreira" |
| `tecnico_visitante` | `string` | Sim | Nome do treinador do visitante | Ex.: "Rogério Ceni" |

---

## 3. Dataset: `cartoes` (`cartoes.parquet` / `cartoes.csv`)
* **Descrição:** Registro individual de cada advertência disciplinar (amarela ou vermelha) aplicada no Campeonato Brasileiro da Série A entre 2014 e 2024.
* **Granularidade:** 1 linha por cartão aplicado.
* **Volume:** 20.953 cartões.
* **Chave Estrangeira:** `partida_id` $\rightarrow$ `partidas.partida_id`.

| Campo | Tipo | Nulos | Descrição | Regras e Valores Válidos |
| :--- | :--- | :---: | :--- | :--- |
| `partida_id` | `int64` | Não | ID da partida correspondente | FK para `partidas` |
| `temporada` | `int64` | Não | Ano da edição do campeonato | 2014 a 2024 |
| `rodada` | `int64` | Não | Rodada em que ocorreu o cartão | 1 a 38 |
| `clube` | `string` | Não | Clube do atleta punido | Ex.: "Corinthians" |
| `clube_slug` | `string` | Não | Slug padronizado do clube | Ex.: `corinthians` |
| `cartao` | `string` | Não | Tipo de advertência disciplinar | `Amarelo` (19.867) ou `Vermelho` (1.086) |
| `atleta` | `string` | Não | Nome completo do atleta punido | "Nao Informado" em 6 registros históricos |
| `atleta_slug` | `string` | Não | Slug canônico do atleta | Lowercase, sem acento (ex.: `fagner`) |
| `num_camisa` | `Int64` | Sim | Número da camisa do jogador | Nullable integer (386 ausentes na origem) |
| `posicao` | `string` | Não | Posição tática em campo | `Meio-campo`, `Zagueiro`, `Atacante`, `Goleiro`, `Nao Informada` |
| `minuto_continuo` | `int64` | Não | Minuto acumulado do cartão | Soma tempo nominal e acréscimos (`45+2'` $\rightarrow$ 47) |
| `minuto_nominal` | `int64` | Não | Minuto oficial de relógio | Ex.: 45, 90 |
| `acrescimo` | `int64` | Não | Minutos concedidos de tempo adicional | $\ge 0$ (ex.: 2 para `45+2`) |
| `periodo` | `string` | Não | Etapa da partida em que ocorreu | `1T` ($\le 45'$) ou `2T` ($> 45'$) |

---

## 4. Dataset: `estatisticas` (`estatisticas.parquet` / `estatisticas.csv`)
* **Descrição:** Scouts consolidados por clube em cada partida da Série A (2003–2024).
* **Granularidade:** 2 linhas por partida (1 mandante, 1 visitante).
* **Volume:** 17.570 registros.
* **Chave Estrangeira:** `partida_id` $\rightarrow$ `partidas.partida_id`.

| Campo | Tipo | Nulos | Descrição | Regras e Valores Válidos |
| :--- | :--- | :---: | :--- | :--- |
| `partida_id` | `int64` | Não | ID da partida correspondente | FK para `partidas` |
| `temporada` | `int64` | Não | Edição do campeonato | 2003 a 2024 |
| `rodada` | `int64` | Não | Rodada da partida | 1 a 38/42/46 |
| `clube` | `string` | Não | Clube correspondente às estatísticas | Ex.: "Gremio" |
| `clube_slug` | `string` | Não | Slug padronizado do clube | Ex.: `gremio` |
| `chutes` | `int64` | Não | Total de finalizações tentadas | $\ge 0$ |
| `chutes_no_alvo` | `int64` | Não | Finalizações que acertaram o gol | $\le chutes$ |
| `posse_de_bola_pct`| `float64` | Sim | Percentual de posse de bola | Escala decimal `[0.0, 1.0]` (ex.: 0.53 para 53%) |
| `passes` | `int64` | Não | Total de passes tentados | $\ge 0$ |
| `precisao_passes_pct`| `float64` | Sim | Taxa de acerto de passes | Escala decimal `[0.0, 1.0]` |
| `faltas` | `int64` | Não | Total de faltas cometidas pelo clube | $\ge 0$ |
| `cartao_amarelo` | `int64` | Não | Cartões amarelos recebidos | Agregação por clube |
| `cartao_vermelho` | `int64` | Não | Cartões vermelhos recebidos | Agregação por clube |
| `impedimentos` | `int64` | Não | Total de impedimentos assinalados | $\ge 0$ |
| `escanteios` | `int64` | Não | Total de escanteios a favor | $\ge 0$ |
| `scouts_validos` | `bool` | Não | Indicador de confiabilidade dos scouts | `True` para 2015–2023; `False` para 2003–2013 e 2024 |

---

## 5. Dataset: `gols` (`gols.parquet` / `gols.csv`)
* **Descrição:** Registro de todos os gols marcados no Brasileirão Série A entre 2014 e 2024.
* **Granularidade:** 1 linha por gol marcado.
* **Volume:** 9.861 gols.
* **Chave Estrangeira:** `partida_id` $\rightarrow$ `partidas.partida_id`.

| Campo | Tipo | Nulos | Descrição | Regras e Valores Válidos |
| :--- | :--- | :---: | :--- | :--- |
| `partida_id` | `int64` | Não | ID da partida | FK para `partidas` |
| `temporada` | `int64` | Não | Edição do campeonato | 2014 a 2024 |
| `rodada` | `int64` | Não | Rodada da partida | 1 a 38 |
| `clube` | `string` | Não | Clube do autor do gol | Ex.: "Flamengo" |
| `clube_slug` | `string` | Não | Slug padronizado do clube | Ex.: `flamengo` |
| `atleta` | `string` | Não | Nome do autor do gol | "Nao Informado" quando ausente |
| `atleta_slug` | `string` | Não | Slug canônico do atleta | Ex.: `gabriel_barbosa` |
| `minuto_continuo` | `int64` | Não | Minuto contínuo em que o gol saiu | $\ge 0$ |
| `minuto_nominal` | `int64` | Não | Minuto regulamentar de relógio | Ex.: 45, 90 |
| `acrescimo` | `int64` | Não | Minutos de acréscimo | $\ge 0$ |
| `periodo` | `string` | Não | Etapa do gol | `1T` ou `2T` |
| `tipo_de_gol` | `string` | Não | Modo de conversão do gol | `Normal` (8.678), `Penalty` (935), `Gol Contra` (248) |

---

## 6. Datasets de Apostas e Exposição (`data/processed/betting/`)

### 6.1 Dataset: `trends_mensal` e `trends_anual`
* **Descrição:** Série histórica de interesse por apostas esportivas no Brasil extraída do Google Trends (2015–2025).
* **Granularidade:** Mensal (132 registros) e Anual (11 registros).
* **Campos Principais:**
  * `ano` (`int64`): Temporada de referência (2015–2025).
  * `mes` (`int64`, mensal): Mês de referência (1 a 12).
  * `fase_regulatoria` (`string`): `Pre-Legalizacao`, `Legalizacao_Expansao`, `Regulamentacao`, `Mercado_Regulado`.
  * `google_trends_score` (`float64`): Pontuação de interesse relativo na escala 0 a 100.
  * `trends_normalizado` (`float64`): Escala decimal `[0.0, 1.0]`.

### 6.2 Dataset: `exposicao_clubes_temporada`
* **Descrição:** Matriz histórica de patrocínios de bets e cálculo do índice de exposição dos clubes na Série A (2015–2024).
* **Granularidade:** 1 linha por clube $\times$ temporada (200 registros = 20 clubes $\times$ 10 anos).
* **Chave Composta:** `temporada` + `clube_slug`.

| Campo | Tipo | Nulos | Descrição | Regras e Valores Válidos |
| :--- | :--- | :---: | :--- | :--- |
| `temporada` | `int64` | Não | Edição do campeonato | 2015 a 2024 |
| `clube_slug` | `string` | Não | Slug canônico do clube | Ex.: `flamengo`, `palmeiras` |
| `tem_patrocinio_bet` | `bool` | Não | Indica existência de patrocínio de aposta | `True` ou `False` |
| `tipo_patrocinio_bet` | `string` | Não | Categoria da propriedade no uniforme | `master`, `mangas`, `secundario`, `nenhum` |
| `marca_principal_bet` | `string` | Não | Marca de aposta patrocinadora | Ex.: "Pixbet", "Betano" ou "Nenhum" |
| `num_marcas_bet` | `int64` | Não | Contagem de marcas de apostas vinculadas | $\ge 0$ |
| `score_posicao` | `float64` | Não | Peso da posição na camisa ($S_{\text{pos}}$) | 1.0 (master), 0.5 (mangas), 0.3 (secundário), 0.0 |
| `score_quantidade` | `float64` | Não | Multiplicidade de marcas ($S_{\text{qtd}}$) | $\min(1.0, \text{num\_marcas}/2)$ |
| `score_macro` | `float64` | Não | Ambiente macro digital ($S_{\text{macro}}$) | Média anual normalizada do Google Trends |
| `bet_exposure_clube` | `float64` | Não | Exposição contratual direta do clube | $0.75 \times S_{\text{pos}} + 0.25 \times S_{\text{qtd}} \in [0.0, 1.0]$ |
| `bet_exposure_total` | `float64` | Não | Exposição combinada com efeito macro | $0.60 \times S_{\text{pos}} + 0.15 \times S_{\text{qtd}} + 0.25 \times S_{\text{macro}} \in [0.0, 1.0]$ |
| `categoria_exposicao_clube` | `string` | Não | Classificação ordinal | `Nenhuma` ($=0$), `Baixa/Media` ($<0,7$), `Alta` ($\ge 0,7$) |
| `fonte_informacao` | `string` | Não | Origem do dado de patrocínio | IBOPE Repucom, Balanços, GE |

---

## 7. Dataset Enriquecido: `partidas_com_exposure`
* **Localização:** `data/processed/serie_a/partidas_com_exposure.parquet` (e `.csv`).
* **Volume:** 8.785 partidas (2003–2024) $\times$ 39 colunas.
* **Colunas Adicionadas ao Dataset de Partidas:**
  * `tem_bet_mandante` / `tem_bet_visitante` (`bool`): Indicadores por equipe.
  * `tipo_bet_mandante` / `tipo_bet_visitante` (`string`): `master`, `mangas`, etc.
  * `marca_bet_mandante` / `marca_bet_visitante` (`string`): Marcas patrocinadoras.
  * `exposure_clube_mandante` / `exposure_clube_visitante` (`float64`): Índices contratuais $[0.0, 1.0]$.
  * `exposure_total_mandante` / `exposure_total_visitante` (`float64`): Índices totais $[0.0, 1.0]$.
  * `exposure_clube_partida` (`float64`): Média simples entre mandante e visitante $[0.0, 1.0]$.
  * `exposure_total_partida` (`float64`): Média simples do índice total $[0.0, 1.0]$.
  * `ambos_patrocinados_bet` (`bool`): `True` se ambos os times têm patrocinador de aposta.
  * `algum_patrocinado_bet` (`bool`): `True` se ao menos um dos times tem patrocinador de aposta.
  * `categoria_exposicao_partida` (`string`): `Nenhuma`, `Parcial (1 clube)`, `Total (2 clubes)`.

---

## 8. Datasets Processados da Série B (`data/processed/serie_b/`)

Gerados a partir do parsing direto das Súmulas Eletrônicas da CBF (`conteudo.cbf.com.br/sumulas/{ano}/242{partida}se.pdf`).

### 8.1 Dataset: `partidas` (`data/processed/serie_b/partidas.parquet` e `.csv`)
* **Descrição:** Registros consolidados de partidas disputadas na Série B do Campeonato Brasileiro extraídos das súmulas oficiais.
* **Granularidade:** 1 linha por partida.
* **Campos:** `partida_id`, `temporada`, `serie` ("B"), `rodada`, `data` (ISO 8601), `horario`, `estadio`, `cidade`, `uf_estadio`, `clube_mandante`, `clube_mandante_slug`, `mandante_uf`, `clube_visitante`, `clube_visitante_slug`, `visitante_uf`, `arbitro`, `gols_mandante`, `gols_visitante`, `total_gols`, `resultado`.

### 8.2 Dataset: `cartoes` (`data/processed/serie_b/cartoes.parquet` e `.csv`)
* **Descrição:** Advertências disciplinares detalhadas, contendo pela primeira vez o texto literal do motivo da infração redigido pelo árbitro.
* **Granularidade:** 1 linha por cartão aplicado.
* **Campos Principais:**
  * `partida_id` (`int64`): Número da partida.
  * `temporada` (`int64`): Ano da edição.
  * `serie` (`string`): "B".
  * `clube` / `clube_slug` (`string`): Equipe punida.
  * `cartao` (`string`): `Amarelo` ou `Vermelho`.
  * `atleta` / `atleta_slug` (`string`): Nome do jogador punido.
  * `num_camisa` (`string`): Camisa do atleta ou comissão técnica.
  * `minuto_nominal` / `minuto_continuo` (`int64`): Minuto do cartão.
  * `periodo` (`string`): `1T` ou `2T`.
  * `motivo_completo` (`string`): Texto oficial transcrito da súmula.
  * `categoria_infracao` (`string`): Classificação temática da infração (`falta_temeraria`, `reclamacao`, `cera_retardar`, `conduta_antidesportiva`, `mao_intencional`, `outro`).

### 8.3 Dataset: `gols` (`data/processed/serie_b/gols.parquet` e `.csv`)
* **Descrição:** Gols das partidas da Série B com minutagem e tipo de lance.
* **Campos:** `partida_id`, `temporada`, `serie`, `rodada`, `clube`, `clube_slug`, `atleta`, `atleta_slug`, `minuto_nominal`, `minuto_continuo`, `acrescimo`, `periodo`, `tipo_de_gol` (`Normal`, `Penalty`, `Gol Contra`, `Falta`).

---

## 9. Dataset de Integridade: Casos Investigados da Operação Penalidade Máxima

* **Localização:** `data/processed/integrity/casos_penalidade_maxima.parquet` (e `.csv`).
* **Volume:** 14 casos investigados e judicializados (Série A e Série B, 2022).
* **Finalidade Metodológica:** Constitui o *ground truth* (base de verdade de campo) com eventos ilícitos confessados e sentenciados pelo STJD / MP-GO, permitindo calibrar modelos de triagem de anomalias e contrastar padrões comportamentais com a população geral.
* **Chave Primária:** `caso_id`.

| Campo | Tipo | Nulos | Descrição | Regras e Valores Válidos |
| :--- | :--- | :---: | :--- | :--- |
| `caso_id` | `string` | Não | Identificador único do caso catalogado | Ex.: `PM-001`, `PM-002` |
| `operacao` | `string` | Não | Nome oficial da investigação | "Operação Penalidade Máxima" |
| `temporada` | `int64` | Não | Edição do campeonato brasileiro | 2022 |
| `serie` | `string` | Não | Divisão em que ocorreu o evento | `A` ou `B` |
| `rodada` | `int64` | Não | Rodada da partida investigada | 1 a 38 |
| `data` | `string` | Não | Data da partida no formato ISO 8601 | `YYYY-MM-DD` |
| `confronto` | `string` | Não | Descrição textual da partida | Ex.: "Juventude vs Fortaleza" |
| `clube_mandante` | `string` | Não | Clube mandante | Ex.: "Juventude" |
| `clube_visitante` | `string` | Não | Clube visitante | Ex.: "Fortaleza" |
| `clube_atleta` | `string` | Não | Clube defendido pelo atleta aliciado | Ex.: "Juventude", "Santos" |
| `atleta` | `string` | Não | Nome do atleta denunciado/investigado | Ex.: "Gabriel Tota", "Paulo Miranda" |
| `atleta_slug` | `string` | Não | Slug canônico do atleta | Ex.: `gabriel_tota`, `paulo_miranda` |
| `posicao` | `string` | Não | Posição tática em campo | `Zagueiro`, `Meio-campo`, `Lateral-direito`, `Lateral-esquerdo` |
| `evento_alvo` | `string` | Não | Evento encomendado pela quadrilha | `cartao_amarelo`, `penalti_cometido`, `cartao_vermelho` |
| `minuto_alvo` | `string` | Não | Janela temporal encomendada | `1T` ou `qualquer` |
| `mercado_aposta` | `string` | Não | Mercado explorado nas casas de apostas | Ex.: "Cartao Amarelo no 1T", "Cometer Penalti no 1T" |
| `executado_com_sucesso` | `bool` | Não | Se o atleta executou a conduta acordada | `True` ou `False` |
| `evento_ocorreu` | `bool` | Não | Se a infração/punição de fato aconteceu | `True` ou `False` |
| `minuto_real` | `float64` | Sim | Minuto contínuo em que o evento ocorreu | Ex.: 38.0, 45.0 (nulo se não ocorreu) |
| `detalhes` | `string` | Não | Resumo factual da conduta e lances | Descrição textual da súmula e autos |
| `situacao_stjd` | `string` | Não | Situação jurídica no tribunal desportivo | Suspensão, Eliminação, Multa |
| `fonte_documental` | `string` | Não | Autos do processo e acórdãos oficiais | Autos MP-GO / Acórdãos STJD |

---

## 10. Dataset de Modelagem: Painel Clube x Partida

* **Localização:** `data/processed/panel/painel_clube_partida.parquet` (e `.csv`).
* **Volume:** 7.598 observações de equipe-jogo (Série A, 2015 a 2024, cobrindo 3.799 partidas disputadas).
* **Granularidade:** 1 linha por clube em cada partida disputada (2 linhas por jogo: mandante e visitante).
* **Finalidade Metodológica:** Base analítica estruturada para regressões de efeitos fixos bidirecionais (TWFE), modelos de diferença-em-diferenças (DiD) e estudos de eventos com adoção escalonada.
* **Chave Composta:** `partida_id` + `clube_slug`.

| Campo | Tipo | Nulos | Descrição | Regras e Valores Válidos |
| :--- | :--- | :---: | :--- | :--- |
| `partida_id` | `int64` | Não | ID único da partida | FK para `partidas` |
| `temporada` | `int64` | Não | Edição do campeonato | 2015 a 2024 |
| `rodada` | `int64` | Não | Rodada da competição | 1 a 38 |
| `data` | `string` | Não | Data da partida no padrão ISO 8601 | `YYYY-MM-DD` |
| `clube` / `clube_slug` | `string` | Não | Nome e slug canônico do clube observado | Ex.: `flamengo`, `palmeiras` |
| `clube_uf` | `string` | Não | Estado da federação do clube | Ex.: `RJ`, `SP` |
| `adversario_slug` | `string` | Não | Slug da equipe adversária no confronto | Ex.: `corinthians` |
| `is_mandante` | `int64` | Não | Dummy indicativa de mando de campo | 1 se mandante, 0 se visitante |
| `mesma_uf` | `int64` | Não | Dummy de clássico regional | 1 se mandante e visitante são da mesma UF |
| `gols_pro` / `gols_contra` | `int64` | Não | Gols marcados e sofridos pelo clube | $\ge 0$ |
| `saldo_gols` | `int64` | Não | Diferença de gols da equipe no jogo | `gols_pro - gols_contra` |
| `vitoria` / `derrota` / `empate` | `int64` | Não | Dummies binárias de desfecho da partida | 1 ou 0 |
| `tem_patrocinio_bet` | `bool` | Não | Clube possui patrocínio ativo de apostas | `True` ou `False` |
| `tipo_patrocinio_bet` | `string` | Não | Propriedade no uniforme | `master`, `mangas`, `secundario`, `nenhum` |
| `marca_bet` | `string` | Não | Nome da marca parceira | Ex.: `Betano`, `Pixbet` |
| `bet_exposure_clube` | `float64` | Não | Exposição contratual estrita do clube | Escala $[0.0, 1.0]$ |
| `bet_exposure_total` | `float64` | Não | Exposição combinada com ambiente macro | Escala $[0.0, 1.0]$ |
| `exposure_adversario` | `float64` | Não | Exposição total da equipe adversária | Escala $[0.0, 1.0]$ |
| `categoria_exposicao_partida` | `string` | Não | Grau de exposição do confronto | `Nenhuma`, `Parcial (1 clube)`, `Total (2 clubes)` |
| `era_var` | `int64` | Não | Presença do árbitro de vídeo | 1 para temporadas $\ge 2019$, 0 antes |
| `pos_2018` | `int64` | Não | Pós-marco legal da Lei 13.756/2018 | 1 para temporadas $\ge 2019$, 0 antes |
| `rodada_final` | `int64` | Não | Reta decisiva do campeonato | 1 se $\text{rodada} \ge 31$, 0 antes |
| `did_tratado` | `int64` | Não | Indicador de adoção de bet pós-2018 | 1 se adotou em algum momento, 0 se nunca adotou |
| `did_interacao` | `int64` | Não | Termo de interação DiD canônico | `did_tratado * pos_2018` |
| `faltas` | `int64` | Não | Faltas cometidas pelo clube | $\ge 0$ |
| `cartao_amarelo` / `cartao_vermelho` | `int64` | Não | Contagem de cartões por tipo | $\ge 0$ |
| `cartoes_totais` | `int64` | Não | Soma de amarelos e vermelhos do clube | `cartao_amarelo + cartao_vermelho` |
| `cartoes_1t` / `cartoes_2t` | `int64` | Não | Cartões recebidos por tempo de jogo | $\ge 0$ |
| `taxa_conversao` | `float64` | Sim | Cartões totais por falta cometida | `cartoes_totais / faltas` (nulo se faltas = 0) |
| `prop_cartoes_1t` | `float64` | Não | Proporção de cartões no 1º tempo | `cartoes_1t / max(cartoes_totais, 1)` |
| `gols_penalty_marcados` | `int64` | Não | Gols de pênalti convertidos pelo clube | $\ge 0$ |
| `gols_penalty_sofridos` | `int64` | Não | Gols de pênalti convertidos pelo adversário | $\ge 0$ |
| `penalti_na_partida` | `int64` | Não | Houve pênalti convertido no confronto | 1 ou 0 |
| `scouts_validos` | `bool` | Não | Confiabilidade dos dados de faltas | `True` para 99,95% das observações |



