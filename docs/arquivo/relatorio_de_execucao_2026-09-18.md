# Relatório de Execução — 18 de setembro de 2026

**Escopo:** F2-02 (ingestão da temporada 2025) e fechamento da F2-03 (Série B 2024).
**Suíte ao final:** 153 testes passando (eram 149 no início), nenhum ignorado.

---

## 1. O que esta sessão fez

Duas coisas, e a segunda não estava prevista.

A primeira foi eliminar o buraco de uma temporada inteira na base: **1.140 súmulas**
ingeridas, 380 partidas em cada uma das três lacunas (Série A 2025, Série B 2025, Série B
2024). A Série B passa a cobrir 2022 a 2025 integralmente.

A segunda foi encontrar **quatro defeitos**, três deles preexistentes e um criado durante a
própria correção. Nenhum estava no backlog. Um deles adulterava a guarda contra vazamento
temporal do escore pré-jogo, que é o controle técnico mais importante da Fase 3.

---

## 2. O resumo em uma tabela

| Antes desta sessão | Depois |
| :--- | :--- |
| 2025 inteiramente ausente nas duas séries | **380/380 partidas** em A e B |
| Série B 2024 com 5 partidas de 380 | **380/380** |
| Base do escore pré-jogo: 57.406 registros | **107.990** |
| Rodadas avaliadas no walk-forward: 111 | **210** |
| Escore pré-jogo perdia da linha de base em k = 1 | **Supera em todos os k** |
| Divergências evento × escalação: 8 | **0** |
| Escalações com `registro_cbf` ausente: 1 | **0** |

---

## 3. A ingestão

### 3.1 Verificação prévia do padrão de URL

A tarefa alertava que o código de competição poderia mudar de ano para ano. Antes de disparar
760 downloads, foram feitas seis sondagens HTTP HEAD — partidas 1, 190 e 380 de cada série:

```
A   1  HTTP 200  https://conteudo.cbf.com.br/sumulas/2025/1421se.pdf
A 190  HTTP 200  https://conteudo.cbf.com.br/sumulas/2025/142190se.pdf
A 380  HTTP 200  https://conteudo.cbf.com.br/sumulas/2025/142380se.pdf
B   1  HTTP 200  https://conteudo.cbf.com.br/sumulas/2025/2421se.pdf
B 190  HTTP 200  https://conteudo.cbf.com.br/sumulas/2025/242190se.pdf
B 380  HTTP 200  https://conteudo.cbf.com.br/sumulas/2025/242380se.pdf
```

Os códigos 142 (Série A) e 242 (Série B) continuam valendo. O risco não se materializou.

### 3.2 Resultado

| Série | Temporada | Súmulas | Partidas | Gols | Cartões |
| :---: | :---: | ---: | ---: | ---: | ---: |
| A | 2025 | 380/380 | 380 | 945 | 2.045 |
| B | 2025 | 380/380 | 380 | 826 | 2.087 |
| B | 2024 | 380/380 | 380 | 824 | 2.220 |

**Nenhuma súmula retornou 404.** Oito downloads da Série A falharam por erro transitório de
rede durante a rajada. Foram identificados por diferença entre o conjunto esperado e o baixado
— não pelo log, que apenas contava "8 erros" — e recuperados numa segunda passada: partidas
365, 366, 370, 371, 372, 375, 376 e 378.

### 3.3 Estado final das bases

| Série | Cobertura | Partidas | Cartões | Escalações |
| :---: | :--- | ---: | ---: | ---: |
| A | 2003–2025 completas; 2026 em curso (266) | 9.431 | 24.368 | 29.356 |
| B | 2022–2025 completas; 2026 em curso (269) | 1.789 | 9.880 | 78.634 |

Zero duplicatas na chave `(temporada, partida_id)`. O motivo do cartão (`motivo_completo`)
está preenchido para 2025 nas duas séries, sem pendência de reprocessamento.

Taxa de extração da relação de atletas por temporada: **98,4% a 99,3%**. As 23 partidas sem
relação decorrem de PDFs incompletos na origem, sem a primeira página, e estão listadas em
`reports/tables/partidas_sem_escalacao.csv`.

---

## 4. Os quatro defeitos

Os três primeiros se descobriram em cadeia. Cada um só ficou visível porque o seguinte falhou
— e o último deles falhou *errado*, acusando um problema que não era o dele.

### 4.1 Escalação gravada sem identidade

`src/cleaning/cbf_delta_processor.py`

Quando o apelido vem vazio na súmula, a coluna desaparece e todos os campos deslizam uma
posição. O parser ancorava no token de condição (`T`/`R`) e lia a camisa três posições antes —
que, no layout deslizado, é o **registro CBF da linha anterior**. Seis dígitos, que
`isdigit()` aceita sem reclamar.

O efeito: o atleta entrava na base com o registro no lugar da camisa e **sem `registro_cbf`
nenhum**. Como a identidade do atleta no projeto é o registro, e não o nome — decisão da F2-04,
tomada justamente para não fundir homônimos —, esse atleta ficava sem identidade.

