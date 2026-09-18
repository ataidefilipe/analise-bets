# Relatório Técnico 08 — Escore de Risco Pré-Jogo por Atleta Escalado

**Projeto:** Impacto das Apostas Esportivas no Futebol Brasileiro
**Fase:** 3 — Produto · tarefa F3-01
**Data:** 2026-09-16
**Status:** Implementado, validado sem vazamento temporal e exposto no feed de produto

---

## 1. Resumo Executivo

Este relatório documenta o primeiro componente do projeto com **poder preditivo demonstrado e
medido sem vazamento temporal**. O escore estima, para cada atleta relacionado numa partida,
o número esperado de cartões no 1º tempo, usando exclusivamente informação anterior à rodada.

1. **Supera a linha de base ingênua em k = 3, 5 e 10**, e perde em k = 1. Ranquear por
   "quem tem mais cartões acumulados" continua sendo melhor para apontar um único nome.
2. **Ganho de 2,4× a 3,0× sobre a seleção aleatória** entre os atletas relacionados.
3. **Teste de vazamento aprovado:** corromper todo o alvo a partir de um corte cronológico não
   altera nenhum dos 40.054 escores anteriores a ele.
4. **O contraste com a Fase 1 é o ponto.** O índice de partida não superava o acaso em nenhum
   limiar (relatório 07, seção 3.7). O nível do atleta, com o histórico correto e o denominador
   de minutos em campo, supera — modestamente, mas de forma mensurável.

> **O que este escore mede.** Atipicidade estatística do perfil disciplinar do atleta, e **não**
> probabilidade de fraude. Um atleta com estilo de falta tática precoce e um atleta aliciado
> produzem assinaturas semelhantes. A finalidade é priorizar atenção humana; não constitui
> acusação, indício ou prova de conduta irregular. Esta ressalva acompanha o dado no feed JSON
> e na tabela `avisos` do banco SQLite.

---

## 2. Decisão de Fonte de Escalação

A súmula oficial só é publicada **após** a partida, de modo que a escalação real não está
disponível pré-jogo. A tarefa previa três opções, e adotou-se a terceira:

| Opção | Decisão | Razão |
| :--- | :---: | :--- |
| Escalação provável de fonte externa | Adiada | Adiciona dependência de terceiro antes de saber se o modelo funciona |
| Elenco inscrito | Descartada por ora | Entrega risco de plantel, não de jogo |
| **Modo retroativo (escalação real da súmula)** | **Adotada** | Permite medir o poder preditivo antes de assumir qualquer dependência |

Em produção, o único insumo que muda é a lista de quem entra em campo. O perfil histórico, o
cálculo e a validação são idênticos. A escolha da fonte de produção passa a depender deste
resultado — e, com ganho de 2,4× a 3,0×, a decisão de contratar um provedor de escalação
provável tem agora uma base quantitativa, que antes não existia.

---

## 3. Modelo

Para cada atleta, a taxa de cartões no 1º tempo por minuto jogado é estimada com encolhimento
bayesiano empírico em direção à taxa populacional:

$$\hat{\lambda}_{i} = \frac{C^{1T}_{i,<r} + M_0 \cdot \lambda_{0,<r}}{\text{Minutos}_{i,<r} + M_0}$$

$$\text{SCORE}_{i} = \hat{\lambda}_{i} \cdot \mathbb{E}[\text{Minutos}_{i}]$$

Onde $C^{1T}_{i,<r}$ são os cartões no 1º tempo do atleta antes da rodada $r$, $M_0 = 500$
minutos é a força do prior, e $\lambda_{0,<r}$ é a taxa populacional acumulada até $r-1$. Os
minutos esperados são 82 para titulares e 13 para reservas, estimados na própria base.

**Por que o encolhimento.** Sem ele, um atleta com um único cartão em vinte minutos jogados
teria a maior taxa da liga por construção. Com $M_0 = 500$ — cerca de cinco partidas completas
—, o histórico só supera a taxa populacional quando há exposição suficiente para sustentá-lo.

