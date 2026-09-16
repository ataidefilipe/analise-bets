# F3-03 — Dossiê de rodada em PDF

**Fase:** 3 — Produto
**Responsável sugerido:** Rebeka Lemos
**Tamanho:** P
**Depende de:** F3-02
**Status:** Backlog

---

## Descrição

Gerar automaticamente, a cada rodada processada, um documento PDF com a fila de triagem, a
memória de cálculo de cada item sinalizado e o registro de proveniência dos dados.

## Objetivo

Entregar o produto no formato que as personas institucionais efetivamente consomem e
arquivam, e produzir um artefato com valor probatório de diligência.

## Contexto

As três personas institucionais do produto consomem documento, não interface:

* **Analista de federação / STJD** — precisa anexar a peça que fundamenta a abertura ou o
  arquivamento de um procedimento.
* **Compliance de clube** — arquiva o relatório semanal como evidência de monitoramento.
* **Integrity officer de operadora** — precisa demonstrar diligência ao regulador. O valor
  aqui está menos na predição e mais no **registro datado e auditável** de que a partida foi
  monitorada.

Para essa última persona, o PDF carimbado com data, fonte oficial e hash de integridade é
literalmente o produto. É o item de backlog com a relação valor/esforço mais alta de toda a
Fase 3, porque reaproveita integralmente o que a F3-02 já produz.

## Definition of Done

- [ ] Geração automática do PDF ao final da execução do pipeline delta, sem intervenção
      manual.
- [ ] Conteúdo: cabeçalho com rodada, data de geração e versão do modelo; fila priorizada;
      memória de cálculo por item; tabela de proveniência com nome do arquivo de súmula,
      hash SHA-256 e data de download.
- [ ] Aviso de interpretação (desvio estatístico, não acusação) em página própria e no rodapé
      de cada página.
- [ ] Tratamento de nomes conforme a F4-02.
- [ ] Versionamento do documento: dois dossiês da mesma rodada gerados em datas diferentes
      devem ser distinguíveis e rastreáveis.
- [ ] Um dossiê de exemplo gerado sobre uma rodada real de 2026 e arquivado em `reports/`.
- [ ] Teste automatizado verificando que o PDF é gerado e contém as seções obrigatórias.

## Riscos e observações

* O documento pode circular fora do controle da equipe. O aviso de interpretação e a política
  de nomes não são formalidade — são a proteção jurídica do projeto e dos atletas citados.
