# F3-04 — Consulta de due diligence por atleta

**Fase:** 3 — Produto
**Responsável sugerido:** Nickolas Gomes
**Tamanho:** P
**Depende de:** F4-02
**Status:** Backlog

---

## Descrição

Construir a consulta individual: dado um atleta, retornar seu histórico disciplinar completo
e seu perfil de atipicidade ao longo das temporadas disponíveis — distribuição dos cartões
por período do jogo, minutagem, tipologia das infrações e posição percentil frente à
distribuição da liga em cada temporada.

## Objetivo

Atender ao caso de uso de maior disposição a pagar identificado no ICP primário: a avaliação
de um atleta **antes da contratação**.

## Contexto

Na segmentação de clientes, o clube SAF é o ICP primário, e a dor mais concreta que ele
descreve não é monitorar o elenco atual — é **não contratar um problema**. Um clube que
contrata um atleta com histórico de atipicidade e depois enfrenta um caso público assume
custo esportivo, financeiro e reputacional simultâneos.

É também o caso de uso com ciclo de venda mais curto, porque é pontual, tem gatilho claro
(janela de transferências) e não exige assinatura recorrente para gerar a primeira receita.

A cobertura da Série B é decisiva aqui: boa parte das contratações de clubes da Série A vem
da Série B, exatamente a divisão com menor cobertura pelos provedores comerciais de dados.

**Esta é a funcionalidade de maior sensibilidade jurídica de todo o produto.** Ela produz um
parecer nominal sobre uma pessoa física, com potencial direto de afetar sua contratação. Por
isso depende formalmente da F4-02, e não pode ser construída antes dela.

## Definition of Done

- [ ] Consulta por atleta implementada, retornando: histórico de cartões por temporada e
      clube, distribuição 1º/2º tempo, minutagem, tipologia das infrações (onde houver
      motivo) e percentil na distribuição da liga por temporada.
- [ ] Série temporal do percentil, permitindo distinguir atipicidade pontual de traço
      persistente.
- [ ] Comparação contra um grupo de pares da mesma posição, para não penalizar zagueiros e
      volantes pela natureza da função.
- [ ] Controles da F4-02 aplicados: base legal, registro de finalidade e log de acesso por
      consulta.
- [ ] Bloco textual obrigatório na saída, explicando o que o resultado significa e o que não
      significa, e informando o direito de contestação previsto no art. 20 da LGPD.
- [ ] Log de auditoria: quem consultou, qual atleta, quando e com que finalidade declarada.
- [ ] Testes unitários da consulta e do log.
- [ ] Suíte `pytest` passando.

## Riscos e observações

* **Maior exposição jurídica do backlog.** Um parecer que prejudique a contratação de um
  atleta não condenado é risco concreto de ação por dano moral. O controle por posição, o
  bloco interpretativo e o log de finalidade são mitigações mínimas, não opcionais.
* Não expor esta funcionalidade em nenhuma camada aberta ou pública. Uso restrito a ambiente
  contratado, com identificação do consulente.
