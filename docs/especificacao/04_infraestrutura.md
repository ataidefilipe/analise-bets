# 04 — Infraestrutura

**Destrava:** etapa 3 (AWS).
**Escopo:** protótipo / MVP.

O dimensionamento abaixo parte de números medidos, não estimados. O sistema é pequeno: cabe
numa instância modesta e roda por minutos, uma vez ao dia.

---

## 1. Dimensionamento medido

| Item | Valor | Origem |
| :--- | ---: | :--- |
| Base processada (Parquet + CSV) | **67 MB** | medido |
| Banco do feed (SQLite) | **44 MB** | medido |
| Súmulas brutas em PDF | **113 MB** | medido, ~2.400 arquivos |
| Linhas na maior tabela | **107.990** | `escalacoes`, `risco_pre_jogo` |
| Total de linhas em todas as tabelas | **~300.000** | |

### Execução do pipeline

| Etapa | Tempo medido |
| :--- | ---: |
| Ingestão de 760 súmulas (temporada completa) | ~185 s |
| Ingestão de uma rodada (10 partidas) | **< 10 s** |
| Recálculo do escore pré-jogo (base inteira) | ~90 s |
| Geração dos feeds | ~10 s |
| **Execução diária típica (D+1)** | **< 3 minutos** |

### Crescimento

Uma temporada completa das duas séries adiciona ~760 partidas, ~4.000 cartões e ~35.000 linhas
de escalação — cerca de **35 MB/ano** de PDF e **10 MB/ano** de base processada.

> **Conclusão de dimensionamento:** este não é um problema de escala. Qualquer arquitetura
> serverless ou de instância única resolve com folga. Otimizar para volume seria desperdício de
> esforço; o que merece atenção é o controle de acesso ao dado pessoal.

---

## 2. Componentes [MVP]

```
┌─────────────┐   diário    ┌──────────────────┐
│ EventBridge │────────────▶│  ECS Fargate     │  pipeline (Python 3.13)
│  (cron)     │             │  Task pontual    │  ingestão → parsing → escores → feeds
└─────────────┘             └────────┬─────────┘
                                     │ escreve
                     ┌───────────────┼────────────────┐
                     ▼               ▼                ▼
              ┌────────────┐  ┌────────────┐  ┌──────────────┐
              │ S3         │  │ RDS        │  │ Secrets      │
              │ súmulas    │  │ PostgreSQL │  │ Manager      │
              │ PDF brutas │  │ (db.t4g.   │  │ segredo de   │
              │            │  │  micro)    │  │ pseudonimo   │
              └────────────┘  └─────┬──────┘  └──────┬───────┘
                                    │ lê            │ lê
                             ┌──────▼────────────────▼──┐
                             │  ECS Fargate — API       │
                             │  FastAPI, 1 task         │
                             └──────────┬───────────────┘
                                        │ HTTPS
                             ┌──────────▼───────────────┐
                             │  ALB + ACM (TLS)         │
                             └──────────┬───────────────┘
                                        │
                             ┌──────────▼───────────────┐
                             │  S3 + CloudFront (front) │
                             └──────────────────────────┘
```

### Escolhas e por quês

| Componente | Escolha MVP | Racional |
| :--- | :--- | :--- |
| Banco | **RDS PostgreSQL `db.t4g.micro`** | O SQLite atual é artefato de desenvolvimento — um arquivo não serve a leituras concorrentes de uma API. Postgres é o menor salto que resolve |
| Pipeline | **ECS Fargate Task** disparada por EventBridge | Roda em ~3 min, muito além do limite de 15 min do Lambda não ser problema — mas `pdfplumber` e `scikit-learn` estouram o tamanho de camada do Lambda com folga |
| API | **ECS Fargate Service**, 1 task | FastAPI. Sem auto-scaling no MVP |
| PDFs | **S3**, classe Standard-IA | Não versionados no Git (decisão de 18/09/2026). São a fonte primária e a prova de procedência |
| Front | **S3 + CloudFront** | Estático |
| Segredos | **Secrets Manager** | Ver §5 — item crítico |
| Logs | **CloudWatch**, retenção 30 dias | |

### Ambientes [MVP]

**Um só: produção.** Sem homologação, sem staging.

> **[MVP] Dívida.** Sem ambiente de homologação, toda mudança de pipeline é testada em
> produção. Mitigação parcial: a suíte de 153 testes roda local antes do deploy, e o pipeline é
> idempotente — reexecutar não corrompe. O que **não** está mitigado é uma migração de schema
> defeituosa.

---

## 3. Modelo de dados em produção

O SQLite atual mapeia quase diretamente para Postgres. Tabelas, com índices que a API precisa:

