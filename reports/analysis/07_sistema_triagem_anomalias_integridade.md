# Relatório Técnico 07 — Sistema de Triagem e Anomaly Scoring de Integridade Esportiva

**Projeto:** Impacto das Apostas Esportivas no Futebol Brasileiro  
**Fase:** Fase 8 — Sistema de Triagem, Anomaly Scoring e Validação Ground-Truth  
**Data:** 2026-09-10 · **Revisado em:** 2026-09-16 (tarefas F1-01 e F1-02)  
**Autor:** Agente Antigravity (Advanced Agentic Coding)  
**Status:** Fase 1 concluída (F1-01 a F1-04): fórmula reconciliada, ground truth reancorado,
validação fora da amostra e carga operacional medidas.  

---

## 1. Resumo Executivo

Este relatório documenta a concepção, calibração matemática e validação empírica do **Sistema de Triagem e Detecção de Anomalias Disciplinares de Integridade Esportiva**. O sistema foi projetado para atuar como uma camada de conformidade (*compliance* e *integrity screening*) capaz de auditar grandes volumes de dados de súmulas eletrônicas oficiais da CBF e sinalizar partidas e atletas que apresentem desvios disciplinares estatisticamente improváveis sob o padrão basal do futebol brasileiro.

A modelagem harmonizou **4.559 partidas** (Série A 2015–2024 e Série B 2022–2023) e avaliou **3.694 registros de atleta-temporada** (atletas com $\ge 3$ advertências na temporada). A sensibilidade do algoritmo é aferida contra o **Ground Truth da Operação Penalidade Máxima** (Ministério Público de Goiás / STJD, 2022), composto por 14 incidentes com condenações criminais ou desportivas transitadas em julgado. Esta aferição é **in-sample** no caso do classificador de ML e está sujeita às ressalvas da seção 3.4.

### Principais Conclusões e Achados de Integridade:
1. **Sensibilidade de 42,9% dos escores estatísticos.** Com a fórmula reconciliada, a base
   corrigida e as identidades do ground truth resolvidas, os escores sinalizam **6 dos 14
   incidentes** em faixa prioritária. Dois dos oito não sinalizados são fraudes que não se
   consumaram em campo (seção 3.5).
2. **A sensibilidade de 100% do classificador de ML era memorização.** Sob leave-one-out, a
   captura no tier de Alto Risco cai de 7/7 para **1/7** no nível do atleta e de 12/14 para
   6/14 no nível da partida. Treinado na Série B e avaliado na Série A, o modelo captura 1 de
   9 partidas (seção 3.6).
3. **O casamento do ground truth associava atletas errados.** O percentil de 99,67% publicado
   como sendo de Nino Paraíba (Ceará) pertence a Nino (Fluminense); o registro real de Nino
   Paraíba está em 34,50%. Oito das dez identidades estavam incorretas (seção 3.3).
4. **Os eventos individuais do ground truth não reconciliam com as súmulas.** De 14 casos,
   apenas 1 tem o evento confirmado na base (seção 3.4).
5. **Não há ganho demonstrável sobre a seleção aleatória.** No nível da partida, nenhum limiar
   captura mais casos do que sortear a mesma quantidade de partidas ao acaso — o melhor ponto
   da curva fica em $p = 0{,}118$; nos tiers de Extrema Anomalia e Alta Prioridade a captura é
   zero. No nível do atleta há sinal ($p = 0{,}019$), mas só ao custo de sinalizar 40% da base
   (seção 3.7).
6. **O desencontro é de unidade de análise.** O índice de partida mede distorção coletiva; os
   incidentes são atos individuais. É o mesmo achado da econometria do projeto, que encontrou
   efeito nulo da exposição sobre a proporção coletiva de cartões no 1º tempo. O caminho com
   evidência é o nível do atleta, que depende da escalação por partida (F2-04) e do escore
   pré-jogo (F3-01).
7. **O índice deixou de embutir exposição comercial a apostas.** O subscore $S_{\text{bet}}$
   foi removido por circularidade metodológica e por indefensabilidade operacional; a variável
   permanece como contexto de estratificação (seção 2.1).
8. **A carga de alerta passou a ser um parâmetro, não um acidente.** Com tiers por percentil
   empírico, o sistema sinaliza 455 partidas (9,98% da base) contra 10 (0,22%) da
   configuração anterior. A calibração do corte por persona é objeto da tarefa F1-04.
9. **Casos de fraude frustrada.** Nos incidentes em que a manipulação foi combinada mas não se
   consumou em campo (Romário, que não foi escalado; Bauermann, que não executou o combinado
   contra o Avaí), o índice de partida permanece basal — o sistema não gera sinal quando o
   evento acordado não ocorre nos 90 minutos.
10. **Governança ética e presunção de inocência.** Conforme as diretrizes institucionais do
   projeto (`.agent.md`), escores elevados refletem **anomalias estatísticas sob escrutínio
   probabilístico**, e **nunca prova de fraude**. A denominação de manipulação é restrita a
   casos judicializados com condenação transitada em julgado.

---

## 2. Fundamentação Teórica e Algoritmos Matemáticos

O algoritmo de triagem foi desenvolvido em duas dimensões complementares: o **Score Composto de Partida (`MATCH_ANOMALY_SCORE`)** e o **Score Composto de Atleta (`ATHLETE_ANOMALY_SCORE`)**.

```
                           +------------------------------------+
                           | Súmulas Oficiais CBF (4.559 Jogos) |
                           +------------------------------------+
                                      |              |
                   +------------------+              +------------------+
                   v                                                    v
      +-------------------------+                          +-------------------------+
      | Nível Partida           |                          | Nível Atleta-Temporada  |
      | - Distribuição Temporal |                          | - Teste Binomial P-Val  |
      | - Cartões Precoces      |                          | - Proporção 1º Tempo    |
      | - Volume & Z-Score      |                          | - Minuto de Jogo Corrido|
      | - Pênaltis no 1º Tempo  |                          +-------------------------+
      +-------------------------+                                       |
                   |                                                   v
                   |                                       +-------------------------+
                   v                                       | ATHLETE_ANOMALY_SCORE   |
      +-------------------------+                          | [0.0, 100.0]            |
      | MATCH_ANOMALY_SCORE     |                          +-------------------------+
      | [0.0, 100.0]            |                                       |
      +-------------------------+                                       v
                   \                                                   /
                    \                                                 /
                     v                                               v
              +-------------------------------------------------------------+
              | Matriz de Triagem e Alertas (Percentis Empíricos)           |
              | - Extrema Anomalia            (Top 1%  / Percentil >= 99) |
              | - Alta Prioridade de Escrutínio (Top 5%  / Percentil >= 95) |
              | - Média Prioridade            (Top 10% / Percentil >= 90) |
              | - Típico / Baixa Prioridade   (< Percentil 90)              |
              +-------------------------------------------------------------+
                                             |
                                             v
              +-------------------------------------------------------------+
              | Validação Empírica: 14 Casos Operação Penalidade Máxima     |
              | Sensibilidade dos escores estatísticos = 6/14 (42,9%)       |
              | Classificador de ML fora da amostra: ver secoes 3.5 e 3.6   |
              +-------------------------------------------------------------+
```