**Não há parâmetro ajustado ao alvo.** A taxa populacional é ela própria acumulada no tempo.
Estimá-la sobre a base inteira pareceria inofensivo, por ser um agregado de liga sem poder de
discriminar atletas — mas é informação do futuro entrando no escore do passado, e a primeira
versão do teste de vazamento a detectou.

---

## 4. Validação Walk-Forward

Base: 107.990 registros de atleta × partida, das temporadas com súmula (Série A 2025 e 2026;
Série B 2022 a 2026). As cinco primeiras rodadas de cada temporada são descartadas, por não
haver histórico suficiente. Restam 210 rodadas avaliadas.

> **Atualização de 18/09/2026 (F2-02).** A ingestão da temporada 2025 nas duas séries e da
> Série B 2024 quase dobrou a base — de 57.406 para 107.990 registros, e de 111 para 210
> rodadas avaliadas. Os números abaixo substituem os da primeira versão. A mudança de
> substância é que o escore passou a superar a linha de base **em todos os k**, inclusive
> k = 1, onde antes perdia.

O alvo é observável e frequente: **o atleta recebeu cartão no 1º tempo naquela partida**. Não
se usa o ground truth da Operação Penalidade Máxima, que tem 14 casos — número insuficiente
para medir poder preditivo, como a Fase 1 demonstrou.

| k | Acertos | Precisão@k do escore | Linha de base | Taxa do acaso | Ganho sobre o acaso | Supera a base? |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 20/210 | **9,5%** | 9,1% | 4,0% | 2,37× | **sim** |
| 3 | 68/630 | **10,8%** | 9,1% | 4,0% | 2,69× | **sim** |
| 5 | 118/1050 | **11,2%** | 9,2% | 4,0% | 2,80× | **sim** |
| 10 | 250/2100 | **11,9%** | 8,6% | 4,0% | 2,96× | **sim** |

A linha de base é o ranking por cartões acumulados na temporada, conforme a DoD. A taxa do
acaso é a proporção de atletas relacionados que recebem cartão no 1º tempo (entre titulares,
sobe para 7,8%).

**Leitura.** O escore acerta de 2,4 a 3,0 vezes mais do que sortear entre os relacionados, e
a vantagem sobre a linha de base **cresce com k**: de 0,4 ponto percentual em k = 1 para 3,3
em k = 10. É o padrão que o desenho previa — o encolhimento troca precisão no topo absoluto,
onde a amostra de cada atleta é pequena, por estabilidade ao longo da lista. Para a pergunta de
produto — *dos relacionados de hoje, quais cinco merecem atenção?* — é o comportamento em
k ≥ 3 que importa, e é onde a diferença aparece.

Com a base anterior, metade do tamanho, o escore perdia da linha de base em k = 1. Não perde
mais. Vale registrar o que isso não significa: a linha de base continua próxima, e o ganho
sobre o acaso mede **atipicidade disciplinar**, não conduta.

---

## 5. Teste de Vazamento Temporal

É o maior risco técnico da tarefa: usar qualquer estatística da temporada completa para
pontuar uma rodada dessa mesma temporada invalida o resultado.

### 5.1 O teste adotado

Todo o alvo a partir de um corte cronológico é corrompido — passa a marcar cartão no 1º tempo
em todas as linhas seguintes — e o pipeline é recalculado. Os escores anteriores ao corte têm
de ficar **idênticos, bit a bit**.

| Linhas comparadas | Linhas divergentes | Resultado |
| :---: | :---: | :---: |
| 75.291 | **0** | Aprovado |

O corte é feito sobre a ordem cronológica global de cada série, e não sobre o número da rodada:
com várias temporadas na base, a rodada 10 de 2023 vem depois da rodada 30 de 2022, e cortar
por número de rodada misturaria passado com futuro. A primeira versão do teste cometia esse
erro e acusava divergência em metade das linhas.

