# Relatório de Execução — 16 de setembro de 2026

**Escopo:** oito tarefas do backlog de transição para produto, em nove commits no branch
`fase-1-credibilidade`.
**Suíte ao final:** 139 testes passando (eram 67 no início), nenhum ignorado.

---

## 1. Por que este documento existe

O trabalho desta sessão fez duas coisas ao mesmo tempo: executou tarefas do backlog e
**desfez afirmações que o projeto já tinha publicado**. A segunda parte é a mais importante e
a mais fácil de se perder no histórico de commits, porque não aparece como funcionalidade
nova — aparece como número que caiu.

Este relatório registra o que foi feito, o que mudou nos resultados e o que continua aberto.

---

## 2. O resumo em uma tabela

| Afirmação anterior | Situação após esta sessão |
| :--- | :--- |
| Sensibilidade de 100% (14/14) no ground truth | **6/14 (42,9%)** pelos escores estatísticos |
| Atletas investigados no Top 10% da liga | **Oito das dez identidades estavam erradas** |
| Sistema de detecção de manipulação | **Sem ganho demonstrável sobre sorteio** no nível de partida |
| Classificador de ML com 100% de sensibilidade | **1/7 no nível do atleta** fora da amostra |
| — | **Escore pré-jogo com ganho de 2,4× a 2,7×**, medido sem vazamento |

---

## 3. Tarefas executadas

### F1-01 e F1-02 — Reconciliação da fórmula e remoção do subscore de apostas
*Commit `d4bb694`*

A fórmula publicada e a executada divergiam em seis pontos: pesos, `p0` dos dois testes
binomiais, multiplicador logarítmico, `S_volume` e `S_penalti`. A especificação canônica passou
a viver em constantes no topo de `src/models/anomaly_detection.py`, fixadas por teste.

O subscore de exposição comercial (`S_bet`) saiu do índice e a `exposure_total_partida` saiu do
espaço de features do classificador, por dois motivos independentes: **circularidade** — a mesma
variável cujo efeito a econometria estima não pode ser preditor de suspeição — e
**indefensabilidade operacional** — nenhum clube contrata um índice que o penaliza pelo
patrocinador da camisa.

Os tiers deixaram de usar limiar absoluto e passaram a percentil empírico. A configuração
anterior classificava 10 de 4.559 partidas fora do tier basal, e nenhuma delas era do ground
truth: a carga de alerta era efeito acidental da escala do escore, não parâmetro.

### F1-03 — Ancoragem do ground truth e validação fora da amostra
*Commit `d4bb694`*

O cruzamento com os 14 casos da Operação Penalidade Máxima usava correspondência parcial de
nome e **associava atletas errados em 8 dos 10 casos**. O percentil de 99,67% publicado como
sendo de Nino Paraíba (Ceará) pertence a Nino (Fluminense), atleta sem qualquer relação com a
operação; o registro real de Nino Paraíba está em 34,5%.

Substituído por mapa de identidade explícito em `src/models/ground_truth_resolver.py`, com
evidência e grau de confiança por associação. Casos sem correspondente defensável ficam
declaradamente `nao_resolvido`, em vez de receberem o escore de um homônimo.

A verificação de evento mostrou que os metadados por incidente do ground truth **não
reconciliam com as súmulas**: de 14 casos, 1 confirmado, 2 com divergência de minuto e 5
ausentes. O rótulo positivo passou a ser definido nos níveis agregados de partida e
atleta-temporada.

Validação fora da amostra com leave-one-out agrupado por entidade e separação por série:

| Nível | Critério | In-sample | Leave-one-out | IC 95% |
| :--- | :--- | :---: | :---: | :---: |
| Partida | Classe 2 | 12/14 | **6/14** | 21,4% – 67,4% |
| Atleta | Classe 2 | 7/7 | **1/7** | 2,6% – 51,3% |

### F1-04 — Precisão, carga de alerta e ganho sobre o acaso
*Commit `362226b`*

Sem falsos positivos rotulados, precisão absoluta não é estimável — uma partida sinalizada e
nunca investigada não é um negativo confirmado. O entregável honesto passou a ser carga de
alerta, precisão@k sobre o ground truth disponível e um teste hipergeométrico contra sorteio.