Ocorreu na Série B 2024, partida 181 (Vila Nova). A linha na súmula, com o nome substituído,
era:

```
70 <nome completo> ... R 2198626
```

contra o layout normal, que tem apelido e marca de presença:

```
23 <apelido> ... <nome completo> R P 617642
```

O registro `617642` é do atleta da linha anterior — é exatamente ele que o parser gravava como
número de camisa do atleta seguinte.

**Correção.** Validação de alinhamento antes de aceitar a leitura, e tratamento da marca de
presença ausente. Se o campo lido como camisa não for plausível e o seguinte for, os campos são
deslocados de volta.

### 4.2 O escore pré-jogo descartava esse atleta em silêncio

`src/models/score_pre_jogo.py`

`_acumulados_anteriores` agrupa por `(serie, registro_cbf)`, e o `groupby` do pandas descarta
chave nula por padrão. A linha ficava **sem grupo**: o acumulado saía `NaN`, e o escore também.
Sem erro, sem aviso, sem entrada em log.

**Correção.** `dropna=False` no agrupamento e `fillna(0)` antes do acúmulo. Um atleta sem
histórico é pontuado apenas pelo prior populacional, que é a resposta correta para quem não tem
passado — não `NaN`.

### 4.3 A guarda contra vazamento acusava esse `NaN` como vazamento

`src/models/score_pre_jogo.py`

`teste_de_vazamento` corrompe todo o futuro a partir de um corte cronológico e exige que os
escores anteriores fiquem idênticos. A comparação era `(a != b).sum()`.

Em pandas, **`NaN != NaN` é sempre verdadeiro**. A única linha com escore ausente era contada
como divergência, e o teste reprovava:

```
linhas_comparadas  linhas_divergentes  aprovado
          75.294                    1    False
```

Este é o defeito mais sério dos quatro, e não por causa do impacto numérico — é uma linha em
75 mil. É porque a guarda reprovava por um motivo que não é o que ela existe para detectar. Uma
guarda acostumada a reprovar é uma guarda que ninguém investiga quando o vazamento for real.

**Correção.** Comparação ciente de `NaN`: duas ausências são iguais entre si.

### 4.4 O defeito que a própria correção criou

A primeira versão da validação de alinhamento definia camisa como um inteiro **entre 1 e 99**.
Está errado. O Ceará relacionou a camisa **100** na Série A 2025, e o Palmeiras a **188**:

```
100 <apelido> <nome completo> T P 459744
```

O guard apagou esses atletas da relação. O defeito foi pego pelo teste de consistência entre
eventos e escalação, que passou a apontar gols atribuídos a quem não constava da partida —
saiu de 1 para 8 divergências.

**Correção.** O que separa camisa de registro não é a magnitude, é o **tamanho do campo**:
camisa tem até três dígitos, registro tem seis ou sete.

### 4.5 Por que os dois primeiros ficaram tanto tempo invisíveis

Eles se anulavam. A camisa errada na escalação (`617642`) casava com a camisa errada no evento,
e a junção `(temporada, partida_id, clube_slug, num_camisa)` fechava normalmente. O teste de
consistência via 1 divergência e o limiar tolerava 5.

Corrigir **um** dos lados quebrou o equilíbrio e fez o outro aparecer. É a razão pela qual o
número de divergências subiu para 8 antes de cair para 0: o caminho de um estado consistente e
errado para um estado consistente e correto passa por um estado inconsistente.

---

## 5. Efeito nos resultados publicados

### 5.1 Escore pré-jogo (F3-01)

A base quase dobrou — de 57.406 para 107.990 registros de atleta × partida, e de 111 para 210
rodadas avaliadas no walk-forward.

| k | Ganho sobre o acaso (antes) | Agora | Supera a linha de base? |
| :---: | :---: | :---: | :---: |
| 1 | 2,73× | **2,37×** | não → **sim** |
| 3 | 2,58× | **2,69×** | sim |
| 5 | 2,41× | **2,80×** | sim |
| 10 | 2,73× | **2,96×** | sim |

A mudança de substância é k = 1: o escore perdia da linha de base ingênua (ranking por cartões
acumulados) e agora não perde mais. A vantagem cresce com k — de 0,4 ponto percentual em k = 1
para 3,3 em k = 10 —, que é o padrão que o desenho previa: o encolhimento bayesiano troca
precisão no topo absoluto, onde a amostra individual é pequena, por estabilidade ao longo da
lista.

Vale registrar o que isso **não** significa. A linha de base continua próxima, e o ganho sobre o
acaso mede atipicidade disciplinar — não conduta.

### 5.2 Teste de vazamento

| Linhas comparadas | Linhas divergentes | Resultado |
| :---: | :---: | :---: |
| 75.291 | **0** | Aprovado |

### 5.3 Um argumento do relatório 08 que precisou ser reescrito

A primeira versão argumentava que o embaralhamento da ordem temporal — o teste previsto na
tarefa — não serve como guarda, porque o desempenho **subia** ao embaralhar: destruir a
cronologia faz a janela "anterior" de cada atleta conter partidas futuras, o que dá informação
ao modelo em vez de tirar.

