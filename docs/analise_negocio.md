# Análise de Negócio — Transição de Artigo Acadêmico para Produto

**Projeto:** Impacto das Apostas Esportivas no Futebol Brasileiro
**Data:** 16 de setembro de 2026
**Status:** Análise preliminar — **hipóteses ainda não validadas em mercado**
**Backlog derivado:** [`tasks/README.md`](../tasks/README.md)

---

## Nota sobre o status epistêmico deste documento

Este documento é uma **análise**, não uma **validação**. Todas as afirmações sobre cliente,
disposição a pagar, dor percebida e prioridade de compra são **hipóteses derivadas de
raciocínio sobre o mercado e sobre os ativos do projeto** — não houve, até esta data,
nenhuma entrevista com cliente potencial.

A evidência de mercado é produzida pelas tarefas da Fase 5 do backlog
([F5-01](../tasks/backlog/F5-01-entrevistas-com-personas.md),
[F5-02](../tasks/backlog/F5-02-teste-das-hipoteses-criticas.md),
[F5-03](../tasks/backlog/F5-03-dossie-de-evidencia-de-demanda.md)). Este documento deve ser
revisado à luz daquele resultado.

A distinção importa: um trabalho que apresenta hipótese como evidência é frágil sob
arguição. Um que declara o que sabe e o que ainda supõe, não.

**Relação com os demais documentos:**

| Documento | Papel |
| :--- | :--- |
| `docs/analise_negocio.md` (este) | **Análise** — diagnóstico do mercado e dos ativos, hipóteses de cliente e produto |
| `docs/visao_produto.md` (a produzir em [F6-01](../tasks/backlog/F6-01-documento-de-visao-de-produto.md)) | **Decisão** — o que será construído, já com a evidência da Fase 5 |
| `reports/white_paper_*.md` | **Evidência empírica** — fundamentação causal e de integridade |

---

## 1. Sumário executivo

O projeto foi concebido como estudo econométrico sobre o efeito da expansão das casas de
apostas na dinâmica disciplinar do futebol brasileiro. O redirecionamento para produto exige
responder a três perguntas que um artigo não precisa responder: **quem é o cliente, o que ele
quer saber, e em que forma**.

As conclusões centrais desta análise:

1. **O ativo defensável não é o modelo de scoring — é o pipeline de súmulas oficiais.** A
   esteira que converte diariamente PDFs da CBF em base relacional rastreável por hash, com
   minutagem exata e motivo textual do árbitro, é o que nenhum concorrente possui.

2. **A hipótese inicial de que o cliente são as casas de apostas está parcialmente correta e
   é comercialmente frágil.** As operadoras têm o maior orçamento e a menor necessidade deste
   sinal específico, além de um conflito de interesse estrutural com a finalidade declarada do
   projeto (§3).

3. **O ICP primário recomendado são clubes e entidades de integridade** — federações, STJD e
   unidades de compliance. As operadoras entram como segmento secundário, com produto
   deliberadamente restrito em granularidade.

4. **O produto não é "detecção de fraude" — é "priorização de escrutínio".** A diferença não é
   retórica: ela determina qual métrica é reportada, o que é prometido ao cliente e qual é a
   exposição jurídica assumida (§9).
   > **Revisão de 2026-09-16 (F1-04).** Medida a carga de alerta, a premissa não se sustenta no
   > nível da partida: nenhum limiar captura mais casos conhecidos do que sortear a mesma
   > quantidade de partidas (melhor ponto da curva em $p = 0{,}118$). Um priorizador é avaliado por
   > precisão no topo da lista, e o topo da lista não contém os casos conhecidos. O
   > posicionamento vigente é **instrumento de medição de atipicidade disciplinar**, e a unidade
   > de análise com sinal é o atleta. Ver o relatório 07, seções 3.7 e 3.8.

5. **Três lacunas técnicas bloqueiam qualquer venda ou demonstração** e estão endereçadas na
   Fase 1 do backlog: precisão indeterminada, validação in-sample e circularidade metodológica
   no índice (§9).

---

## 2. Inventário de ativos

Levantamento do que existe no repositório em 16/09/2026, classificado por valor de produto.

