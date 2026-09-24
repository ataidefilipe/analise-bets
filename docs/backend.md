# Backend e banco da POC

**Para:** quem mantém ou evolui o backend (etapas 4 e 6).
**Escopo:** POC. O contrato está em [especificacao/01](especificacao/01_api_e_autorizacao.md). Este
documento descreve **o que foi implementado** e onde isso difere do contrato.

| Se você quer... | Leia |
| :--- | :--- |
| Consumir a API pelo front | [integracao_frontend.md](integracao_frontend.md) |
| Mexer no front (`frontend/`) | [frontend/docs/arquitetura.md](../frontend/docs/arquitetura.md) |
| Entender o que o contrato previa | [especificacao/](especificacao/README.md) |
| Saber de onde vêm as colunas de entrada | [data_dictionary.md](data_dictionary.md) |

---

## 1. Visão geral

```
 data/processed/*.parquet  ──►  src/api/carga.py  ──►  banco da API  ──►  src/api/main.py  ──►  front
 data/raw/cbf/manifest_delta.json ─┘   (lote, ~10 s)     (SQLite/Postgres)   (FastAPI, só leitura)
```

Três princípios, todos herdados da especificação:

1. **Nenhum escore é calculado em requisição.** O pipeline calcula; a carga materializa percentil e
   tier; a API só lê.
2. **A identidade vem da chave.** Perfil e clube são atributos de `clientes_api`, nunca parâmetros.
3. **A projeção por camada é do backend.** A camada aberta não recebe linha individual de atleta
   (salvo condenado), em nenhum endpoint.

### Stack

| | |
| :--- | :--- |
| Linguagem | Python 3.13 |
| API | FastAPI + Uvicorn |
| Acesso a dados | SQLAlchemy 2 Core (sem ORM), SQL textual portável |
| Banco | SQLite em `data/api/analise_bets_api.db` (padrão) ou PostgreSQL por URL |
| Dependências | [`requirements-api.txt`](../requirements-api.txt) |

---

## 2. Módulos — `src/api/`

| Arquivo | Responsabilidade |
| :--- | :--- |
| [`config.py`](../src/api/config.py) | Variáveis de ambiente, limiares por perfil, textos de aviso, `tier_atleta()` e a verificação do segredo na subida |
| [`modelo.py`](../src/api/modelo.py) | Schema do banco (tabelas, chaves, índices) em SQLAlchemy Core |
| [`db.py`](../src/api/db.py) | Engine único por processo; `definir_engine()` para testes |
| [`carga.py`](../src/api/carga.py) | Monta as tabelas de leitura a partir do Parquet e cadastra as chaves demo |
| [`clientes.py`](../src/api/clientes.py) | CLI de cadastro, listagem e desativação de chaves |
| [`auth.py`](../src/api/auth.py) | Resolve a chave em `Contexto` imutável; `exigir(*perfis)` protege endpoints |
| [`erros.py`](../src/api/erros.py) | `ErroApi` e os *handlers* que garantem o formato `{"erro", "detalhe"}` |
| [`main.py`](../src/api/main.py) | App FastAPI, CORS e os endpoints |

### Reaproveitado do pipeline, não reimplementado

| O quê | De onde |
| :--- | :--- |
| Matriz de perfis e camadas | `src/pipeline/perfis_de_acesso.py::PERFIS` |
| Condenados nomináveis | `src/pipeline/camadas_de_exposicao.py::status_juridico_por_atleta` |
| Cortes e rótulos de tier | `src/models/anomaly_detection.py::TIERS_ATLETA` |
| Texto do aviso interpretativo | `src/pipeline/serve_product_feed.py::AVISO_INTERPRETATIVO` |

---

## 3. Caminho de uma requisição

