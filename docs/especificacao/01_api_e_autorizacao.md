# 01 — Contrato de API e modelo de autorização

**Destrava:** etapa 4 (backend) e etapa 5 (front-end).
**Escopo:** protótipo / MVP.

Autorização e contrato de API estão no mesmo documento de propósito: neste sistema, **a
resposta muda conforme quem pergunta**. Especificar os endpoints sem o modelo de autorização
produziria um backend que devolve nome de atleta para quem não pode vê-lo.

---

## 1. O princípio inegociável

> **A identidade do chamador vem do token. Nunca do corpo ou da query da requisição.**

Hoje, `aplicar_perfil(df, perfil, clube_do_cliente=...)` recebe o perfil e o clube como
argumentos — quem chama declara quem é. Isso é aceitável numa biblioteca, e é uma falha de
autorização num serviço.

No backend, `perfil` e `clube` **não são parâmetros de entrada**. São atributos da credencial,
resolvidos antes de qualquer consulta. Um cliente do perfil `clube` que passar
`?clube=palmeiras` na URL deve receber **400**, não os dados do Palmeiras.

---

## 2. Autenticação [MVP]

**Chave de API estática, no header.**

```
Authorization: Bearer <api_key>
```

A chave é gerada manualmente e cadastrada na tabela `clientes_api`. Não há auto-atendimento,
cadastro, recuperação de senha nem rotação automática.

### Tabela `clientes_api`

| Coluna | Tipo | Observação |
| :--- | :--- | :--- |
| `id` | uuid | PK |
| `nome` | text | Identificação humana do cliente |
| `api_key_hash` | text | **SHA-256 da chave.** A chave em claro nunca é persistida |
| `perfil` | text | Um de: `federacao_stjd`, `clube`, `operadora_integrity`, `imprensa_academia` |
| `clube_slug` | text | Obrigatório quando `perfil = 'clube'`; nulo nos demais |
| `ativo` | boolean | Desativação é a única revogação prevista |
| `criado_em` | timestamptz | |

> **[MVP] Dívida assumida.** Chave estática sem expiração, sem escopo por endpoint, sem
> rotação e sem limite de taxa. Para produção: OAuth2 client credentials com tokens de vida
> curta, rate limiting por cliente e trilha de auditoria de acesso. O item mais urgente da
> lista não é o OAuth — é o **rate limiting**, porque sem ele uma chave vazada permite
> reconstruir a base inteira por varredura.

### Resolução do contexto

A cada requisição, antes do roteamento:

1. Extrair a chave do header. Ausente ou malformada → **401**.
2. `SHA-256` da chave, buscar em `clientes_api`. Não encontrada ou `ativo = false` → **401**.
3. Carregar `perfil` e `clube_slug` num objeto de contexto imutável.
4. Se `perfil = 'operadora_trading'` → **403** com o motivo da recusa. *(O perfil não deve
   sequer ser cadastrável; a verificação existe como defesa em profundidade.)*

O contexto acompanha a requisição até a camada de dados. Nenhuma consulta é montada sem ele.

---

## 3. Camadas de dados e projeção da resposta

Cada perfil enxerga uma **camada**. A projeção é responsabilidade do backend e acontece na
saída, sempre — nunca é opcional, nunca depende do endpoint lembrar de aplicá-la.

| Camada | Perfis | O que sai |
| :--- | :--- | :--- |
| `identificada` | `federacao_stjd`, `clube` | Nome, apelido, `registro_cbf`, número de camisa |
| `aberta` | `operadora_integrity`, `imprensa_academia` | Agregados por clube, rodada e temporada. Nenhuma linha individual |

A camada `pseudonimizada` existe no código e **não é usada por nenhum perfil no MVP**. Fica
especificada para quando houver um perfil que precise acompanhar o mesmo atleta ao longo do
tempo sem saber quem é.

### Identificador de atleta na resposta

