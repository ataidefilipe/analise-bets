# 05 — Automação de alimentação

**Destrava:** etapa 6.
**Escopo:** protótipo / MVP.

A boa notícia desta etapa: **o pipeline já existe, é idempotente e está em uso.** O que falta
não é construí-lo, é operá-lo — agendamento, tratamento de falha, portões de qualidade e
monitoramento.

---

## 1. O que já está pronto

`src/pipeline/run_delta_pipeline.py` executa a esteira completa:

1. **Ingestão delta** — `HTTP HEAD` em cada súmula, comparando `ETag`, `Last-Modified` e
   tamanho contra `manifest_delta.json`. Baixa só o que é novo ou mudou, e grava o SHA-256.
2. **Parsing e upsert idempotente** — partidas, gols, cartões, escalações, substituições.
3. **Geração de feeds** — JSON por camada e banco do produto.

Reexecutar com os mesmos dados não duplica nada e não altera resultado. Isso foi verificado
nesta sessão: a temporada 2025 foi reprocessada sete vezes durante a correção de defeitos, sem
divergência.

### O que precisa ser acrescentado

| Item | Situação |
| :--- | :--- |
| Agendamento | Não existe — execução é manual |
| Recálculo dos escores | Passo separado hoje; precisa entrar na esteira |
| Portões de qualidade | Não existem |
| Notificação de falha | Não existe |
| Carga para Postgres | Hoje escreve Parquet, CSV e SQLite |

---

## 2. Cadência

**Uma execução diária, D+1.**

A CBF publica a súmula algumas horas após o apito final; jogos noturnos terminam por volta das
23h. Uma execução às **05:00 BRT** pega com folga tudo do dia anterior.

```
cron(0 8 * * ? *)   # 08:00 UTC = 05:00 BRT
```

Não há necessidade de execução intradiária. O produto é de triagem pré-jogo com base em
histórico, não de tempo real — e o perfil que precisaria de baixa latência
(`operadora_trading`) é justamente o que o projeto decidiu não atender.

### Janela de rodada

A escalação de uma partida só existe depois que a súmula sai, ou seja, **depois do jogo**. A
fila de triagem de uma rodada futura usa a escalação *da rodada anterior* como proxy do elenco
relacionado.

> **Limitação estrutural, não defeito.** A fonte de escalação provável — insumo de terceiro que
> permitiria triagem verdadeiramente pré-jogo — é decisão em aberto, registrada em
> [`reports/analysis/08`](../../reports/analysis/08_score_pre_jogo_por_atleta.md). Em produção,
> o único insumo que muda é a lista de quem entra em campo; o perfil histórico e o cálculo são
> idênticos. A etapa 6 deve deixar esse ponto de injeção isolado.

---

## 3. A esteira diária

| # | Passo | Comando | Tempo |
| :---: | :--- | :--- | ---: |
| 1 | Ingestão delta da temporada corrente | `run_delta_pipeline --ano <ano> --series A,B --skip-feed` | < 30 s |
| 2 | Minutos em campo | `python -m src.analysis.escalacoes_e_minutos` | ~20 s |
| 3 | Escore pré-jogo | `python -m src.models.score_pre_jogo` | ~90 s |
| 4 | Feeds e carga no Postgres | `python -m src.pipeline.serve_product_feed` | ~15 s |
| 5 | Portões de qualidade | ver §4 | < 5 s |

Sequencial. Falha em qualquer passo **interrompe a esteira** — não faz sentido recalcular
escores sobre uma ingestão parcial.

### Escopo da execução

Só a **temporada corrente**. Temporadas fechadas não mudam, e reprocessá-las diariamente
gastaria 3 minutos para produzir o mesmo resultado. Reprocessamento histórico é operação
manual, sob demanda.

---

## 4. Portões de qualidade

Verificações após a carga. **Falha bloqueia a publicação**: o feed anterior continua servindo,
que é melhor do que servir dado corrompido.

Os quatro primeiros correspondem a defeitos que já ocorreram de verdade.

| # | Portão | Regra | Defeito que já aconteceu |
| :---: | :--- | :--- | :--- |
| G1 | Chave única de partida | Zero duplicatas em `(serie, temporada, partida_id)` | 5 partidas fantasma ao ingerir súmulas numa temporada já completa |
| G2 | Identidade de atleta | Zero linhas de `escalacoes` com `registro_cbf` nulo | Súmula com apelido vazio deslocava colunas |
| G3 | Número de camisa | Todo `num_camisa` com no máximo 3 dígitos | Registro CBF gravado no lugar da camisa |
| G4 | Consistência evento × escalação | ≤ 5 atletas com cartão ou gol fora da relação da partida | Camisa errada nos dois lados se anulava |
| G5 | Escore sem nulo | Zero `score_pre_jogo` nulo | `groupby` descartava chave nula e produzia NaN silencioso |
| G6 | Volume plausível | Cartões por partida entre 2 e 12 na média da rodada | — |
| G7 | Exposição nominal | Zero atletas sem condenação nominados em artefato de camada aberta | Ranking nominal publicado |

