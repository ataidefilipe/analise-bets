# F2-02 — Ingerir a temporada 2025 (Séries A e B)

**Fase:** 2 — Ativo de dados
**Responsável sugerido:** Filipe Ataíde
**Tamanho:** P
**Depende de:** —
**Status:** Backlog

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
