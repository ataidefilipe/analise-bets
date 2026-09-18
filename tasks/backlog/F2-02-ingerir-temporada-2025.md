# F2-02 — Ingerir a temporada 2025 (Séries A e B)

**Fase:** 2 — Ativo de dados
**Responsável sugerido:** Filipe Ataíde
**Tamanho:** P
**Depende de:** —
**Status:** Concluído (2026-09-18)

---

## Descrição

A base processada tem um buraco de uma temporada inteira. As temporadas presentes são:

* **Série A** (`data/processed/serie_a/partidas.csv`): 2003 a 2024 e **2026**.
* **Série B** (`data/processed/serie_b/partidas.csv`): 2022, 2023, 2024 e **2026**.

**2025 está inteiramente ausente nas duas séries.** O pipeline delta foi executado apenas
para 2024 e 2026.

Executar o pipeline delta para `ano=2025`, Séries A e B, e integrar o resultado às bases
canônicas.

## Objetivo

Eliminar a descontinuidade temporal da base, condição necessária para qualquer produto que
prometa série histórica contínua e para qualquer análise longitudinal que atravesse o
período.

## Contexto

A lacuna compromete três frentes simultaneamente:

1. **Produto.** Um cliente que consulta o histórico disciplinar de um atleta e recebe um
   vazio em 2025 não confia na base. Due diligence de contratação (F3-04) fica inviável para
   qualquer atleta cujo ano relevante seja 2025.
2. **Modelagem.** O score pré-jogo (F3-01) depende de perfil histórico recente do atleta.
   2025 é o ano mais próximo da temporada corrente e o mais informativo.
3. **Academia.** Qualquer extensão da janela econométrica além de 2024 precisa de 2025 para
   não gerar um gap na estrutura de painel.

A execução é barata: o pipeline delta já está operacional e comprovadamente funcional —
a última execução (16/09/2026) baixou 216 súmulas novas da Série A 2026 com detecção
incremental via HTTP HEAD, ETag e SHA-256, sem erros.

## Definition of Done

- [ ] `run_delta_pipeline.py` executado para `ano=2025`, séries A e B, com log de execução
      arquivado.
- [ ] Partidas, gols e cartões de 2025 presentes nas bases canônicas das duas séries.
- [ ] Contagens conferidas contra o esperado: 380 partidas na Série A, 380 na Série B.
- [ ] Súmulas indisponíveis (HTTP 404) listadas explicitamente, com o motivo, em vez de
      simplesmente ausentes.
- [ ] Motivo do cartão preenchido para 2025 nas duas séries (depende de F2-01 para a Série A;
      se F2-01 ainda não estiver concluída, registrar a pendência e reprocessar depois).
- [ ] Manifestos (`manifest_delta.json`, `manifest_processed.json`) atualizados.
- [ ] Feed de produto (`serve_product_feed.py`) regenerado incluindo 2025.
- [ ] Suíte `pytest` passando.

## Riscos e observações

* Se as súmulas de 2025 tiverem código de competição diferente do assumido pelo ingestor
  (a URL segue o padrão `conteudo.cbf.com.br/sumulas/<ano>/<codigo><n>se.pdf`), será
  necessário descobrir o código correto antes de rodar.
* Executar esta tarefa **antes** da F2-04 e da F3-01, que consomem a base completa.

---

## Registro de execução (2026-09-18)

### O que foi ingerido

| Série | Temporada | Súmulas | Partidas | Gols | Cartões |
| :---: | :---: | ---: | ---: | ---: | ---: |
| A | 2025 | 380/380 | 380 | 945 | 2.045 |
| B | 2025 | 380/380 | 380 | 826 | 2.087 |
| B | 2024 | 380/380 | 380 | 824 | 2.220 |

O padrão de URL de 2025 foi verificado antes da execução, em seis sondagens HTTP HEAD (partidas
1, 190 e 380 das duas séries): o código de competição continua 142 para a Série A e 242 para a
B. O risco previsto na tarefa não se materializou.

**Nenhuma súmula retornou 404.** Oito downloads da Série A falharam por erro transitório de
rede durante a rajada, foram identificados por diferença entre o conjunto esperado e o baixado,
e recuperados numa segunda passada — as partidas 365, 366, 370, 371, 372, 375, 376 e 378.