```
GET /v1/atletas/900001   Authorization: Bearer ab_...
  │
  ├─ auth.contexto()
  │    ├─ query tem perfil/clube/clube_slug/camada?  → 400 parametro_invalido
  │    ├─ header ausente ou não-Bearer?              → 401
  │    ├─ SHA-256 da chave em clientes_api, ativo?   → senão 401
  │    └─ perfil atendido?                           → senão 403
  │    ⇒ Contexto(cliente_id, nome, perfil, clube_slug)
  │
  ├─ auth.exigir("federacao_stjd", "clube")          → perfil fora da lista: 403
  │
  ├─ main.ficha_atleta()
  │    ├─ SELECT em atletas, minutos_em_campo, cartoes, anomalia_atleta
  │    └─ _registrar_consulta()  → INSERT em consultas_atleta (falha só gera log CRITICAL)
  │
  └─ JSON  |  ErroApi → erros._erro_api  |  exceção → 500 erro_interno (stack só no log)
```

### Autorização por endpoint

| Endpoint | Dependência | Projeção aplicada |
| :--- | :--- | :--- |
| `GET /saude` | nenhuma | — |
| `GET /v1/me` | `contexto` | — |
| `GET /v1/cobertura` | `contexto` | — (só temporadas e rodadas) |
| `GET /v1/rodadas/{serie}/{temporada}/{rodada}/fila` | `exigir(federacao, clube)` | `clube`: `WHERE clube_slug = <credencial>` antes do corte |
| `GET /v1/atletas?busca=` | `exigir(federacao, clube)` | sem escore; 20 resultados; registra consulta |
| `GET /v1/atletas/{atleta_id}` | `exigir(federacao, clube)` | registra consulta com `proprio_elenco` |
| `GET /v1/atletas/nominaveis` | `contexto` | — |
| `GET /v1/partidas` | `contexto` | nenhuma (partida não é dado pessoal); paginada, até 50 por página |
| `GET /v1/partidas/{serie}/{temporada}/{partida_id}/dossie` | `contexto` | aberta: cartões sem atleta (salvo nominável) e `atletas_sinalizados = null`; `clube`: sinalizados só do elenco |
| `GET /v1/agregados/{serie}/{temporada}` | `contexto` | só agregados por clube ou rodada |

A rota `/v1/atletas/nominaveis` é declarada **antes** de `/v1/atletas/{atleta_id}`; invertida, a
palavra "nominaveis" seria lida como id.

---

## 4. Banco de dados

### 4.1 Dois grupos de tabela

| Grupo | Tabelas | Na recarga |
| :--- | :--- | :--- |
| **Leitura** | `partidas`, `clubes`, `atletas`, `escalacoes`, `cartoes`, `minutos_em_campo`, `risco_pre_jogo`, `anomalia_atleta`, `nominaveis` | Apagadas e recriadas numa transação |
| **Operacional** | `clientes_api`, `consultas_atleta` | **Preservadas.** Contêm credenciais e a trilha de due diligence |

### 4.2 Relacionamento

Não há *foreign keys* declaradas: as tabelas de leitura são substituídas em bloco, e FK só
atrapalharia a recarga. As junções usadas pela API são:

```
partidas (serie, temporada, partida_id) ─┬─< escalacoes      (serie, temporada, partida_id)
                                         ├─< cartoes         (serie, temporada, partida_id)
                                         └─< risco_pre_jogo  (serie, temporada, partida_id)

atletas (registro_cbf) ─┬─< escalacoes, cartoes, minutos_em_campo, risco_pre_jogo  (registro_cbf)
                        ├─< anomalia_atleta   (atleta_slug | apelido_slug)   ← vínculo por nome
                        └─< nominaveis        (registro_cbf, pode ser nulo)

clientes_api (id) ─< consultas_atleta (cliente_api_id)
```

**`partida_id` sozinho não é único**: repete entre séries e temporadas. A chave é sempre o trio.

**A identidade do atleta é `registro_cbf`.** Os cartões não trazem o registro na origem; a carga o
herda da escalação da mesma partida por `(serie, temporada, partida_id, clube_slug, num_camisa)`.

### 4.3 Tabelas

Linhas da carga de 2026-09-23.

**`partidas`** — 11.220 linhas. PK `(serie, temporada, partida_id)`. Índice `(serie, temporada, rodada)`.