| Ativo | Estado | Valor de produto |
| :--- | :--- | :---: |
| **Pipeline delta CBF D+1** (`src/ingestion/cbf_delta_updater.py`, `src/pipeline/run_delta_pipeline.py`) | **Operacional na temporada 2026.** Última execução em 16/09/2026: 380 partidas inspecionadas, 216 súmulas novas, detecção incremental por HTTP HEAD, ETag e SHA-256, zero erros | **Muito alto** |
| **Parser de súmulas** (`src/cleaning/parse_cbf_sumulas.py`) | Extrai minutagem exata e **motivo textual digitado pelo árbitro** | **Alto** |
| **Feed de produto** (`src/pipeline/serve_product_feed.py`) | SQLite com índices e WAL, feeds JSON, classificação consolidada | Médio |
| **Anomaly scoring** (partida e atleta) | 4.559 partidas e 3.694 atleta-temporadas pontuados | Médio |
| **Classificador ML** (IsolationForest + PU) | Treinado e serializado, mas **validado dentro da amostra** (§9.2) | Baixo hoje |
| **Econometria TWFE e Event Study** | Concluída, tendências paralelas validadas | Acadêmico |
| **Ground truth judicial** (14 incidentes, Operação Penalidade Máxima) | Estruturado e documentado | Alto valor narrativo, baixo poder estatístico |

**Leitura:** o projeto tem infraestrutura de dados em produção e modelagem madura. O que não
tem é embalagem, cliente e métricas de produto.

---

## 3. Diagnóstico da hipótese inicial: "o cliente são as bets"

A hipótese de partida era vender avaliação de risco de fraude em cartões e faltas para casas
de apostas. Quatro objeções, em ordem de gravidade:

### 3.1 Timing — a objeção decisiva

Mercados de cartões e faltas **liquidam no apito final**. Um escore calculado em D+1 chega
depois do pagamento das apostas. Para uma operadora, detectar manipulação ontem não recupera
prejuízo; serve, no máximo, como defesa regulatória.

O que gera valor para o operador é decisão **antes** do jogo: suspender um micro-mercado,
reduzir limites, não oferecer determinado mercado naquela partida. Detecção ex-post não é o
produto que ele compra.

### 3.2 Sinal inferior ao que a operadora já possui

Sportradar (UFDS), Genius Sports e a IBIA monitoram movimentação de odds e padrões de aposta
em tempo real. Esse é dado **transacional**, que antecede o evento em campo e reflete
intenção. Uma súmula é box-score: registra o que aconteceu, depois que aconteceu.

A pergunta "por que comprar de vocês em vez da Sportradar?" será feita tanto pela banca quanto
por qualquer cliente. A resposta não pode ser "somos melhores" — tem de ser "somos
complementares, e cobrimos o que eles não cobrem" (§8).

### 3.3 Conflito de interesse estrutural

Um escore que indica "este atleta concentra 70% dos seus cartões no 1º tempo" é
simultaneamente:

* **sinal de integridade** — útil para priorizar auditoria; e
* **sinal de trading** — útil para precificar micro-mercados de cartão.

Vendido à mesa de precificação de uma operadora, o produto deixa de proteger o esporte e passa
a fornecer vantagem competitiva nos exatos mercados que o white paper do projeto identifica
como vetor de vulnerabilidade à manipulação.

Esta é a contradição mais séria do projeto. A resposta adotada é restringir granularidade por
finalidade, por instrumento contratual e por controle técnico
([F4-03](../tasks/backlog/F4-03-termo-de-uso-e-licenciamento.md)).

### 3.4 Concentração de compradores

O mercado regulado brasileiro tem poucas dezenas de operadoras relevantes, e as maiores já têm
contrato com os incumbentes globais. Ciclo de venda longo, poucos logos possíveis, alta
dependência de cada conta.

### 3.5 O que permanece válido na hipótese

Operadoras licenciadas têm **obrigação regulatória** de monitorar e reportar apostas
suspeitas. Isso cria orçamento de compliance — e compliance compra **evidência auditável**,
não predição. Nesse recorte específico, o projeto é forte, porque a base vem da fonte oficial
com hash de integridade e carimbo de data.

---

## 4. Definição do produto

> **Camada de inteligência de integridade para o futebol brasileiro, construída sobre a fonte
> oficial (súmulas da CBF), com rastreabilidade auditável ponta a ponta.**

Três camadas, em ordem crescente de valor e de dificuldade de construção:

### Camada 1 — Dados como serviço

Base canônica das Séries A e B: partidas, gols e cartões com **minuto e motivo**, árbitro,
atualização D+1, manifesto de proveniência com SHA-256.

* **Compradores:** mídia esportiva, fantasy, casas de análise, times de modelagem, pesquisa.
* **Característica:** fácil de vender, fácil de copiar. Financia as camadas seguintes.

