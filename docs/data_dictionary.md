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