### 2.1 Anomaly Scoring de Partidas (`MATCH_ANOMALY_SCORE`)

O score da partida é a média ponderada de quatro subíndices de campo normalizados em $[0, 100]$:

$$\text{MATCH\_ANOMALY\_SCORE} = 0{,}39 \cdot S_{\text{tempo}} + 0{,}28 \cdot S_{\text{precoce}} + 0{,}22 \cdot S_{\text{volume}} + 0{,}11 \cdot S_{\text{penalti}}$$

Os coeficientes, as probabilidades basais e os limiares estão declarados como constantes no
topo de `src/models/anomaly_detection.py` e são fixados pelo teste
`tests/test_anomaly_detection.py::test_pesos_publicados_nao_mudam_sem_atualizar_o_teste`:
alterar a fórmula sem atualizar este relatório quebra a suíte.

#### 1. Subscore de Concentração no 1º Tempo ($S_{\text{tempo}}$)
A distribuição basal de cartões no futebol brasileiro é assimétrica: **35,1%** das advertências
ocorrem no 1º tempo ($p_0 = 0{,}351$, estimado sobre os 23.369 cartões da própria base
harmonizada). Partidas com concentração precoce violam essa dinâmica:
$$P(X \ge k \mid n, p_0 = 0{,}353) = \sum_{j=k}^{n} \binom{n}{j} p_0^j (1 - p_0)^{n-j}$$
$$S_{\text{tempo}} = \text{clip}\left(-25 \cdot \log_{10}(p_{\text{tempo}}), 0, 100\right)$$
Um p-valor de $0{,}01$ corresponde a 50 pontos; $10^{-4}$ ou menos, a 100 pontos.

#### 2. Subscore de Cartões Precoces até os 30 minutos ($S_{\text{precoce}}$)
A probabilidade basal de um cartão ser aplicado até o minuto 30 **de jogo corrido** é de
**15,6%** ($p_0 = 0{,}156$), também estimada na base:
$$S_{\text{precoce}} = \text{clip}\left(-25 \cdot \log_{10}(p_{\text{precoce}}), 0, 100\right)$$

#### 3. Subscore de Volume Extremo de Cartões ($S_{\text{volume}}$)
Desvio padronizado do volume de cartões **dentro de cada temporada e divisão**:
$$Z_{\text{cartoes}} = \frac{\text{Cartões} - \mu_{\text{temporada, série}}}{\sigma_{\text{temporada, série}}}$$
$$S_{\text{volume}} = \text{clip}\left(25{,}0 \cdot Z_{\text{cartoes}}, 0{,}0, 100{,}0\right)$$
Uma partida de volume médio ($Z = 0$) recebe **0 ponto**: o subscore mede excesso, não nível.

#### 4. Subscore de Pênaltis no 1º Tempo ($S_{\text{penalti}}$)
$$S_{\text{penalti}} = \begin{cases} 80{,}0, & \text{se } \ge 2 \text{ pênaltis no 1ºT} \\ 40{,}0, & \text{se } 1 \text{ pênalti no 1ºT} \\ 0{,}0, & \text{caso contrário} \end{cases}$$

#### Por que não há subscore de exposição comercial ($S_{\text{bet}}$)

Até a revisão de setembro de 2026 o índice embutia um quinto componente proporcional à
exposição das equipes a patrocinadores de apostas. Ele foi **removido** (tarefa F1-02) por
duas razões independentes:

1. **Circularidade metodológica.** O projeto usa a econometria de painel (TWFE / Event Study)
   para *estimar* a associação entre exposição a bets e comportamento disciplinar. Usar a
   mesma exposição como componente do índice de suspeição faz o instrumento confirmar a
   hipótese por construção — o achado deixa de ser empírico e passa a ser aritmético.
2. **Indefensabilidade operacional.** Com o componente ativo, um clube recebia escore de
   suspeição mais alto por causa do patrocinador estampado na camisa, independentemente do
   que ocorreu em campo. Nenhuma federação instaura procedimento sobre essa base, e nenhum
   clube contrata um sistema que o penaliza por uma decisão comercial lícita.

A variável `exposure_total_partida` **permanece na base** como coluna de contexto e de
estratificação analítica — ela apenas não compõe nenhum escore. O mesmo vale para o espaço de
features do classificador de ML (`src/models/integrity_classifier.py`), de onde também foi
retirada. O peso de 0,10 que ela ocupava foi redistribuído proporcionalmente entre os quatro
subscores de campo, preservando a razão entre eles.

#### Tiers de triagem por percentil empírico

A prioridade de escrutínio deixou de usar limiares absolutos de escore (80 / 65 / 50) e passa
a ser definida pelo **percentil empírico da própria distribuição**:

| Tier | Corte | Partidas sinalizadas | % da base |
| :--- | :---: | :---: | :---: |
| Extrema Anomalia (Top 1%) | Percentil $\ge$ 99 | 45 | 0,99% |
| Alta Prioridade de Escrutínio (Top 5%) | Percentil $\ge$ 95 | 184 | 4,04% |
| Média Prioridade (Top 10%) | Percentil $\ge$ 90 | 226 | 4,96% |
| Típico / Baixa Prioridade | — | 4.104 | 90,02% |

A motivação é operacional: com limiares absolutos, a fórmula anterior classificava **10 de
4.559 partidas** (0,22%) fora do tier basal, e nenhuma das 14 partidas do ground truth estava
entre elas. A carga de alerta era uma consequência acidental da escala do escore. Com corte
por percentil, ela passa a ser um **parâmetro explícito**, que a tarefa F1-04 calibrará por
persona.

### 2.2 Anomaly Scoring Individual de Atletas (`ATHLETE_ANOMALY_SCORE`)

Para cada atleta com pelo menos 3 cartões na temporada, calcula-se o score individual ponderado:

$$\text{ATHLETE\_ANOMALY\_SCORE} = 0{,}50 \cdot S_{\text{atleta\_tempo}} + 0{,}30 \cdot S_{\text{atleta\_taxa}} + 0{,}20 \cdot S_{\text{atleta\_minuto}}$$

Onde:
1. **$S_{\text{atleta\_tempo}}$:** Teste binomial da probabilidade de o atleta acumular $k$ cartões no 1º tempo dentre $n$ cartões totais, sob $p_0 = 0{,}353$:
   $$S_{\text{atleta\_tempo}} = \text{clip}\left(-25 \cdot \log_{10}(p_{\text{binom}}), 0, 100\right)$$