### Camada 2 — Dossiê de auditoria D+1

Por rodada, a fila priorizada de partidas e atletas fora da distribuição basal, **com a
memória de cálculo aberta**: qual subscore disparou, qual p-valor, qual minuto, qual motivo
textual do árbitro, e o link para a súmula-fonte com hash.

* **Compradores:** CBF e federações, STJD, compliance de clubes, MP, área de integridade de
  operadoras.
* **Característica:** o diferencial aqui não é acurácia — é **explicabilidade e
  admissibilidade**. Um escore de caixa-preta não fundamenta um despacho; um teste binomial
  explícito, com a súmula original anexada, fundamenta.

### Camada 3 — Risco ex-ante de micro-mercado

Antes do apito inicial: perfil de risco dos atletas escalados combinado ao contexto da partida
(rodada, situação na tabela, série).

* **Compradores:** clubes, operadoras (com restrição), entidades de integridade.
* **Característica:** é a camada de maior valor comercial e a única que responde ao problema
  de timing (§3.1). Ainda não construída —
  [F3-01](../tasks/backlog/F3-01-score-pre-jogo-por-atleta.md).
* **Viabilidade:** sustentada por evidência do próprio projeto. O perfil de atipicidade
  individual **persiste entre temporadas e clubes** — Nino Paraíba no percentil 100,0 em 2020
  pelo Bahia e 99,67 em 2022 pelo Ceará. Traço persistente é previsível; evento isolado, não.

---

## 5. Segmentação e definição do ICP

| Segmento | Dor principal | Paga? | Ciclo | Posição |
| :--- | :--- | :---: | :---: | :--- |
| **Clubes (SAF)** — compliance e diretoria de futebol | Proteger o clube; avaliar atleta antes de contratar; se defender de acusação | Sim, orçamento novo e crescente | Médio | **ICP primário** |
| **Federações, CBF, STJD** | Triagem sistemática; hoje o processo é reativo e por denúncia | Sim, com decisão política | Longo | **ICP secundário, alto prestígio** |
| **Operadoras — integridade e compliance** | Cumprir obrigação regulatória; demonstrar diligência à SPA/MF | Sim | Longo | Secundário, produto **restrito** |
| **Operadoras — trading e risco** | Precificar micro-mercado, ajustar limites | Sim, com folga | Longo | **Não atendido** — decisão a formalizar em F4-03 |
| **Empresários e entidades de atletas** | Defender o atleta limpo; contestar suspeição | Pouco | Curto | Nicho defensivo, alto valor de legitimidade |
| **Seguradoras e patrocinadores** | Risco reputacional de contrato | Talvez | Longo | Explorar posteriormente |
| **Jornalismo de dados** | Pauta investigativa | Quase nada | Curto | **Canal de distribuição, não receita** |
| **Regulador (SPA/MF), MP e GAECO** | Instrução de casos | Compra pública | Muito longo | Usuário-farol, não cliente inicial |

**Recomendação:** ICP primário em **clubes e entidades de integridade**. As operadoras entram
como segmento secundário, com produto agregado em nível de partida, sem a granularidade que
serviria como sinal de aposta. Esse desenho resolve o conflito de §3.3 e ainda assim acessa o
orçamento de compliance de §3.5.

---

## 6. Personas

Para cada persona: a pergunta que ela faz, o formato em que quer a resposta, e a métrica pela
qual ela julga o produto.

### P1 — Gerente de compliance de clube (SAF)

* **Pergunta:** *"Algum atleta do meu elenco está com perfil estatístico atípico? E o volante
  que vamos contratar da Série B — tem histórico?"*
* **Formato:** relatório semanal por e-mail, mais consulta pontual por atleta antes de assinar
  contrato. **Documento, não API.**
* **Métrica dele:** nenhuma surpresa pública envolvendo o clube.
* **Observação:** a dor mais concreta não é monitorar o elenco atual — é **não contratar um
  problema**. Tem gatilho claro (janela de transferências) e ciclo de decisão curto.

### P2 — Analista de integridade de federação ou STJD

* **Pergunta:** *"Da rodada inteira, quais três jogos eu mando para revisão de vídeo?"*
* **Formato:** fila priorizada com corte fixo e justificativa aberta. Precisa fundamentar, em
  despacho, por que abriu ou arquivou.
* **Métrica dele:** **volume de alerta.** Três itens por rodada é acionável; quarenta é ruído.
  Esta persona rejeita o sistema atual na configuração vigente (§9.1).

### P3 — Integrity officer de operadora licenciada

