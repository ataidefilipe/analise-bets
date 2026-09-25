# Relatório Técnico — Radar da Integridade

**Projeto:** Impacto das Apostas Esportivas no Futebol Brasileiro (`analise-bets`)
**Data:** 2026-09-24
**Escopo:** consolida, num único documento, o estado da solução a partir da documentação do
repositório. Não substitui as fontes. Cada seção aponta onde está o detalhe.

| Fonte principal | Conteúdo |
| :--- | :--- |
| [backend.md](backend.md) | API, banco, operação, deploy, segurança |
| [especificacao/](especificacao/README.md) | Contrato do MVP: API, regras de negócio, telas, infraestrutura, automação |
| [../frontend/docs/arquitetura.md](../frontend/docs/arquitetura.md) | Front Next.js |
| [../reports/analysis/](../reports/analysis/) | Relatórios técnicos 01 a 08 (dados, EDA, econometria, triagem, escore pré-jogo) |
| [arquivo/](arquivo/) | Registro de decisões e relatórios de execução de 16/09 e 18/09 |

> **Aviso.** O sistema mede **atipicidade estatística do perfil disciplinar**. Não mede fraude,
> não estima probabilidade de manipulação e não constitui indício contra ninguém. Essa
> restrição resulta da validação (seção 5.4) e condiciona todas as decisões de produto descritas
> aqui.

---

## Sumário