2. **$S_{\text{atleta\_taxa}}$:** Proporção percentual direta de advertências recebidas no 1º tempo ($k / n \times 100$);
3. **$S_{\text{atleta\_minuto}}$:** Penalização pela minutagem média em que o atleta recebe advertências:
   $$S_{\text{atleta\_minuto}} = \text{clip}\left((90{,}0 - \overline{\text{Minuto}}) \cdot 1{,}5, 0{,}0, 100{,}0\right)$$

O minuto usado aqui é o **minuto de jogo corrido** (`minuto_partida`), harmonizado entre as
duas divisões — ver a seção 3.1. A classificação do atleta segue os mesmos cortes percentílicos
da partida (Top 1% / Top 5% / Top 10%), aplicados sobre a distribuição dos 3.694 registros de
atleta-temporada.

---

## 3. Reconciliação, Ancoragem, Validação e Carga Operacional (F1-01 a F1-04, F2-03)

Esta seção registra o que mudou na revisão de setembro de 2026 e por quê. Todos os artefatos
citados adiante foram regenerados a partir do código corrigido.

### 3.1 Defeitos de base corrigidos

Quatro defeitos foram identificados e corrigidos. Nenhum deles é problema de fórmula: todos
corrompiam as **entradas** do índice.

| Defeito | Diagnóstico | Efeito antes da correção |
| :--- | :--- | :--- |
| Chave de junção incompleta | A `partida_id` da Série B reinicia em 1 a cada temporada (1–380 em 2022 e de novo em 2023). A junção usava apenas `(serie, partida_id)`. | Cada partida da Série B recebia a soma dos cartões das duas temporadas. O volume médio da divisão aparecia como 9,7 cartões por jogo contra 5,0 da Série A. |
| Semântica de minuto divergente | A Série A registra o minuto em escala de jogo (0–90); as súmulas da CBF (Série B) registram o minuto **dentro do tempo**, de modo que um cartão aos 20' do 2º tempo era lido como minuto 20. | 47,8% dos cartões da Série B contavam como "até os 30 minutos", contra 15,4% da Série A — um artefato de escala, não um padrão de campo. A minutagem média dos atletas da Série B era subestimada em 15 a 25 minutos. |
| Janela temporal implícita | O filtro da Série A era `temporada >= 2015`, sem teto, enquanto a base de partidas ia até 2024. | A sincronização da temporada 2026 (commit `9b19acb`) injetou 204 registros de atleta-temporada de 2026 na distribuição de referência, sem que nada no código sinalizasse a mudança. |

| Perda da seção de cartões amarelos | O parser em lote (`parse_cbf_sumulas.py`) localizava as seções da súmula sem guarda de primeira ocorrência. O token `2º Cartão Amarelo` — subtipo de expulsão, que aparece **dentro** da seção de vermelhos — sobrescrevia o índice da seção de amarelos com uma posição posterior à dos vermelhos, e o recorte `tokens[idx_amarelo:idx_vermelho]` virava vazio. | Toda partida com uma expulsão por segundo amarelo perdia **todos** os seus cartões amarelos. A Série B 2022–2023 estava sem **519 cartões** (14% do total da divisão no período), em 35 partidas de 2022 e um número equivalente em 2023. Corrigido na tarefa F2-03. |

A correção consiste em usar `(serie, temporada, partida_id)` como chave, adotar o
`minuto_continuo` como minuto de jogo nas duas séries e declarar a janela temporal em
constantes (`SERIE_A_TEMPORADA_MIN`, `SERIE_A_TEMPORADA_MAX`, `SERIE_B_TEMPORADAS`). Os três
casos estão cobertos por testes de regressão em `tests/test_anomaly_detection.py`. A perda da
seção de amarelos foi corrigida no parser e coberta em `tests/test_cbf_delta.py`; as súmulas da
Série B 2022–2023 foram reprocessadas, e as probabilidades basais do índice reestimadas sobre a
base completa ($p_0 = 0{,}351$ para o 1º tempo, contra $0{,}353$ antes).

### 3.2 Efeito da reconciliação sobre o ranking

Os artefatos de comparação estão em `reports/tables/comparacao_f1_reconciliacao_*.csv` e são
reproduzíveis por `python -m src.analysis.comparacao_reconciliacao_score`.

| Métrica | Especificação anterior | Especificação vigente |
| :--- | :---: | :---: |
| Partidas na base | 4.559 | 4.559 |
| Escore médio | 18,39 | 7,21 |
| Escore máximo | 68,07 | 56,55 |
| Partidas fora do tier basal | 10 (0,22%) | 455 (9,98%) |
| Correlação de Spearman entre os dois rankings | — | 0,846 |
| Partidas que mudam de tier | — | 455 |

A correlação de 0,846 indica que a ordenação relativa se preserva em boa medida: o que muda
substancialmente é a **escala** e, com ela, o corte operacional.

### 3.3 Ancoragem do ground truth: resolvedor de identidade (F1-03)

O cruzamento entre os 14 casos e a base era feito por correspondência parcial de nome
(`str.contains` do primeiro token do slug) seguida do primeiro registro encontrado, sem filtro
de série ou de clube. O procedimento associava atletas errados na maioria dos casos.

Ele foi substituído por um **mapa de identidade explícito** em
`src/models/ground_truth_resolver.py`, em que cada associação carrega a evidência que a
sustenta e o seu grau de confiança, e em que casos sem correspondente defensável ficam
declaradamente **não resolvidos** — e não recebem o escore de um homônimo parcial.

**Erros corrigidos:**

| Atleta do ground truth | Associação anterior (errada) | Associação correta | Percentil publicado → real |
| :--- | :--- | :--- | :---: |
| Nino Paraíba (Ceará) | Nino (Fluminense) | `nino_paraiba` (Ceará) | 99,67% → **34,50%** |
| Paulo Miranda (Juventude) | atl_3146e8f6133cd258 (Tombense, Série B) | `paulo_miranda` (Juventude) | 95,29% → 90,04% |
| Moraes Jr (Juventude) | Anderson W. de Moraes Rodrigues (Sampaio Corrêa, Série B) | `onitlasi_junior_de_moraes_rodrigues` | 93,29% → 75,24% |
| Eduardo Bauermann (Santos) | atl_6bd8b2e068a1299f (Vila Nova, Série B) | `eduardo` (Santos) | 90,46% → 74,05% |
| Gabriel Tota (Juventude) | atl_e284276c1c8ed74d (Atlético-GO) | `gabriel_tota` — **abaixo do mínimo de 3 cartões** | 98,16% → sem escore |
| Igor Cariús (Cuiabá) | Igor Marques Paciência Cardoso (Ponte Preta, Série B) | **não resolvido** | 92,37% → sem escore |
| Ygor Catatau (Sampaio Corrêa) | atl_1131b959776a0cc1 (Criciúma) | `ygor_de_oliveira_ferreira` | 77,75% → 62,58% |
| Romário (Vila Nova) | atl_b4fd772b78e1ac7c | **não resolvido** (sem cartão em 2022) | 51,45% → sem escore |