* **Pergunta:** *"Se a SPA me perguntar, consigo provar que monitorei esta partida?"*
* **Formato:** registro auditável, datado, com fonte oficial e hash, exportável e arquivável.
* **Métrica dele:** completude do registro.
* **Observação:** **compra papel, não predição.** É o caso de uso com melhor relação entre
  valor entregue e esforço de construção, porque reaproveita integralmente o que a Camada 2 já
  produz.

### P4 — Head de trading de operadora

* **Pergunta:** *"Devo suspender o mercado de cartão do lateral-direito deste jogo?"*
* **Formato:** API pré-jogo, latência baixa, cobertura total.
* **Métrica dele:** margem.
* **Observação:** **é quem mais pagaria, e é quem o projeto decidiu não atender** sem
  restrição de granularidade. Ver §3.3 e F4-03.

### P5 — Repórter de dados esportivos

* **Pergunta:** *"Me dá o número."*
* **Formato:** base agregada aberta.
* **Observação:** não paga, mas gera a credibilidade pública que sustenta a venda a P1 e P2.

---

## 7. Modelo de receita

| Produto | Cliente | Modelo | Ordem de grandeza |
| :--- | :--- | :--- | :--- |
| API de dados canônicos | Mídia, fantasy, modeladores | SaaS por volume | Ticket baixo, volume alto |
| Dossiê de rodada | Federação, STJD | Assinatura anual institucional | Ticket médio, recorrente |
| Monitoramento de elenco e due diligence | Clube SAF | Assinatura mais consulta avulsa por atleta | Ticket médio, alta retenção |
| Relatório de conformidade | Integridade de operadora | Assinatura mais laudo sob demanda | Ticket alto por conta |
| Laudo técnico pericial | MP, advocacia desportiva | Projeto | Ticket alto, receita irregular |

**Estrutura de custo:** o custo marginal por cliente adicional é próximo de zero — a fonte é
pública e o processamento é automatizado. A margem estrutural é alta; o gargalo é aquisição de
cliente, não entrega.

---

## 8. Vantagens competitivas

1. **Proveniência oficial e auditável.** Súmula da CBF, SHA-256, ETag, manifesto por arquivo.
   Para uso jurídico-desportivo, proveniência vale mais que cobertura. Provedores comerciais de
   dados esportivos não oferecem essa cadeia de custódia.

2. **Motivo textual do árbitro estruturado.** Na Série B 2022–2023, **28,9% dos 3.671 cartões
   decorrem de infrações comportamentais não-físicas** — reclamação 15,8%, cera 8,4%, conduta
   antidesportiva 4,8%, toque de mão 0,9%. Esta é justamente a categoria mais fácil de
   encomendar, porque **não depende de disputa de bola**: um cartão por falta temerária exige
   que o lance aconteça; um por reclamação, não. Nenhum provedor comercial disponibiliza esse
   campo estruturado.

3. **Persistência do traço individual.** Caso Nino Paraíba (§4, Camada 3) — base empírica para
   o produto ex-ante.

4. **Cobertura da Série B.** A Operação Penalidade Máxima começou na Série B. É onde o risco é
   maior e a atenção comercial é menor; os provedores globais cobrem mal divisões de acesso.

5. **Explicabilidade.** Fórmula fechada com teste binomial explícito, não caixa-preta. Instrui
   procedimento disciplinar — e é vantagem de produto, não limitação técnica.

6. **Custo marginal quase nulo.** Fonte pública, processamento automatizado.

---

## 9. Desvantagens, riscos e restrições

### 9.1 Precisão indeterminada e carga de alerta

Todo o sistema é avaliado por **sensibilidade** — quantos casos reais foram capturados.
Não existe métrica de **precisão** nem de carga operacional.

O tier de alto risco marca **8,93% das partidas**. Sobre 4.559 jogos, isso equivale a cerca de
**400 partidas sinalizadas para 14 incidentes conhecidos** — precisão aparente inferior a 4%,
e mesmo esse número é indeterminado, porque não se sabe quantos dos demais sinalizados são
casos reais nunca investigados.

Para a persona P2, isso significa centenas de revisões de vídeo por safra. **Precisão do
alerta é a métrica do cliente; sensibilidade é a métrica do paper.**

**Consequência adotada:** reposicionar o produto de "detector de fraude" para **"priorizador
de fila de auditoria"**, avaliado por precisão@k no topo da lista e não por precisão global.
Tecnicamente mais honesto e comercialmente mais forte.
→ [F1-04](../tasks/backlog/F1-04-precisao-e-volume-de-alerta.md)