| Camada | Campo | Valor |
| :--- | :--- | :--- |
| `identificada` | `atleta_id` | `registro_cbf` |
| `pseudonimizada` | `atleta_id` | `atl_<16 hex>`, HMAC-SHA256 do registro |
| `aberta` | — | Não há atleta na resposta |

O front trata `atleta_id` como opaco. **Não deve derivar nada dele**, nem assumir formato.

### A exceção dos condenados

Atletas com condenação transitada em julgado são fato público e podem ser nominados em
qualquer camada. Hoje são os 10 atletas da Operação Penalidade Máxima. A lista é servida por
`GET /v1/atletas/nominaveis` e **não é hard-coded no front**.

---

## 4. Endpoints [MVP]

Seis endpoints. REST, JSON, prefixo `/v1`.

Convenções: datas em ISO-8601 com fuso; `serie` é `"A"` ou `"B"`; `temporada` é o ano com
quatro dígitos; toda lista devolve `{ "dados": [...], "total": n }`.

---

### 4.1 `GET /v1/me`

Quem sou eu e o que posso. O front chama **uma vez no início da sessão** e usa a resposta para
decidir quais telas montar.

```json
{
  "perfil": "federacao_stjd",
  "rotulo": "Federação, STJD ou órgão de investigação",
  "camada": "identificada",
  "granularidade": ["partida", "atleta"],
  "clube_slug": null,
  "limiar_padrao": { "percentil": 70.0, "alertas_por_rodada_esperados": 3.0 },
  "aviso_interpretativo": "Este escore mede ATIPICIDADE ESTATÍSTICA..."
}
```

---

### 4.2 `GET /v1/rodadas/{serie}/{temporada}/{rodada}/fila`

**A tela principal.** Fila de triagem: dos atletas escalados na rodada, quais concentram
atipicidade disciplinar.

Perfis: `federacao_stjd`, `clube`.

| Parâmetro | Tipo | Padrão | Observação |
| :--- | :--- | :--- | :--- |
| `percentil` | float | o de `/v1/me` | Corte do escore. Ver [02 §3](02_regras_de_negocio.md) |
| `limite` | int | 50 | Máximo 200 |

```json
{
  "contexto": {
    "serie": "A", "temporada": 2026, "rodada": 28,
    "percentil_aplicado": 70.0,
    "total_relacionados": 920,
    "total_sinalizados": 3
  },
  "dados": [
    {
      "atleta_id": "459744",
      "atleta": "Nome do Atleta",
      "num_camisa": 10,
      "clube_slug": "exemplo_fc",
      "partida_id": 271,
      "confronto": "Exemplo FC x Outro FC",
      "condicao": "Titular",
      "score_pre_jogo": 0.1842,
      "percentil": 99.2,
      "tier": "Extrema Anomalia Temporal (Top 1%)",
      "componentes": {
        "minutos_previos": 2430,
        "cartoes_1t_previos": 7,
        "taxa_1t_ajustada": 0.00205,
        "minutos_esperados": 82.0
      }
    }
  ],
  "total": 3,
  "aviso_interpretativo": "Este escore mede ATIPICIDADE ESTATÍSTICA..."
}
```

**`componentes` é obrigatório.** O escore é uma conta aberta —
`taxa_1t_ajustada × minutos_esperados` — e a persona P2 precisa fundamentar em despacho por
que abriu ou arquivou. Uma fila sem os componentes é uma caixa-preta e não serve.

Para `perfil = 'clube'`, o backend filtra por `clube_slug` da credencial **antes** de aplicar o
corte por percentil. O clube vê os seus atletas sinalizados, não os atletas do seu clube que
estariam na fila geral.

---

### 4.3 `GET /v1/atletas/{atleta_id}`

Consulta pontual. É a dor mais concreta da persona P1: *não contratar um problema*.

Perfis: `federacao_stjd`, `clube`.

Para `perfil = 'clube'`, o atleta precisa estar no elenco do clube **ou** o clube precisa ter
declarado interesse — ver §5. Fora disso, **403**.