**Achado central: não há ganho demonstrável sobre a seleção aleatória.** No nível da partida
nenhum limiar atinge significância — o melhor ponto da curva fica em p = 0,118 — e nos tiers
Top 1% e Top 5% a captura é zero. No nível do atleta há sinal (p = 0,019), mas só ao sinalizar
40% da base.

O desencontro é de unidade de análise: o índice de partida mede distorção coletiva, e os
incidentes são atos individuais. É o mesmo achado da econometria do projeto, que estima efeito
nulo da exposição sobre a proporção coletiva de cartões no 1º tempo.

**Consequência de posicionamento:** o produto passou a ser descrito como *instrumento de
medição de atipicidade disciplinar* — o que comprovadamente faz —, e não como detector nem
como priorizador de manipulação.

### F2-01 — Motivo do cartão na Série A
*Commit `95bffe7`*

`align_dataframe_types` truncava o dado novo para o schema do histórico. Como a base da Série A
veio do Kaggle, sem `motivo_completo`, **o motivo textual do árbitro era descartado em silêncio
a cada execução do pipeline delta**. A função passou a unir os schemas.

Cobertura resultante: 6.970 cartões com motivo (25,0% da base), dos quais **30,4% são infrações
comportamentais não-físicas** — proporção estável entre séries e temporadas, e a primeira vez
que o dado existe para a Série A.

### F2-03 (parcial) — 519 cartões perdidos da Série B
*Commit `bdd1877`*

Ao reprocessar a Série B para corrigir a atribuição de clube em expulsões, o reparse devolveu
519 cartões a mais do que a base continha.

Causa: `parse_cbf_sumulas.py` localizava as seções da súmula sem guarda de primeira ocorrência.
O token `2º Cartão Amarelo` — subtipo de expulsão, que aparece **dentro** da seção de vermelhos
— sobrescrevia o índice da seção de amarelos, e o recorte virava vazio. **Toda partida com
expulsão por segundo amarelo perdia todos os seus cartões amarelos.** A Série B 2022–2023
estava sem 14% dos seus cartões.

Com a base de calibração corrigida, as probabilidades basais foram reestimadas e toda a cadeia
de artefatos, regenerada. As conclusões da Fase 1 não mudaram; os números melhoraram
marginalmente, dentro dos intervalos já reportados.

### F2-04 — Relação de atletas e minutos em campo
*Commits `fb6b4f9` e `8cbad37`*

Três tabelas novas, extraídas da relação de jogadores da súmula: `escalacoes` (57.406
registros), `substituicoes` (11.826) e `minutos_em_campo` (3.945). Taxa de extração de 99,2%;
as 11 partidas sem relação são PDFs incompletos na origem, listadas explicitamente.

**Achado que mudou a identificação de atleta no projeto:** a súmula trunca o nome completo em
~40% dos registros e apelidos se repetem dentro do mesmo elenco — o Juventude de 2026 tem dois
atletas de mesmo apelido, de camisas 10 e 47. O `registro_cbf` está presente em 100% dos registros e
passou a ser o identificador canônico. É a saída estrutural para o problema de identidade da
F1-03.

### F3-01 — Escore de risco pré-jogo por atleta
*Commit `832ff8e`*

Primeiro componente do projeto com **poder preditivo demonstrado e medido sem vazamento**.
Estima os cartões no 1º tempo esperados de cada atleta relacionado, usando só informação
anterior à rodada, com encolhimento bayesiano empírico em direção à taxa populacional.

| k | Escore | Linha de base | Acaso | Ganho |
| :---: | :---: | :---: | :---: | :---: |
| 1 | 10,8% | 11,7% | 4,0% | 2,73× |
| 3 | 10,2% | 9,0% | 4,0% | 2,58× |
| 5 | 9,6% | 9,0% | 4,0% | 2,41× |
| 10 | 10,8% | 8,2% | 4,0% | 2,73× |

