# F4-02 — Arquitetura de anonimização por camada

**Fase:** 4 — Governança
**Responsável sugerido:** Luan de Oliveira
**Tamanho:** M
**Depende de:** F4-01
**Status:** Backlog

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

- [ ] As três camadas implementadas no pipeline, com a camada de saída sendo parâmetro
      explícito de cada função de exportação.
- [ ] Mapeamento pseudônimo ↔ nome armazenado separadamente das bases analíticas, com acesso
      controlado.
- [ ] Marcação formal do status jurídico de cada atleta citado: condenado com trânsito em
      julgado, investigado sem condenação, ou sem qualquer registro.
- [ ] **Revisão retroativa de todos os artefatos já existentes** no repositório — tabelas 16,
      17 e 20, relatório 07, white paper, notebooks e figuras — reclassificando conforme a
      camada adequada.
- [ ] Teste automatizado que falha se um nome de atleta sem condenação transitada em julgado
      aparecer em artefato destinado à camada aberta.
- [ ] Decisão registrada sobre o repositório: se o histórico do Git contém nomes que não
      deveriam estar em camada aberta, definir e executar o tratamento.
- [ ] Suíte `pytest` passando.

## Riscos e observações

* A revisão retroativa é a parte mais trabalhosa e a mais importante. O dado já está
  publicado no repositório; a correção só é efetiva se alcançar o que já existe.
* Esta tarefa bloqueia a F3-04 e condiciona a F3-02, a F3-03 e a F6-02. Priorizar dentro da
  Fase 4.