```json
{
  "atleta_id": "459744",
  "atleta": "Nome do Atleta",
  "clubes": ["exemplo_fc", "outro_fc"],
  "historico": [
    {
      "temporada": 2025, "serie": "A", "clube_slug": "exemplo_fc",
      "partidas_jogadas": 34, "minutos_em_campo": 2890,
      "cartoes_total": 11, "cartoes_1t": 8,
      "prop_cartoes_1t": 0.727,
      "athlete_anomaly_score": 68.4,
      "percentil": 98.7,
      "tier": "Extrema Anomalia Temporal (Top 1%)"
    }
  ],
  "cartoes": [
    {
      "temporada": 2025, "partida_id": 89, "rodada": 9,
      "minuto_continuo": 23, "periodo": "1T", "cartao": "Amarelo",
      "categoria_infracao": "falta_temeraria",
      "motivo_completo": "A4. Infringir persistentemente as regras do jogo - ..."
    }
  ],
  "aviso_interpretativo": "..."
}
```

`motivo_completo` só existe onde a súmula tem o campo: **100% da Série B, 14% da Série A** (só
2025 e 2026 — os anos de origem Kaggle não têm o dado na fonte). O front precisa lidar com a
ausência sem parecer defeito.

---

### 4.4 `GET /v1/partidas/{serie}/{temporada}/{partida_id}/dossie`

Registro auditável de uma partida. É o que a persona P3 compra: **papel, não predição**.

Perfis: todos os atendidos. A camada determina o conteúdo — `aberta` recebe o dossiê sem a
seção de atletas.

```json
{
  "partida": {
    "partida_id": 271, "serie": "A", "temporada": 2026, "rodada": 28,
    "data": "2026-09-14", "arena": "...", "arbitro": "...",
    "clube_mandante_slug": "exemplo_fc", "clube_visitante_slug": "outro_fc",
    "placar": "2-1"
  },
  "match_anomaly_score": 12.4,
  "percentil": 71.2,
  "tier": "Típico / Baixa Prioridade",
  "cartoes": [ "..." ],
  "atletas_sinalizados": [ "..." ],
  "procedencia": {
    "fonte": "Súmula Eletrônica CBF",
    "url": "https://conteudo.cbf.com.br/sumulas/2026/142271se.pdf",
    "sha256": "a3f1...",
    "baixado_em": "2026-09-15T02:14:07-03:00",
    "processado_em": "2026-09-15T02:19:33-03:00"
  },
  "aviso_interpretativo": "..."
}
```

**`procedencia` é o produto**, não metadado. A persona P3 precisa provar à SPA que monitorou a
partida, citando fonte oficial, hash e data. Os três campos já existem em
`data/raw/cbf/manifest_delta.json` e precisam ser promovidos a coluna da tabela `partidas`.

---

### 4.5 `GET /v1/agregados/{serie}/{temporada}`

Camada aberta. Serve P5 e a visão macro de P3.

| Parâmetro | Tipo | Padrão |
| :--- | :--- | :--- |
| `por` | enum: `clube` \| `rodada` | `clube` |

```json
{
  "dados": [
    {
      "clube_slug": "exemplo_fc",
      "partidas": 38, "cartoes": 92, "cartoes_1t": 31,
      "prop_cartoes_1t": 0.337,
      "media_cartoes_por_partida": 2.42
    }
  ],
  "total": 20
}
```

Sem atleta, em nenhuma circunstância.

---

### 4.6 `GET /v1/atletas/nominaveis`

Lista de atletas que podem ser nominados em qualquer camada, por condenação transitada em
julgado. Consumida pelo front para decidir exibição de nome; **não é lista de suspeitos**.

```json
{
  "dados": [
    { "atleta_id": "...", "atleta": "...", "sancao": "...", "fonte": "STJD, processo ..." }
  ],
  "total": 10
}
```

---

## 5. Autorização por perfil, endpoint a endpoint

