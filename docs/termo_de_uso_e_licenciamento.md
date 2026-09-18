# Termo de Uso e Política de Licenciamento

**Projeto:** Impacto das Apostas Esportivas no Futebol Brasileiro
**Tarefa:** F4-03 — Fase 4, Governança
**Versão:** Minuta 1 — 2026-09-16
**Status:** **Minuta técnica, pendente de revisão jurídica**

> **Sobre esta minuta.** O texto abaixo foi redigido por quem construiu o produto, para que a
> restrição de granularidade existisse ao mesmo tempo no contrato e no código. Ele organiza as
> decisões de produto e as vedações que o projeto assume, mas **não substitui revisão por
> profissional habilitado**, que deve preceder qualquer assinatura ou publicação externa. Os
> pontos que dependem da definição de base legal estão marcados com ⚠ e remetem à tarefa F4-01,
> ainda em aberto.

---

## 1. Objeto

Este termo rege o acesso aos escores de atipicidade disciplinar produzidos pelo projeto —
`MATCH_ANOMALY_SCORE`, `ATHLETE_ANOMALY_SCORE` e o escore de risco pré-jogo por atleta — e aos
conjuntos de dados derivados das súmulas oficiais da CBF.

## 2. Natureza do produto e cláusula de não-imputação

O contratante reconhece expressamente, como condição do acesso, que:

1. Os escores medem **desvio estatístico** em relação à distribuição disciplinar basal do
   futebol brasileiro, e **não constituem prova, indício ou acusação** de manipulação de
   resultados, fraude ou qualquer infração.
2. Um atleta com estilo de jogo de falta tática precoce e um atleta aliciado produzem
   **assinaturas estatísticas semelhantes**. O instrumento não os distingue, e não se propõe a
   distinguir.
3. A denominação de manipulação, fraude ou corrupção esportiva é **reserva de jurisdição** dos
   órgãos competentes — Ministério Público, Polícia Federal, STJD, FIFA —, mediante condenação
   ou confissão formal.
4. O produto **não demonstrou capacidade de priorizar casos conhecidos de manipulação** no
   nível de partida: a captura não se distingue de seleção aleatória (relatório técnico 07,
   seção 3.7). O escore pré-jogo por atleta supera a linha de base ingênua, mas para o evento
   observável "cartão no 1º tempo", não para manipulação (relatório 08).

O descumprimento desta cláusula — em especial a apresentação de um escore como evidência de
conduta — é causa de rescisão imediata.

## 3. Finalidades permitidas e matriz de granularidade

| Segmento | Atendido | Camada | Granularidade | Finalidade permitida |
| :--- | :---: | :--- | :--- | :--- |
| Federação, STJD ou órgão de investigação | Sim | Identificada | Partida e atleta | Auditoria desportiva e instrução de procedimento |
| Clube | Sim | Identificada | Atleta, **restrita ao próprio elenco** e a alvos de contratação declarados | Compliance interno e due diligence |
| Operadora — integrity ou compliance | Sim | Aberta | Partida, agregada | Monitoramento regulatório e registro de diligência |
| **Operadora — mesa de trading ou precificação** | **Não** | — | — | — |
| Imprensa e academia | Sim | Aberta | Partida, agregada | Divulgação e pesquisa |

A matriz é **executável**: está implementada em `src/pipeline/perfis_de_acesso.py` e aplicada
na geração dos feeds. Um perfil não atendido não é um pedido negado por e-mail — é uma exceção
levantada em tempo de execução.

### 3.1 Camadas de exposição

* **Aberta** — agregados por clube, rodada e temporada, sem identificação individual.
* **Pseudonimizada** — perfil individual sob identificador estável derivado do registro CBF por
  HMAC-SHA256, não reversível sem o segredo do projeto.
* **Identificada** — nome do atleta. Apenas em ambiente contratado, com finalidade declarada e
  registro de acesso.

**Exceção de fato público:** atletas com condenação transitada em julgado podem ser nominados
em qualquer camada. Hoje são os 10 atletas da Operação Penalidade Máxima já julgados. Atleta
investigado sem condenação não entra nessa exceção, e atleta apenas estatisticamente atípico
muito menos — este é o grupo mais numeroso e o mais exposto a dano.

## 4. Vedações expressas

É vedado ao contratante, sob qualquer perfil:

1. **Utilizar o produto, no todo ou em parte, para precificação, definição de odds, ajuste de
   limites de mercado, construção de mercados derivados ou qualquer finalidade de exploração
   comercial de apostas.** Esta vedação alcança inclusive o perfil de integrity de operadora,
   e o compartilhamento interno com áreas de trading caracteriza descumprimento.