Com a base dobrada, o embaralhamento passou a degradar o desempenho em todos os k, e o teste
"passaria". Isso não o reabilita: o sinal apareceu porque a base cresceu, não porque o teste
melhorou. E as duas colunas nem são comparáveis — o embaralhamento muda quais rodadas têm
histórico suficiente, e avalia 310 rodadas contra 210 da cronologia real.

O embaralhamento segue publicado como diagnóstico. Quem decide é a corrupção determinística do
futuro.

### 5.4 O que não mudou, de propósito

A janela de modelagem da Fase 1 continua declarada em `src/models/anomaly_detection.py` como
**Série A 2015–2024 e Série B 2022–2023**. 2025 está na base e **fora dos modelos**. Nenhum
número da Fase 1 mudou nesta sessão.

Estender a janela mexeria em todos os resultados publicados — escores, tiers, percentis,
classificação de ML, validação contra o ground truth. Merece ser decidido de propósito, e não
acontecer como efeito colateral de uma ingestão de dados.

---

## 6. Governança

> **Nota sobre este próprio documento.** A primeira versão citava o nome dos três atletas
> envolvidos nos defeitos de parsing, para ilustrar o layout da súmula. Nenhum deles tem
> qualquer relação com investigação — a única particularidade é o layout do PDF em que
> aparecem. O teste `test_nenhum_atleta_sem_condenacao_nominado_em_camada_aberta` reprovou e
> os nomes foram substituídos por marcadores. O número de registro basta para auditar o caso.

A exportação dos artefatos foi reconferida depois da regeneração, com o mesmo critério da
F4-02: fatos esportivos que a CBF publica seguem nominados; **inferência que o projeto produz
sobre a pessoa, não**.

| Artefato | Atletas sem condenação nominados |
| :--- | :---: |
| `product_feed/risco_pre_jogo.json` | 0 |
| `integrity/score_pre_jogo.parquet` | 0 |
| `tabela_16_ranking_atletas_anomalos.csv` | 0 |
| `tabela_20_classificacao_atletas_ml.csv` | 0 |
| `tabela_23c_score_pre_jogo_ranking.csv` | 0 |

---

## 7. Súmulas brutas fora do versionamento

Decisão tomada nesta sessão: os PDFs de súmula **não são versionados**. São cerca de 2.400
arquivos e dezenas de megabytes, e o repositório não precisa deles para ser reproduzível.

`data/raw/cbf/manifest_delta.json` guarda, para cada arquivo, a URL de origem, o ETag, o
`Last-Modified` e o **SHA-256**. Para reconstituir o conjunto:

```bash
python -m src.pipeline.run_delta_pipeline --ano 2025 --series A,B
```

A detecção incremental compara o hash: arquivos já presentes e inalterados não são rebaixados.

> **Pendência.** 1.308 PDFs já estavam versionados de sessões anteriores e continuam no índice
> do Git. A regra nova só impede que os 1.140 novos entrem. Deixar os dois conjuntos em regimes
> diferentes é inconsistente, e removê-los do índice é uma decisão do responsável pelo projeto:
> afeta quem já clonou. Registrado aqui para ser decidido.

---

## 8. Testes

Quatro testes novos, todos de contrato, nenhum fixando valor calculado:

| Teste | O que protege |
| :--- | :--- |
| `test_relacao_sem_apelido_nao_desloca_as_colunas` | Defeito 4.1 |
| `test_camisa_de_tres_digitos_nao_e_descartada` | Defeito 4.4 |
| `test_atleta_sem_registro_cbf_e_pontuado_e_nao_sai_NaN` | Defeito 4.2 |
| `test_vazamento_nao_acusa_divergencia_por_escore_ausente` | Defeito 4.3 |

Suíte: **153 testes passando**, ante 149 no início da sessão.

---

## 9. O que continua aberto

Em ordem de gravidade, não de esforço:

1. **Ground truth da Operação Penalidade Máxima.** De 14 eventos, **1 foi confirmado** na
   súmula; 5 estão ausentes da base, 5 não são verificáveis e 2 divergem no minuto. Todo
   número de validação do projeto repousa sobre esses 14 casos. Exige fonte primária — autos,
   denúncia, decisões do STJD.
2. **F4-01 — RIPD e base legal.** Bloqueia qualquer exposição externa. Exige profissional
   jurídico.
3. **Histórico do Git.** As tabelas 16, 20 e 03 publicadas em commits anteriores continuam
   nominais. Decisão registrada em `docs/decisao_historico_git_exposicao_nominal.md`.
4. **F5-01 — entrevistas com personas.** Nenhuma evidência de demanda foi coletada.
5. **Extensão da janela de modelagem para 2025**, discutida em 5.4.
6. **F2-05** — tipologia de infrações estendida a toda a base, agora com 2025 disponível.
7. **23 súmulas incompletas na origem**, sem a primeira página.

> Caso o seu projeto envolva dados pessoais ou dados pessoais sensíveis, comunique ao time de
> Segurança da Informação através do e-mail seginfo@gcb.com.br