| Coluna | Tipo | Origem / nota |
| :--- | :--- | :--- |
| `serie`, `temporada`, `partida_id` | text, int, int | `serie_{a,b}/partidas.parquet`. Série A de origem Kaggle vem com `serie` nula e é preenchida com `A` |
| `rodada`, `data`, `horario` | int, text, text | |
| `clube_mandante[_slug]`, `clube_visitante[_slug]` | text | |
| `gols_mandante`, `gols_visitante` | int | |
| `arena`, `cidade`, `uf_estadio`, `arbitro` | text | |
| `match_anomaly_score`, `percentil_anomalia`, `tier_partida` | real, real, text | `integrity/partidas_anomaly_scored.parquet`. Só A 2015–2024 e B 2022–2023 |
| `sumula_url`, `sumula_sha256`, `baixado_em` | text | `data/raw/cbf/manifest_delta.json`. Só A 2025–2026 e B 2024–2026 |
| `processado_em` | text | Momento da carga, gravado onde há procedência |
| `busca_texto` | text | Nomes dos dois clubes, sem acento e minúsculos. A listagem de partidas usa `LIKE` aqui |

**`clubes`** — 87 linhas. PK `clube_slug`. Coluna `nome`: o nome da temporada mais recente em que
o clube aparece em `partidas`. A API usa esta tabela para devolver `clube` ao lado de todo
`clube_slug`.

**`atletas`** — 3.350 linhas. PK `registro_cbf`. Derivada de `escalacoes`, um registro por atleta com os
dados da última escalação.

| Coluna | Nota |
| :--- | :--- |
| `registro_cbf` | Identificador; é o `atleta_id` da API |
| `nome_completo`, `apelido`, `atleta_slug`, `apelido_slug` | Da última escalação |
| `busca_texto` | `nome_completo + apelido`, sem acento e minúsculo. A busca usa `LIKE` aqui |
| `clubes` | Slugs separados por vírgula |
| `clube_atual`, `ultima_temporada` | Da última escalação. `clube_atual` decide `proprio_elenco` |

**`escalacoes`** — 107.990 linhas. PK sintética `id`. Índices `(serie, temporada, partida_id)` e
`(registro_cbf)`. Colunas: `serie, temporada, partida_id, rodada, clube_slug, num_camisa,
registro_cbf, condicao, goleiro`. Linhas sem `registro_cbf` são descartadas com log de erro (documento
02 §6). Hoje, zero.

**`cartoes`** — 34.248 linhas. PK sintética `id`. Índices `(serie, temporada, partida_id)` e
`(registro_cbf)`. Colunas: `serie, temporada, partida_id, rodada, clube_slug, num_camisa,
registro_cbf, atleta, cartao, minuto_continuo, periodo, tipo_cartao_detalhe, categoria_infracao,
motivo_completo`. `registro_cbf` é nulo nos anos sem súmula eletrônica e em ~7% dos cartões dos anos
com súmula (camisa sem correspondência na escalação).

**`minutos_em_campo`** — 6.561 linhas. PK sintética `id`. Índice `(registro_cbf, temporada)`. Colunas:
`serie, temporada, clube_slug, registro_cbf, partidas_jogadas, minutos_em_campo`.

**`risco_pre_jogo`** — 107.990 linhas. PK sintética `id`. Índices `(serie, temporada, rodada, percentil)`
e `(serie, temporada, partida_id)`.

| Coluna | Nota |
| :--- | :--- |
| `serie, temporada, rodada, partida_id, clube_slug, registro_cbf, num_camisa, condicao` | `integrity/score_pre_jogo.parquet` |
| `minutos_previos, cartoes_1t_previos, taxa_1t_ajustada, minutos_esperados, score_pre_jogo` | Componentes do escore, calculados pelo pipeline |
| `percentil` | **Materializado na carga:** `rank(pct, method="max") × 100` dentro de `(serie, temporada)` |
| `tier` | **Materializado na carga:** `config.tier_atleta(percentil)` com os cortes de `TIERS_ATLETA` |

