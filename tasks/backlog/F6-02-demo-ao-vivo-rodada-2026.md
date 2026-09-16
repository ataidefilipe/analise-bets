# F6-02 — Demo ao vivo da rodada 2026

**Fase:** 6 — Entregáveis
**Responsável sugerido:** Filipe Ataíde
**Tamanho:** M
**Depende de:** F3-02, F4-02
**Status:** Backlog

---

## Descrição

Preparar e ensaiar uma demonstração ao vivo do produto, executando o pipeline sobre a rodada
mais recente do Brasileirão 2026 e exibindo a fila de triagem resultante.

Roteiro proposto, com duração alvo de cinco a sete minutos:

1. Execução do pipeline delta ao vivo: detecção incremental, download das súmulas novas,
   parsing e atualização das bases.
2. Abertura da tela com a fila da rodada.
3. Detalhamento de um item sinalizado: subscores, p-valor, minutagem, motivo digitado pelo
   árbitro.
4. Link para a súmula-fonte, com o hash de integridade.
5. Enquadramento explícito: desvio estatístico, não acusação.

## Objetivo

Demonstrar que o produto existe e funciona sobre dado real e corrente, e não apenas sobre uma
base histórica congelada.

## Contexto

Esta é a peça de maior impacto na avaliação do redirecionamento para produto. Um sistema que
processa a rodada do fim de semana anterior, ao vivo, comunica "produto" de forma que nenhum
relatório comunica.

A capacidade já existe e está comprovada: a última execução do pipeline delta, em 16/09/2026,
inspecionou 380 partidas da Série A 2026, baixou 216 súmulas novas via detecção incremental
com HTTP HEAD, ETag e SHA-256, sem erros, e atualizou o feed de produto. A base processada já
contém 1.370 cartões da Série A 2026 e 1.383 da Série B.

O que falta não é capacidade técnica — é **ensaio e enquadramento**. Uma demo que trava, ou
que exibe nome de atleta sem o tratamento da F4-02, produz o efeito oposto ao pretendido.

## Definition of Done

- [ ] Roteiro escrito, com tempo alvo e responsável por cada etapa.
- [ ] Demo executada de ponta a ponta ao menos três vezes em ensaio, sem intervenção manual.
- [ ] **Plano de contingência**: gravação em vídeo e captura da base já processada, para o
      caso de falha de rede ou indisponibilidade da fonte no momento da apresentação.
- [ ] Tratamento de nomes conforme a F4-02 aplicado à tela usada na demo.
- [ ] Enquadramento interpretativo dito em voz alta e exibido na tela, não deixado implícito.
- [ ] Respostas preparadas para as perguntas previsíveis: precisão do sistema, comparação com
      Sportradar e Genius, conflito de interesse com operadoras, tratamento de LGPD.
- [ ] Verificação prévia de que a rodada escolhida tem ao menos um item interessante para
      detalhar.

## Riscos e observações

* **Dependência de fonte externa ao vivo.** Se o site da CBF estiver indisponível no momento
  da apresentação, a demo cai. O plano de contingência não é opcional.
* Escolher com antecedência a rodada e o item a detalhar. Improvisar sobre a fila ao vivo
  arrisca cair em um caso de leitura ambígua.
* Não apresentar nenhum caso como suspeita concreta. O enquadramento estatístico precisa estar
  em cada frase da narração.