**Correção de partida.** O ground truth registra o caso PM-005 como "Náutico x Sampaio Corrêa"
na rodada 23, mas naquela rodada o Náutico enfrentou o CRB. O único Náutico x Sampaio Corrêa da
Série B 2022 é o da rodada 31. Sem a correção, o caso era pontuado contra uma partida que o
Sampaio Corrêa não disputou.

**Situação final da ancoragem:** 14 de 14 partidas resolvidas (1 com correção de rodada);
7 de 10 atletas resolvidos, 1 abaixo do mínimo de cartões e 2 sem correspondente defensável.
Artefatos em `reports/tables/auditoria_ground_truth_{partidas,atletas,eventos}.csv`.

### 3.4 Verificação de evento: a maior parte dos incidentes não está na súmula

O teste de ancoragem mais forte disponível é verificar se o evento descrito pelo ground truth
aparece na súmula, no atleta e na partida resolvidos. Dos 14 casos:

| Status | Casos | Leitura |
| :--- | :---: | :--- |
| Confirmado | 1 | PM-011: cartão vermelho aos 93' na rodada 37, exatamente como descrito. |
| Divergência de minuto | 2 | O atleta recebeu cartão na partida, em minuto distinto do declarado (Nino Paraíba: 55' na base contra 45' no ground truth; Moraes Jr: 5' contra 31'). |
| Ausente | 5 | O atleta não recebeu cartão algum na partida resolvida. |
| Não verificável | 5 | Pênalti cometido não deixa registro de cartão, ou o atleta não foi resolvido. |
| Não aplicável | 1 | O evento combinado não se consumou em campo. |

**Consequência metodológica.** Os metadados por incidente do ground truth (rodada, minuto e, em
alguns casos, a atribuição do cartão) **não reconciliam com os registros de súmula**. As
partidas são confiáveis; os eventos individuais, não. Por isso o rótulo positivo usado daqui em
diante é definido em dois níveis agregados — *esta partida contém um incidente conhecido* e
*este atleta-temporada esteve envolvido* —, e não *este cartão específico foi manipulado*. A
reconstituição dos incidentes a partir dos autos originais do MP-GO fica registrada como
pendência de fonte documental.

### 3.5 Sensibilidade dos escores estatísticos (Tabela 17)

| Caso ID | Série | Confronto | Atleta | Identidade na base | Status | Percentil da partida | Score do atleta (Pct) | Status da triagem |
| :---: | :---: | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **PM-001** | B | Vila Nova x Sport | Romario | `—` | nao_resolvido | 92,94% | — (—%) | Detectado (Alta Prioridade / Top 10%) |
| **PM-002** | B | Criciuma x Tombense | Joseph | `joseph_mauricio_de_oliveira_figueiredo` | resolvido | 23,21% | 29,13 (68,46%) | Prioridade Basal (não sinalizado) |
| **PM-003** | B | Sampaio Correa x Londrina | Mateusinho | `mateus_da_silva_duarte` | resolvido | 7,81% | 28,75 (67,69%) | Prioridade Basal (não sinalizado) |
| **PM-004** | B | Sampaio Correa x Londrina | Ygor Catatau | `ygor_de_oliveira_ferreira` | resolvido | 7,81% | 25,92 (62,67%) | Prioridade Basal (não sinalizado) |
| **PM-005** | B | Nautico x Sampaio Correa | Mateusinho | `mateus_da_silva_duarte` | resolvido | 75,51% | 28,75 (67,69%) | Detectado (Média Prioridade / Top 25%) |
| **PM-006** | A | Juventude x Avai | Paulo Miranda | `paulo_miranda` | resolvido | 87,67% | 42,08 (90,20%) | Detectado (Alta Prioridade / Top 10%) |
| **PM-007** | A | Palmeiras x Juventude | Paulo Miranda | `paulo_miranda` | resolvido | 23,21% | 42,08 (90,20%) | Detectado (Alta Prioridade / Top 10%) |
| **PM-008** | A | Juventude x Fortaleza | Gabriel Tota | `gabriel_tota` | abaixo_do_minimo_de_cartoes | 39,83% | — (—%) | Prioridade Basal (não sinalizado) |
| **PM-009** | A | Fluminense x Juventude | Gabriel Tota | `gabriel_tota` | abaixo_do_minimo_de_cartoes | 7,81% | — (—%) | Prioridade Basal (não sinalizado) |
| **PM-010** | A | Santos x Avai | Eduardo Bauermann | `eduardo` | resolvido | 43,78% | 31,66 (74,35%) | Não Ocorreu em Campo (Fraude Frustrada) |
| **PM-011** | A | Botafogo x Santos | Eduardo Bauermann | `eduardo` | resolvido | 53,42% | 31,66 (74,35%) | Prioridade Basal (não sinalizado) |
| **PM-012** | A | Ceara x Cuiaba | Nino Paraiba | `nino_paraiba` | resolvido | 87,56% | 17,15 (34,89%) | Detectado (Média Prioridade / Top 25%) |
| **PM-013** | A | Goias x Juventude | Moraes Jr | `onitlasi_junior_de_moraes_rodrigues` | resolvido | 91,95% | 32,07 (75,50%) | Detectado (Alta Prioridade / Top 10%) |
| **PM-014** | A | Cuiaba x Palmeiras | Igor Carius | `—` | nao_resolvido | 28,65% | — (—%) | Prioridade Basal (não sinalizado) |

Com as identidades corretas, os escores estatísticos sinalizam **6 dos 14 casos (42,9%)** em
faixa prioritária. Dois dos oito não sinalizados são fraudes que não se consumaram em campo
(PM-001 e PM-010), em que a ausência de sinal é o comportamento desejado.

O resultado anterior de 100% se sustentava em atletas que não eram os investigados. O de 64,3%,
reportado na revisão intermediária (F1-01/F1-02), ainda usava o casamento defeituoso.

### 3.6 Validação fora da amostra do classificador de ML (Tabela 22)

**Distinção essencial.** `MATCH_ANOMALY_SCORE` e `ATHLETE_ANOMALY_SCORE` são fórmulas fechadas
calibradas em distribuição basal: não veem o ground truth em momento algum, e a sua
sensibilidade é a mesma dentro e fora da amostra. O `IsolationForest` também é não
supervisionado. **Apenas o `BaggingPUClassifier` é treinado nos rótulos** — e só ele sofre do
problema de avaliação in-sample, objeto desta seção.

Protocolos implementados em `src/models/validacao_out_of_sample.py`:

