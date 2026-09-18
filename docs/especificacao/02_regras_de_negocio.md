# 02 — Regras de negócio e limiares

**Destrava:** etapas 4 (backend) e 5 (front-end).
**Escopo:** protótipo / MVP.

---

## 0. A restrição que precede todas as outras

> **O escore mede atipicidade estatística do perfil disciplinar. Não mede fraude, não estima
> probabilidade de manipulação e não constitui indício.**

Um atleta com estilo de falta tática precoce e um atleta aliciado produzem assinaturas
estatísticas semelhantes. O sistema não os distingue e não foi construído para isso.

Isso não é cautela jurídica nem texto de rodapé. É o resultado apurado:

| Afirmação | Situação |
| :--- | :--- |
| Sensibilidade contra o ground truth judicial | **6 de 14 (42,9%)** |
| Capacidade de priorizar no nível da **partida** | **Não se distingue de sorteio** (melhor ponto: p = 0,118) |
| Classificador de ML fora da amostra, nível atleta | **1 de 7** |
| Escore pré-jogo por **atleta** | **Ganho de 2,4× a 3,0×** sobre sorteio, sem vazamento |

**Consequências obrigatórias para o produto:**

1. O campo `aviso_interpretativo` acompanha toda resposta que contenha escore, e o front **tem
   de exibi-lo** na tela onde o escore aparece — não num rodapé, não num modal que se fecha.
2. Nenhum rótulo de tela pode usar as palavras *suspeito*, *fraude*, *manipulação*, *risco de
   fraude* ou equivalente. O vocabulário aprovado está em §5.
3. A unidade onde há sinal é o **atleta**, não a partida. Qualquer tela que ordene partidas por
   escore está oferecendo algo que a validação não sustenta.

---

## 1. Os dois escores

O sistema produz dois escores independentes. Confundi-los é o erro mais provável de quem chegar
agora.

### 1.1 Escore pré-jogo por atleta — `score_pre_jogo`

**O que é:** número esperado de cartões no 1º tempo que o atleta receberá nesta partida,
calculado só com informação anterior ao apito inicial.

**Fórmula:**

```
taxa_1t_ajustada = (cartoes_1t_previos + M0 × taxa_populacional) / (minutos_previos + M0)
score_pre_jogo   = taxa_1t_ajustada × minutos_esperados
```

* `M0 = 500` minutos — força do prior de encolhimento bayesiano. Sem ele, um atleta com um
  cartão em 20 minutos jogados teria a maior taxa da liga.
* `taxa_populacional` é acumulada no tempo, não calculada sobre a base inteira. É o que impede
  vazamento.
* `minutos_esperados`: **82,0** para titular, **13,0** para reserva — médias observadas na
  base, não arredondamentos. Constantes em `score_pre_jogo.MINUTOS_ESPERADOS`.

**Uso:** é o escore da fila de triagem. É o único com ganho preditivo demonstrado.

**Escala:** não é 0–100 nem probabilidade. É uma contagem esperada, tipicamente entre 0 e 0,5.
**O front nunca exibe o valor bruto** — exibe percentil e tier. Ver §3.

### 1.2 Escores de anomalia retrospectivos — `match_anomaly_score`, `athlete_anomaly_score`

**O que são:** desvio do padrão disciplinar observado numa partida ou numa temporada de um
atleta, em escala 0–100. Olham para trás.

**Uso:** contexto histórico na consulta por atleta e no dossiê de partida. **Não** para
ranquear a rodada.

**Restrição:** no nível da partida, não discriminam melhor que sorteio. A tela pode exibi-los
como informação, nunca como recomendação de ação.

---

## 2. Tiers

Percentis empíricos da distribuição, **não** cortes absolutos. Recalculados a cada execução do
pipeline: um escore de 30 pode ser Top 1% numa temporada e Top 5% em outra.

São **dois vocabulários distintos**, um por nível. O front não deve unificá-los: o tier de
atleta fala de *concentração precoce de cartões*, o de partida fala de *prioridade de
escrutínio*, e são coisas diferentes.

**Nível partida** (`anomaly_detection.TIERS_PARTIDA`):

| Corte | Rótulo |
| :---: | :--- |
| ≥ p99 | Extrema Anomalia (Top 1%) |
| ≥ p95 | Alta Prioridade de Escrutínio (Top 5%) |
| ≥ p90 | Média Prioridade (Top 10%) |
| < p90 | Típico / Baixa Prioridade |

**Nível atleta** (`anomaly_detection.TIERS_ATLETA`):

| Corte | Rótulo |
| :---: | :--- |
| ≥ p99 | Extrema Anomalia Temporal (Top 1%) |
| ≥ p95 | Alta Concentração Precoce (Top 5%) |
| ≥ p90 | Média Concentração (Top 10%) |
| < p90 | Padrão Basal Normal |

O backend devolve `tier` (a chave) e `percentil`. **O front não recalcula tier a partir do
escore** — o corte pertence ao backend e muda a cada pipeline.