| Tabela | Linhas | Índices |
| :--- | ---: | :--- |
| `partidas` | 11.220 | `(serie, temporada, rodada)`, PK `(serie, temporada, partida_id)` |
| `cartoes` | 34.248 | `(temporada, partida_id, clube_slug, num_camisa)`, `(registro_cbf)` |
| `gols` | 15.310 | idem |
| `escalacoes` | 107.990 | `(serie, temporada, rodada)`, `(registro_cbf)` |
| `minutos_em_campo` | 6.561 | `(registro_cbf, temporada)` |
| `risco_pre_jogo` | 107.990 | `(serie, temporada, rodada, score_pre_jogo DESC)` |
| `classificacao` | 598 | |
| `avisos` | 1 | chave-valor |
| **`clientes_api`** | — | **Nova.** Ver [01 §2](01_api_e_autorizacao.md) |

### Três acréscimos necessários

1. **`clientes_api`** — não existe hoje. É o que sustenta toda a autorização.
2. **Colunas de procedência em `partidas`** — `sumula_url`, `sumula_sha256`, `baixado_em`,
   `processado_em`. Os dados já existem em `data/raw/cbf/manifest_delta.json` e precisam ser
   promovidos a coluna, porque são o produto vendido a P3.
3. **Colunas de percentil e tier** — `risco_pre_jogo` guarda o escore bruto; percentil e tier
   são calculados no pipeline e devem ser **materializados**, não computados por requisição.

---

## 4. Segurança

### 4.1 O dado é pessoal

As tabelas `escalacoes`, `cartoes`, `gols`, `minutos_em_campo` e `risco_pre_jogo` contêm nome,
apelido e registro CBF de atletas — **dado pessoal sob a LGPD**. A tabela `risco_pre_jogo`
combina identificação com inferência sobre a pessoa, que é a combinação de maior sensibilidade
do sistema.

Requisitos mínimos:

* RDS em **subnet privada**, sem IP público. Acesso só pela API e pela task do pipeline.
* **Criptografia em repouso** no RDS e no S3 (`SSE-S3` basta no MVP).
* TLS obrigatório. Sem porta 80 aberta, redirect no ALB.
* Bucket de PDFs **sem acesso público**, com *Block Public Access* ligado.
* Logs **não registram** payload de resposta nem nome de atleta. Logar `atleta_id`, nunca
  `atleta`.

### 4.2 Trilha de acesso [MVP]

Log de acesso com: timestamp, `cliente_api.id`, endpoint, parâmetros e código de resposta.
Retenção 30 dias.

> **[MVP] Dívida.** Sem log de *quais atletas* foram consultados por cada cliente. Para uma
> eventual requisição de titular sob a LGPD, isso seria necessário — e a base legal em si
> (F4-01) também não existe.

---

## 5. O segredo de pseudonimização — item crítico

Hoje, em `src/pipeline/perfis_de_acesso.py`:

```python
SEGREDO_PSEUDONIMIZACAO = os.environ.get(
    "ANALISE_BETS_PSEUDONIMO_SECRET", "desenvolvimento-nao-usar-em-producao"
)
```

**Se a variável não estiver definida, o sistema sobe com o segredo de desenvolvimento e não
avisa.** O valor padrão está no código-fonte, e o espaço de registros da CBF é pequeno o
bastante para ser varrido por força bruta em minutos — a pseudonimização vira decoração.

**Requisitos:**

1. Segredo gerado aleatoriamente (≥ 32 bytes) e guardado no **Secrets Manager**.
2. Injetado como variável de ambiente na task da API e na do pipeline.
3. **A aplicação deve recusar subir** se a variável não estiver definida ou se for igual ao
   valor de desenvolvimento. Falhar ruidosamente, nunca silenciosamente.
4. O segredo **nunca muda** sem reprocessamento: trocá-lo invalida todos os pseudônimos já
   emitidos e quebra a continuidade de acompanhamento do mesmo atleta.

> Esta é a única mudança de código que a etapa 3 exige antes do deploy. As demais são
> configuração.

---

## 6. Custo estimado

| Item | Ordem de grandeza mensal (USD) |
| :--- | ---: |
| RDS `db.t4g.micro`, 20 GB | ~15 |
| ECS Fargate — API, 0,25 vCPU contínua | ~10 |
| ECS Fargate — pipeline, 3 min/dia | < 1 |
| ALB | ~18 |
| S3 + CloudFront | < 2 |
| Secrets Manager | < 1 |
| **Total** | **~45–50** |

O ALB é o maior item isolado. Se o custo for restrição, API Gateway HTTP + Lambda sai mais
barato ao custo de reempacotar as dependências pesadas — troca que não vale no MVP.

---

## 7. Deploy [MVP]

Manual, documentado num `README` de infraestrutura. Sem CI/CD, sem IaC obrigatório — embora
Terraform ou CDK valha o esforço mesmo no MVP, porque o ambiente será recriado várias vezes.

> **[MVP] Dívida.** Sem pipeline de deploy, sem rollback automatizado, sem *blue/green*. Um
> deploy ruim da API derruba o serviço até alguém reverter à mão.

> Caso o seu projeto envolva dados pessoais ou dados pessoais sensíveis, comunique ao time de
> Segurança da Informação através do e-mail seginfo@gcb.com.br