| Protocolo | Nível | Cenário | Critério | Capturados | Sensibilidade | IC 95% (Wilson) |
| :--- | :---: | :--- | :--- | :---: | :---: | :---: |
| In-sample | partida | — | Classe 2 (Alto Risco) | 12/14 | **85,7%** | 60,1% – 96,0% |
| In-sample | partida | — | Classe 1 ou 2 (sinalizado) | 14/14 | **100,0%** | 78,5% – 100,0% |
| In-sample | atleta | — | Classe 2 (Alto Risco) | 7/7 | **100,0%** | 64,6% – 100,0% |
| In-sample | atleta | — | Classe 1 ou 2 (sinalizado) | 7/7 | **100,0%** | 64,6% – 100,0% |
| Leave-one-out | partida | — | Classe 2 (Alto Risco) | 6/14 | **42,9%** | 21,4% – 67,4% |
| Leave-one-out | partida | — | Classe 1 ou 2 (sinalizado) | 11/14 | **78,6%** | 52,4% – 92,4% |
| Leave-one-out | atleta | — | Classe 2 (Alto Risco) | 1/7 | **14,3%** | 2,6% – 51,3% |
| Leave-one-out | atleta | — | Classe 1 ou 2 (sinalizado) | 2/7 | **28,6%** | 8,2% – 64,1% |
| Separação por série | partida | treina em B avalia em A | Classe 2 (Alto Risco) | 1/9 | **11,1%** | 2,0% – 43,5% |
| Separação por série | partida | treina em B avalia em A | Classe 1 ou 2 (sinalizado) | 3/9 | **33,3%** | 12,1% – 64,6% |
| Separação por série | partida | treina em A avalia em B | Classe 2 (Alto Risco) | 3/5 | **60,0%** | 23,1% – 88,2% |
| Separação por série | partida | treina em A avalia em B | Classe 1 ou 2 (sinalizado) | 4/5 | **80,0%** | 37,5% – 96,4% |
| Separação por série | atleta | treina em B avalia em A | Classe 2 (Alto Risco) | 1/4 | **25,0%** | 4,6% – 69,9% |
| Separação por série | atleta | treina em B avalia em A | Classe 1 ou 2 (sinalizado) | 1/4 | **25,0%** | 4,6% – 69,9% |
| Separação por série | atleta | treina em A avalia em B | Classe 2 (Alto Risco) | 0/3 | **0,0%** | 0,0% – 56,1% |
| Separação por série | atleta | treina em A avalia em B | Classe 1 ou 2 (sinalizado) | 1/3 | **33,3%** | 6,2% – 79,2% |

**Leitura dos resultados:**

1. **A sensibilidade de 100% era memorização.** No nível do atleta, o classificador captura
   7 de 7 positivos quando eles estão no próprio treino e **0 de 7** quando cada um é retirado.
   O tier de Alto Risco não sobrevive à retirada de um único exemplo.
2. **No nível da partida o modelo retém algum sinal.** O leave-one-out mantém 5 de 14 no tier
   de Alto Risco e 10 de 14 em alguma faixa de alerta — consistente com o fato de as features de
   partida (concentração no 1º tempo, precocidade, volume) carregarem informação de campo que
   não depende do rótulo.
3. **A generalização entre divisões é fraca.** Treinado apenas com os positivos da Série B e
   avaliado na Série A, o classificador captura 1 de 9 partidas no tier de Alto Risco (11,1%).
   Este é o cenário que mais se aproxima do uso real — detectar um esquema novo com um modelo
   calibrado em esquemas anteriores.
4. **Com N = 14, todo intervalo é largo.** A estimativa pontual de 35,7% no nível da partida é
   compatível com qualquer valor entre 16,3% e 61,2%. Nenhuma das cifras desta tabela deve ser
   citada sem o seu intervalo.

**Conclusão.** O componente de machine learning, tal como treinado, não generaliza a ponto de
sustentar uma afirmação de eficácia. O que sustenta o produto é o escore estatístico fechado,
que não depende de rótulo algum — e cuja utilidade se mede por carga de alerta e precisão no
topo da lista, não por sensibilidade (tarefa F1-04).

---

### 3.7 Precisão, carga de alerta e curva operacional (F1-04)

Até aqui o sistema foi avaliado por sensibilidade. Falta a pergunta que a persona faz antes de
comprar: **quantos alertas isso custa?**

#### Limitação que atravessa toda esta seção

Não existem falsos positivos rotulados. O ground truth cobre uma operação, uma temporada e 13
partidas em 4.559: uma partida sinalizada e nunca investigada **não é** um negativo confirmado.
Por isso a precisão absoluta não é estimável, e não será inventado um denominador. O que se pode
medir com honestidade é a **carga de alerta**, a **precisão@k sobre o ground truth disponível**
e o **ganho sobre sortear a mesma quantidade de registros ao acaso**.

#### Tabela 21 — Carga de alerta por tier

| Nível | Tier | Sinalizados | % da base | Alertas por rodada / temporada | Casos conhecidos no tier | Alertas por caso conhecido |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| partida | Extrema Anomalia (Top 1%) | 45 | 0,99% | 0,10 | 0/13 | — |
| partida | Alta Prioridade de Escrutínio (Top 5%) | 184 | 4,04% | 0,40 | 0/13 | — |
| partida | Média Prioridade (Top 10%) | 226 | 4,96% | 0,49 | 2/13 | 113,0 |
| partida | Típico / Baixa Prioridade | 4104 | 90,02% | 8,96 | 11/13 | 373,1 |
| atleta | Extrema Anomalia Temporal (Top 1%) | 38 | 1,03% | 3,17 | 0/7 | — |
| atleta | Alta Concentração Precoce (Top 5%) | 147 | 3,98% | 12,25 | 0/7 | — |
| atleta | Média Concentração (Top 10%) | 186 | 5,04% | 15,50 | 1/7 | 186,0 |
| atleta | Padrão Basal Normal | 3323 | 89,96% | 276,92 | 6/7 | 553,8 |
| partida | TOTAL SINALIZADO (todos os tiers) | 455 | 9,98% | 0,99 | 2/13 | 227,5 |
| atleta | TOTAL SINALIZADO (todos os tiers) | 371 | 10,04% | 30,92 | 1/7 | 371,0 |

Onze dos treze casos conhecidos estão no tier basal. Nenhum caso aparece nos tiers de Extrema
Anomalia ou Alta Prioridade, nos dois níveis.

#### Precisão@k por rodada

Restrita às 9 rodadas que contêm ao menos um caso do ground truth. Uma rodada tem 10 partidas,
então **k = 10 equivale a inspecionar a rodada inteira** e o recall de 100% não informa nada. O
teto aritmético da precisão@k é `positivos_na_rodada / k`, reportado ao lado.

| k | Rodadas | Partidas inspecionadas | Capturados | Precisão@k | Teto possível | Recall@k | Ganho sobre o acaso |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1.0 | 9.0 | 9.0 | 1.0/13.0 | 11,1% | 100,0% | 7,7% | 0,77 |
| 3.0 | 9.0 | 27.0 | 5.0/13.0 | 18,5% | 48,1% | 38,5% | 1,28 |
| 5.0 | 9.0 | 45.0 | 5.0/13.0 | 11,1% | 28,9% | 38,5% | 0,77 |
| 10.0 | 9.0 | 90.0 | 13.0/13.0 | 14,4% | 14,4% | 100,0% | 1,00 |