1. [Instruções de execução](#1-instruções-de-execução)
2. [Arquitetura da solução](#2-arquitetura-da-solução)
3. [Tecnologias e decisões técnicas](#3-tecnologias-e-decisões-técnicas)
4. [Testes e critérios de avaliação](#4-testes-e-critérios-de-avaliação)
5. [Resultados quantitativos e qualitativos](#5-resultados-quantitativos-e-qualitativos)
6. [Limitações e possibilidades de evolução](#6-limitações-e-possibilidades-de-evolução)

---

## 1. Instruções de execução

### 1.1 Pré-requisitos

| Item | Versão usada |
| :--- | :--- |
| Python | 3.13 (suíte validada em 3.13.5) |
| Node.js + pnpm | pnpm 11.4.0 (fixado em `frontend/package.json`) |
| Banco | SQLite (padrão local) ou PostgreSQL (Railway) |
| Rede | Necessária para baixar súmulas da CBF e as fontes do Google Fonts no build do front |

### 1.2 Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows, ative o ambiente com `.venv\Scripts\activate`.

`requirements.txt` contém **só as dependências da API e da carga** (FastAPI, Uvicorn, SQLAlchemy,
psycopg, pandas, pyarrow, SciPy, httpx). O pipeline analítico, os modelos, os notebooks e os
testes também importam bibliotecas que não estão listadas:

```bash
pip install scikit-learn statsmodels matplotlib seaborn joblib nbformat pytrends pytest
```

Essa lacuna está registrada nas limitações (seção 6.3).

### 1.3 Pipeline de dados

Os dados processados (`data/processed/`) estão versionados. **A API e o front sobem sem rodar
o pipeline.** Rode o pipeline só para atualizar a temporada corrente ou reprocessar a base.

**Atualização da temporada corrente (esteira D+1, [05 §3](especificacao/05_automacao.md)):**

```bash
python -m src.pipeline.run_delta_pipeline --ano 2026 --series A,B --skip-feed
python -m src.analysis.escalacoes_e_minutos
python -m src.models.score_pre_jogo
python -m src.pipeline.serve_product_feed
python -m src.api.carga
```

| Passo | O que faz | Tempo medido |
| :--- | :--- | ---: |
| `run_delta_pipeline` | `HEAD` em cada súmula (ETag, Last-Modified, tamanho), baixa só o que mudou, grava SHA-256, faz parsing e upsert idempotente | < 30 s por rodada |
| `escalacoes_e_minutos` | Minutos em campo por atleta | ~20 s |
| `score_pre_jogo` | Recalcula o escore pré-jogo da base inteira | ~90 s |
| `serve_product_feed` | JSON por camada e SQLite do feed | ~10–15 s |
| `src.api.carga` | Recria as tabelas de leitura da API a partir dos Parquets | ~10 s |

**Reprocessamento histórico** (após corrigir um defeito de parsing, [05 §7](especificacao/05_automacao.md)):

```bash
for spec in "A 2025" "B 2022" "B 2023" "B 2024" "B 2025"; do
  set -- $spec
  python -m src.pipeline.run_delta_pipeline --ano $2 --series $1 --skip-ingest --skip-feed
done
python -m src.analysis.escalacoes_e_minutos
python -m src.models.score_pre_jogo
python -m src.pipeline.serve_product_feed
```

**Reconstituir as súmulas brutas.** Os PDFs não são versionados. O manifesto
`data/raw/cbf/manifest_delta.json` guarda URL, ETag e SHA-256 de cada arquivo:

```bash
python -m src.pipeline.run_delta_pipeline --ano 2025 --series A,B
```

**Modelos e análises da fase de pesquisa** (cada módulo tem `__main__`):

```bash
python -m src.models.anomaly_detection
python -m src.models.ground_truth_resolver
python -m src.models.integrity_classifier
python -m src.models.validacao_out_of_sample
python -m src.analysis.precisao_e_carga_alerta
python -m src.analysis.comparacao_reconciliacao_score
python -m src.visualization.plot_anomalies
```

Os quatro notebooks em `notebooks/` (pipeline, EDA, econometria, triagem) reproduzem a
narrativa da pesquisa.

### 1.4 API (backend)

```bash
# monta o banco local e, na primeira vez, cria uma chave demo por perfil
python -m src.api.carga

# sobe a API em modo de desenvolvimento
ANALISE_BETS_AMBIENTE=dev uvicorn src.api.main:app --reload --port 8000
```

No PowerShell, defina a variável antes com `$env:ANALISE_BETS_AMBIENTE = "dev"`.

As chaves demo ficam em `data/restrito/chaves_api_poc.json`, fora do Git. Para cadastrar
chaves reais:

```bash
python -m src.api.clientes criar --nome "STJD" --perfil federacao_stjd
python -m src.api.clientes criar --nome "Compliance X" --perfil clube --clube <clube_slug>
python -m src.api.clientes listar
python -m src.api.clientes desativar --id <uuid>
```

| Variável | Padrão | Efeito |
| :--- | :--- | :--- |
| `ANALISE_BETS_DATABASE_URL` | `sqlite:///data/api/analise_bets_api.db` | Banco da API |
| `DATABASE_URL` | — | Alternativa aceita (URL do PostgreSQL injetada pelo Railway) |
| `ANALISE_BETS_AMBIENTE` | `producao` | `dev` permite subir com o segredo de desenvolvimento |
| `ANALISE_BETS_PSEUDONIMO_SECRET` | valor de desenvolvimento | Fora de `dev`, **a API não sobe** sem ele |
| `ANALISE_BETS_CORS` | `*` | Origens permitidas |

Verificação: `GET http://localhost:8000/saude` responde 200.

### 1.5 Front-end

```bash
cd frontend
pnpm install --frozen-lockfile
pnpm dev --port 3000
```

`ANALISE_BETS_API_URL` aponta para a API (padrão `http://localhost:8000`). A entrada é em
`/entrar`, com uma chave de API.

No app desktop, os dois serviços estão em `.claude/launch.json` com os nomes `api` e `front`.

Para build de produção, use `pnpm build` seguido de `pnpm start`.

### 1.6 Testes

```bash
python -m pytest -q                 # suíte completa (~60 s)
python -m pytest tests/test_api.py  # só a API, em banco sintético temporário
```

### 1.7 Deploy (POC no Railway)

Configurado em `railway.json`. A cada deploy, o Railway:

1. instala `requirements.txt`;
2. roda `python -m src.api.carga --sem-demo` contra o PostgreSQL. Esse passo recria as tabelas
   de leitura e preserva `clientes_api` e `consultas_atleta`;
3. sobe `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`;
4. verifica `/saude`.

O front é outro serviço do mesmo repositório (root `/frontend`), com `ANALISE_BETS_API_URL`
apontando para o **DNS privado** da API. Só o front tem domínio público. Os passos completos
estão em [backend.md §5.5–5.8](backend.md#55-deploy-railway-da-poc).

---

## 2. Arquitetura da solução

### 2.1 Visão geral

A solução tem duas camadas. Uma é um **pipeline analítico em lote**, que transforma súmulas
oficiais em escores. A outra é uma **aplicação de consulta só de leitura**, que serve esses
escores com controle de acesso por perfil.

```
                        ┌──────────────────── PIPELINE EM LOTE (Python) ────────────────────┐
 Súmulas CBF (PDF) ──►  │ ingestion/  ──►  cleaning/  ──►  models/  ──►  pipeline/           │
 Adão Duque (CSV)       │ download,        parsing,        anomalia,     camadas de          │
 Sofascore 2024         │ delta ETag/      harmonização,   escore pré-   exposição, perfis,  │
 Patrocínios / Trends   │ SHA-256          slugs, minuto   jogo, painel  feed JSON/SQLite    │
                        └───────────────────────────┬───────────────────────────────────────┘
                                                    │ data/processed/*.parquet
                                                    ▼
                                   src/api/carga.py (lote, ~10 s, transacional)
                                                    │
                                                    ▼
                               Banco da API: SQLite (local) | PostgreSQL (Railway)
                               ├─ leitura: partidas, clubes, atletas, escalacoes, cartoes,
                               │           minutos_em_campo, risco_pre_jogo, anomalia_atleta,
                               │           nominaveis            (recriadas a cada carga)
                               └─ operacional: clientes_api, consultas_atleta  (preservadas)
                                                    │
                                                    ▼
                                 FastAPI (src/api/main.py): só leitura, auth Bearer
                                                    │  DNS privado
                                                    ▼
                          Next.js 16 (frontend/): chamadas só no servidor, cookie httpOnly
                                                    │  HTTPS público
                                                    ▼
                                               Navegador
```

### 2.2 Pipeline analítico — `src/`

| Pacote | Responsabilidade | Módulos-chave |
| :--- | :--- | :--- |
| `ingestion/` | Coleta com manifesto de integridade | `download_adaoduque`, `download_cbf_sumulas`, `cbf_delta_updater`, `ingest_serie_a_2024_scouts`, `build_betting_data`, `extract_google_trends`, `build_integrity_data` |
| `cleaning/` | Parsing de PDF, harmonização de minuto, slugs, índice de exposição | `parse_cbf_sumulas`, `cbf_delta_processor`, `clean_serie_a`, `clean_betting` |
| `analysis/` | EDA, minutos em campo, carga de alerta, varredura de exposição nominal | `eda_*`, `escalacoes_e_minutos`, `precisao_e_carga_alerta`, `varredura_exposicao_nominal` |
| `models/` | Econometria, escores, ML, validação | `prepare_panel`, `econometric_models`, `anomaly_detection`, `score_pre_jogo`, `integrity_classifier`, `ground_truth_resolver`, `validacao_out_of_sample` |
| `pipeline/` | Orquestração e governança de exposição | `run_delta_pipeline`, `camadas_de_exposicao`, `perfis_de_acesso`, `serve_product_feed` |
| `visualization/` | Figuras, notebooks, apresentação | `plot_*`, `build_notebooks`, `build_html_presentation` |

Os dados brutos nunca são alterados. Toda transformação gera um derivado em
`data/processed/`, e cada conjunto tem manifesto com origem e hash.

### 2.3 Backend — `src/api/`

Três princípios, herdados da especificação ([backend.md §1](backend.md#1-visão-geral)):

1. **Nenhum escore é calculado na requisição.** O pipeline calcula. A carga materializa
   percentil e tier. A API só lê.
2. **A identidade vem da chave.** Perfil e clube são atributos de `clientes_api`. Passá-los
   como parâmetro de query gera `400`.
3. **A projeção por camada é feita no backend.** A camada aberta não recebe linha individual de
   atleta em nenhum endpoint. A exceção são os condenados com trânsito em julgado.

**Caminho de uma requisição:**
`auth.contexto()` rejeita parâmetros de identidade na query, valida o header Bearer, compara o
SHA-256 da chave com `clientes_api` e verifica se o perfil é atendido. Depois,
`auth.exigir(*perfis)` restringe o endpoint. O handler consulta o banco e, em buscas e fichas,
grava a consulta em `consultas_atleta`. Erros saem sempre no formato `{"erro", "detalhe"}`.

| Endpoint | Perfis | Projeção |
| :--- | :--- | :--- |
| `GET /saude` | público | — |
| `GET /v1/me`, `/v1/cobertura` | qualquer chave | — |
| `GET /v1/rodadas/{serie}/{temporada}/{rodada}/fila` | federação, clube | `clube`: só o próprio elenco |
| `GET /v1/atletas?busca=`, `/v1/atletas/{id}` | federação, clube | Registra a consulta (trilha de due diligence) |
| `GET /v1/atletas/nominaveis` | qualquer chave | — |
| `GET /v1/partidas`, `/v1/partidas/{serie}/{temporada}/{id}/dossie` | qualquer chave | Camada aberta: cartões sem atleta, `atletas_sinalizados = null` |
| `GET /v1/agregados/{serie}/{temporada}` | qualquer chave | Só agregados por clube ou rodada |

**Modelo de dados.** A chave de partida é sempre o trio `(serie, temporada, partida_id)`, porque
`partida_id` se repete entre séries e anos. A identidade do atleta é `registro_cbf`. Os cartões
não trazem o registro na origem, então a carga o herda da escalação por
`(serie, temporada, partida_id, clube_slug, num_camisa)`. Não há *foreign keys*, porque as
tabelas de leitura são substituídas em bloco a cada carga.

### 2.4 Perfis e camadas de exposição

A matriz existe em código (`src/pipeline/perfis_de_acesso.py::PERFIS`) e é reaproveitada pela
API.

| Perfil | Persona | Camada | Granularidade |
| :--- | :--- | :--- | :--- |
| `federacao_stjd` | Analista de integridade | identificada | partida + atleta |
| `clube` | Compliance de clube | identificada | fila só do elenco; consulta a qualquer atleta, registrada |
| `operadora_integrity` | Integrity officer | aberta | partida |
| `imprensa_academia` | Repórter de dados | aberta | partida |
| `operadora_trading` | Head de trading | **não atendido** | a recusa acontece no backend |

### 2.5 Front-end — `frontend/`

Next.js 16 (App Router), React 19, TypeScript e Tailwind v4. Tem quatro telas:

| Tela | Rota | Camada |
| :--- | :--- | :--- |
| T1 — Fila de triagem da rodada | `/triagem` | identificada |
| T2 — Busca e ficha do atleta | `/atletas`, `/atletas/[id]` | identificada |
| T3 — Dossiê de partida | `/partidas`, `/partidas/[serie]/[temporada]/[id]` | todas |
| T4 — Panorama agregado | `/agregados` | todas |

Decisões estruturais ([arquitetura.md](../frontend/docs/arquitetura.md)):

* A chave de API nunca chega ao navegador. Ela fica num cookie `httpOnly`, e toda chamada à API
  roda em componente de servidor ou Server Action.
* Os adaptadores em `lib/api/` são o único código que conhece o formato da API.
* O menu é montado a partir da `camada` de `/v1/me`. Tela sem permissão não aparece no DOM.
* O front nunca recalcula tier nem exibe o escore bruto do pré-jogo.

### 2.6 Infraestrutura

| | POC em execução (Railway) | Arquitetura-alvo do MVP (AWS, [04](especificacao/04_infraestrutura.md)) |
| :--- | :--- | :--- |
| Banco | PostgreSQL gerenciado, volume de 5 GB | RDS PostgreSQL `db.t4g.micro`, subnet privada |
| API | Serviço Railway, DNS privado, sem domínio público | ECS Fargate, 1 task, atrás de ALB + ACM |
| Front | Serviço Railway (`/frontend`), domínio público | S3 + CloudFront |
| Pipeline | Manual. Dados reconstruídos dos Parquets a cada deploy | ECS Fargate Task diária (EventBridge, 05:00 BRT) |
| Segredos | Variável de ambiente do Railway | Secrets Manager |
| Custo | Plano pago do Railway | ~US$ 45–50/mês estimados |

---

## 3. Tecnologias e decisões técnicas

### 3.1 Stack

| Camada | Tecnologia | Uso |
| :--- | :--- | :--- |
| Linguagem | Python 3.13 | Pipeline, modelos, API |
| Dados | pandas, NumPy, PyArrow (Parquet) | Transformação e armazenamento colunar |
| Estatística | SciPy, statsmodels | Testes binomiais e hipergeométricos, Welch, Mann-Whitney, TWFE, event study |
| ML | scikit-learn, joblib | Isolation Forest, Bagging PU-Learning |
| Visualização | matplotlib, seaborn | Figuras dos relatórios |
| Parsing de PDF | `zlib` da biblioteca padrão | Leitura direta dos fluxos das súmulas, sem dependência externa |
| API | FastAPI, Uvicorn | Endpoints só de leitura |
| Acesso a dados | SQLAlchemy 2 Core, sem ORM | SQL textual portável entre SQLite e PostgreSQL |
| Banco | SQLite / PostgreSQL (psycopg 3) | Local / POC |
| Front | Next.js 16, React 19, TypeScript 5, Tailwind 4, Phosphor Icons | Interface |
| Testes | pytest, `fastapi.testclient` (httpx) | 171 testes |
| Deploy | Railway (Railpack), `railway.json` | POC |

### 3.2 Decisões de dados

| Decisão | Racional |
| :--- | :--- |
| **Súmula oficial da CBF como fonte primária** das temporadas recentes | É a única fonte pública com relação de atletas, minuto e motivo do cartão. Cada PDF tem URL e SHA-256, o que dá a procedência que se vende à persona de operadora |
| **Ingestão delta por ETag/Last-Modified/SHA-256** | É idempotente: a temporada 2025 foi reprocessada sete vezes sem divergência. Baixa só o que mudou |
| **Identidade do atleta = `registro_cbf`**, nunca o nome | Evita fundir homônimos. O casamento por nome associava o atleta errado em 8 de 10 casos do ground truth |
| **Chave de partida = `(serie, temporada, partida_id)`** | A `partida_id` da Série B reinicia a cada temporada. A junção por `(serie, partida_id)` somava os cartões de dois anos |
| **`minuto_continuo` nas duas séries** | A Série B registra o minuto dentro do tempo. Sem harmonizar, 47,8% dos cartões dela contavam como "até 30'", contra 15,4% da Série A |
| **Janela de modelagem declarada em constantes** (A 2015–2024, B 2022–2023) | Evita que uma ingestão mude silenciosamente a distribuição de referência. A extensão para 2025 é decisão pendente |
| **PDFs fora do Git** | São ~2.400 arquivos. O manifesto basta para reconstituir o conjunto |

### 3.3 Decisões de modelagem

| Decisão | Racional |
| :--- | :--- |
| **Remoção do subscore de exposição comercial (`S_bet`)** do índice e das features de ML | Por circularidade: a variável cujo efeito a econometria estima não pode compor o índice de atipicidade. E por indefensabilidade: penalizaria o clube pelo patrocinador da camisa |
| **Tiers por percentil empírico** em vez de limiares absolutos | Com limiares 80/65/50, só 10 de 4.559 partidas saíam do tier basal. A carga de alerta passa a ser um parâmetro explícito |
| **Escore pré-jogo com encolhimento bayesiano empírico** (`M0 = 500` min) | Sem encolhimento, um cartão em 20 minutos daria a maior taxa da liga |
| **Taxa populacional acumulada no tempo** | Estimá-la sobre a base inteira é vazamento, e a primeira versão do teste de vazamento o detectou |
| **Alvo observável (cartão no 1º tempo)** em vez do ground truth judicial | Com 14 casos, não há poder estatístico para validar um modelo preditivo |
| **Corrupção determinística do futuro** como guarda de vazamento, e não embaralhamento | O embaralhamento dá informação futura ao modelo em vez de tirar: um teste que passa com e sem vazamento não testa nada |
| **Modo retroativo de escalação** (escalação real da súmula) | Mede o poder preditivo antes de contratar um provedor de escalação provável |

### 3.4 Decisões de produto, segurança e governança

| Decisão | Racional |
| :--- | :--- |
| **Recusa ao perfil `operadora_trading`**, aplicada em tempo de execução | Um escore de concentração de cartões serve para precificar micro-mercados, exatamente o vetor de vulnerabilidade estudado |
| **Nome só na camada identificada**, ou quando há condenação transitada em julgado | Um ranking de atipicidade é composto majoritariamente por pessoas nunca investigadas |
| **Vocabulário controlado** ("atípico", "prioridade de escrutínio"; nunca "suspeito" ou "fraude") | A palavra na tela vira palavra no despacho |
| **`aviso_interpretativo` obrigatório** em toda resposta com escore | A restrição acompanha o dado |
| **Chave de API guardada só como SHA-256**, exibida uma única vez | Um vazamento do banco não expõe credenciais |
| **Trilha `consultas_atleta`**, cuja falha gera log `CRITICAL` sem derrubar a requisição | Com a due diligence liberada sem aprovação prévia, o registro posterior é o controle que sobra |
| **API recusa subir sem o segredo de pseudonimização** fora de `dev` | Com o segredo padrão, o espaço de registros CBF é varrível por força bruta |
| **API sem domínio público** no Railway | Não há rate limiting. O Next.js acessa a API pelo DNS privado |
| **Percentil e tier materializados na carga**, não no pipeline | É a menor mudança possível num pipeline já validado |
| **SQLite local, PostgreSQL na POC**, com o mesmo SQL | SQLite não serve a leituras concorrentes. O schema é portável |

---

## 4. Testes e critérios de avaliação

### 4.1 Suíte automatizada

**Execução de 2026-09-24:** `python -m pytest -q` resultou em **171 testes aprovados** em 60 s,
nenhum ignorado, com Python 3.13.5.

A suíte cresceu de 50 testes (fase acadêmica) para 67, 139 (16/09), 153 (18/09) e 171 (API e
integração com o front).

| Arquivo | Testes | O que protege |
| :--- | :---: | :--- |
| `test_api.py` | 18 | 401/400/403/422, corte da fila, fila do clube restrita ao elenco, busca sem escore, registro de consultas, dossiê sem identificação na camada aberta, formato de erro, paginação |
| `test_anomaly_detection.py` | 16 | Pesos publicados (fixados por teste), chave de junção, harmonização de minuto, janela temporal |
| `test_perfis_de_acesso.py` | 15 | Matriz de perfis, recusa de trading, projeção por camada |
| `test_cbf_delta.py` | 13 | Ingestão delta, seção de cartões amarelos, relação sem apelido, camisa de 3 dígitos |
| `test_score_pre_jogo.py` | 13 | Encolhimento, atleta sem histórico (sem `NaN`), **teste de vazamento** |
| `test_parse_cbf.py` | 12 | Parser de súmulas |
| `test_precisao_e_carga_alerta.py` | 11 | Carga de alerta, precisão@k, curva operacional |
| `test_camadas_de_exposicao.py` | 10 | **Nenhum atleta sem condenação nominado em artefato de camada aberta** |
| `test_ground_truth_resolver.py` | 10 | Mapa de identidade explícito, casos não resolvidos |
| `test_validacao_out_of_sample.py` | 9 | Leave-one-out, separação por série, IC de Wilson |
| `test_clean_betting.py`, `test_html_presentation.py` | 6 cada | Índice de exposição, apresentação |
| `test_clean_serie_a.py`, `test_econometric_models.py`, `test_integrity_classifier.py`, `test_scouts_2024.py` | 5 cada | Limpeza, painel, ML, scouts |
| `test_notebooks.py` | 2 | Notebooks válidos |

**Princípio da suíte:** testes de **contrato**, não de valor calculado. Quando a base cresceu 14%
e depois dobrou, nenhum teste precisou ser reescrito para acomodar números novos. As exceções
deliberadas são os pesos publicados do índice: mudá-los sem atualizar o relatório quebra a suíte.

**Front:** `pnpm build` concluído com sucesso em 2026-09-24, com compilação, verificação de
TypeScript e geração de rotas. Não há testes automatizados de componente.

### 4.2 Portões de qualidade de dados

Definidos em [05 §4](especificacao/05_automacao.md). Quatro deles correspondem a defeitos que já
ocorreram.

| # | Regra | Situação |
| :---: | :--- | :--- |
| G1 | Zero duplicatas em `(serie, temporada, partida_id)` | Teste existente |
| G2 | Zero escalações sem `registro_cbf` | Teste existente (hoje: 0) |
| G3 | `num_camisa` com até 3 dígitos | Teste existente |
| G4 | ≤ 5 atletas com evento fora da relação da partida | Teste existente (hoje: 0) |
| G5 | Zero `score_pre_jogo` nulo | Teste existente |
| G6 | Cartões por partida entre 2 e 12 na média da rodada | **Não implementado** |
| G7 | Zero atletas sem condenação nominados na camada aberta | Teste existente. É o portão de governança |

### 4.3 Critérios de avaliação dos modelos

| Componente | Critério | Por quê |
| :--- | :--- | :--- |
| Econometria (TWFE, event study) | Coeficiente, erro-padrão clusterizado por clube, teste F conjunto de tendências paralelas (`e ≤ −2`) | Controla heterogeneidade de clube e temporada e testa a premissa de identificação |
| Escores retrospectivos | Sensibilidade contra os 14 casos judiciais, com **IC 95% de Wilson** | Com N = 14, toda estimativa pontual sem intervalo engana |
| Classificador de ML | **Leave-one-out** e **separação por série** (treina em B, avalia em A e vice-versa) | Só o PU-Learning vê os rótulos, e a avaliação dentro da amostra mede memorização |
| Triagem operacional | **Carga de alerta** (alertas por rodada), **precisão@k**, **ganho sobre o acaso**, p-valor **hipergeométrico** | Não há falsos positivos rotulados, então a precisão absoluta não é estimável e nenhum denominador é inventado |
| Escore pré-jogo | **Walk-forward** em 210 rodadas, precisão@k (k = 1, 3, 5, 10) contra linha de base ingênua e contra o acaso | Replica o uso real: só informação anterior à rodada |
| Guarda de vazamento | Corromper todo o alvo após um corte cronológico e exigir escores anteriores **idênticos bit a bit** | Detecta qualquer uso de informação futura |

Classificação dos resultados, seguindo [`.agent.md`](../.agent.md): associação, evidência de
alteração, evidência de anomalia. "Manipulação" só se aplica com confirmação independente
(decisão judicial ou desportiva).

---

## 5. Resultados quantitativos e qualitativos

### 5.1 Ativo de dados

| Item | Valor |
| :--- | ---: |
| Cobertura | Série A 2003–2025, Série B 2022–2025, 2026 em curso |
| Partidas | 11.220 |
| Cartões | 34.248 |
| Registros atleta × partida (escalações) | 107.990 |
| Atletas (por `registro_cbf`) | 3.350 |
| Clubes | 87 |
| Súmulas oficiais ingeridas | ~2.400 PDFs (1.140 só na sessão de 18/09, nenhum 404) |
| Taxa de extração da relação de atletas | 98,4% a 99,3% por temporada |
| Partidas com PDF incompleto na origem | 23 |
| Base processada | 109 MB em disco, dos quais 6,98 MB são os Parquets lidos pela API |

### 5.2 Análise exploratória — o "paradoxo disciplinar" (Série A)

| | 2017 | 2024 | Variação |
| :--- | ---: | ---: | ---: |
| Faltas por jogo | 31,41 | 25,36 | −19,3% |
| Cartões por jogo | 5,05 | 5,53 | +9,5% |
| Taxa de conversão falta → cartão | 0,160 | 0,220 | +37,1% |

* O jogo ficou menos faltoso e mais punido. Em 2024 houve recorde de 128 expulsões.
* Pré-bets (2014–2018) contra 2022–2024: +0,457 cartão/jogo (Welch `p = 8,7 × 10⁻⁷`).
* Série A contra Série B (2022–2023): 5,44 contra 4,87 cartões/jogo (`p = 8,9 × 10⁻⁶`).
* 28,9% dos cartões da Série B vêm de infração sem disputa de bola (reclamação, cera, conduta).

### 5.3 Econometria (painel clube × partida, Série A 2015–2024, N = 7.598)

| Variável dependente | β (`bet_exposure`) | p-valor |
| :--- | ---: | ---: |
| Cartões totais | +0,2665 | 0,006 |
| Cartões amarelos | +0,2598 | 0,008 |
| Taxa de conversão falta → cartão | +0,0126 | 0,063 |
| Faltas cometidas | +0,5003 | 0,369 (n.s.) |
| **Proporção de cartões no 1º tempo** | −0,0129 | 0,592 (n.s.) |

* **Event study:** efeito a partir do ano de estreia do patrocínio (`e = 0`: +0,13; `e = +1`:
  +0,31; `e = +2`: +0,32). Teste de tendências paralelas: `F = 2,43, p = 0,10` para cartões e
  `p = 0,70` para a taxa de conversão.
* **Achado central para o produto:** a exposição **não altera a concentração coletiva de cartões
  no 1º tempo**. A manipulação por micro-apostas é conduta individual, não comportamento de
  clube. Isso motivou a mudança da unidade de análise da partida para o atleta.

> **Nota de leitura.** O white paper descreve esse efeito como "causal comprovado". Esta
> consolidação recomenda uma leitura mais conservadora: **associação robusta com desenho
> quase-experimental**. Há quatro motivos. (i) O TWFE com adoção escalonada e efeitos
> heterogêneos pode ser viesado (Goodman-Bacon, 2021; Callaway & Sant'Anna, 2021), e esses
> estimadores não foram aplicados. (ii) O coeficiente `e ≤ −3` fica no limite (`p = 0,051`), e o
> teste conjunto de pré-tendência de cartões (`p = 0,10`) não rejeita, mas também não é folgado.
> (iii) O VAR (2019) coincide com a primeira coorte de adoção. (iv) O índice de exposição foi
> construído pelo próprio projeto. A decisão sobre a redação final é do responsável pela
> pesquisa.

### 5.4 Triagem retrospectiva (escores de anomalia)

Base: 4.559 partidas (A 2015–2024, B 2022–2023) e 3.694 registros atleta-temporada.
Ground truth: 14 incidentes da Operação Penalidade Máxima.

| Afirmação | Resultado |
| :--- | :--- |
| Sensibilidade dos escores estatísticos | **6/14 (42,9%)**. Dois dos não sinalizados são fraudes não consumadas em campo |
| Partidas sinalizadas (≥ p90) | 455 (9,98%), ≈ 1 alerta por rodada |
| Ganho sobre o acaso, nível partida | **Nenhum limiar é distinguível do acaso** (melhor ponto: P85, 2,05×, `p = 0,118`). Captura zero nos tiers Top 1% e Top 5% |
| Ganho sobre o acaso, nível atleta | Há sinal só em P60 (6/7, 2,15×, `p = 0,019`), mas isso exige sinalizar 40% da base |
| Classificador de ML, dentro da amostra | 100% (7/7 atletas, 14/14 partidas) |
| Classificador de ML, leave-one-out | **1/7 atletas (14,3%)**, 6/14 partidas no tier de Alto Risco |
| Classificador de ML, treino em B e avaliação em A | 1/9 partidas (11,1%, IC 2,0%–43,5%) |
| Eventos do ground truth confirmados na súmula | **1 de 14** |

Com isso, o sistema foi reposicionado como **instrumento de medição de atipicidade
disciplinar**, e não como detector ou priorizador de manipulação.

### 5.5 Escore pré-jogo por atleta (componente com poder preditivo)

Walk-forward em 210 rodadas e 107.990 registros atleta × partida.

| k | Precisão@k | Linha de base (cartões acumulados) | Acaso | Ganho sobre o acaso |
| :---: | :---: | :---: | :---: | :---: |
| 1 | 9,5% | 9,1% | 4,0% | 2,37× |
| 3 | 10,8% | 9,1% | 4,0% | 2,69× |
| 5 | 11,2% | 9,2% | 4,0% | 2,80× |
| 10 | 11,9% | 8,6% | 4,0% | 2,96× |

* Supera a linha de base em **todos os k**, e a vantagem cresce com k (de +0,4 p.p. para
  +3,3 p.p.).
* **Teste de vazamento aprovado:** 0 divergências em 75.291 linhas.
* O ganho mede **atipicidade disciplinar**, não conduta. A linha de base continua próxima.

### 5.6 Produto (POC)

| Entrega | Situação em 2026-09-24 |
| :--- | :--- |
| API FastAPI com 10 endpoints, autenticação por chave e projeção por perfil | Em execução no Railway (`/saude` 200), sem domínio público |
| Banco PostgreSQL com 9 tabelas de leitura e 2 operacionais | Carregado no pré-deploy (14 caracteres NUL removidos na carga) |
| Front Next.js com 4 telas integradas à API real | Em execução, com domínio público; `/entrar` responde 200 |
| Feed de produto em JSON por camada e SQLite | Regenerável por um comando |
| Minuta de termo de uso e matriz de granularidade | [termo_de_uso_e_licenciamento.md](termo_de_uso_e_licenciamento.md) |

### 5.7 Resultados qualitativos

1. **O projeto desfez as próprias afirmações quando os dados não as sustentaram.** Três números
   caíram na sessão de 16/09: a sensibilidade de 100%, que era memorização; a de 64,3%, que usava
   o casamento defeituoso; e o "Top 10%" de atletas investigados, com 8 de 10 identidades
   erradas. Resultados negativos foram preservados e publicados.
2. **Qualidade de dados foi o principal risco técnico, e não a modelagem.** Foram encontrados e
   corrigidos 17 defeitos, nenhum previsto no backlog. Entre eles: 519 cartões perdidos na
   Série B por um token de subtipo de expulsão; o registro CBF gravado no lugar da camisa; um
   `groupby` que descartava chave nula; e uma guarda de vazamento que lia `NaN != NaN` como
   vazamento. Dois desses defeitos se anulavam mutuamente na junção entre evento e escalação.
3. **A unidade de análise certa é o atleta.** Econometria, triagem retrospectiva e escore
   pré-jogo convergem: o sinal não está na distorção coletiva da partida.
4. **Governança executável.** Regras de exposição nominal, recusa ao perfil de trading e
   vocabulário foram implementadas como código e teste (G7), não como política escrita.
5. **Postura de transparência.** Cada simplificação do MVP está marcada como `[MVP]`, com a dívida
   explicitada na especificação.

---

## 6. Limitações e possibilidades de evolução

### 6.1 Limitações dos dados

| Limitação | Efeito |
| :--- | :--- |
| **Ground truth pequeno e frágil:** 14 casos, uma operação, e só 1 evento confirmado na súmula | Toda cifra de validação tem intervalo largo e repousa sobre metadados que não reconciliam com a fonte oficial |
| **Não existem falsos positivos rotulados** | A precisão absoluta não é estimável |
| **Volume de apostas indisponível** (dado das operadoras) | Não se mede a pressão de mercado. A exposição é aproximada por patrocínio e Google Trends |
| **Relação de atletas só nas temporadas com súmula eletrônica** (A 2025–2026, B 2022–2026) | O escore pré-jogo não cobre a Série A histórica. ~7% dos cartões dessas temporadas ficam sem `registro_cbf` |
| **Motivo do cartão ausente em 86% da Série A** | Tipologia de infração incompleta (F2-05) |
| **Séries C e D fora da base** | A hipótese H3 (diferença entre divisões) só é testada entre A e B |
| **Eixo econômico não executado** (receita, público, folha) | As perguntas 5 a 11 da proposta seguem abertas |

### 6.2 Limitações metodológicas

* **O escore pré-jogo foi validado em modo retroativo**, com a escalação real que só existe
  depois do jogo. Em produção, o desempenho depende da qualidade da escalação provável.
* **O alvo é cartão no 1º tempo, não manipulação.** A ligação entre os dois é hipótese do projeto.
* **Os escores retrospectivos não discriminam melhor que sorteio no nível da partida.**
* **O classificador de ML não generaliza** fora da amostra.
* **A identificação causal da econometria está condicionada** às ressalvas da seção 5.3.
* **A janela dos escores retrospectivos está congelada** em A 2015–2024 e B 2022–2023. 2025 está
  na base e fora dos modelos.
* **As capacidades das personas (3, 1, 10 alertas por rodada) são premissas.** Nenhuma persona
  foi entrevistada (F5-01).
* **A semântica do percentil da fila está em aberto:** o p70 padrão coloca ~30% da rodada na
  fila, contra ~3 alertas estimados pelo escore retrospectivo.

### 6.3 Limitações de engenharia e segurança

| Item | Situação |
| :--- | :--- |
| Rate limiting e expiração de chave | **Não implementados.** Uma chave vazada permite varrer a base atleta a atleta |
| Retenção de 12 meses de `consultas_atleta` e trilha técnica | Não implementadas |
| Agendamento do pipeline, notificação de falha, tabela `execucoes_pipeline` | Não existem. A execução é manual |
| Portão G6 (volume plausível) | Não implementado |
| Ambiente de homologação, CI/CD, rollback | Não existem |
| Carga pré-deploy | Substitui as tabelas enquanto a versão anterior ainda recebe tráfego, o que pode causar falha breve de consulta |
| Fila de rodada futura | Retorna `422`. Não há fonte de escalação provável |
| `requirements.txt` | Não lista as dependências analíticas (scikit-learn, statsmodels, matplotlib, seaborn, joblib, nbformat, pytrends, pytest) |
| Testes do front | Só build e verificação de tipos |
| Histórico do Git | Tabelas nominais de commits antigos e 1.308 PDFs ainda versionados. A decisão é do responsável |

### 6.4 LGPD

O banco da API combina **identificação** (nome, registro CBF) com **inferência estatística sobre a
pessoa**, a combinação de maior sensibilidade do sistema. **A base legal e o RIPD (F4-01) não
foram estabelecidos.** Isso é condição para qualquer uso fora do ambiente acadêmico.

> Caso o seu projeto envolva dados pessoais ou dados pessoais sensíveis, comunique ao time de
> Segurança da Informação através do e-mail seginfo@gcb.com.br

### 6.5 Possibilidades de evolução

Ordenadas por dependência e impacto, a partir do backlog (`tasks/backlog/`) e das seções `[MVP]`
da especificação.

**Condições para exposição externa**

1. RIPD e base legal (F4-01), com apoio jurídico.
2. Rate limiting por cliente, expiração e rotação de chave. É o primeiro item de produção, à
   frente do OAuth.
3. Retenção de `consultas_atleta` e trilha técnica de acesso.

**Credibilidade analítica**

4. Reconstituir o ground truth a partir de fonte primária (autos do MP-GO, decisões do STJD).
5. Reestimar a econometria com estimadores robustos à adoção escalonada (Callaway & Sant'Anna,
   Sun & Abraham) e com efeito fixo de árbitro.
6. Decidir se a janela dos escores retrospectivos passa a incluir 2025.
7. Medir o escore pré-jogo com escalação provável de terceiros, o que tornaria a triagem de
   fato pré-jogo.
8. Incorporar contexto de partida (rodada, situação na tabela, clássico) ao escore pré-jogo, com
   a mesma exigência de walk-forward e teste de vazamento.

**Operação**

9. Esteira diária agendada (EventBridge + Fargate, ou cron no Railway) com portões G1–G7,
   notificação de falha, listagem explícita de súmulas faltantes e registro em
   `execucoes_pipeline`.
10. Carga sem janela de indisponibilidade (tabelas-sombra com troca atômica).
11. CI com a suíte de testes e o build do front. Infraestrutura como código.
12. Completar `requirements.txt`, ou separar em `requirements-analise.txt`.

**Produto e escopo**

13. Entrevistas com personas (F5-01) para calibrar os limiares por perfil e testar as hipóteses
    críticas (F5-02).
14. Dossiê de rodada em PDF (F3-03) e fluxo de due diligence por atleta (F3-04).
15. Tipologia de infrações em toda a base (F2-05).
16. Extensão às Séries C e D e aos estaduais, reaproveitando o parser de súmulas.
17. Eixo econômico da pesquisa: receitas, público e competitividade.
