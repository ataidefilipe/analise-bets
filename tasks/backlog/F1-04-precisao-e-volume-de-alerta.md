# F1-04 — Publicar precisão e volume de alerta (Tabela 21)

**Fase:** 1 — Credibilidade
**Responsável sugerido:** Lacê Rene
**Tamanho:** M
**Depende de:** F1-03
**Status:** Backlog

---

## Descrição

Todo o sistema de triagem é avaliado hoje por **sensibilidade** (quantos casos reais foram
capturados). Não existe nenhuma métrica de **precisão** ou de **carga operacional**
(quantos alertas são gerados para cada caso real).

Produzir a Tabela 21 com as métricas que o cliente efetivamente usa para decidir compra.

## Objetivo

Substituir a métrica de pesquisa (sensibilidade) pela métrica de produto (precisão e volume
de alerta por rodada), e usar o resultado para reposicionar o sistema de "detector de
fraude" para "priorizador de fila de auditoria".

## Contexto

O tier de Alto Risco do classificador marca **8,93%** das partidas das Séries A e B. Sobre
os 4.559 jogos da base harmonizada, isso corresponde a aproximadamente **400 partidas
sinalizadas** para 14 incidentes conhecidos. A precisão aparente é inferior a 4% — e mesmo
esse número é indeterminado, porque não se sabe quantos dos demais sinalizados são casos
reais nunca investigados.

Para as personas do produto, este é o número que decide:

* **Analista de federação / STJD:** quantas revisões de vídeo por rodada o alerta gera. Três
  é acionável; quarenta não é.
* **Compliance de clube:** quantos atletas do elenco aparecem sinalizados numa temporada.
* **Integrity de operadora:** quantos registros precisam de tratamento documental.

A precisão baixa não inviabiliza o produto — **inviabiliza o posicionamento atual**. Um
priorizador de fila é avaliado por *precisão no topo da lista* (precisão@k), não por
precisão global. Reposicionar para precisão@3 ou precisão@5 por rodada é tecnicamente
honesto e comercialmente mais forte.

## Definition of Done

- [ ] Tabela 21 (`reports/tables/tabela_21_precisao_e_carga_de_alerta.csv`) contendo, por
      tier de prioridade e por nível (partida e atleta):
      número absoluto de sinalizados, percentual da base, alertas por rodada, alertas por
      caso conhecido do ground truth.
- [ ] Precisão@k calculada para k = 1, 3, 5 e 10 por rodada, nos casos em que há ground
      truth disponível na rodada.
- [ ] Declaração explícita, no relatório 07, da **limitação de precisão**: o ground truth
      cobre uma operação, uma temporada, e não permite estimar falsos positivos reais.
- [ ] Reposicionamento textual do sistema no relatório 07 e no white paper: de "detecção"
      para "priorização de escrutínio", com a justificativa métrica.
- [ ] Figura nova mostrando o trade-off sensibilidade × volume de alerta conforme o limiar
      de corte varia (curva de carga operacional).
- [ ] Recomendação de limiar operacional por persona, derivada da curva.
- [ ] Suíte `pytest` passando.

## Riscos e observações

* Sem falsos positivos rotulados, **precisão absoluta não é estimável**. O entregável
  honesto é a *carga de alerta* e a *precisão@k sobre o ground truth disponível*, com a
  limitação declarada. Não inventar um denominador.
* Esta tarefa alimenta diretamente a F3-02 (a tela precisa de um limiar definido) e a F6-04
  (métricas de produto).