### 5.2 Por que o embaralhamento previsto na tarefa não serve

A tarefa propunha embaralhar a ordem temporal e verificar que o desempenho degrada. O
diagnóstico mostra que ele **não degrada** — e a razão é estrutural:

| k | Ganho com a cronologia real | Ganho com a ordem embaralhada |
| :---: | :---: | :---: |
| 1 | 2,37× | 2,25× |
| 3 | 2,69× | 2,63× |
| 5 | 2,80× | 2,67× |
| 10 | 2,96× | 2,68× |

Ao destruir a cronologia, o embaralhamento faz a janela "anterior" de cada atleta conter
partidas futuras. Isso **dá** informação ao modelo em vez de tirar. Com a base da primeira
versão, o desempenho chegava a **subir** em k = 3 e k = 5 — um teste que passa tanto com
vazamento quanto sem ele não testa nada.

Com a base dobrada pela F2-02, o embaralhamento passou a degradar o desempenho em todos os k,
e o teste "passaria". Isso não o reabilita, por duas razões. A primeira é que ele continua sem
poder de detecção garantido: o sinal só apareceu porque a base cresceu, não porque o teste
ficou melhor. A segunda é que as duas colunas não são comparáveis — o embaralhamento muda
quais rodadas têm histórico suficiente, e a coluna embaralhada avalia 310 rodadas contra 210
da real. O embaralhamento permanece publicado como diagnóstico, não como guarda; quem decide
é a corrupção determinística do futuro, em 5.1.

---

## 6. Limitações

1. **A validação é retroativa.** Usa a escalação real da súmula, que só existe após a partida.
   O desempenho em produção depende da qualidade da escalação provável, e será menor na medida
   em que ela errar quem entra em campo.
2. **Cobertura restrita às temporadas com súmula.** Série A apenas 2026; Série B de 2022 em
   diante. Para a Série A histórica não há relação de atletas na fonte.
3. **O histórico entre temporadas é curto.** A Série A 2026 é a primeira temporada com
   escalação, então nenhum atleta dela tem histórico de temporada anterior na mesma série.
4. **Alvo observável, não fraude.** O escore é validado contra cartão no 1º tempo — o evento
   que os mercados negociam —, não contra manipulação. A relação entre um e outro é hipótese
   do projeto, não resultado deste relatório.
5. **Contexto de partida não implementado.** Rodada, situação na tabela e clássico regional
   estavam entre os componentes propostos e ficaram fora desta versão: o perfil individual já
   supera a linha de base, e acrescentar features sem ganho medido só aumentaria a superfície
   de vazamento. Fica como extensão, com a mesma exigência de validação.

---

## 7. Rastreabilidade

* **Implementação:** `src/models/score_pre_jogo.py`
* **Testes:** `tests/test_score_pre_jogo.py` (11 testes, incluindo o de vazamento)
* **Tabelas:**
  * `reports/tables/tabela_23_score_pre_jogo_avaliacao.csv`
  * `reports/tables/tabela_23b_score_pre_jogo_teste_vazamento.csv`
  * `reports/tables/tabela_23c_score_pre_jogo_ranking.csv`
  * `reports/tables/tabela_23d_score_pre_jogo_ordem_embaralhada.csv`
* **Dataset:** `data/processed/integrity/score_pre_jogo.parquet`
* **Feed de produto:** `data/processed/product_feed/risco_pre_jogo.json` e tabela
  `risco_pre_jogo` do banco SQLite, acompanhada da tabela `avisos`.

> **Restrição de exposição.** Esta é a saída com maior potencial de uso indevido para
> precificação de mercado. A restrição de granularidade por segmento de cliente é definida na
> tarefa F4-03 e **deve estar concluída antes de qualquer exposição externa**.