**`anomalia_atleta`** — 3.694 linhas. Índice `(atleta_slug, temporada)`. Colunas: `serie, temporada,
clube_slug, atleta_slug, athlete_anomaly_score, percentil, tier`. Vem de
`integrity/atletas_anomaly_scored.parquet`. **Indexada por slug de nome**, porque os anos cobertos
não têm registro CBF na fonte; a ficha casa pelo `atleta_slug` ou `apelido_slug` do atleta.

**`nominaveis`** — 10 linhas. PK `atleta_slug`. Condenados com trânsito em julgado. `registro_cbf` só
é preenchido quando o apelido identifica um único atleta de `atletas`; hoje, 3 de 10.

**`clientes_api`** — PK `id` (uuid). `api_key_hash` único (SHA-256; a chave em claro nunca é gravada),
`nome`, `perfil`, `clube_slug` (obrigatório para `clube`), `ativo`, `criado_em`.

**`consultas_atleta`** — PK `id` (uuid). Índices `(cliente_api_id, consultado_em)` e `(atleta_id)`.
Colunas `cliente_api_id`, `atleta_id` (nulo na busca), `termo_busca` (nulo na ficha),
`proprio_elenco` (nulo para federação), `consultado_em`.

### 4.4 O que ficou de fora do banco

`gols` e `classificacao` não são usados por nenhum endpoint e continuam só no `brasileirao.db` do
feed. `execucoes_pipeline` (documento 05 §6) pertence à etapa 6.

---

## 5. Operação

### 5.1 Variáveis de ambiente

| Variável | Padrão | Efeito |
| :--- | :--- | :--- |
| `ANALISE_BETS_DATABASE_URL` | `sqlite:///data/api/analise_bets_api.db` | Banco. Para Postgres: `postgresql+psycopg://usuario:senha@host/banco` (instale `psycopg[binary]`) |
| `DATABASE_URL` | — | Alternativa de `ANALISE_BETS_DATABASE_URL`; aceita a URL PostgreSQL injetada pelo Railway |
| `ANALISE_BETS_AMBIENTE` | `producao` | `dev` libera subir com o segredo de desenvolvimento |
| `ANALISE_BETS_PSEUDONIMO_SECRET` | valor de desenvolvimento | Fora de `dev`, **a API recusa subir** se não estiver definido (documento 04 §5) |
| `ANALISE_BETS_CORS` | `*` | Origens do front, separadas por vírgula |

### 5.2 Comandos

```bash
pip install -r requirements-api.txt

# (re)carrega as tabelas de leitura; na primeira vez, cria as chaves demo
python -m src.api.carga
python -m src.api.carga --sem-demo

# sobe a API (local)
ANALISE_BETS_AMBIENTE=dev uvicorn src.api.main:app --reload --port 8000

# chaves
python -m src.api.clientes criar --nome "STJD" --perfil federacao_stjd
python -m src.api.clientes criar --nome "Compliance X" --perfil clube --clube <clube_slug>
python -m src.api.clientes listar
python -m src.api.clientes desativar --id <uuid>

# testes da API (banco sintético temporário, não toca no banco real)
python -m pytest tests/test_api.py
```

### 5.3 Quando recarregar

Depois de cada execução do pipeline (documento 05 §3), como último passo:

```
run_delta_pipeline → escalacoes_e_minutos → score_pre_jogo → serve_product_feed → src.api.carga
```

A carga é idempotente. Enquanto ela roda, a API continua servindo; no SQLite, as leituras esperam
o fim da transação.

### 5.4 Chaves de demonstração

Criadas só se `clientes_api` estiver vazia, e gravadas em `data/restrito/chaves_api_poc.json`: uma por
perfil, com o `clube` apontando para `flamengo`. Para regenerar, apague o arquivo e as linhas de
`clientes_api`, depois rode a carga.

### 5.5 Deploy Railway da POC

Esta configuração é para a POC Railway e não substitui a arquitetura AWS descrita em
[`especificacao/04_infraestrutura.md`](especificacao/04_infraestrutura.md).

