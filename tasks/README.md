# Tasks — Backlog de Transição para Produto

Este diretório organiza o trabalho de transição do projeto de **artigo acadêmico** para
**produto**, conforme redirecionamento acordado com o orientador.

## Origem

Este backlog deriva da análise de negócio em
[`docs/analise_negocio.md`](../docs/analise_negocio.md), que documenta o diagnóstico de
mercado, o inventário de ativos, a segmentação de clientes, as personas, as vantagens
competitivas e os riscos. **Ler aquele documento antes de pegar uma tarefa** — ele explica
por que cada uma existe.

## Estrutura

* `tasks/backlog/` — uma tarefa por arquivo, no formato `F<fase>-<seq>-<slug>.md`.
* Cada tarefa contém: **Descrição**, **Objetivo**, **Contexto**, **Definition of Done (DoD)**
  e, quando aplicável, **Riscos e Observações**.

## Fases

| Fase | Nome | Propósito |
| :---: | :--- | :--- |
| **1** | Credibilidade | Corrigir o que impede o projeto de ser demonstrado a cliente ou banca |
| **2** | Ativo de dados | Completar cobertura e recuperar o diferencial competitivo |
| **3** | Produto | Construir a camada pré-jogo e a interface de entrega |
| **4** | Governança | LGPD, anonimização e licenciamento de uso |
| **5** | Validação de mercado | Evidência de demanda junto às personas reais |
| **6** | Entregáveis | Materiais de banca e instrumentação de métricas |

## Índice

| ID | Tarefa | Fase | Resp. sugerido | Tam. | Depende de |
| :--- | :--- | :---: | :--- | :---: | :--- |
| F1-01 | Reconciliar pesos e subscore de pênalti entre código e documentação | 1 | Rebeka | P | — |
| F1-02 | Remover `score_bet` do índice de suspeição | 1 | Filipe | P | — |
| F1-03 | Validação out-of-sample do classificador de integridade | 1 | Lacê | M | F1-01, F1-02 |
| F1-04 | Publicar precisão e volume de alerta (Tabela 21) | 1 | Lacê | M | F1-03 |
| F2-01 | Migrar schema da Série A para carregar o motivo do cartão | 2 | Filipe | M | — |
| F2-02 | Ingerir a temporada 2025 (Séries A e B) | 2 | Filipe | P | — |
| F2-03 | Corrigir a ingestão parcial da Série B 2024 | 2 | Filipe | P | — |
| F2-04 | Extrair a relação de atletas (escalação) da súmula | 2 | Nickolas | M/G | F2-01 |
| F2-05 | Estender a tipologia de infrações a toda a base | 2 | Rebeka | P | F2-01, F2-02 |
| F3-01 | Score de risco pré-jogo por atleta escalado | 3 | Filipe | G | F2-04, F1-04 |
| F3-02 | Tela de fila de triagem da rodada | 3 | Rebeka | M | F1-04 |
| F3-03 | Dossiê de rodada em PDF | 3 | Rebeka | P | F3-02 |
| F3-04 | Consulta de due diligence por atleta | 3 | Nickolas | P | F4-02 |
| F4-01 | RIPD/DPIA e definição de base legal LGPD | 4 | Luan | M | — |
| F4-02 | Arquitetura de anonimização por camada | 4 | Luan | M | F4-01 |
| F4-03 | Termo de uso e política de licenciamento | 4 | Luan | P | F4-01 |
| F5-01 | Roteiro e execução de entrevistas com personas | 5 | Nickolas | M | — |
| F5-02 | Teste das três hipóteses críticas de produto | 5 | Nickolas | M | F5-01 |
| F5-03 | Dossiê de evidência de demanda | 5 | Nickolas | P | F5-02 |
| F6-01 | Documento de visão de produto | 6 | Filipe | M | — |
| F6-02 | Demo ao vivo da rodada 2026 | 6 | Filipe | M | F3-02, F4-02 |
| F6-03 | Reestruturação do white paper em dois braços | 6 | Luan + Nickolas | G | F1-04, F5-03 |
| F6-04 | Definição e instrumentação de métricas de produto | 6 | Lacê | M | F1-04 |

**Tamanho:** P = até meio dia · M = 1 a 3 dias · G = mais de 3 dias.

## Caminho crítico

```
F1-01 F1-02 ──► F1-03 ──► F1-04 ──┐
                                  ├──► F3-02 ──► F6-02
F2-01 F2-02 F2-03 ──► F2-04 ──► F3-01 ┘

F5-01 → F5-02 → F5-03   (paralelo, inicia imediatamente — gargalo de calendário)
F4-01 → F4-02 → F4-03   (paralelo; F4-02 trava F6-02 se houver nome de atleta)
```

## Convenção de status

Marcar no topo de cada arquivo: `Status: Backlog | Em andamento | Em revisão | Concluído`.