#### Curva de carga operacional — nível partida

| Corte | Score mínimo | Sinalizados | % da base | Alertas/rodada | Capturados | Sensibilidade | Ganho sobre o acaso | p-valor |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| P100 | 46,04 | 5.0 | 0,11% | 0,01 | 0.0/13.0 | 0,0% | 0,00 | 1,000 |
| P100 | 33,40 | 24.0 | 0,53% | 0,05 | 0.0/13.0 | 0,0% | 0,00 | 1,000 |
| P99 | 30,24 | 45.0 | 0,99% | 0,10 | 0.0/13.0 | 0,0% | 0,00 | 1,000 |
| P98 | 25,99 | 90.0 | 1,97% | 0,20 | 0.0/13.0 | 0,0% | 0,00 | 1,000 |
| P97 | 23,58 | 138.0 | 3,03% | 0,30 | 0.0/13.0 | 0,0% | 0,00 | 1,000 |
| P96 | 21,98 | 183.0 | 4,01% | 0,40 | 0.0/13.0 | 0,0% | 0,00 | 1,000 |
| P95 | 20,92 | 229.0 | 5,02% | 0,50 | 0.0/13.0 | 0,0% | 0,00 | 1,000 |
| P92 | 18,94 | 343.0 | 7,52% | 0,75 | 1.0/13.0 | 7,7% | 1,02 | 0,639 |
| P90 | 16,65 | 455.0 | 9,98% | 0,99 | 2.0/13.0 | 15,4% | 1,54 | 0,378 |
| P85 | 14,37 | 685.0 | 15,03% | 1,50 | 4.0/13.0 | 30,8% | 2,05 | 0,118 |
| P80 | 12,27 | 913.0 | 20,03% | 1,99 | 4.0/13.0 | 30,8% | 1,54 | 0,253 |
| P75 | 10,83 | 1139.0 | 24,98% | 2,49 | 5.0/13.0 | 38,5% | 1,54 | 0,205 |
| P70 | 9,43 | 1369.0 | 30,03% | 2,99 | 5.0/13.0 | 38,5% | 1,28 | 0,346 |
| P60 | 7,38 | 1823.0 | 39,99% | 3,98 | 5.0/13.0 | 38,5% | 0,96 | 0,647 |
| P50 | 5,51 | 2281.0 | 50,03% | 4,98 | 6.0/13.0 | 46,2% | 0,92 | 0,711 |

#### Curva de carga operacional — nível atleta-temporada

| Corte | Score mínimo | Sinalizados | % da base | Alertas/temporada | Capturados | Sensibilidade | Ganho sobre o acaso | p-valor |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| P100 | 77,52 | 4.0 | 0,11% | 0,30 | 0.0/7.0 | 0,0% | 0,00 | 1,000 |
| P100 | 71,63 | 19.0 | 0,51% | 1,60 | 0.0/7.0 | 0,0% | 0,00 | 1,000 |
| P99 | 67,25 | 38.0 | 1,03% | 3,20 | 0.0/7.0 | 0,0% | 0,00 | 1,000 |
| P98 | 63,67 | 74.0 | 2,00% | 6,20 | 0.0/7.0 | 0,0% | 0,00 | 1,000 |
| P97 | 56,89 | 112.0 | 3,03% | 9,30 | 0.0/7.0 | 0,0% | 0,00 | 1,000 |
| P96 | 51,85 | 148.0 | 4,01% | 12,30 | 0.0/7.0 | 0,0% | 0,00 | 1,000 |
| P95 | 49,14 | 185.0 | 5,01% | 15,40 | 0.0/7.0 | 0,0% | 0,00 | 1,000 |
| P92 | 44,54 | 278.0 | 7,53% | 23,20 | 0.0/7.0 | 0,0% | 0,00 | 1,000 |
| P90 | 41,76 | 371.0 | 10,04% | 30,90 | 1.0/7.0 | 14,3% | 1,42 | 0,524 |
| P85 | 38,78 | 555.0 | 15,02% | 46,20 | 1.0/7.0 | 14,3% | 0,95 | 0,680 |
| P80 | 35,37 | 739.0 | 20,01% | 61,60 | 1.0/7.0 | 14,3% | 0,71 | 0,791 |
| P75 | 31,89 | 924.0 | 25,01% | 77,00 | 2.0/7.0 | 28,6% | 1,14 | 0,556 |
| P70 | 29,97 | 1109.0 | 30,02% | 92,40 | 3.0/7.0 | 42,9% | 1,43 | 0,353 |
| P60 | 24,73 | 1479.0 | 40,04% | 123,20 | 6.0/7.0 | 85,7% | 2,14 | 0,019 |
| P50 | 21,46 | 1849.0 | 50,05% | 154,10 | 6.0/7.0 | 85,7% | 1,71 | 0,063 |

O p-valor é o de um teste hipergeométrico: a probabilidade de capturar ao menos aquele número de
casos sorteando a mesma quantidade de registros ao acaso.

![Curva de carga operacional](../figures/integrity/04_curva_carga_operacional.png)

#### O achado central: não há ganho demonstrável sobre a seleção aleatória

**No nível da partida, nenhum limiar produz ganho estatisticamente distinguível do acaso.** O
melhor ponto da curva (P85, 1,5 alerta por rodada) captura 4 de 13 casos com ganho de 2,05×, a
um p-valor de 0,118. Nos tiers operacionalmente atraentes — Top 1% e Top 5% — a captura é **zero**.

**No nível do atleta há sinal, mas fora da faixa útil.** O único ponto com p < 0,05 é o corte no
percentil 60: captura 6 dos 7 atletas, ganho de 2,15×, p = 0,019 — ao custo de sinalizar **40% de
todos os atletas da base**, cerca de 123 por temporada e divisão. Não é uma fila de auditoria;
é a lista telefônica.

#### Por que isso é coerente com o resto do trabalho

O resultado não é um acidente de calibração: é um **desencontro entre o instrumento e o
fenômeno**. O `MATCH_ANOMALY_SCORE` mede distorção coletiva da partida — concentração temporal,
precocidade, volume. Os incidentes da Operação Penalidade Máxima são atos individuais: um cartão
amarelo de um atleta, um pênalti cometido por um zagueiro. Um cartão combinado em uma partida
com mais 4 cartões legítimos não move a distribuição da partida.

A própria econometria deste projeto já havia registrado isso: a exposição a apostas tem efeito
**nulo** sobre a proporção coletiva de cartões no 1º tempo ($\beta = -0{,}0129$, $p = 0{,}5916$).
A manipulação por micro-apostas não é comportamento de clube, é conduta individual — e por isso
a unidade de análise que pode funcionar é o **atleta**, não a partida.