---

## 3. Limiar de alerta por persona

O limiar é **parâmetro explícito do produto**, não constante escondida. A pergunta que ele
responde não é "qual o corte certo", e sim **"quantos casos você consegue tratar por rodada?"**.

Da tabela `tabela_21d_limiar_por_persona.csv`:

| Perfil | Capacidade assumida | Percentil | Alertas/rodada | Sensibilidade esperada |
| :--- | :---: | :---: | :---: | :---: |
| `federacao_stjd` | 3 por rodada | **70,0** | 3,0 | 5/13 (38,5%) |
| `clube` | 1 por rodada | **90,0** | 1,0 | 2/13 (15,4%) |
| `operadora_integrity` | 10 por rodada | **50,0** | 5,0 | 6/13 (46,2%) |

Esses são os **padrões**, servidos por `GET /v1/me`. O usuário pode alterar o percentil na
requisição, e a tela deve mostrar o efeito — ver [03 — Telas §3](03_telas.md).

> **Premissa não validada.** As capacidades (3, 1, 10) são estimativas plausíveis, nunca
> medidas com usuário real. Quando houver uso, este é o primeiro número a corrigir.

A relação é um trade-off direto, e a tela precisa deixá-lo visível: **baixar o corte captura
mais casos e produz mais alarme falso.** A p50, a sensibilidade sobe para 46% ao custo de
dobrar a fila.

---

## 4. Regras de visibilidade

### 4.1 Nome de atleta

| Situação | Nome? |
| :--- | :--- |
| Camada `identificada` (`federacao_stjd`, `clube`) | Sim |
| Camada `aberta` | Não — não há atleta na resposta |
| Atleta com condenação transitada em julgado | Sim, em qualquer camada |

A lista de nomináveis vem de `GET /v1/atletas/nominaveis`. Hoje são os 10 atletas da Operação
Penalidade Máxima.

**O motivo da regra:** um ranking de atipicidade é composto majoritariamente por atletas que
nunca foram investigados. Nomeá-los num sistema sobre integridade associa pessoa não
investigada a contexto de suspeição — que é exatamente o dano que o produto existe para não
causar.

### 4.2 Escopo do perfil `clube`

O clube vê apenas atletas que estão ou estiveram no seu elenco. Consulta a terceiros:
**403**. A funcionalidade de due diligence pré-contratação **não está no MVP** — ver
[01 §5](01_api_e_autorizacao.md#o-escopo-do-perfil-clube-mvp).

### 4.3 O perfil de trading

`operadora_trading` não é atendido. A verificação é do backend, não da tela.

---

## 5. Vocabulário

O produto é lido por quem decide abrir procedimento contra uma pessoa. A palavra na tela vira
palavra no despacho.

| ❌ Não usar | ✅ Usar |
| :--- | :--- |
| Suspeito, suspeição | Atípico, atipicidade |
| Risco de fraude / manipulação | Prioridade de escrutínio |
| Detecção | Triagem, priorização |
| Probabilidade | Escore, percentil |
| Alerta de manipulação | Alerta de atipicidade |
| Atleta sinalizado como... | Atleta no tier X |

O nome do produto e os títulos de tela seguem a mesma regra.

---

## 6. Casos de borda

| Situação | Comportamento esperado |
| :--- | :--- |
| Rodada sem escalação publicada | **422** com mensagem explicativa. É o estado normal antes da súmula sair, não erro |
| Atleta sem histórico (estreante) | Pontuado só pelo prior populacional. Aparece com `minutos_previos = 0`. **Nunca `null`** |
| Atleta sem `registro_cbf` na origem | Não deve existir — corrigido no parser em 18/09/2026. Se aparecer, é regressão: logar e excluir da fila |
| Primeiras 5 rodadas da temporada | Excluídas da avaliação por falta de histórico. A fila **existe**, mas a tela deve avisar que a base é rasa |
| Cartão sem `motivo_completo` | 86% da Série A não tem o campo na fonte. Exibir "motivo não disponível na súmula", nunca vazio |
| Partida sem súmula | 23 partidas, por PDF incompleto na origem. Listadas em `reports/tables/partidas_sem_escalacao.csv` |

---

## 7. Janela de dados

| Uso | Cobertura |
| :--- | :--- |
| Consulta histórica e agregados | Série A 2003–2025, Série B 2022–2025, 2026 em curso |
| Escore pré-jogo | Série A 2025–2026, Série B 2022–2026 *(exige escalação da súmula)* |
| Escores de anomalia retrospectivos | Série A 2015–2024, Série B 2022–2023 |

A janela dos escores retrospectivos é mais estreita de propósito: estendê-la mudaria todos os
números publicados e é decisão pendente. **A tela não deve prometer escore de anomalia fora
dessa janela.**

> Caso o seu projeto envolva dados pessoais ou dados pessoais sensíveis, comunique ao time de
> Segurança da Informação através do e-mail seginfo@gcb.com.br
