# F2-04 — Extrair a relação de atletas (escalação) da súmula

**Fase:** 2 — Ativo de dados
**Responsável sugerido:** Nickolas Gomes
**Tamanho:** M/G
**Depende de:** F2-01
**Status:** Concluído (2026-09-16)

---

## Descrição

O parser de súmulas extrai hoje apenas eventos: gols, cartões e substituições. Não extrai a
**relação de atletas** de cada partida — titulares, reservas, número de camisa, posição e
capitão — que consta da súmula oficial da CBF.

Implementar a extração e criar a tabela relacional `escalacoes` nas bases das duas séries.

## Objetivo

Habilitar a camada pré-jogo do produto, que exige saber quais atletas entram em campo antes
da partida começar.

## Contexto

Esta é a tarefa que destrava o item de maior valor comercial do projeto (F3-01). Sem
escalação, o sistema só consegue responder depois do jogo — e detecção ex-post não é o que o
cliente compra, porque os mercados de cartões e faltas já liquidaram no apito final.

O projeto tem evidência direta de que o perfil de risco individual é **persistente**, e não
ruído de uma partida: Nino Paraíba aparece no topo absoluto do ranking histórico de
atipicidade em duas temporadas e clubes distintos — 2020 pelo Bahia (percentil 100,0) e 2022
pelo Ceará (percentil 99,67), com 70% a 85% dos cartões concentrados no 1º tempo. Traço
persistente é justamente o que permite antecipar risco antes do jogo.

Com escalação disponível, o produto passa a responder à pergunta que as personas de
compliance de clube e de trading realmente fazem: dos 22 que vão entrar em campo hoje,
quais carregam perfil atípico?

**Nota de escopo:** a súmula oficial só fica disponível após a partida. Para uso
genuinamente pré-jogo será necessária uma fonte de escalação provável, a ser definida na
F3-01. Esta tarefa constrói a **base histórica de participação** — sem ela não há como
calcular o perfil do atleta nem validar o modelo retroativamente.

## Definition of Done

- [x] Parser estendido para extrair a relação de atletas de cada súmula: nome, slug, número,
      posição, condição (titular / reserva), clube e indicação de capitão quando disponível.
- [x] Tabela `escalacoes` materializada em `data/processed/serie_a/` e `serie_b/`, em CSV e
      Parquet, com chave `partida_id` + `atleta_slug`.
- [x] Taxa de extração bem-sucedida reportada por temporada; súmulas com layout não
      reconhecido listadas explicitamente.
- [x] Consistência validada: todo atleta que recebeu cartão ou marcou gol numa partida deve
      constar da escalação daquela partida. Divergências listadas.
- [x] Métrica de **minutos em campo por atleta-temporada** derivada de escalação mais
      substituições — insumo direto para o denominador do escore individual.
- [x] `docs/data_dictionary.md` atualizado com a tabela nova.
- [x] Feed de produto expondo a tabela nova.
- [x] Testes unitários em `tests/test_parse_cbf.py` cobrindo ao menos uma súmula de cada
      temporada disponível.
- [x] Suíte `pytest` passando.

## Riscos e observações

* **Principal risco de esforço do backlog.** O layout da súmula pode variar entre temporadas
  e séries, exigindo tokenização específica por período. Se o custo estourar, a mitigação é
  restringir o escopo a 2022 em diante (período com súmula eletrônica consistente) e degradar
  a F3-01 para nível de partida em vez de atleta.
* A métrica de minutos em campo corrige uma limitação conhecida do `ATHLETE_ANOMALY_SCORE`
  atual, que usa minutagem nominal do cartão como proxy em vez de exposição real em campo.


---

## Execução (2026-09-16)

**Cobertura.** 57.406 registros de atleta-partida extraídos de 1.297 súmulas: Série A 2026 e
Série B 2022, 2023, 2024 e 2026. Taxa de extração de 99,2%; as 11 partidas sem relação estão
listadas em `reports/tables/partidas_sem_escalacao.csv` e decorrem de **PDFs incompletos na
origem** (falta a primeira página), não de layout desconhecido — nessas súmulas também faltam
cabeçalho, clubes e rodada.

**Consistência.** De cerca de 30 mil eventos, apenas **1** atleta com cartão não consta da
relação da sua partida (Kauan Richard, Ituano 2023). As demais 88 divergências estão nas 11
súmulas incompletas.

**Achado de identidade.** A súmula trunca o nome completo em ~40% dos registros, e apelidos se
repetem dentro do mesmo elenco — o Juventude de 2026 tem dois "Marcos Paulo", de camisas 10 e
47. O `registro_cbf` está presente em **100%** dos registros e passa a ser o identificador
canônico de atleta do projeto. É a saída estrutural para o problema que a F1-03 encontrou no
ground truth.

**Correção adjacente.** O split do nome nas expulsões usava a última ocorrência de `" - "`, o
que quebrava em clubes cujo nome a contém (`Gremio Novorizontino - SAF/SP` virava clube `Saf`).
Passou a usar a primeira ocorrência.

**Escopo não coberto.** A súmula só fica disponível depois da partida. Esta tarefa entrega a
base histórica de participação; a fonte de escalação provável, necessária para uso
genuinamente pré-jogo, segue como decisão da F3-01.