> **Resultado da F1-04 (2026-09-16).** A medição refutou a hipótese de reposicionamento. No nível
> da partida a captura não se distingue de sorteio em nenhum limiar; nos tiers Top 1% e Top 5% é
> zero. No nível do atleta há sinal ($p = 0{,}019$), mas só ao sinalizar 40% da base. O produto
> passa a ser descrito como **instrumento de medição de atipicidade disciplinar** — o que ele
> comprovadamente faz — e o roteiro de produto muda: a escalação por partida (F2-04) e o escore
> pré-jogo por atleta (F3-01) deixam de ser incrementos e viram pré-requisitos.

### 9.2 Validação dentro da amostra

Em `src/models/integrity_classifier.py`, as funções de treino (linhas 105 e 174) recebem o
ground truth da Operação Penalidade Máxima para construir os rótulos, e a avaliação (linha
240) roda sobre os mesmos casos. **A sensibilidade de 100% é medida sobre os dados de
treino.**

Com 14 positivos, qualquer classificador atinge 100% in-sample — o número não carrega
informação. A afirmação aparece hoje no relatório 07, em `docs/arquivo/decisoes_e_progresso.md`, na
proposta de projeto e no white paper.

Ressalva importante: os escores estatísticos fechados (`MATCH_ANOMALY_SCORE` e
`ATHLETE_ANOMALY_SCORE`) **não** são treinados no ground truth — são fórmulas calibradas em
distribuição basal e não sofrem deste problema. A distinção precisa ficar explícita.
→ [F1-03](../tasks/backlog/F1-03-validacao-out-of-sample.md)

### 9.3 Circularidade metodológica no índice

O `MATCH_ANOMALY_SCORE` embute um subscore de exposição comercial a casas de apostas
(`src/models/anomaly_detection.py:144,154`). Dois problemas:

* **Circularidade.** O projeto usa a econometria para *estimar* a associação entre exposição a
  bets e cartões. Usar a mesma exposição como *feature* de suspeição confirma a hipótese por
  construção.
* **Indefensabilidade comercial.** Um clube recebe escore de suspeição mais alto por causa do
  patrocinador na camisa, independentemente do que ocorreu em campo. Nenhum clube compra um
  produto que o penaliza por uma decisão comercial lícita.

→ [F1-02](../tasks/backlog/F1-02-remover-score-bet-do-indice.md)

### 9.4 Confundidores esportivos legítimos

O relatório 07 já os reconhece: arbitragem rigorosa no início para controlar os ânimos, falta
tática precoce para conter contra-ataque, clássicos de alta rivalidade, estilo de marcação sob
pressão. **Cada um é um falso positivo com nome e sobrenome.**

### 9.5 Dependência de fonte única

Todo o produto depende do portal da CBF. Mudança de layout do PDF, alteração de padrão de URL
ou restrição de acesso interrompem a operação. Risco a declarar explicitamente.

### 9.6 Riscos jurídicos e de LGPD

O produto trata dado pessoal de pessoas identificadas e produz sobre elas inferência com
potencial de dano reputacional relevante. Ainda que o escore de atipicidade não seja dado
sensível na definição do art. 5º, II da LGPD, o **efeito prático** de uma sinalização sobre a
carreira de um atleta exige o mesmo nível de cuidado.

Pontos críticos:

* **Base legal** a definir e justificar, com teste de proporcionalidade documentado.
* **Art. 20 da LGPD** — direito de revisão de decisão automatizada. Exige canal e procedimento
  reais, não menção formal.
* **Risco concreto e já materializado.** A Tabela 16 e o relatório 07 exibem ranking nominal de
  atletas atípicos que inclui pessoas **nunca investigadas**. Publicar ou comercializar essa
  lista é exposição direta a ação por dano moral.
* **Três status jurídicos distintos** exigem tratamento distinto: condenado com trânsito em
  julgado (fato público, pode ser nominado), investigado sem condenação (ambiente restrito) e
  apenas estatisticamente atípico (nunca nominado em camada aberta) — este último é o grupo
  mais numeroso e mais exposto.

Normas aplicáveis a conferir na redação vigente antes de citar: Lei 13.709/2018 (LGPD), Lei
13.756/2018, Lei 14.790/2023 e Lei 14.597/2023.
→ [F4-01](../tasks/backlog/F4-01-ripd-e-base-legal-lgpd.md),
[F4-02](../tasks/backlog/F4-02-anonimizacao-por-camada.md)