O repositório inclui `railway.json` e `requirements.txt`. O Railway instala as dependências da
API e, antes de cada deploy, executa `python -m src.api.carga --sem-demo` contra o PostgreSQL.
Essa carga recria as tabelas de leitura a partir dos Parquets versionados em `data/processed/`,
mas preserva `clientes_api` e `consultas_atleta`. Em seguida, inicia o Uvicorn usando `PORT` e
verifica `/saude`.

No Railway:

1. Adicione um serviço PostgreSQL ao projeto.
2. No serviço da API, crie `DATABASE_URL` como referência à variável `DATABASE_URL` do serviço
   PostgreSQL (por exemplo, `${{Postgres.DATABASE_URL}}`). Não defina `ANALISE_BETS_DATABASE_URL`
   no Railway, pois ela tem precedência.
3. Defina `ANALISE_BETS_PSEUDONIMO_SECRET` com um segredo aleatório forte. A API recusa iniciar
   sem ele.
4. O front atual (`frontend/`) chama a API do servidor Next.js, então CORS não é necessário para
   esse fluxo. Se no futuro o navegador chamar a API diretamente, defina `ANALISE_BETS_CORS` com
   as origens permitidas.
5. Faça o primeiro deploy. Cadastre cada chave necessária uma única vez com o Railway CLI,
   ligado ao serviço da API, por exemplo:

   ```bash
   railway run python -m src.api.clientes criar --nome "STJD" --perfil federacao_stjd
   ```

   A chave é exibida uma vez; guarde-a fora do repositório. Repita com o perfil e o clube
   adequados para cada cliente.

A carga pré-deploy substitui as tabelas de leitura do banco e preserva as tabelas operacionais;
durante esse passo, a API da versão anterior pode ter uma breve interrupção ao consultar os dados.
Ela não cria chaves de demonstração no serviço, evitando depender de um arquivo local efêmero para
recuperar credenciais. A POC passa a persistir as chaves e a trilha de consultas no PostgreSQL; os
dados de leitura continuam sendo reconstruídos dos Parquets em cada deploy.

### 5.6 Decisão, tamanho dos dados e próximos passos

**Decisão da POC:** usar PostgreSQL gerenciado no Railway por persistência de `clientes_api` e
`consultas_atleta`. A API local continua usando SQLite por padrão. Os dados analíticos permanecem
nos Parquets do repositório e são carregados no PostgreSQL antes de cada deploy; não adicionar
armazenamento externo nem automação de pipeline nesta etapa.

**Medição em 2026-09-23:** `data/processed/` ocupa 109,14 MB em 61 arquivos. Distribuição por
pasta: `product_feed` 56,98 MB; `serie_a` 14,68 MB; `serie_b` 17,05 MB; `integrity` 18,61 MB;
`panel` 1,75 MB; `betting` 0,06 MB. O conteúdo inclui 43,09 MB de SQLite de feed, além de CSV,
JSON e modelos que a carga da API não lê. A carga lê arquivos Parquet; o conjunto Parquet totaliza
6,98 MB. Portanto, o caminho simples é viável e não exige um bucket para esta POC. Uma redução
futura do contexto do deploy pode excluir os artefatos que a API não consome.

**Estado:** a configuração e a documentação estão no repositório; PostgreSQL, variáveis e domínio
ainda não foram configurados no painel Railway, e não foi feito deploy.

O pull de `origin/main` (commit `9444f97`) trouxe o front para `frontend/` e completou a integração
com a API. Também adicionou `clubes`, `partidas.busca_texto`, `/v1/partidas` e `/v1/cobertura`.
`src.api.carga` agora carrega a tabela `clubes`, que está incluída em `TABELAS_DE_LEITURA`; por
isso, o comando pré-deploy existente permanece compatível com o schema novo. Não houve conflito
com a configuração Railway/PostgreSQL local.

**Próximas ações:**

1. Sincronizar a branch de trabalho atual do front com `main`; o front integrado recebido está em
   `frontend/`.