O teste de vazamento previsto na tarefa — embaralhar a ordem temporal e esperar degradação —
**não discrimina**: embaralhar destrói a cronologia e com isso *dá* ao modelo acesso a partidas
futuras, de modo que o desempenho sobe. Foi substituído por corrupção determinística do futuro,
que reprovou duas versões do pipeline antes de aprovar a terceira.

### F4-03 — Restrição de granularidade por perfil de cliente
*Commit `8b0b30c`*

Antecipada em relação à ordem do backlog, porque a F3-01 entregou uma saída com valor comercial
real e potencial de uso indevido em precificação.

**Posição registrada: o projeto não atende mesas de trading nem áreas de precificação.** O mesmo
escore é sinal de integridade e sinal de trading; fornecido a quem precifica micro-mercados de
cartão, o produto daria vantagem competitiva nos exatos mercados que o trabalho identifica como
vetor de vulnerabilidade.

A matriz de granularidade é executável (`src/pipeline/perfis_de_acesso.py`): um perfil não
atendido levanta exceção em tempo de execução. O feed servido por padrão passou a ser o
agregado, e a camada identificada foi isolada em diretório restrito.

---

## 4. Defeitos de dados encontrados e corrigidos

Nenhum destes estava no backlog. Todos foram encontrados durante a execução e todos afetavam
resultados já publicados.

| # | Defeito | Efeito | Onde |
| :---: | :--- | :--- | :--- |
| 1 | Chave de junção sem a temporada | A `partida_id` da Série B reinicia a cada ano: cada partida recebia os cartões de duas temporadas somados | F1-01 |
| 2 | Semântica de minuto divergente | A Série B registra o minuto dentro do tempo; 47,8% dos cartões contavam como "até 30 minutos", contra 15,4% da Série A | F1-01 |
| 3 | Janela temporal sem teto | A sincronização de 2026 injetou 204 registros de atleta-temporada na distribuição de referência | F1-01 |
| 4 | Casamento de identidade por nome parcial | Oito das dez identidades do ground truth estavam erradas | F1-03 |
| 5 | Fixture errada no ground truth | O caso PM-005 apontava para uma partida que o Sampaio Corrêa não disputou | F1-03 |
| 6 | `align_schema` truncando colunas novas | O motivo do cartão era descartado a cada execução do pipeline delta | F2-01 |
| 7 | Seção da súmula atribuída como clube | 283 expulsões com `clube_slug` igual a `cartao_vermelho_direto` | F2-01 |
| 8 | Teste destruindo a base de produção | `pytest` reconstruía a Série A do Kaggle e apagava a temporada 2026 | F2-01 |
| 9 | Seção de amarelos perdida | Toda partida com expulsão por segundo amarelo perdia todos os seus cartões amarelos — 519 na Série B | F2-03 |
| 10 | Split de nome pela última ocorrência | `Gremio Novorizontino - SAF/SP` virava o clube `Saf` | F2-04 |
| 11 | Partidas fantasma na Série A 2024 | Ingerir 5 súmulas numa temporada completa do Kaggle criou 5 duplicatas | F2-04 |
| 12 | Agregação de atleta por nome | Dois homônimos no mesmo elenco viravam um atleta com 47 jogos numa temporada de 38 | F2-04 |
| 13 | Taxa populacional estimada sobre a base inteira | Informação do futuro entrando no escore do passado | F3-01 |

Os defeitos 4 e 12 são o mesmo erro — identificar pessoa por nome — cometido em dois lugares
diferentes, um deles por mim durante esta sessão. O `registro_cbf` resolve ambos.

---

## 5. A suíte de testes

De 67 para 139 testes. O ponto não é a quantidade: é que **nenhum teste precisou ser reescrito
para acomodar números novos** quando a base mudou 14% de volume na F2-03. A suíte fixa
contratos e propriedades, não valores.

