# F4-02 — Arquitetura de anonimização por camada

**Fase:** 4 — Governança
**Responsável sugerido:** Luan de Oliveira
**Tamanho:** M
**Depende de:** F4-01
**Status:** Concluído (2026-09-18) — exceto a decisão sobre o histórico do Git, que é do responsável pelo projeto

---

## Descrição

Implementar, no código e nas bases, uma separação estrita entre camadas de exposição de
dados de atletas:

| Camada | Conteúdo | Destino |
| :--- | :--- | :--- |
| **Aberta** | Agregados por clube, rodada, temporada e categoria de infração. Sem identificação individual | Repositório público, white paper, artigo, imprensa |
| **Pseudonimizada** | Perfil individual sob identificador estável, sem nome | Demonstrações, validação metodológica, banca |
| **Identificada** | Nome do atleta | Apenas ambiente contratado, com finalidade declarada e log de acesso |

A exceção é o conjunto de casos judicializados com condenação transitada em julgado, que
podem ser nominados nas três camadas por serem fato público.

## Objetivo

Impedir que o produto ou qualquer entregável acadêmico exponha nominalmente atletas não
condenados, sem perder capacidade analítica ou demonstrativa.

## Contexto

O risco é concreto e já materializado no repositório. A Tabela 16 e o relatório 07 exibem um
ranking nominal de "atletas anômalos" que inclui pessoas **nunca investigadas** — o ranking
histórico de atipicidade tem nomes no topo que não têm qualquer relação com a Operação
Penalidade Máxima. Publicar ou vender essa lista é exposição direta a ação por dano moral.

A distinção que a arquitetura precisa preservar:

* **Condenado com trânsito em julgado** — fato público, pode ser nominado. É o caso dos
  atletas da Operação Penalidade Máxima já julgados.
* **Investigado sem condenação** — não pode ser nominado fora de ambiente restrito.
* **Nunca investigado, apenas estatisticamente atípico** — este é o grupo mais exposto e o
  mais numeroso. Não pode ser nominado em nenhuma camada aberta, sob nenhuma circunstância.

O próprio relatório 07 já estabelece a diretriz de presunção de inocência e reserva de
jurisdição. Esta tarefa converte a diretriz declarada em **controle técnico efetivo**.

## Definition of Done

- [x] As três camadas implementadas no pipeline, com a camada de saída sendo parâmetro
      explícito de cada função de exportação.
- [x] Mapeamento pseudônimo ↔ nome armazenado separadamente das bases analíticas, com acesso
      controlado.
- [x] Marcação formal do status jurídico de cada atleta citado: condenado com trânsito em
      julgado, investigado sem condenação, ou sem qualquer registro.
- [x] **Revisão retroativa de todos os artefatos já existentes** no repositório — tabelas 16,
      17 e 20, relatório 07, white paper, notebooks e figuras — reclassificando conforme a
      camada adequada.
- [x] Teste automatizado que falha se um nome de atleta sem condenação transitada em julgado
      aparecer em artefato destinado à camada aberta.
- [x] Decisão registrada sobre o repositório: se o histórico do Git contém nomes que não
      deveriam estar em camada aberta, definir e executar o tratamento.
- [x] Suíte `pytest` passando.

## Riscos e observações

* A revisão retroativa é a parte mais trabalhosa e a mais importante. O dado já está
  publicado no repositório; a correção só é efetiva se alcançar o que já existe.
* Esta tarefa bloqueia a F3-04 e condiciona a F3-02, a F3-03 e a F6-02. Priorizar dentro da
  Fase 4.


---

## Execução (2026-09-18)

**Status jurídico formalizado.** Os 10 atletas do ground truth têm sanção do STJD registrada e
são classificados como `condenado` — fato público, nomináveis em qualquer camada. Todo o resto
da base é `sem_registro`. Publicado em `reports/tables/status_juridico_atletas.csv`.

**Camada como parâmetro explícito.** `src/pipeline/camadas_de_exposicao.py` aplica a camada a
qualquer quadro, e os pontos de exportação das tabelas nominais passaram a chamá-la. O
pseudônimo é estável entre artefatos, de modo que o mesmo atleta continua rastreável na análise
sem estar nominado.

**Varredura retroativa.** `src/analysis/varredura_exposicao_nominal.py` encontrou **2.897
ocorrências em 8 arquivos**. Tratamento:

| Artefato | Ocorrências | Tratamento |
| :--- | ---: | :--- |
| Tabela 23c (ranking pré-jogo) | 2.786 | Regenerada pseudonimizada |
| Tabela 20 (classificação ML) | 42 | Regenerada pseudonimizada |
| Tabela 16 (ranking de atipicidade) | 38 | Regenerada pseudonimizada |
| Tabela 03 (outliers do 1º tempo) | 17 | Regenerada pseudonimizada |
| Relatório 07 | 9 | Editado — inclui a tabela de correções de identidade, o caso mais delicado: são atletas nomeados justamente por terem sido confundidos com investigados |
| `02_eda_profunda_serie_a.md`, `data_dictionary.md`, relatório de execução | 5 | Editados |

Varredura final: **zero ocorrências**.

**Mapa de reidentificação** em `data/restrito/mapa_pseudonimos.csv`, fora do versionamento —
versioná-lo anularia a pseudonimização, já que qualquer clone traria a chave junto.

**Teste de guarda.** `test_nenhum_atleta_sem_condenacao_nominado_em_camada_aberta` reprova a
suíte se um nome reaparecer. Se falhar após alteração legítima, a saída é aplicar a camada no
ponto de exportação que voltou a nominar — não afrouxar o teste.

## Pendência: o histórico do Git

O repositório está publicado no GitHub e os commits anteriores continuam com os nomes: 40
atletas nunca investigados figuram na Tabela 16 publicada. Reescrever histórico publicado é
destrutivo e irreversível para terceiros, e por isso **não foi executado**. As opções, os
custos e a recomendação estão em
[`docs/decisao_historico_git_exposicao_nominal.md`](../../docs/decisao_historico_git_exposicao_nominal.md).