### 3.8 Reposicionamento: nem detector, nem priorizador — instrumento de medição

A tarefa F1-04 previa reposicionar o sistema de "detecção de fraude" para "priorização de
escrutínio". O reposicionamento é necessário, mas **não é suficiente**: um priorizador é avaliado
por precisão no topo da lista, e o topo da lista não contém os casos conhecidos.

O que os dados sustentam afirmar hoje:

1. **O sistema mede atipicidade disciplinar com rigor estatístico.** Os subscores são testes
   binomiais calibrados na distribuição basal de 23.369 cartões, com fórmula publicada,
   reproduzível e testada. Isso é verdadeiro e verificável, e independe do ground truth.
2. **O sistema não demonstra capacidade de priorizar os casos conhecidos de manipulação.** Nem
   no topo da lista, nem em nenhum limiar testado, no nível da partida.
3. **O caminho com evidência é o nível do atleta**, que mostra sinal ainda que fora da faixa
   operacional, e que depende de dados que o projeto ainda não tem: a escalação por partida
   (tarefa F2-04) e o escore pré-jogo por atleta (F3-01).

**Recomendação de posicionamento.** Descrever o produto como *instrumento de medição de
atipicidade disciplinar* — que é o que ele comprovadamente faz — e não como detector ou
priorizador de manipulação, até que exista evidência de ganho sobre o acaso. Afirmar capacidade
de priorização hoje não sobrevive à primeira diligência técnica de um comprador.

#### Limiar por persona, sob a ressalva acima

Os limiares abaixo são o corte mais permissivo que cabe na capacidade declarada de cada persona.
As capacidades são **premissas**, a serem confirmadas nas entrevistas da tarefa F5-01, e a
sensibilidade esperada carrega toda a ressalva desta seção.

| Persona | Capacidade (por rodada) | Corte | Alertas/rodada | Casos capturados | Sensibilidade |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Analista de federação / STJD | 3 | P70 | 2,99 | 5/13 | 38,5% |
| Compliance de clube | 1 | P90 | 0,99 | 2/13 | 15,4% |
| Integrity de operadora | 10 | P50 | 4,98 | 6/13 | 46,2% |

---

## 4. Análise dos Rankings de Triagem (Tabelas 15 e 16)

### 4.1 Top 5 partidas sinalizadas (Tabela 15)

| Ranking | Partida ID | Temporada | Série | Rodada | Confronto | Total Cartões | Cartões 1ºT | Cartões $\le 30'$ | Pênaltis 1ºT | Match Anomaly Score | Percentil | Prioridade de Triagem |
| :---: | :---: | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1º** | 7998 | 2022 | A | 36 | Bragantino x America-MG | 8 | 8 | 3 | 2 | **56,55** | 100,00% | Extrema Anomalia (Top 1%) |
| **2º** | 145 | 2022 | B | 15 | Novorizontino x Vasco da Gama | 9 | 7 | 6 | 0 | **49,92** | 99,98% | Extrema Anomalia (Top 1%) |
| **3º** | 7110 | 2020 | A | 23 | Santos x Sport | 6 | 6 | 4 | 1 | **49,21** | 99,96% | Extrema Anomalia (Top 1%) |
| **4º** | 8345 | 2023 | A | 32 | Fluminense x Sao Paulo | 11 | 7 | 7 | 0 | **48,61** | 99,93% | Extrema Anomalia (Top 1%) |
| **5º** | 8082 | 2023 | A | 6 | Corinthians x Sao Paulo | 6 | 6 | 4 | 1 | **47,11** | 99,91% | Extrema Anomalia (Top 1%) |

O topo do ranking é ocupado por partidas em que **todos** os cartões saíram no 1º tempo ou em
que a concentração precoce se combina a volume atípico. O primeiro colocado (Bragantino x
América-MG, 2022) reúne os três marcadores simultaneamente: 8 cartões, todos no 1º tempo, e
2 pênaltis na etapa inicial.

### 4.2 Top 5 atletas sinalizados (Tabela 16)

> **Nota de exposição (F4-02).** Identificadores no formato `atl_...` substituem o nome de
> atletas **sem condenação**. Eles são pseudônimos estáveis derivados do registro do atleta,
> de modo que o mesmo atleta é reconhecível entre tabelas, e o mapeamento de reidentificação
> vive fora do repositório. Atletas com condenação da Operação Penalidade Máxima seguem
> nominados, por serem fato público. Um escore alto significa desvio estatístico, nunca
> conduta — e nomear quem nunca foi investigado transformaria a ressalva em letra morta.


| Ranking | Atleta | Temporada | Série | Clube | Total Cartões | Cartões 1ºT | % Cartões 1ºT | Minuto Médio | Athlete Anomaly Score | Percentil | Classificação |
| :---: | :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1º** | atl_20b829edd2790353 | 2024 | A | fluminense | 6 | 6 | 100,0% | 34,7' | **80,66** | 99,99% | Extrema Anomalia Temporal (Top 1%) |
| **2º** | atl_e05a95826461267d | 2022 | A | coritiba | 6 | 6 | 100,0% | 34,7' | **80,66** | 99,99% | Extrema Anomalia Temporal (Top 1%) |
| **3º** | atl_8dc959eb5befb439 | 2022 | B | bahia | 5 | 5 | 100,0% | 19,6' | **78,41** | 99,93% | Extrema Anomalia Temporal (Top 1%) |
| **4º** | atl_610529b609dd55ca | 2017 | A | vasco | 5 | 5 | 100,0% | 16,6' | **78,41** | 99,93% | Extrema Anomalia Temporal (Top 1%) |
| **5º** | Marlon | 2023 | A | fluminense | 5 | 5 | 100,0% | 27,6' | **77,13** | 99,89% | Extrema Anomalia Temporal (Top 1%) |

Os cinco primeiros colocados têm 100% dos cartões da temporada aplicados no 1º tempo, com
minutagem média entre 16' e 35'. Nenhum deles é investigado: o ranking mede **atipicidade
estatística**, não conduta — ver a seção 6.1.

---

## 5. Visualizações Geradas

O pipeline gerou três gráficos de alta resolução armazenados em `reports/figures/integrity/`:

1. **`01_distribuicao_anomaly_scores.png`:** Histogramas e curvas de densidade (KDE) demonstrando as distribuições de cauda longa do `MATCH_ANOMALY_SCORE` e `ATHLETE_ANOMALY_SCORE`, com a marcação visual dos limiares de corte percentílicos.
2. **`02_dispersao_tempo_vs_volume.png`:** Gráfico de dispersão cruzando a anomalia temporal ($S_{\text{tempo}}$) com a precocidade ($S_{\text{precoce}}$) e o volume de cartões, destacando os confrontos reais investigados na Operação Penalidade Máxima.
3. **`04_curva_carga_operacional.png`:** Curvas de carga operacional nos dois níveis, contra a referência de seleção aleatória, com os limiares por persona marcados. É a figura que sustenta a seção 3.7.
4. **`03_validacao_sensibilidade_ground_truth.png`:** Diagrama de sensibilidade que mapeia os percentis individuais e status de detecção dos 14 casos reais investigados, cujos percentis individuais estão sujeitos à ressalva da seção 3.4.