| Endpoint | `federacao_stjd` | `clube` | `operadora_integrity` | `imprensa_academia` |
| :--- | :---: | :---: | :---: | :---: |
| `/me` | ✅ | ✅ | ✅ | ✅ |
| `/rodadas/.../fila` | ✅ | ✅ *(só o próprio elenco)* | ❌ 403 | ❌ 403 |
| `/atletas/{id}` | ✅ | ⚠️ *(escopo, abaixo)* | ❌ 403 | ❌ 403 |
| `/partidas/.../dossie` | ✅ completo | ✅ completo | ✅ sem atletas | ✅ sem atletas |
| `/agregados/...` | ✅ | ✅ | ✅ | ✅ |
| `/atletas/nominaveis` | ✅ | ✅ | ✅ | ✅ |

### O escopo do perfil `clube` [MVP]

A regra de negócio diz: *o clube vê o próprio elenco e alvos de contratação declarados*.

**No MVP, só a primeira metade é implementada.** O clube consulta atletas que estão ou
estiveram no seu elenco em qualquer temporada da base. Consulta a terceiros retorna **403**.

> **[MVP] Dívida assumida.** Não há fluxo de declaração de alvo de contratação — nem tela, nem
> registro, nem expiração. Isso remove do MVP justamente o caso de uso que a análise de negócio
> aponta como a dor mais concreta de P1 (*due diligence antes de assinar*). É a maior lacuna
> funcional desta especificação, e é deliberada: o fluxo exige registro de finalidade,
> aprovação e prazo de validade, que são precisamente os controles que a tarefa F4-01 deveria
> fundamentar — e F4-01 não foi feita.

---

## 6. Erros

| Código | Quando | Corpo |
| :---: | :--- | :--- |
| 400 | Parâmetro inválido, ou tentativa de passar `perfil`/`clube` na requisição | `{"erro": "parametro_invalido", "detalhe": "..."}` |
| 401 | Chave ausente, malformada, desconhecida ou inativa | `{"erro": "nao_autenticado"}` |
| 403 | Perfil sem acesso ao endpoint, ou fora do escopo do elenco | `{"erro": "sem_permissao", "detalhe": "..."}` |
| 404 | Rodada, partida ou atleta inexistente na base | `{"erro": "nao_encontrado"}` |
| 422 | Rodada ainda sem escalação publicada | `{"erro": "sem_escalacao", "detalhe": "..."}` |
| 500 | — | `{"erro": "erro_interno"}` — nunca vaza stack trace |

O **422** merece atenção do front: a escalação só existe depois que a CBF publica a súmula.
Consultar a fila de uma rodada futura é o caso normal, não um erro do usuário. Ver
[03 — Telas §6](03_telas.md).

---

## 7. O que o backend precisa reaproveitar, e não reimplementar

O cálculo dos escores está implementado, testado e validado contra vazamento temporal. **Não
deve ser reescrito em outra linguagem.**

| Regra | Onde vive | Nota |
| :--- | :--- | :--- |
| Projeção por camada | `src/pipeline/perfis_de_acesso.py::aplicar_perfil` | Trocar o argumento `perfil` pelo contexto do token |
| Escore pré-jogo | `src/models/score_pre_jogo.py::calcular_score` | Batch. A API lê o resultado |
| Escores de anomalia | `src/models/anomaly_detection.py` | Batch |
| Pseudonimização | `perfis_de_acesso.py::pseudonimizar` | Ver [04 §5](04_infraestrutura.md) sobre o segredo |
| Atletas nomináveis | `src/pipeline/camadas_de_exposicao.py::nomes_nominaveis` | |

O backend é uma camada de leitura sobre tabelas pré-calculadas pelo pipeline. **Nenhum escore é
computado em tempo de requisição** — ver [05 — Automação](05_automacao.md).

> Caso o seu projeto envolva dados pessoais ou dados pessoais sensíveis, comunique ao time de
> Segurança da Informação através do e-mail seginfo@gcb.com.br