2. Redistribuir, sublicenciar, revender ou publicar os dados recebidos, integral ou
   parcialmente, em qualquer camada.
3. Tentar reidentificar atletas a partir da camada pseudonimizada, inclusive por cruzamento com
   bases externas.
4. Apresentar escores como evidência, indício ou fundamento de acusação, em qualquer foro.
5. Nominar publicamente atleta não condenado com trânsito em julgado.
6. Empregar o produto como critério único e automatizado de decisão que afete a carreira do
   atleta — contratação, dispensa, sanção. ⚠ A revisão humana obrigatória e o canal de contestação
   dependem da posição sobre o art. 20 da LGPD, a ser fixada na tarefa F4-01.

## 5. Posição sobre o segmento de trading

**O projeto não atende mesas de trading nem áreas de precificação de operadoras de apostas.**
A decisão é deliberada e registrada aqui por exigência da tarefa F4-03.

**Razão.** Um escore que indica concentração atípica de cartões no 1º tempo é, ao mesmo tempo,
um sinal de integridade e um sinal de trading. Fornecido a quem precifica micro-mercados de
cartão, o instrumento deixa de proteger o esporte e passa a conferir vantagem competitiva nos
exatos mercados que o trabalho do projeto identifica como vetor de vulnerabilidade à
manipulação. O produto financiaria o problema que diz combater.

**Custo assumido.** O segmento recusado é justamente o de maior disposição a pagar. A recusa
não é uma perda a esconder: é o que permite ao produto ser apresentado a federações, clubes e
órgãos de investigação sem conflito de interesse aparente, e é parte do argumento comercial
perante esses segmentos.

**Fronteira do que é aceito.** A área de integrity de uma operadora é atendida — com dado
agregado por partida, sem identificação individual — porque a obrigação regulatória de
monitoramento é legítima e a granularidade concedida não tem utilidade para precificação. A
separação interna entre integrity e trading é responsabilidade contratual do contratante, e a
vedação da cláusula 4.1 alcança o compartilhamento entre elas.

## 6. Licenciamento da camada aberta

Os agregados da camada aberta — métricas por clube, rodada, temporada e categoria de infração,
sem identificação individual — são licenciados para **uso acadêmico e jornalístico** mediante:

1. Citação da fonte, incluindo a versão do conjunto de dados e o commit correspondente;
2. Reprodução da cláusula de não-imputação da seção 2 em qualquer publicação derivada;
3. Vedação de uso comercial e das finalidades da seção 4.

⚠ A licença formal a adotar (por exemplo CC BY-NC-SA 4.0, com adendo de não-imputação) depende
de revisão jurídica e da definição de titularidade sobre os dados derivados das súmulas
oficiais, cuja fonte primária é pública.

## 7. Consequências do descumprimento

1. **Rescisão imediata** e revogação de acesso, sem devolução de valores.
2. Responsabilização por perdas e danos, inclusive por dano moral a terceiro — notadamente ao
   atleta indevidamente nominado ou associado a conduta irregular.
3. ⚠ Comunicação às autoridades competentes quando o descumprimento configurar tratamento
   irregular de dado pessoal, nos termos a definir na tarefa F4-01.

## 8. Limitações conhecidas do controle técnico

Registradas por honestidade, e porque um controle cuja lacuna não é declarada é pior do que
controle nenhum:

1. A varredura retroativa foi executada na tarefa **F4-02**: as tabelas nominais e os
   relatórios saem pseudonimizados, e um teste automatizado reprova a suíte se um nome
   reaparecer. Permanece a exposição no **histórico do Git**, já publicado — os commits
   anteriores contêm as listas nominais. Enquanto o tratamento do histórico não for decidido
   (ver `docs/decisao_historico_git_exposicao_nominal.md`), este termo não pode ser oposto a
   terceiros com base na proteção da árvore atual.
2. O segredo de pseudonimização tem valor de desenvolvimento embutido no código para tornar os
   testes determinísticos. Em produção precisa vir do ambiente, e a troca do segredo invalida
   a continuidade dos identificadores.
3. A base legal do tratamento ainda não está fixada (tarefa F4-01). Até lá, este termo descreve
   a política de produto, não o fundamento jurídico dela.

---

## Referências internas

* Matriz executável: `src/pipeline/perfis_de_acesso.py`
* Matriz publicada: `reports/tables/matriz_de_granularidade_por_segmento.csv`
* Camada identificada: `data/processed/product_feed/restrito/`
* Evidência sobre capacidade do produto: relatório 07 (seções 3.7 e 3.8) e relatório 08

> Caso o seu projeto envolva dados pessoais ou dados pessoais sensíveis, comunique ao time de
> Segurança da Informação através do e-mail seginfo@gcb.com.br