### 9.7 Riscos comerciais

* Incumbentes com dado transacional superior e relacionamento estabelecido.
* Poucos compradores, ciclo longo, decisão política em federações.
* Clubes brasileiros fora do grupo de maior receita são compradores lentos e de baixo ticket.

### 9.8 Lacunas de dados identificadas

Três falhas encontradas na auditoria do repositório, todas endereçadas na Fase 2:

* O motivo do cartão extraído das súmulas oficiais da Série A **está sendo descartado** na
  gravação, porque o schema herdado da base histórica não possui a coluna. Afeta os 1.370
  cartões da Série A 2026. → [F2-01](../tasks/backlog/F2-01-schema-serie-a-motivo-cartao.md)
* **A temporada 2025 está inteiramente ausente** nas duas séries. →
  [F2-02](../tasks/backlog/F2-02-ingerir-temporada-2025.md)
* A Série B 2024 foi ingerida com **27 cartões**, contra cerca de 1.900 esperados — e a falha
  não disparou nenhum alerta. → [F2-03](../tasks/backlog/F2-03-corrigir-serie-b-2024.md)

Para um produto vendido sobre a promessa de base auditável, uma ingestão parcial silenciosa é
falha mais grave que o dado ausente em si.

---

## 10. Concorrência e posicionamento

| Concorrente | Força | Onde o projeto não compete | Onde o projeto compete |
| :--- | :--- | :--- | :--- |
| **Sportradar (UFDS)** | Monitoramento global de odds em tempo real | Detecção em tempo real; cobertura internacional | Fonte oficial, explicabilidade, motivo do árbitro, Série B |
| **Genius Sports** | Dado oficial de ligas, integração com operadoras | Relacionamento com operadoras; dado in-play | Proveniência auditável, custo, nicho nacional |
| **IBIA** | Rede de alerta entre operadoras | Acesso a dado transacional de apostas | Base pública verificável, uso por clubes e federações |
| **Sofascore, Opta** | Cobertura ampla e granular de eventos | Volume e amplitude de dados esportivos | Motivo textual do árbitro, cadeia de custódia |

**Posicionamento recomendado:** complementar, não substituto. Os incumbentes operam sobre
**sinal de mercado**; o projeto opera sobre **registro oficial**. Um alerta de movimentação
atípica de odds e uma anomalia disciplinar documentada em súmula são evidências de naturezas
diferentes, e a segunda é a que instrui procedimento disciplinar.

---

## 11. Conclusões e encaminhamentos

1. **O produto é a camada de inteligência de integridade sobre fonte oficial**, entregue em
   três camadas: dado canônico, fila priorizada explicável e risco pré-jogo.

2. **O cliente primário são clubes e entidades de integridade**, não casas de apostas. As
   operadoras são segmento secundário, com produto restrito.

3. **O cliente não quer saber "houve fraude?"** — pergunta que o sistema não pode responder e
   que o projeto não deve prometer. Ele quer saber **"onde eu olho primeiro?"**.

4. **A forma de entrega é documento e fila curta com justificativa**, não notebook nem tabela
   bruta. Apenas a persona de trading quer API — e é a que o projeto decidiu restringir.

5. **Nada disso é demonstrável antes da Fase 1 do backlog.** Precisão indeterminada, validação
   in-sample e circularidade no índice são bloqueadores de credibilidade, não pendências de
   polimento.

6. **Nada disso é afirmável como evidência antes da Fase 5.** Até lá, este documento registra
   hipóteses fundamentadas — e deve ser lido como tal.

---

## Referências internas

* Backlog completo e caminho crítico: [`tasks/README.md`](../tasks/README.md)
* Sistema de triagem e validação: [`reports/analysis/07_sistema_triagem_anomalias_integridade.md`](../reports/analysis/07_sistema_triagem_anomalias_integridade.md)
* Tipologia de infrações da Série B: [`reports/analysis/05_comparacao_series_a_b_e_penalidade_maxima.md`](../reports/analysis/05_comparacao_series_a_b_e_penalidade_maxima.md)
* Evidência causal: [`reports/analysis/06_modelagem_econometrica_painel_did.md`](../reports/analysis/06_modelagem_econometrica_painel_did.md)
* Síntese acadêmica: [`reports/white_paper_impacto_bets_futebol_brasileiro.md`](../reports/white_paper_impacto_bets_futebol_brasileiro.md)
* Proposta original do projeto: [`docs/arquivo/proposta_projeto.md`](arquivo/proposta_projeto.md)
