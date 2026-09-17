# F4-03 — Termo de uso e política de licenciamento

**Fase:** 4 — Governança
**Responsável sugerido:** Luan de Oliveira
**Tamanho:** P
**Depende de:** F4-01
**Status:** Minuta concluída (2026-09-16) — pendente de revisão jurídica

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

- [x] Termo de uso redigido, cobrindo: finalidades permitidas, vedações expressas,
      granularidade por perfil, proibição de redistribuição e consequências do descumprimento.
- [x] **Vedação expressa** ao uso do produto para precificação, definição de odds, ajuste de
      limites de mercado ou qualquer finalidade de exploração comercial de apostas.
- [x] Matriz de granularidade por segmento formalizada e vinculada tecnicamente às camadas da
      F4-02.
- [x] Cláusula de não-imputação: o cliente reconhece que o escore indica desvio estatístico e
      não constitui prova ou indício de manipulação.
- [x] Posição registrada sobre atender ou não o segmento de trading, com a justificativa — é
      decisão de posicionamento do projeto e precisa estar escrita.
- [x] Política de licenciamento da camada aberta definida (dado agregado, uso acadêmico e
      jornalístico).

## Riscos e observações

* A decisão sobre o segmento de trading deve ser tomada **conscientemente e documentada**, não
  deixada em aberto. É a diferença entre um produto de integridade e um fornecedor de sinal
  para apostas, e define o enquadramento ético de todo o trabalho.
* Vale antecipar que o segmento recusado é justamente o de maior disposição a pagar. A
  justificativa da recusa é parte do argumento de produto, não uma perda a esconder.


---

## Execução (2026-09-16)

Antecipada em relação à ordem do backlog. Razão: a F3-01 entregou uma saída com valor
comercial real e potencial de uso indevido em precificação, e publicá-la sem a restrição de
granularidade seria fornecer sinal de trading por omissão.

**Controle técnico** em `src/pipeline/perfis_de_acesso.py`. A matriz de granularidade é
executável: `operadora_trading` levanta `PerfilNaoAtendido` em tempo de execução, o perfil de
clube exige o elenco declarado, e as camadas aberta e pseudonimizada removem os
identificadores em vez de confiar em quem consome. Quinze testes travam o comportamento.

**Feeds segmentados.** O feed servido por padrão passou a ser o da camada aberta — agregado por
clube e partida, sem atleta. A camada identificada foi para `product_feed/restrito/`, com
`AVISO.md`. O banco SQLite recebe a camada pseudonimizada, com identificador HMAC estável.

**Minuta do termo** em `docs/termo_de_uso_e_licenciamento.md`, com a vedação expressa ao uso
para precificação, a cláusula de não-imputação e a posição registrada sobre o segmento de
trading. Os pontos que dependem da base legal estão marcados e remetem à F4-01.

## O que esta tarefa NÃO resolve

A exposição nominal **já publicada no repositório** continua de pé: Tabela 16, rankings
nominais do relatório 07 e o feed de elenco somam milhares de atletas identificados, a maioria
nunca investigada. O controle criado aqui protege as saídas novas; a varredura retroativa é a
**F4-02**, e o termo não pode ser oposto a terceiros antes dela.

Dois commits desta sessão agravaram o problema antes de mitigá-lo: o feed de elenco (F2-04) e o
de risco pré-jogo (F3-01) publicaram 3.945 e 6.445 atletas nominados. O segundo foi corrigido
aqui; o primeiro segue para a F4-02.