G1 a G5 e G7 já existem como testes sobre a base real em `tests/` e podem ser reaproveitados
diretamente — a etapa 6 precisa executá-los, não reescrevê-los. **G6 é o único que não tem
teste** e precisa ser implementado do zero.

**G7 é o portão de governança** e não deve ser afrouxado: se falhar, algum ponto de exportação
voltou a nominar atleta sem condenação.

---

## 5. Falhas e recuperação

### Taxonomia

| Falha | Frequência observada | Tratamento |
| :--- | :--- | :--- |
| Erro transitório de rede no download | **Ocorreu: 8 em 760** | Repetir até 3 vezes com espera progressiva. Se persistir, seguir e reportar as faltantes |
| Súmula ainda não publicada (404) | Esperado | **Não é falha.** Registrar como pendente; a execução do dia seguinte tenta de novo |
| PDF incompleto na origem | 23 partidas | Registrar em `partidas_sem_escalacao`. Não bloqueia |
| Mudança de layout da súmula | Não observada, mas é o risco real | G2/G3/G4 detectam. **Bloqueia** |
| Mudança no código de competição na URL | Não ocorreu em 2025 | Ingestão retorna zero arquivos. **Bloqueia** |
| Falha de carga no banco | — | **Bloqueia.** Transação, sem carga parcial |

### A falha que importa

**Erro transitório de rede não pode ser silencioso.** Na execução desta sessão, 8 de 760
downloads falharam e o log registrou apenas `8 erros` — sem dizer quais. Foram descobertos por
comparação entre o conjunto esperado e o obtido.

Requisito: ao final da ingestão, comparar o conjunto de partidas esperado com o obtido e
**listar explicitamente as faltantes**, com o motivo. Um contador agregado não serve.

### Notificação [MVP]

SNS → e-mail, em dois casos: esteira interrompida por falha, ou portão de qualidade reprovado.
O e-mail cita o passo, a mensagem e o link do log no CloudWatch.

Sem alarme de silêncio no MVP — se a execução simplesmente não acontecer, ninguém é avisado.
Mitigação barata: alarme do CloudWatch se não houver invocação da task em 26 horas.

---

## 6. Observabilidade [MVP]

Toda execução grava um registro em `execucoes_pipeline`:

| Coluna | |
| :--- | :--- |
| `id`, `iniciado_em`, `terminado_em`, `duracao_s` | |
| `temporada`, `series` | |
| `sumulas_novas`, `sumulas_atualizadas`, `sumulas_pendentes`, `sumulas_com_erro` | |
| `partidas_upserted`, `cartoes_upserted`, `gols_upserted` | |
| `portoes_aprovados` (bool), `portao_reprovado` (text) | |
| `sucesso` (bool), `erro` (text) | |

O arquivo `data/processed/delta_pipeline_last_run.json` já produz quase tudo isso — basta
persistir em tabela em vez de sobrescrever um arquivo.

---

## 7. Reprocessamento histórico

Operação manual, fora da esteira diária. Necessária quando um defeito de parsing é corrigido —
aconteceu duas vezes nesta sessão.

```bash
for spec in "A 2025" "B 2022" "B 2023" "B 2024" "B 2025"; do
  set -- $spec
  python -m src.pipeline.run_delta_pipeline --ano $2 --series $1 --skip-ingest --skip-feed
done
python -m src.analysis.escalacoes_e_minutos
python -m src.models.score_pre_jogo
python -m src.pipeline.serve_product_feed
```

`--skip-ingest` reaproveita os PDFs já em S3, sem rebaixar. O reprocessamento completo das
temporadas com súmula leva **menos de 5 minutos**.

> **Requisito para a etapa 6:** este comando precisa ser executável como task pontual no
> Fargate, com parâmetros, e não só na máquina de alguém.

---

## 8. Fora do MVP

* Execução intradiária ou em tempo real.
* Reprocessamento automático ao detectar mudança de layout.
* Versionamento de base com possibilidade de voltar a um estado anterior.
* Integração com fonte de escalação provável — o insumo que tornaria a triagem verdadeiramente
  pré-jogo.

> Caso o seu projeto envolva dados pessoais ou dados pessoais sensíveis, comunique ao time de
> Segurança da Informação através do e-mail seginfo@gcb.com.br
