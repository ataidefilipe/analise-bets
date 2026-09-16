# F4-03 — Termo de uso e política de licenciamento

**Fase:** 4 — Governança
**Responsável sugerido:** Luan de Oliveira
**Tamanho:** P
**Depende de:** F4-01
**Status:** Backlog

---

## Descrição

Redigir o termo de uso do produto e a política de licenciamento por segmento de cliente,
definindo quem recebe qual nível de granularidade e para qual finalidade.

## Objetivo

Resolver, por instrumento contratual e por desenho de produto, o conflito de interesse
estrutural entre uso de integridade e uso de precificação de mercado.

## Contexto

O mesmo artefato serve a dois propósitos opostos. Um escore que indica "este atleta concentra
70% dos cartões no 1º tempo" é, ao mesmo tempo:

* um **sinal de integridade**, útil para priorizar auditoria; e
* um **sinal de trading**, útil para precificar micro-mercados de cartão.

Vendido à mesa de precificação de uma operadora, o produto deixa de proteger o esporte e
passa a fornecer vantagem competitiva nos exatos mercados que o próprio white paper
identifica como vetor de vulnerabilidade à manipulação. É a contradição mais séria do projeto
e a pergunta mais provável de uma banca.

A resposta não é recusar o segmento — é **restringir granularidade por finalidade**:

| Segmento | Granularidade concedida | Finalidade permitida |
| :--- | :--- | :--- |
| Federação, STJD, órgão de investigação | Partida e atleta, identificada | Auditoria e instrução |
| Clube | Atleta, restrita ao próprio elenco e a alvos declarados de contratação | Compliance interno e due diligence |
| Operadora — integrity/compliance | Partida, agregada | Monitoramento regulatório e registro de diligência |
| Operadora — trading | **Não atendido** | — |
| Imprensa e academia | Agregada, camada aberta | Divulgação e pesquisa |

A restrição precisa ser simultaneamente **contratual** (termo de uso) e **técnica** (a camada
da F4-02 aplicada por perfil de cliente). Cláusula sem controle técnico não se sustenta.

## Definition of Done

- [ ] Termo de uso redigido, cobrindo: finalidades permitidas, vedações expressas,
      granularidade por perfil, proibição de redistribuição e consequências do descumprimento.
- [ ] **Vedação expressa** ao uso do produto para precificação, definição de odds, ajuste de
      limites de mercado ou qualquer finalidade de exploração comercial de apostas.
- [ ] Matriz de granularidade por segmento formalizada e vinculada tecnicamente às camadas da
      F4-02.
- [ ] Cláusula de não-imputação: o cliente reconhece que o escore indica desvio estatístico e
      não constitui prova ou indício de manipulação.
- [ ] Posição registrada sobre atender ou não o segmento de trading, com a justificativa — é
      decisão de posicionamento do projeto e precisa estar escrita.
- [ ] Política de licenciamento da camada aberta definida (dado agregado, uso acadêmico e
      jornalístico).

## Riscos e observações

* A decisão sobre o segmento de trading deve ser tomada **conscientemente e documentada**, não
  deixada em aberto. É a diferença entre um produto de integridade e um fornecedor de sinal
  para apostas, e define o enquadramento ético de todo o trabalho.
* Vale antecipar que o segmento recusado é justamente o de maior disposição a pagar. A
  justificativa da recusa é parte do argumento de produto, não uma perda a esconder.
