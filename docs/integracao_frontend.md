# Guia de integração do front-end — API da POC

**Para:** time de front-end (etapa 5).
**Escopo:** POC. Não é contrato de produção. Onde a implementação difere da
[especificação](especificacao/README.md), a diferença está listada na [§9](#9-diferenças-em-relação-à-especificação-e-limitações-da-poc).

Leia antes: [02 — Regras de negócio](especificacao/02_regras_de_negocio.md) (vocabulário e tiers)
e [03 — Telas](especificacao/03_telas.md) (as quatro telas). Este guia diz **como chamar a API**;
aqueles dizem **o que mostrar**.

> Todos os exemplos usam nomes e registros fictícios.

---

## 1. Subir a API localmente

```bash
pip install -r requirements-api.txt
python -m src.api.carga                      # monta o banco (uma vez, ~10 s) e cria chaves demo
ANALISE_BETS_AMBIENTE=dev uvicorn src.api.main:app --reload --port 8000
```

No Windows (PowerShell): `$env:ANALISE_BETS_AMBIENTE="dev"` antes do `uvicorn`.

| | |
| :--- | :--- |
| URL base | `http://localhost:8000` |
| Documentação interativa (Swagger) | `http://localhost:8000/docs` |
| Schema OpenAPI (para gerar cliente tipado) | `http://localhost:8000/openapi.json` |
| Verificação de vida, sem autenticação | `GET /saude` → `{"status": "ok"}` |

Sem `ANALISE_BETS_AMBIENTE=dev`, a API **recusa subir** se o segredo de pseudonimização não
estiver configurado. Isso é intencional (documento 04 §5).

### Chaves de demonstração

A primeira carga cria uma chave por perfil e grava todas em `data/restrito/chaves_api_poc.json`
(fora do Git). Peça o arquivo a quem subiu o backend: as chaves **não** vão por chat nem por
repositório.

| Perfil | Camada | Clube |
| :--- | :--- | :--- |
| `federacao_stjd` | identificada | — |
| `clube` | identificada | `flamengo` |
| `operadora_integrity` | aberta | — |
| `imprensa_academia` | aberta | — |

Outras chaves: `python -m src.api.clientes criar --nome "..." --perfil clube --clube <slug>`.

---

## 2. Autenticação

Toda chamada em `/v1` leva o header:

```
Authorization: Bearer <api_key>
```

**Perfil e clube vêm da chave, nunca da requisição.** Se a URL tiver `perfil`, `clube`,
`clube_slug` ou `camada` na query, a resposta é **400**. O front não precisa (e não pode)
informar quem é o usuário: basta enviar a chave.

Na POC, a chave é estática. Para teste local, guarde-a em memória ou em `sessionStorage`. Não
coloque a chave no bundle nem em `localStorage` compartilhado.

---

## 3. Convenções

| Item | Regra |
| :--- | :--- |
| Formato | JSON, UTF-8, só `GET` |
| `serie` | `"A"` ou `"B"`, em maiúscula. Qualquer outro valor gera 400 |
| `temporada` | ano com quatro dígitos |
| Listas | `{ "dados": [...], "total": n }`. `total` é o número de itens em `dados` |
| Datas | `data`: `YYYY-MM-DD`. Carimbos de procedência: ISO-8601 com fuso |
| `atleta_id` | **opaco.** Hoje é o registro CBF, mas não derive nada dele nem valide formato |
| Nulos | Campo ausente na fonte vem como `null`. Não trate como erro |
| CORS | Liberado para qualquer origem na POC (`ANALISE_BETS_CORS` restringe) |

---

## 4. Fluxo de sessão

```
login (usuário cola a chave)
   └─ GET /v1/me ──► guarda perfil, camada, granularidade, limiar_padrao, aviso
         ├─ camada = "identificada" → menu: T1 Fila · T2 Atletas · T3 Dossiê · T4 Panorama
         └─ camada = "aberta"       → menu: T3 Dossiê · T4 Panorama
```

Uma tela negada **não aparece**, nem desabilitada (documento 03 §0). Monte o menu a partir de
`camada`:

| Tela | Endpoint | Aparece quando |
| :--- | :--- | :--- |
| T1 Fila de triagem | `/v1/rodadas/.../fila` | `camada === "identificada"` |
| T2 Busca e ficha | `/v1/atletas`, `/v1/atletas/{id}` | `camada === "identificada"` |
| T3 Dossiê de partida | `/v1/partidas`, `/v1/partidas/.../dossie` | sempre |
| T4 Panorama | `/v1/agregados/...` | sempre |

Mesmo assim, o backend é quem decide: se a tela for chamada por um perfil sem acesso, a
resposta é 403.

Para montar os filtros de série, temporada e rodada, chame `GET /v1/cobertura` uma vez por
sessão (§5.8). Não fixe anos no código: a cobertura muda a cada execução do pipeline.

**Nomes de clube.** Todo objeto que traz `clube_slug` traz também `clube`, o nome legível.
Exiba `clube`, nunca o slug. Em listas (`clubes` da busca e da ficha), cada item é
`{"clube_slug": "...", "clube": "..."}`.

---

## 5. Endpoints

### 5.1 `GET /v1/me`

```json
{
  "perfil": "clube",
  "rotulo": "Clube",
  "camada": "identificada",
  "granularidade": ["atleta"],
  "clube_slug": "exemplo_fc",
  "clube": "Exemplo FC",
  "limiar_padrao": { "percentil": 90.0, "alertas_por_rodada_esperados": 1.0 },
  "aviso_interpretativo": "Este escore mede ATIPICIDADE ESTATÍSTICA ..."
}
```

`limiar_padrao` é `null` em `imprensa_academia`. Use `limiar_padrao.percentil` como valor
inicial do slider da T1.

---

### 5.2 `GET /v1/rodadas/{serie}/{temporada}/{rodada}/fila` — T1

Perfis: `federacao_stjd`, `clube`.

| Query | Tipo | Padrão | Faixa |
| :--- | :--- | :--- | :--- |
| `percentil` | número | `limiar_padrao.percentil` do perfil | 0 a 100 |
| `limite` | inteiro | 50 | 1 a 200 |

```json
{
  "contexto": {
    "serie": "A", "temporada": 2026, "rodada": 20,
    "percentil_aplicado": 70.0,
    "clube_slug": null,
    "clube": null,
    "total_relacionados": 458,
    "total_sinalizados": 136,
    "base_rasa": false,
    "aviso_base_rasa": null
  },
  "dados": [
    {
      "atleta_id": "900001",
      "atleta": "Fulano",
      "nome_completo": "Fulano de Tal",
      "num_camisa": 5,
      "clube_slug": "exemplo_fc",
      "clube": "Exemplo FC",
      "partida_id": 191,
      "confronto": "Exemplo FC x Outro FC",
      "condicao": "Titular",
      "score_pre_jogo": 0.2118,
      "percentil": 99.5,
      "tier": "Extrema Anomalia Temporal (Top 1%)",
      "componentes": {
        "minutos_previos": 1079.0,
        "cartoes_1t_previos": 4.0,
        "taxa_1t_ajustada": 0.00282,
        "minutos_esperados": 82.0
      }
    }
  ],
  "total": 1,
  "aviso_interpretativo": "Este escore mede ATIPICIDADE ESTATÍSTICA ..."
}
```

**Como usar na tela:**

* **Contador do slider:** `"{total_sinalizados} de {total_relacionados} relacionados"`.
  `dados` vem limitado por `limite`; `total_sinalizados` traz o total acima do corte.
* **Slider:** a cada mudança, chame de novo com `?percentil=`. Use *debounce* de uns 300 ms.
  Texto fixo abaixo dele: *"Baixar o corte captura mais casos conhecidos e também mais alarme falso."*
* **Linha de justificativa (obrigatória), montada a partir de `componentes`:**
  `"{cartoes_1t_previos} cartões no 1º tempo em {minutos_previos} minutos jogados · {condicao} · taxa ajustada {taxa_1t_ajustada}"`.
* **Nunca exiba `score_pre_jogo`.** O campo vem para depuração e para quem quiser refazer a
  conta. Exiba `percentil` e `tier`.
* `base_rasa = true` (rodadas 1 a 5): mostre `aviso_base_rasa` como faixa informativa.
* **Perfil `clube`:** a fila já vem filtrada para o elenco do clube. `contexto.clube_slug` traz
  o clube, então use-o no cabeçalho *"Elenco do [clube]"*.
* Ordem: `percentil` decrescente, já feita pelo backend.
* Clique em "ver ficha" → T2 com `atleta_id`.

**Estados:** `422 sem_escalacao` quando a rodada ainda não tem súmula. É o estado normal para
rodada futura, não erro. `dados` vazio quer dizer que ninguém passou do corte: mostre *"Nenhum
atleta acima do corte atual. Reduza o percentil para ampliar a fila."*

Cobertura: Série A 2025–2026 e Série B 2022–2026.

---

### 5.3 `GET /v1/atletas?busca=` — T2, busca

Perfis: `federacao_stjd`, `clube`.

| Query | Obrigatório | Observação |
| :--- | :---: | :--- |
| `busca` | sim | Mínimo 3 caracteres. Não diferencia acento nem caixa. Casa nome completo ou apelido |
| `serie` | não | `A` ou `B` |
| `temporada` | não | ano |

```json
{
  "dados": [
    {
      "atleta_id": "900001",
      "atleta": "Fulano",
      "nome_completo": "Fulano de Tal",
      "clubes": [
        { "clube_slug": "exemplo_fc", "clube": "Exemplo FC" },
        { "clube_slug": "outro_fc", "clube": "Outro FC" }
      ],
      "ultima_temporada": 2026
    }
  ],
  "total": 1
}
```

* No máximo **20 resultados**, sem paginação. Se vierem 20, sugira refinar a busca.
* **Não traz escore nem tier**, por decisão de desenho.
* Desabilite o botão com menos de 3 caracteres. O backend também devolve 400.
* Sem resultado: *"Nenhum atleta encontrado. A busca cobre atletas com súmula eletrônica:
  Série A desde 2025 e Série B desde 2022."* (veja a [§9](#9-diferenças-em-relação-à-especificação-e-limitações-da-poc)).

---

### 5.4 `GET /v1/atletas/{atleta_id}` — T2, ficha

Perfis: `federacao_stjd`, `clube`. O `clube` pode consultar **qualquer** atleta (due diligence).

```json
{
  "atleta_id": "900001",
  "atleta": "Fulano",
  "nome_completo": "Fulano de Tal",
  "clubes": [{ "clube_slug": "exemplo_fc", "clube": "Exemplo FC" }],
  "clube_atual": "exemplo_fc",
  "historico": [
    {
      "temporada": 2026, "serie": "A", "clube_slug": "exemplo_fc",
      "partidas_jogadas": 10, "minutos_em_campo": 900,
      "cartoes_total": 3, "cartoes_1t": 2, "prop_cartoes_1t": 0.667,
      "athlete_anomaly_score": null, "percentil": null, "tier": null
    }
  ],
  "cartoes": [
    {
      "serie": "A", "temporada": 2026, "partida_id": 92, "rodada": 10,
      "clube_slug": "exemplo_fc", "minuto_continuo": 42, "periodo": "1T",
      "cartao": "Amarelo", "tipo_cartao_detalhe": "", "categoria_infracao": "outro",
      "motivo_completo": "A1.3. Cometer uma falta tática ...",
      "motivo_disponivel": true
    }
  ],
  "aviso_interpretativo": "Este escore mede ATIPICIDADE ESTATÍSTICA ..."
}
```

* `historico` vem da temporada mais recente para a mais antiga. `tier`, `percentil` e
  `athlete_anomaly_score` só existem na janela do escore retrospectivo. Fora dela vêm `null`:
  mostre "—" e **não** prometa escore.
* `prop_cartoes_1t` vem `null` quando o atleta não tem cartão na temporada.
* **`motivo_disponivel = false`:** `motivo_completo` já chega com o texto *"motivo não
  registrado na súmula desta temporada"*. Mostre esse texto em estilo secundário, para não
  parecer defeito.
* `partida_id` + `serie` + `temporada` do cartão levam ao dossiê (T3).
* Enquadramento visual **neutro**: sem vermelho, sem ícone de alerta, sem selo (documento 03 §3).
* Toda abertura de ficha e toda busca ficam registradas no backend. É invisível ao usuário:
  não mostre confirmação nem aviso.

---

### 5.5a `GET /v1/partidas` — T3, listagem

Perfis: todos. Navegação até um dossiê. Partida não é dado pessoal, então não há restrição de
camada.

| Query | Obrigatório | Observação |
| :--- | :---: | :--- |
| `serie` | sim | `A` ou `B` |
| `temporada` | não | ano; sem ele, todas as temporadas da série |
| `rodada` | não | |
| `busca` | não | Nome de qualquer um dos dois clubes. Mínimo 3 caracteres, sem acento nem caixa |
| `pagina` | não | Começa em 1 |
| `por_pagina` | não | Padrão 20, máximo 50 |

```json
{
  "dados": [
    {
      "serie": "A", "temporada": 2026, "partida_id": 271, "rodada": 27, "data": "2026-09-14",
      "clube_mandante": "Exemplo FC", "clube_mandante_slug": "exemplo_fc",
      "clube_visitante": "Outro FC", "clube_visitante_slug": "outro_fc",
      "placar": "2-1",
      "tem_procedencia": true
    }
  ],
  "total": 1,
  "paginacao": { "pagina": 1, "por_pagina": 20, "total_itens": 380, "total_paginas": 19 }
}
```

Ordem: mais recente primeiro. Aqui `total` é o tamanho da página; o total da busca está em
`paginacao.total_itens`. Partidas sem clube na fonte (Série B 2022, rodada 0) não aparecem.
A chave de cada partida é o trio `serie` + `temporada` + `partida_id`: use os três na rota
do dossiê.

---

### 5.5 `GET /v1/partidas/{serie}/{temporada}/{partida_id}/dossie` — T3

Perfis: todos. O conteúdo muda com a camada.

```json
{
  "partida": {
    "partida_id": 100, "serie": "A", "temporada": 2026, "rodada": 10,
    "data": "2026-04-05", "horario": "16:00", "arena": "Estádio Exemplo", "cidade": "Cidade",
    "arbitro": "Nome do Árbitro",
    "clube_mandante": "Exemplo FC", "clube_mandante_slug": "exemplo_fc",
    "clube_visitante": "Outro FC", "clube_visitante_slug": "outro_fc",
    "placar": "1-1"
  },
  "match_anomaly_score": null,
  "percentil": null,
  "tier": null,
  "aviso_partida": "Partida fora da janela do escore de anomalia (...)",
  "cartoes": [
    {
      "clube_slug": "outro_fc", "num_camisa": 8, "atleta": "Fulano de Tal", "atleta_id": "900001",
      "cartao": "Amarelo", "minuto_continuo": 45, "periodo": "1T",
      "tipo_cartao_detalhe": "", "categoria_infracao": "falta_temeraria",
      "motivo_completo": "A1.11. ...", "motivo_disponivel": true
    }
  ],
  "atletas_sinalizados": [
    {
      "atleta_id": "900001", "atleta": "Fulano", "num_camisa": 8, "clube_slug": "outro_fc",
      "condicao": "Titular", "percentil": 97.2, "tier": "Alta Concentração Precoce (Top 5%)"
    }
  ],
  "procedencia": {
    "fonte": "Súmula Eletrônica CBF",
    "url": "https://conteudo.cbf.com.br/sumulas/2026/142100se.pdf",
    "sha256": "a3f1…",
    "baixado_em": "2026-09-15T02:14:07-03:00",
    "processado_em": "2026-09-23T21:47:44-03:00"
  },
  "aviso_interpretativo": "..."
}
```

**Diferenças por camada:**

| Campo | Identificada | Aberta |
| :--- | :--- | :--- |
| `cartoes[].atleta`, `atleta_id`, `num_camisa` | preenchidos | `null`, salvo atleta condenado (nominável) |
| `atletas_sinalizados` | lista, com corte no `limiar_padrao` do perfil | `null`: **não renderize a seção** |

Para o perfil `clube`, `atletas_sinalizados` só traz atletas do próprio clube.

* **`procedencia` é o centro da tela.** Mostre em bloco legível e copiável, com botão de copiar
  URL e SHA-256. Hoje só há procedência para **Série A 2025–2026 e Série B 2024–2026**. Nas
  demais partidas, todos os campos vêm `null`: mostre *"procedência documental não disponível
  para esta partida"*.
* `aviso_partida` **sempre** acompanha o escore da partida, estando ele presente ou não.
* "Exportar PDF" = `window.print()` com CSS `@media print`.

---

### 5.6 `GET /v1/agregados/{serie}/{temporada}?por=clube|rodada` — T4

Perfis: todos. Nunca contém atleta.

`por=clube` (padrão), ordenado por `clube_slug`:

```json
{
  "dados": [
    { "clube_slug": "exemplo_fc", "clube": "Exemplo FC", "partidas": 38, "cartoes": 95,
      "cartoes_1t": 29, "prop_cartoes_1t": 0.305, "media_cartoes_por_partida": 2.5 }
  ],
  "total": 20
}
```

`por=rodada`, ordenado por `rodada`: igual, trocando `clube_slug`/`clube` por `rodada`.

Use `clube` (nome legível) na tabela e no gráfico de barras de `prop_cartoes_1t`. A ordenação
da tabela pode ser feita no cliente. Cobertura: Série A 2003–2026 e Série B 2022–2026. Série e
temporada sem partida retornam 404.

---

### 5.7 `GET /v1/atletas/nominaveis`

Perfis: todos. Lista de atletas com condenação transitada em julgado, que podem ser nominados
em qualquer camada. **Não é lista de suspeitos**: não crie tela para ela. Serve só para
consulta interna do front, se precisar.

```json
{ "dados": [ { "atleta_id": null, "atleta": "Nome", "sancao": "Suspenso por 360 dias",
               "fonte": "Autos MP-GO / Julgamento STJD" } ], "total": 10 }
```

`atleta_id` pode vir `null` quando o atleta não aparece nas súmulas eletrônicas da base.

---

### 5.8 `GET /v1/cobertura`

Perfis: todos. O que existe na base, para montar os filtros.

```json
{
  "A": {
    "temporadas": [2026, 2025, 2024, "..."],
    "fila": [{ "temporada": 2026, "ultima_rodada": 27 }, { "temporada": 2025, "ultima_rodada": 38 }]
  },
  "B": { "temporadas": ["..."], "fila": ["..."] }
}
```

* `temporadas`: temporadas com partidas. Servem para T3 (listagem) e T4.
* `fila`: temporadas com escore pré-jogo e a última rodada com escalação publicada. Servem
  para a T1. Um bom padrão é abrir a fila em `fila[0].temporada` / `fila[0].ultima_rodada`.

---

## 6. Regras de exibição obrigatórias

| # | Regra |
| :---: | :--- |
| R1 | `aviso_interpretativo` aparece **na mesma tela** do escore, visível, fora de rodapé, modal ou tooltip. Use o texto da resposta; nunca fixe o texto no código |
| R2 | Nunca exiba `score_pre_jogo`. Exiba `percentil` e `tier` |
| R3 | `tier` vem pronto do backend. **Não recalcule** a partir do percentil: os cortes mudam a cada pipeline |
| R4 | Tier de atleta e tier de partida são vocabulários distintos. Não unifique cores nem legendas |
| R5 | Não use as palavras *suspeito, fraude, manipulação, detecção, probabilidade*. Use *atipicidade, prioridade de escrutínio, triagem, percentil* (documento 02 §5) |
| R6 | Nome de atleta só quando a resposta traz. `null` não é erro nem campo a preencher |
| R7 | Toda lista vazia tem mensagem explicativa |
| R8 | `atleta_id` é opaco |

---

## 7. Erros

Corpo sempre no formato `{"erro": "<codigo>", "detalhe": "<texto opcional>"}`.

| HTTP | `erro` | Quando | O que a tela mostra |
| :---: | :--- | :--- | :--- |
| 400 | `parametro_invalido` | busca curta, série inválida, percentil fora de 0–100, `perfil`/`clube` na query | Busca curta: *"Digite ao menos 3 caracteres para buscar."* Outros casos: bug do front, então logue |
| 401 | `nao_autenticado` | chave ausente, errada ou desativada | Volta para a tela de chave |
| 403 | `sem_permissao` | perfil sem acesso ao endpoint | *"Seu perfil não tem acesso a esta consulta."* Não mostre o `detalhe` |
| 404 | `nao_encontrado` | partida, atleta ou temporada inexistente | *"Não encontrado."* |
| 422 | `sem_escalacao` | rodada sem súmula publicada | *"A escalação desta rodada ainda não foi publicada pela CBF. A fila fica disponível após a publicação da súmula."* Estado **normal**, não erro |
| 500 | `erro_interno` | falha do servidor | Mensagem genérica. A resposta nunca traz stack trace |

---

## 8. Cliente mínimo (TypeScript)

```ts
const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(public status: number, public erro: string, public detalhe?: string) {
    super(detalhe ?? erro);
  }
}

export async function api<T>(path: string, chave: string, query?: Record<string, string | number>) {
  const url = new URL(path, BASE);
  Object.entries(query ?? {}).forEach(([k, v]) => url.searchParams.set(k, String(v)));
  const r = await fetch(url, { headers: { Authorization: `Bearer ${chave}` } });
  const corpo = await r.json();
  if (!r.ok) throw new ApiError(r.status, corpo.erro, corpo.detalhe);
  return corpo as T;
}

// Uso
const me = await api<Me>("/v1/me", chave);
const fila = await api<Fila>(`/v1/rodadas/A/2026/20/fila`, chave, { percentil: 80 });
```

Para gerar os tipos a partir do OpenAPI: `npx openapi-typescript http://localhost:8000/openapi.json -o src/api.d.ts`.
Na POC as respostas não declaram *schema* de saída, então os tipos de resposta precisam ser
escritos à mão a partir dos exemplos deste guia.

---

## 9. Diferenças em relação à especificação e limitações da POC

| # | Ponto | Situação na POC |
| :---: | :--- | :--- |
| D1 | **Semântica do percentil da fila** | O percentil é calculado na distribuição da **série e temporada**. Com isso, p70 põe cerca de 30% da rodada na fila (ex.: 136 de 458), e não os ~3 alertas que o documento 02 §3 estima. Aquela estimativa vem da curva do escore retrospectivo. **Decisão de produto pendente.** Até lá, o slider e o contador `total_sinalizados` deixam o efeito visível |
| D2 | Rodada futura | Retorna 422. Não há proxy "escalação da rodada anterior" (documento 05 §2) |
| D3 | Cobertura da busca e da ficha | Só atletas com súmula eletrônica: **Série A 2025–2026, Série B 2022–2026** (~3.350 atletas). A mensagem de estado vazio do documento 03 ("Série A desde 2003") foi ajustada |
| D4 | Cartões na ficha | Só os vinculados ao atleta pela escalação (camisa + clube + partida). Cerca de 7% dos cartões dessas temporadas não casam com a escalação e ficam fora da ficha, embora apareçam no dossiê e nos agregados |
| D5 | Escore retrospectivo na ficha | A janela (A 2015–2024, B 2022–2023) quase não cruza com a das súmulas. Na prática, só atletas da Série B 2022–2023 têm `tier` no `historico` |
| D6 | `atletas_sinalizados` no dossiê para `clube` | Filtrado para o próprio elenco, coerente com o documento 02 §4.2 (lista proativa só do próprio elenco). O documento 01 §5 dizia "completo" |
| D7 | Campos e endpoints extras | `nome_completo`, `clube` (nome legível em todo objeto com `clube_slug`), `clube_atual`, `motivo_disponivel`, `aviso_partida`, `base_rasa`, `aviso_base_rasa`, `contexto.clube_slug`. Endpoints `GET /v1/partidas` (listagem) e `GET /v1/cobertura` (filtros). **Muda o contrato em um ponto:** `clubes`, na busca e na ficha, passou de lista de slugs para lista de objetos `{clube_slug, clube}` |
| D8 | `processado_em` | Momento da carga no banco da API, não do parsing do PDF |
| D8b | Cobertura da procedência | O manifesto de download só cobre A 2025–2026 e B 2024–2026. A Série B 2022–2023 tem súmula processada, mas sem registro de URL/hash. O manifesto de A 2024 não casa com os `partida_id` da base (origem diferente) |
| D9 | Dados de origem | A Série B 2022 tem algumas partidas com `rodada = 0` e sem data ou clubes (defeito da fonte). Aparecem em agregados por rodada como rodada 0 |
| D10 | Banco | SQLite local (`data/api/`, fora do Git). O schema é portável para PostgreSQL via `ANALISE_BETS_DATABASE_URL` |
| D11 | Segurança | Sem rate limiting, sem expiração de chave e CORS aberto. **Não expor fora de rede local** |

> **LGPD.** A API serve dado pessoal identificado de atletas (nome, registro CBF e inferência
> estatística sobre o perfil disciplinar). A base legal (tarefa F4-01) não foi estabelecida:
> use apenas em ambiente de desenvolvimento, sem dados de produção fora da máquina local.
>
> Caso o seu projeto envolva dados pessoais ou dados pessoais sensíveis, comunique ao time de
> Segurança da Informação através do e-mail seginfo@gcb.com.br
