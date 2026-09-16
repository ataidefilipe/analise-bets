# F4-01 — RIPD/DPIA e definição de base legal LGPD

**Fase:** 4 — Governança
**Responsável sugerido:** Luan de Oliveira
**Tamanho:** M
**Depende de:** —
**Status:** Backlog

---

## Descrição

Elaborar o Relatório de Impacto à Proteção de Dados Pessoais (RIPD) do produto e definir
formalmente a base legal para o tratamento de dados de atletas, incluindo a posição do
projeto sobre decisão automatizada.

## Objetivo

Estabelecer o fundamento jurídico do produto antes de qualquer exposição externa dos dados,
e transformar conformidade em característica do produto, não em obstáculo.

## Contexto

O produto trata dado pessoal de pessoas identificadas — nome de atleta, clube, histórico
disciplinar — e produz sobre elas uma inferência com potencial de dano reputacional
significativo. Ainda que o escore de atipicidade não seja dado sensível na definição do art.
5º, II da LGPD, o **efeito prático** de uma sinalização de suspeição sobre a carreira de um
atleta exige o mesmo nível de cuidado.

Pontos a resolver no RIPD:

* **Base legal.** Legítimo interesse é o caminho mais provável, e exige o teste de
  proporcionalidade documentado: finalidade legítima, necessidade do tratamento e equilíbrio
  entre o interesse do controlador e os direitos do titular.
* **Art. 20 — decisão automatizada.** O titular tem direito a solicitar revisão de decisão
  tomada unicamente com base em tratamento automatizado que afete seus interesses. O produto
  precisa de um canal e de um procedimento reais para isso, não de uma menção formal.
* **Minimização.** Quais campos são efetivamente necessários para cada finalidade e cada
  perfil de cliente.
* **Retenção.** Por quanto tempo um escore de atipicidade permanece associado a um atleta. Um
  perfil de 2020 deve continuar visível em 2026?
* **Transparência ao titular.** Como o atleta é informado de que existe um sistema que o
  pontua.

A proposta de projeto já previa a anonimização de atletas investigados não condenados como
tarefa de polimento (item 5.1). No contexto de produto isso deixa de ser polimento: passa a
ser requisito de arquitetura, detalhado na F4-02.

## Definition of Done

- [ ] RIPD redigido em `docs/`, cobrindo: finalidades, categorias de dados, titulares,
      fluxos de tratamento, riscos identificados e medidas de mitigação.
- [ ] Base legal definida e justificada, com teste de proporcionalidade documentado para
      legítimo interesse.
- [ ] Procedimento de atendimento ao art. 20 descrito: canal, prazo, responsável e forma de
      resposta.
- [ ] Política de retenção e descarte definida por categoria de dado.
- [ ] Matriz de risco: probabilidade e impacto por cenário (vazamento, uso indevido,
      identificação incorreta, dano reputacional a atleta não condenado).
- [ ] Levantamento das normas aplicáveis, com **conferência da redação vigente** antes de
      citar: Lei 13.709/2018 (LGPD), Lei 13.756/2018, Lei 14.790/2023 e Lei 14.597/2023.
- [ ] Papéis definidos: quem é controlador e quem é operador em cada arranjo de cliente.

## Riscos e observações

* A equipe não tem formação jurídica. O documento deve declarar explicitamente que é uma
  análise técnica preliminar e recomendar revisão por profissional habilitado antes de
  qualquer operação comercial real.
* Citar artigo de lei sem conferir a redação vigente é risco de credibilidade numa banca.
  Conferir cada dispositivo na fonte oficial.