2. Criar o serviço PostgreSQL e referenciar sua `DATABASE_URL` no serviço da API.
3. Definir `ANALISE_BETS_PSEUDONIMO_SECRET` e fazer o primeiro deploy; verificar `/saude` e a
   carga inicial das tabelas.
4. Cadastrar as chaves de API necessárias via Railway CLI e guardar cada chave retornada.
5. Ao hospedar o front, definir `ANALISE_BETS_API_URL` no serviço Next.js com o domínio público da
   API e validar o fluxo ponta a ponta. CORS só precisa ser configurado se o navegador chamar a API
   diretamente.

**Limitação conhecida:** a carga pré-deploy substitui as tabelas de leitura enquanto a versão
anterior pode continuar recebendo tráfego; pode ocorrer uma breve falha de consulta durante esse
passo. As tabelas operacionais e suas chaves permanecem no PostgreSQL.

### 5.7 Avaliação do Railway e do front (2026-09-24)

O plugin Railway ficou disponível nesta sessão e confirmou a conta Railway autenticada. O projeto
`fortunate-charisma` contém o serviço `analise-bets`, ligado ao repositório `ataidefilipe/analise-bets`
na branch `main`; o primeiro deploy está `FAILED`. Ainda não há variáveis de aplicação, domínio
público nem PostgreSQL nesse projeto.

A criação do PostgreSQL pelo agente Railway foi tentada e recusada pela plataforma: o workspace
está no plano Free e atingiu o limite de provisionamento de recursos. Nenhum serviço adicional ou
alteração de cobrança foi criado. É necessário o usuário atualizar o plano no Railway antes de
continuar com API e banco.

**Front:** `frontend/` é um app Next.js 16 com React 19, `pnpm@11.4.0`, lockfile próprio e scripts
`build`/`start`. Está apto a ser configurado como um serviço separado do mesmo repositório, com
root directory `/frontend`. Requer `ANALISE_BETS_API_URL` apontando para o domínio público da API.
As chamadas à API são feitas no servidor Next.js, portanto CORS não é necessário para o fluxo atual.
O serviço chamado `frontend` encontrado em outro projeto Railway aponta para outro repositório e
não foi reutilizado.

As dependências do front foram instaladas com `pnpm install --frozen-lockfile` e o build de produção
`pnpm build` foi concluído com sucesso (Next.js compilou, verificou TypeScript e gerou as rotas).
O primeiro build local sem rede falhou ao buscar Geist e Geist Mono do Google Fonts; com acesso à rede,
o build passou. O Railway ainda não recebeu esses arquivos locais porque as alterações desta branch
não foram publicadas no GitHub.

**Retomada depois da atualização de plano:** provisionar PostgreSQL em `fortunate-charisma`, ligar
`DATABASE_URL` e o segredo na API, publicar as alterações locais do backend/configuração e validar
`/saude`; então criar o serviço Next.js com root `/frontend`, configurar o domínio da API em
`ANALISE_BETS_API_URL` e validar a entrada e as telas com uma chave de API.

### 5.8 Railway após a atualização do plano (2026-09-24)

O serviço `Postgres` foi provisionado em `fortunate-charisma` e está `SUCCESS`, com volume persistente
de 5 GB em `sfo`. A API tem `DATABASE_URL` referenciando `${{Postgres.DATABASE_URL}}` e o segredo
`ANALISE_BETS_PSEUDONIMO_SECRET` foi gerado aleatoriamente e cadastrado sem expor seu valor. O
Railway também recebeu start command, pré-deploy da carga, healthcheck `/saude` e política de restart.

O deploy da API continua `FAILED`: ele ainda usa o commit remoto `9444f97`, sem `railway.json`,
`requirements.txt` e os ajustes locais de PostgreSQL. Os logs não trouxeram a causa além de iniciar o
builder. A publicação desses arquivos e um novo deploy são necessários para validar a API. Depois do
deploy, validar `/saude` e a carga inicial no PostgreSQL.

Não foi criado domínio público para a API. A análise automática rejeitou essa exposição por tratar-se
de uma API com dados identificados. Como o Next.js acessa a API no servidor, o front pode usar o DNS
privado Railway da API por `ANALISE_BETS_API_URL`; isso mantém os dados atrás da autenticação sem
precisar expor a API à internet. O serviço frontend ainda precisa ser criado em `/frontend`.