---

## 6. Governança, Ética e Recomendações Operacionais

### 6.1 Diretrizes de Governança Ética
1. **Presunção de Inocência Irrestrita:** Uma pontuação elevada em `MATCH_ANOMALY_SCORE` ou `ATHLETE_ANOMALY_SCORE` significa estritamente que os eventos disciplinares daquela partida ou atleta desviam da distribuição empírica basal da liga. **Não constitui, sob nenhuma hipótese, prova ou acusação de manipulação de resultados ou infração disciplinar.**
2. **Fatores de Confundimento Esportivo:** Desvios temporais e de volume podem decorrer de fatores esportivos legítimos, tais como:
   * Critério de arbitragem excessivamente rigoroso no início do jogo para "controlar os ânimos";
   * Faltas táticas precoces necessárias para conter contra-ataques iminentes;
   * Clássicos de alta rivalidade regional (derbies);
   * Estilo tático de marcação sob pressão pós-perda (*gegenpressing*).
3. **Reserva de Jurisdição:** A denominação de "manipulação", "fraude" ou "corrupção esportiva" é rigorosamente reservada apenas para fatos comprovados por órgãos estatais competentes (Ministério Público, Polícia Federal, STJD, FIFA) com condenações ou confissões formais.

### 6.2 Protocolo Recomendado de Triagem para Federações e Tribunais Desportivos
Recomenda-se que federações (CBF) e entidades de integridade utilizem o sistema sob o seguinte protocolo em quatro etapas:

```
[Etapa 1: Ingestão de Súmula]
   │
   ▼
[Etapa 2: Anomaly Scoring Automatizado]
   │
   ├── Percentil < 90: Linha de Base (Arquivamento sem Ação)
   ├── P90 <= Percentil < 95: Média Prioridade (Registro em Watchlist de Compliance)
   ├── P95 <= Percentil < 99: Alta Prioridade (Disparo de Auditoria Ativa)
   └── Percentil >= 99: Extrema Anomalia (Auditoria Prioritária da Rodada)
         │
         ▼
[Etapa 3: Auditoria Técnica Multidimensional]
   ├── 1. Revisão em Vídeo dos Lances de Advertência (Critério do Árbitro)
   ├── 2. Cruzamento com Alertas de Monitoramento de Mercado (Genius / Sportradar / IBIA)
   └── 3. Análise de Histórico Disciplinar e Contratual do Atleta
         │
         ▼
[Etapa 4: Encaminhamento Institucional]
   ├── Se Explicado por Dinâmica de Jogo: Arquivamento Justificado
   └── Se Apresentar Indícios Gravosos de Casa de Apostas: Envio Sigiloso ao STJD / MP
```

---

## 7. Rastreabilidade dos Artefatos

* **Código de Scoring e Detecção:** [`src/models/anomaly_detection.py`](file:///d:/Python%20Projetos/analise-bets/src/models/anomaly_detection.py)
* **Script de Visualização:** [`src/visualization/plot_anomalies.py`](file:///d:/Python%20Projetos/analise-bets/src/visualization/plot_anomalies.py)
* **Testes Automatizados:** [`tests/test_anomaly_detection.py`](file:///d:/Python%20Projetos/analise-bets/tests/test_anomaly_detection.py)
* **Auditoria de Reconciliação (F1-01 / F1-02):** [`src/analysis/comparacao_reconciliacao_score.py`](file:///d:/Python%20Projetos/analise-bets/src/analysis/comparacao_reconciliacao_score.py)
* **Resolvedor de Identidade do Ground Truth (F1-03):** [`src/models/ground_truth_resolver.py`](file:///d:/Python%20Projetos/analise-bets/src/models/ground_truth_resolver.py)
* **Validação Fora da Amostra (F1-03):** [`src/models/validacao_out_of_sample.py`](file:///d:/Python%20Projetos/analise-bets/src/models/validacao_out_of_sample.py)
* **Precisão e Carga de Alerta (F1-04):** [`src/analysis/precisao_e_carga_alerta.py`](file:///d:/Python%20Projetos/analise-bets/src/analysis/precisao_e_carga_alerta.py)
* **Tabelas Geradas:**
  * [`reports/tables/tabela_15_ranking_partidas_anomalas.csv`](file:///d:/Python%20Projetos/analise-bets/reports/tables/tabela_15_ranking_partidas_anomalas.csv)
  * [`reports/tables/tabela_16_ranking_atletas_anomalos.csv`](file:///d:/Python%20Projetos/analise-bets/reports/tables/tabela_16_ranking_atletas_anomalos.csv)
  * [`reports/tables/tabela_17_validacao_ground_truth_pm.csv`](file:///d:/Python%20Projetos/analise-bets/reports/tables/tabela_17_validacao_ground_truth_pm.csv)
  * `reports/tables/comparacao_f1_reconciliacao_resumo.csv` (efeito agregado da reconciliação)
  * `reports/tables/comparacao_f1_reconciliacao_migracao_tier.csv` (matriz de migração de tier)
  * `reports/tables/comparacao_f1_reconciliacao_ground_truth.csv` (14 casos, antes e depois)
  * `reports/tables/comparacao_f1_reconciliacao_atletas_gt.csv` (efeito da harmonização de minuto)
  * `reports/tables/auditoria_ground_truth_partidas.csv` / `_atletas.csv` / `_eventos.csv` (ancoragem)
  * `reports/tables/tabela_22_validacao_out_of_sample.csv` (sensibilidade por protocolo)
  * `reports/tables/tabela_22b_validacao_out_of_sample_detalhe.csv` (resultado por dobra)
  * `reports/tables/tabela_21_precisao_e_carga_de_alerta.csv` (carga por tier)
  * `reports/tables/tabela_21b_precisao_at_k.csv` (precisão@k por rodada)
  * `reports/tables/tabela_21c_curva_carga_operacional.csv` / `_21e_..._atleta.csv` (curvas)
  * `reports/tables/tabela_21d_limiar_por_persona.csv` (limiar recomendado)
* **Datasets Resultantes:**
  * `data/processed/integrity/partidas_anomaly_scored.parquet` (4.559 partidas)
  * `data/processed/integrity/atletas_anomaly_scored.parquet` (3.586 atleta-temporadas)
* **Figuras:**
  * `reports/figures/integrity/01_distribuicao_anomaly_scores.png`
  * `reports/figures/integrity/02_dispersao_tempo_vs_volume.png`
  * `reports/figures/integrity/03_validacao_sensibilidade_ground_truth.png`
