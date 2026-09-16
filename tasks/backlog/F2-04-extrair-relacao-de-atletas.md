# F2-04 — Extrair a relação de atletas (escalação) da súmula

**Fase:** 2 — Ativo de dados
**Responsável sugerido:** Nickolas Gomes
**Tamanho:** M/G
**Depende de:** F2-01
**Status:** Backlog

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

- [ ] Parser estendido para extrair a relação de atletas de cada súmula: nome, slug, número,
      posição, condição (titular / reserva), clube e indicação de capitão quando disponível.
- [ ] Tabela `escalacoes` materializada em `data/processed/serie_a/` e `serie_b/`, em CSV e
      Parquet, com chave `partida_id` + `atleta_slug`.
- [ ] Taxa de extração bem-sucedida reportada por temporada; súmulas com layout não
      reconhecido listadas explicitamente.
- [ ] Consistência validada: todo atleta que recebeu cartão ou marcou gol numa partida deve
      constar da escalação daquela partida. Divergências listadas.
- [ ] Métrica de **minutos em campo por atleta-temporada** derivada de escalação mais
      substituições — insumo direto para o denominador do escore individual.
- [ ] `docs/data_dictionary.md` atualizado com a tabela nova.
- [ ] Feed de produto expondo a tabela nova.
- [ ] Testes unitários em `tests/test_parse_cbf.py` cobrindo ao menos uma súmula de cada
      temporada disponível.
- [ ] Suíte `pytest` passando.

## Riscos e observações

* **Principal risco de esforço do backlog.** O layout da súmula pode variar entre temporadas
  e séries, exigindo tokenização específica por período. Se o custo estourar, a mitigação é
  restringir o escopo a 2022 em diante (período com súmula eletrônica consistente) e degradar
  a F3-01 para nível de partida em vez de atleta.
* A métrica de minutos em campo corrige uma limitação conhecida do `ATHLETE_ANOMALY_SCORE`
  atual, que usa minutagem nominal do cartão como proxy em vez de exposição real em campo.