O build local do front foi aprovado. Para disponibilizar as telas, criar o serviço Next.js e configurar
`ANALISE_BETS_API_URL` com a URL privada da API. Uma chave da API só deve ser criada quando o perfil e
o cliente para validação forem definidos.

---

## 6. Testes

[`tests/test_api.py`](../tests/test_api.py) cria um banco SQLite num diretório temporário, insere um
conjunto mínimo (duas equipes, dois atletas, uma partida) e troca o engine com `db.definir_engine()`.
Os 18 testes cobrem:

* 401 sem chave; 400 com `perfil`/`clube` na query; trading não cadastrável;
* corte da fila, componentes obrigatórios, fila do clube restrita ao elenco, 403 para camada aberta, 422 sem escalação;
* busca com 3 caracteres, sem escore, e registro de busca e de ficha em `consultas_atleta`;
* dossiê sem identificação na camada aberta e com sinalizados na identificada;
* agregados sem atleta; formato dos erros 400 e 404;
* nome de clube ao lado do slug; listagem de partidas com paginação e busca; cobertura.

---

## 7. Segurança e LGPD

| Item | Situação |
| :--- | :--- |
| Banco da API | Contém nome e registro CBF **sem pseudônimo**. `data/api/` está no `.gitignore` |
| Chaves | Só o SHA-256 no banco; as chaves demo ficam em `data/restrito/` (fora do Git) |
| Trilha de due diligence | `consultas_atleta`, gravada em toda busca e ficha. Falha de gravação não derruba a requisição e gera log `CRITICAL` com "ALARME" |
| Logs | A API não registra corpo de resposta. O log de erro traz só o caminho da URL |
| Segredo de pseudonimização | Verificado na subida; ver §5.1 |
| **Não implementado** | Rate limiting, expiração de chave, TLS, retenção de 12 meses de `consultas_atleta`, trilha técnica no CloudWatch |

**Não exponha esta API fora de rede local.** Sem rate limiting, uma chave vazada permite varrer a
base atleta a atleta; o registro de consultas só mostraria isso depois.

---

## 8. Diferenças em relação à especificação

A lista completa, com efeito para o front, está em
[integracao_frontend.md §9](integracao_frontend.md#9-diferenças-em-relação-à-especificação-e-limitações-da-poc).
As que afetam o backend:

| Especificação | Implementado | Por quê |
| :--- | :--- | :--- |
| RDS PostgreSQL (04 §2) | SQLite padrão, Postgres por URL | POC local; schema portável |
| Índice `cartoes(registro_cbf)` sobre coluna existente (04 §3) | Coluna criada na carga por junção com `escalacoes` | A coluna não existe na base de origem |
| Percentil e tier materializados (04 §3.4) | Feito, na carga da API, não no pipeline | Menor mudança possível no pipeline validado |
| p70 ≈ 3 alertas/rodada (02 §3) | p70 ≈ 30% da rodada | O percentil é da distribuição do escore pré-jogo; a estimativa veio do escore retrospectivo. **Decisão pendente** |
| Fila de rodada futura com escalação anterior (05 §2) | 422 | Fora do escopo da POC |
| Dossiê "completo" para `clube` (01 §5) | Sinalizados só do elenco | Coerência com 02 §4.2: lista proativa só do próprio elenco |
| Procedência em todas as partidas com súmula | A 2025–2026 e B 2024–2026 | Manifesto não cobre B 2022–2023; o de A 2024 não casa com os ids da base |

> **LGPD.** A base legal do tratamento (tarefa F4-01) não foi estabelecida. O banco da API combina
> identificação com inferência estatística sobre a pessoa, que é a combinação de maior sensibilidade
> do sistema.
>
> Caso o seu projeto envolva dados pessoais ou dados pessoais sensíveis, comunique ao time de
> Segurança da Informação através do e-mail seginfo@gcb.com.br
