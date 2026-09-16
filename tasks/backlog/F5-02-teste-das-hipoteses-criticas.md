# F5-02 — Teste das três hipóteses críticas de produto

**Fase:** 5 — Validação de mercado
**Responsável sugerido:** Nickolas Gomes
**Tamanho:** M
**Depende de:** F5-01
**Status:** Backlog

---

## Descrição

Testar explicitamente, nas entrevistas, as três hipóteses das quais depende a viabilidade do
produto. Cada uma tem consequência direta sobre o que será construído.

**H1 — Tolerância a alerta.** Quantos itens por rodada o cliente consegue efetivamente tratar?
→ Define o limiar de corte da fila (F1-04, F3-02). Se a resposta for "dois ou três por
rodada", o sistema atual, que sinaliza cerca de 9% das partidas, é inutilizável na
configuração vigente.

**H2 — Objeto da compra.** O cliente paga por priorização analítica, ou só pela base de dados
limpa e auditável?
→ Se a resposta for a base, o produto é a Camada 1 e todo o investimento em modelagem tem
valor acadêmico, não comercial. Muda completamente a prioridade da Fase 3.

**H3 — Granularidade aceitável.** O cliente aceita receber nome de atleta, ou exige agregado
por questões jurídicas e de relação com o elenco?
→ Define o produto vendável e valida ou derruba a arquitetura da F4-02 e a funcionalidade de
due diligence (F3-04).

## Objetivo

Converter três decisões hoje tomadas por suposição em decisões tomadas por evidência, antes
que elas custem semanas de desenvolvimento.

## Contexto

Estas três hipóteses são pontos de ramificação do roadmap: dependendo da resposta, tarefas
inteiras da Fase 3 mudam de prioridade ou deixam de fazer sentido.

O caso de H2 é o mais desconfortável e o mais importante. É plenamente possível que o cliente
queira apenas a base canônica das Séries A e B — com minuto, motivo do árbitro e
proveniência auditável — e não tenha interesse no escore. Seria um resultado que reposiciona
o projeto, e é melhor descobri-lo agora do que depois da F3-01, que é o item de maior esforço
do backlog.

Descobrir isso cedo é economia, não fracasso.

## Definition of Done

- [ ] As três hipóteses incorporadas ao roteiro da F5-01, com perguntas que as testem sem
      induzir a resposta.
- [ ] Respostas tabuladas por persona, com o grau de convergência entre entrevistados.
- [ ] Conclusão explícita para cada hipótese: confirmada, refutada ou inconclusiva.
- [ ] Consequência de roadmap registrada para cada conclusão — quais tarefas do backlog mudam
      de prioridade, escopo ou status.
- [ ] `tasks/README.md` atualizado se houver mudança de prioridade.

## Riscos e observações

* Com 5 a 8 entrevistas não há representatividade estatística. O entregável é **direção**, não
  medida — e deve ser apresentado como tal no trabalho acadêmico, sem inflar a conclusão.
* Se H2 for refutada (o cliente quer só o dado), isso não invalida o TCC: a modelagem
  permanece como contribuição acadêmica, e o produto se reposiciona sobre o pipeline. Essa
  leitura deve estar pronta antes da banca.