| Arquivo | Testes | O que trava |
| :--- | ---: | :--- |
| `test_anomaly_detection.py` | 16 | Especificação da fórmula, chave de junção, harmonização de minuto |
| `test_ground_truth_resolver.py` | 10 | Identidade dos 14 casos, com regressões contra os erros anteriores |
| `test_validacao_out_of_sample.py` | 9 | Ausência de vazamento no protocolo, intervalo de Wilson |
| `test_precisao_e_carga_alerta.py` | 11 | Teto aritmético da precisão@k, proibição de precisão absoluta |
| `test_parse_cbf.py` | 14 | Relação de atletas por temporada, 11 titulares por equipe |
| `test_cbf_delta.py` | 13 | União de schema, clube em expulsões, volume reprocessado |
| `test_score_pre_jogo.py` | 11 | Vazamento temporal, encolhimento, ressalva interpretativa |
| `test_perfis_de_acesso.py` | 15 | Recusa do trading, camadas de exposição, feed padrão seguro |
| demais | 40 | Suíte pré-existente |

Três testes merecem menção por serem guardas de honestidade, não de funcionamento:

* `test_nenhuma_tabela_reporta_precisao_absoluta` — falha se alguém publicar uma métrica que os
  dados não sustentam.
* `test_sensibilidade_out_of_sample_nao_supera_a_in_sample` — se superasse, o mais provável
  seria vazamento, não generalização.
* `test_feed_servido_por_padrao_e_o_de_menor_exposicao` — falha se nome de atleta voltar ao
  feed público.

---

## 6. O que continua aberto

### Bloqueia exposição a terceiros

1. **F4-02 — anonimização por camada.** A exposição nominal já publicada continua de pé: Tabela
   16, rankings do relatório 07 e o feed de elenco somam milhares de atletas identificados, a
   maioria nunca investigada. O controle criado na F4-03 protege as saídas novas; a varredura
   retroativa é esta tarefa. **O termo de uso não pode ser oposto a terceiros antes dela.**
2. **F4-01 — RIPD e base legal.** A minuta do termo descreve política de produto, não fundamento
   jurídico. Os pontos marcados com ⚠ dependem dela.

### Dívida de fonte de dados

3. **O ground truth precisa ser refeito.** De 14 incidentes, apenas 1 tem o evento confirmado na
   súmula. Enquanto não for reconstituído a partir dos autos do MP-GO, qualquer métrica contra
   esses casos tem a precisão que a fonte tem — e ela é baixa. Afeta sobretudo a F6-03.
4. **11 súmulas incompletas na origem**, listadas em `reports/tables/partidas_sem_escalacao.csv`.
   Faltam a primeira página, e com ela cabeçalho, clubes e rodada. Merecem redescarga.
5. **Ingestão da Série B 2024** (F2-03), com 5 partidas ingeridas contra as 380 esperadas. É o
   objeto original daquela tarefa, que esta sessão fechou apenas na parte herdada da F2-01.

### Decisões de produto

6. **Fonte de escalação para produção.** A F3-01 validou em modo retroativo, com a escalação da
   súmula, que só existe após a partida. Usar o escore genuinamente pré-jogo exige escolher
   entre provedor externo de escalação provável e elenco inscrito. Com o ganho medido de 2,4× a
   2,7×, a decisão tem base quantitativa.
7. **Segredo de pseudonimização.** Hoje tem valor de desenvolvimento embutido no código, para
   tornar os testes determinísticos. Em produção precisa vir do ambiente.

---

## 7. Como retomar

```bash
# Cadeia completa de regeneração, na ordem
python -m src.models.anomaly_detection
python -m src.models.integrity_classifier
python -m src.models.ground_truth_resolver
python -m src.analysis.comparacao_reconciliacao_score
python -m src.models.validacao_out_of_sample      # ~90 s
python -m src.analysis.precisao_e_carga_alerta
python -m src.analysis.escalacoes_e_minutos
python -m src.models.score_pre_jogo
python -m src.analysis.cobertura_motivo_cartao
python -m src.visualization.plot_anomalies
python -m src.pipeline.serve_product_feed
```

Relatórios técnicos: `reports/analysis/07_*.md` (triagem, reconciliação e carga operacional) e
`reports/analysis/08_*.md` (escore pré-jogo). Decisões numeradas em
`docs/decisoes_e_progresso.md`. Termo de uso em `docs/termo_de_uso_e_licenciamento.md`.

---

> Caso o seu projeto envolva dados pessoais ou dados pessoais sensíveis, comunique ao time de
> Segurança da Informação através do e-mail seginfo@gcb.com.br