A Série B 2024 tinha 5 partidas de 380 na base, pendência que a F2-03 deixara aberta. Foi
ingerida junto, e a F2-03 está fechada.

### Estado final das bases

| Série | Temporadas completas | Partidas | Escalações |
| :---: | :--- | ---: | ---: |
| A | 2003–2025 (2026 em curso, 266) | 9.431 | 29.356 |
| B | 2022–2025 (2026 em curso, 269) | 1.789 | 78.634 |

Zero duplicatas na chave `(temporada, partida_id)`. O motivo do cartão (`motivo_completo`)
está preenchido para 2025 nas duas séries, sem pendência de reprocessamento.

### Três defeitos encontrados durante a execução

Nenhum estava no backlog. Todos afetavam resultados já publicados.

**1. Escalação sem `registro_cbf`, silenciosamente.** Quando o apelido vem vazio na súmula, a
coluna desaparece e os campos deslizam: o token lido como número de camisa passa a ser o
registro CBF da linha anterior — seis dígitos, que `isdigit()` aceita sem reclamar — e o atleta
entra na base sem identidade. O parser não tinha validação de alinhamento.

**2. O escore pré-jogo descartava esse atleta sem avisar.** `_acumulados_anteriores` agrupa por
`registro_cbf`, e o `groupby` do pandas descarta chave nula por padrão. A linha ficava sem
grupo, o acumulado saía `NaN` e o escore também.

**3. O teste de vazamento acusava esse `NaN` como vazamento temporal.** A comparação usava
`!=`, e `NaN != NaN` é sempre verdadeiro. A guarda mais importante da F3-01 reprovava por um
motivo que não é o que ela existe para detectar — e uma guarda acostumada a reprovar é uma
guarda que ninguém investiga quando o vazamento for real.

Os três se descobriram em cadeia: o defeito 1 só apareceu porque produziu o `NaN` do defeito 2,
que só apareceu porque disparou o falso positivo do defeito 3.

### Um quarto, criado e corrigido na mesma sessão

A primeira correção do defeito 1 validava o número de camisa como estando entre 1 e 99. Está
errado: o Ceará relacionou a camisa **100** na Série A 2025 e o Palmeiras a **188**. O guard
apagou esses atletas da relação, e o teste de consistência entre eventos e escalação pegou —
um gol atribuído a quem não constava da partida. O que separa camisa de registro não é a
magnitude, é o tamanho: camisa tem até três dígitos, registro tem seis ou sete.

Os dois defeitos originais vinham se anulando: a camisa errada na escalação casava com a camisa
errada no evento, e a junção fechava. Corrigir só um dos lados fez o outro aparecer.

### Efeito nos resultados publicados

A base do escore pré-jogo passou de 57.406 para 107.990 registros e de 111 para 210 rodadas
avaliadas. O escore, que perdia da linha de base em k = 1, agora a supera em todos os k:

| k | Ganho sobre o acaso (antes) | Ganho (agora) | Supera a base? |
| :---: | :---: | :---: | :---: |
| 1 | 2,73× | 2,37× | não → **sim** |
| 3 | 2,58× | 2,69× | sim |
| 5 | 2,41× | 2,80× | sim |
| 10 | 2,73× | 2,96× | sim |

Teste de vazamento: **0 divergências em 75.291 linhas**. O relatório 08 foi atualizado.

### Fora do escopo desta tarefa

A janela de modelagem da Fase 1 continua declarada em `anomaly_detection.py` como Série A
2015–2024 e Série B 2022–2023. **2025 está na base mas não entra nos modelos**, e nenhum
número da Fase 1 mudou. Estender a janela é decisão separada: mudaria todos os resultados
publicados, e merece ser tomada de propósito, não como efeito colateral de uma ingestão.

### Artefatos

* `logs/delta_2025.log`, `logs/delta_2025_retry.log`, `logs/delta_2024_b.log`
* `data/processed/delta_pipeline_last_run.json`
* Testes novos: `test_relacao_sem_apelido_nao_desloca_as_colunas`,
  `test_camisa_de_tres_digitos_nao_e_descartada`,
  `test_atleta_sem_registro_cbf_e_pontuado_e_nao_sai_NaN`,
  `test_vazamento_nao_acusa_divergencia_por_escore_ausente`
* Suíte: **153 testes passando** (eram 149).
