# F3-01 — Score de risco pré-jogo por atleta escalado

**Fase:** 3 — Produto
**Responsável sugerido:** Filipe Ataíde
**Tamanho:** G
**Depende de:** F2-04, F1-04
**Status:** Concluído (2026-09-16)

---

## Descrição

Construir um escore de risco calculado **antes do apito inicial**, combinando o perfil
histórico de cada atleta escalado com o contexto da partida.

Componentes propostos, a validar empiricamente:

* **Perfil histórico do atleta** — proporção de cartões no 1º tempo, concentração até os 30
  minutos e taxa de cartões por minuto em campo, medidos em temporadas anteriores e na
  temporada corrente até a rodada anterior.
* **Contexto de partida** — rodada, situação das equipes na tabela (com e sem objetivo),
  série, e se o confronto é clássico regional.
* **Composição para o nível de partida** — agregação dos escores individuais dos escalados.

## Objetivo

Deslocar o produto de detecção ex-post para avaliação de risco ex-ante, que é a forma em que
o sinal tem valor de decisão para o cliente.

## Contexto

Este é o item de maior valor comercial do projeto e o principal diferencial frente aos
incumbentes. A razão é de timing: mercados de cartões e faltas liquidam no apito final, de
modo que um alerta D+1 chega depois do pagamento e serve, no máximo, como defesa
regulatória. A decisão que gera valor — suspender um micro-mercado, reduzir limite, acionar
o atleta antes da partida, priorizar acompanhamento — só existe antes do jogo.

A viabilidade é sustentada por evidência do próprio projeto: o perfil de atipicidade
individual **persiste entre temporadas e entre clubes** (caso Nino Paraíba, percentil 100,0
em 2020 pelo Bahia e 99,67 em 2022 pelo Ceará). Um traço persistente é previsível; um evento
isolado, não.

Importante distinguir com clareza, na documentação e na interface: este escore mede
**atipicidade estatística do perfil**, não probabilidade de fraude. Um atleta com perfil de
falta tática precoce e um atleta aliciado produzem assinaturas semelhantes. A finalidade é
priorizar atenção, nunca imputar conduta.

### Restrição de escalação

A súmula oficial só sai após a partida, então a escalação real não está disponível pré-jogo.
Três opções, a decidir no início da tarefa e registrar:

1. **Escalação provável** de fonte externa — maior fidelidade de uso real, adiciona
   dependência de terceiro.
2. **Elenco inscrito** — mais robusto, menos preciso; entrega risco de plantel, não de jogo.
3. **Modo retroativo** para validação — usar escalação real da súmula para medir o poder
   preditivo do modelo, e só depois decidir a fonte de produção.

Recomenda-se começar pela opção 3, porque permite validar antes de assumir dependência
externa.

## Definition of Done

- [x] Decisão de fonte de escalação registrada com justificativa.
- [x] Escore pré-jogo implementado em módulo próprio, com separação estrita entre features
      disponíveis antes do jogo e features pós-jogo (**nenhum vazamento temporal**).
- [x] Validação retroativa walk-forward: o modelo é calibrado apenas com dados anteriores à
      rodada avaliada.
- [x] Poder preditivo reportado com a métrica definida na F1-04 (precisão@k por rodada),
      comparado contra uma linha de base ingênua (por exemplo, ranking por cartões
      acumulados na temporada).
- [x] Teste explícito de vazamento: reexecução do pipeline embaralhando a ordem temporal deve
      degradar o desempenho.
- [x] Saída disponível no feed de produto, por partida e por atleta escalado.
- [x] Documentação da limitação interpretativa (atipicidade ≠ fraude) no código, no feed e em
      qualquer saída visível ao usuário.
- [x] Testes unitários do módulo novo.
- [x] Suíte `pytest` passando.

## Riscos e observações

* **Risco de vazamento temporal é o maior risco técnico da tarefa.** Usar qualquer estatística
  da temporada completa para pontuar uma rodada dessa mesma temporada invalida o resultado.
* Se o poder preditivo não superar a linha de base ingênua, isso deve ser reportado. Um
  escore que não bate "quem tem mais cartões" não justifica produto.
* Esta é a saída com maior potencial de uso indevido para precificação de mercado. A
  restrição de granularidade por segmento de cliente é definida na F4-03 e deve estar
  concluída antes de qualquer exposição externa.


---

## Execução (2026-09-16)

Resultados em `reports/analysis/08_score_pre_jogo_por_atleta.md`.

**Poder preditivo.** O escore supera a linha de base ingênua em k = 3, 5 e 10, e perde em
k = 1. Ganho de 2,4x a 2,7x sobre sortear entre os atletas relacionados. É o primeiro
componente do projeto com poder preditivo demonstrado e medido sem vazamento.

**Vazamento.** O teste previsto na tarefa — embaralhar a ordem temporal e esperar degradação —
não discrimina: embaralhar **dá** ao modelo acesso a partidas futuras, e o desempenho sobe.
Foi substituído por um teste determinístico de corrupção do futuro, que reprovou duas versões
do pipeline antes de aprovar a terceira.

**Contexto de partida não implementado.** Rodada, situação na tabela e clássico regional
ficaram fora: o perfil individual já supera a linha de base, e acrescentar features sem ganho
medido só aumentaria a superfície de vazamento. Fica como extensão, com a mesma exigência de
validação.

**Restrição de exposição.** A saída está no feed com a ressalva interpretativa acoplada ao
dado, mas a granularidade por segmento de cliente (F4-03) precisa estar definida antes de
qualquer exposição externa.
