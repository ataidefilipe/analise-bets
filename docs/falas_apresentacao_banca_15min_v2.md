# Falas — Apresentação de banca (15 min, v2)

**Deck:** [`apresentacao_banca_15min_v2.html`](apresentacao_banca_15min_v2.html) · 13 slides
**Data:** 24 de setembro de 2026

Duas opções de fala por slide. Elas não são variações de redação — mudam o **registro**:

| | Quando usar |
| :--- | :--- |
| **A · Direta** | Voz de pitch. Frase curta, segunda pessoa, vende a ideia. Feita para o Ato 1 e para quem apresenta solto. |
| **B · Formal** | Registro acadêmico. Nomeia o método e o número, antecipa a arguição. Feita para o Ato 2 e para quem prefere script fechado. |

As duas cabem no mesmo tempo. Dá para misturar — usar A no Ato 1 e B no Ato 2 é a combinação mais natural
para uma banca, porque acompanha a mudança de registro que o próprio deck faz.

---

## Travas que valem para toda fala

1. **Vocabulário controlado.** Nunca *suspeito*, *risco de fraude*, *detecção* ou *probabilidade*.
   Sempre *atípico*, *prioridade de escrutínio*, *triagem*, *escore* e *percentil*
   ([`especificacao/02_regras_de_negocio.md`](especificacao/02_regras_de_negocio.md) §5).
   A palavra dita na banca é a mesma que iria no despacho.
2. **Slide 3 não afirma causalidade.** A v2 tirou o resultado econométrico dos slides de propósito.
   A fala fica no contexto: o mercado cresce, o cartão vira produto, a lei passa a exigir monitoramento.
3. **Nenhum nome real de atleta**, nem como exemplo verbal. A tela usa nomes fictícios pelo mesmo motivo.
4. **A decisão é sempre humana.** Sempre que a fala chegar perto de "o sistema identifica",
   corrigir para "o sistema ordena a atenção".

## Orçamento de tempo

| Ato | Slides | Tempo | Ritmo |
| :--- | :--- | :---: | :--- |
| **1 · Pitch** | 1 – 7 | 5 min | ~40 s por slide, sem parar |
| **2 · Como funciona** | 8 – 10 | 6 min | slide 8 rápido; 9 e 10 são os longos |
| **3 · Confiança e mercado** | 11 – 13 | 4 min | ~80 s por slide |

Iniciar o cronômetro com <kbd>S</kbd> antes da primeira palavra. Ele fica âmbar se o pitch passar de 5 min.

---

# ATO 1 · PITCH

## Slide 1 — Capa · ~30 s

**A · Direta**

> Boa noite. Em 2023 o futebol brasileiro descobriu que dava para comprar um cartão amarelo.
> A Operação Penalidade Máxima mostrou atletas combinando o minuto exato de levar a advertência,
> e o mercado de apostas pagando por isso.
> O que a gente construiu se chama Radar da Integridade: um sistema que lê a súmula oficial da CBF
> e diz, antes da rodada, onde vale a pena olhar primeiro.
> Em 15 minutos a gente mostra o problema, o sistema no ar, e o número que diz se ele funciona.

**B · Formal**

> Boa noite. Este trabalho aplica ciência de dados e inteligência artificial à identificação de
> anomalias disciplinares no futebol brasileiro. A fonte é a súmula oficial da CBF, Séries A e B,
> de 2014 a 2026. O produto se chama Radar da Integridade e está em operação.
> A apresentação tem três partes: cinco minutos para o problema e a solução, seis para como o
> sistema funciona, e quatro para segurança, mercado e limites.
> Começo pelo problema, porque ele não é o que a maior parte das pessoas imagina.

*Emenda:* "E o problema não é o que se imagina — não é o resultado do jogo."

---

## Slide 2 — O problema · ~50 s

**A · Direta**

> Para manipular um resultado, você precisa de vários jogadores. Para entregar um cartão, precisa de um só.
> Foi essa diferença que abriu o mercado.
> Hoje a aposta não é só no placar: é no cartão de um jogador específico, no 1º tempo, numa janela de minutos.
> E quem foi aliciado não precisa fazer o time perder — basta reclamar com o árbitro na hora combinada.
> Olhem esse número: **28,9%** dos cartões da Série B não vêm de disputa de bola. São reclamação, cera,
> conduta antidesportiva.
> Um cartão por falta dura depende de o lance acontecer. Um cartão por reclamação, não: depende só da
> vontade do atleta.
> E tudo isso liquida no apito final. Quem descobre depois não recupera nada.

**B · Formal**

> A vulnerabilidade não está no resultado da partida, está nos mercados secundários.
> As micro-apostas incidem sobre eventos fracionários — cartão por jogador, cartão no 1º tempo,
> pênalti em janela de tempo, escanteios.
> A característica que importa é a discricionariedade individual: um único atleta produz o evento
> sem depender dos companheiros e sem alterar o placar de forma visível.
> A leitura das súmulas quantifica isso. Dos **3.671 cartões** da Série B em 2022 e 2023,
> **28,9%** decorrem de infração não-física — reclamação, 15,8%; cera, 8,4%; conduta antidesportiva, 4,8%.
> É a categoria que não exige disputa de bola e, portanto, a mais fácil de encomendar.
> A Operação Penalidade Máxima documentou **14 incidentes** com atleta, confronto, minuto e valor pactuado.

*Emenda:* "E por que isso virou um problema agora, e não há dez anos?"

---

## Slide 3 — Por que agora · ~50 s

> ⚠️ **Não afirmar causalidade neste slide.** O período coincide com a entrada do VAR e com mudança de
> diretriz de arbitragem. A fala é de contexto.

**A · Direta**

> Duas curvas que deveriam andar juntas se separaram.
> Os jogadores estão fazendo **menos faltas** — 25,4 por jogo em 2024, o menor número da série histórica.
> Mas estão levando **mais cartão**: eram 1,6 cartões a cada 10 faltas em 2017, hoje são 2,2.
> O jogo ficou menos físico e mais punido.
> E eu não estou dizendo que a aposta causou isso — tem VAR no meio, tem mudança de arbitragem.
> O que eu estou dizendo é o seguinte: mais cartão significa mais mercado de cartão,
> e mais mercado significa mais incentivo para encomendar um.
> A linha de baixo mostra o momento. 2018 legaliza. Quatro anos sem fiscalização de integridade.
> E só em dezembro de 2023 a lei passa a **exigir** monitoramento. A demanda por isso é de agora.

**B · Formal**

> O gráfico traz duas séries da Série A entre 2015 e 2024, indexadas a 2017 — cada curva dividida
> pelo próprio valor daquele ano, porque faltas por jogo e cartões por falta têm escalas muito diferentes.
> A leitura é esta: as faltas caem para **25,4** por partida, mínima da série;
> a conversão de falta em cartão sobe de **1,6 para 2,2** a cada dez faltas, recorde.
> Não atribuo causalidade aqui: o período coincide com a introdução do VAR e com mudanças de
> diretriz de arbitragem.
> O argumento é de contexto — o volume de cartões cresce no mesmo intervalo em que o mercado de
> apostas se expande sem fiscalização, entre a Lei 13.756, de 2018, e o marco regulatório de
> dezembro de 2023, que passa a exigir monitoramento de integridade das operadoras.

*Emenda:* "Esse é o problema. Agora o que a gente construiu."

*Se perguntarem o que é "2017 = 100":* "É só uma régua comum. Cada série dividida pelo próprio valor de 2017.
81 quer dizer 19% abaixo do que era em 2017."

---

## Slide 4 — A solução · ~45 s

**A · Direta**

> O Radar faz uma coisa só: lê a súmula oficial da CBF no dia seguinte à rodada e organiza a atenção
> de quem precisa decidir. São três entregas.
> A primeira são os **dados** — partida e cartão com minuto e motivo, cada campo rastreável até o PDF da CBF.
> A segunda é o **dossiê**: cada alerta vem com o porquê. O minuto, o motivo escrito pelo árbitro,
> e o link para a súmula. Isso é uma justificativa que cabe num despacho.
> A terceira é a que mais interessa ao clube: o **perfil do atleta antes do jogo — e antes do contrato**.
> E isso funciona por um motivo simples: o comportamento disciplinar atípico se repete ao longo das
> temporadas, mesmo quando o atleta troca de clube.
> Padrão que se repete dá para antecipar. Episódio isolado, não.

**B · Formal**

> A solução é uma camada de inteligência de integridade sobre a fonte oficial, entregue em três níveis.
> Nível um, **dado canônico**: partidas e cartões das Séries A e B com minuto exato e motivo textual,
> com proveniência rastreável até o PDF da CBF.
> Nível dois, **dossiê da rodada**: cada alerta acompanhado da memória de cálculo — o que disparou,
> em que minuto, qual motivo, e o link para a súmula-fonte. O diferencial aqui não é acurácia,
> é **admissibilidade**: um escore de caixa-preta não fundamenta um despacho.
> Nível três, **risco pré-jogo e due diligence**: a fila dos atletas relacionados para a rodada
> e a ficha disciplinar de quem o clube pretende contratar.
> A viabilidade do nível três se apoia em evidência do próprio projeto: o perfil de atipicidade
> individual persiste entre temporadas e entre clubes.

*Emenda:* "E isso não é maquete. Está rodando."

---

## Slide 5 — O sistema hoje · ~45 s

**A · Direta**

> Isso aqui é o sistema rodando. É a fila de uma rodada: **458 atletas relacionados**, e o Radar
> entrega os três primeiros.
> Reparem no que aparece junto de cada nome — quantos cartões no 1º tempo, quantos minutos jogados,
> se é titular. Não é uma nota solta: é uma conta que dá para conferir.
> E reparem no aviso do topo: isso mede **atipicidade estatística**, não probabilidade de fraude.
> Esse aviso não é enfeite. Ele viaja junto com o dado, em toda resposta da API.
> São quatro telas, e cada perfil vê só a sua: a federação vê a rodada inteira, o clube vê só o
> próprio elenco, a operadora vê o dossiê da partida sem nome nenhum.
> Os nomes aqui são fictícios de propósito — mostrar um atleta real sem condenação numa apresentação
> pública seria exatamente o dano que o sistema existe para evitar.

**B · Formal**

> Esta é a tela principal, a fila da rodada. De **458 atletas relacionados**, o corte entrega os três
> de maior percentil, cada um com a base do cálculo à vista: cartões no 1º tempo, minutos em campo
> e condição de titular ou reserva.
> O aviso interpretativo do topo é servido pela API em toda resposta — não é texto fixo da interface,
> de modo que alterá-lo não exige nova publicação do front.
> São quatro telas, e o menu é montado a partir do perfil da credencial: federação e STJD veem a
> rodada completa; o clube, apenas o próprio elenco na fila; a operadora recebe o dossiê da partida
> sem identificação de atleta; e a camada aberta atende imprensa e academia com agregados.
> Os nomes exibidos são fictícios: a exposição nominal de atleta não condenado é vedada por desenho.

*Emenda:* "Quatro telas, quatro perfis. Vale ver quem é cada um e o que ele decide."

*Se houver rede e tempo:* abrir o sistema ao vivo com a chave de federação e depois com a de operadora,
mostrando a mesma consulta devolver camadas diferentes.

---

## Slide 6 — Personas e fluxos de decisão · ~45 s

**A · Direta**

> Quem usa isso, na prática.
> O cliente principal é o **clube**. E a dor dele não é fiscalizar o próprio elenco — é não contratar
> um problema. Tem gatilho claro, que é a janela de transferências, e decisão rápida.
> O segundo é **federação e STJD**, que hoje trabalham por denúncia: chega a denúncia, abre o processo.
> Com o Radar a pergunta vira "da rodada inteira, quais três eu mando para revisão de vídeo?".
> Tem a **operadora**, que não quer previsão nenhuma: ela quer papel, para provar à SPA que monitorou.
> E tem uma persona que a gente **recusou** — a mesa de trading. É quem mais pagaria,
> e é exatamente por isso que não vendemos.
> Em todos os fluxos, quem decide é uma pessoa. O sistema ordena a atenção; não acusa ninguém.

**B · Formal**

> O fluxo é o mesmo em todos os casos, em cinco passos: súmula publicada em D+1, nota de atipicidade
> de cada atleta relacionado, fila no tamanho que o cliente consegue analisar, análise humana com a
> justificativa aberta, e decisão do cliente.
> O que muda é a pergunta de cada persona.
> O clube pergunta se deve contratar determinado atleta, e recebe a ficha individual mais a fila
> restrita ao próprio elenco.
> A federação pergunta quais casos da rodada manda para revisão, e recebe a fila e o dossiê,
> com fundamentação para o despacho.
> A operadora pergunta se consegue comprovar monitoramento à SPA, e recebe o registro datado com hash,
> sem nome de atleta.
> A mesa de trading não é atendida, por conflito de interesse formalizado no termo de uso:
> dado por atleta alimentaria a precificação dos micro-mercados que o projeto existe para proteger.
> Em todos os fluxos, a decisão final é humana.

*Emenda:* "Cada um desses clientes tem uma equipe de tamanho diferente. E é aí que entra o último ponto do pitch."

---

## Slide 7 — O tamanho da fila · ~40 s · **INTERATIVO**

**A · Direta**

> Última coisa do pitch, e é a que mais importa para quem vai usar.
> Antes da rodada, o Radar ordena as centenas de atletas relacionados, do mais atípico para o menos.
> O limiar é só isto: **até onde a fila vai**.
> *[arrasta para 1]* Fila de um: pouquíssimo trabalho por rodada, e pouco caso antecipado no total.
> *[arrasta para 10]* Fila de dez: muito mais casos antecipados, e dez pessoas para alguém analisar
> toda semana.
> *[volta para 3]* Quem escolhe o tamanho é o cliente, conforme a equipe que ele tem.
> E o ponto é este: **em qualquer tamanho de fila, o acerto fica de 2,4 a 3 vezes acima de sortear
> atletas ao acaso.**

**B · Formal**

> O limiar de alerta é parâmetro explícito do produto, não constante escondida.
> Antes de cada rodada, o sistema ordena os atletas relacionados por percentil de atipicidade,
> e o limiar define o corte da fila.
> *[arrasta o slider]* Com fila de três, **10,8%** dos alertados recebem cartão no 1º tempo,
> contra os 4% do sorteio — 2,7 vezes o acaso, o que corresponde a 68 cartões antecipados
> em 210 rodadas.
> Aumentar a fila aumenta o total capturado e a carga de análise; o acerto por alerta se mantém
> na mesma faixa.
> A pergunta que o limiar responde não é qual o corte correto, e sim **quantos casos o cliente
> consegue tratar por rodada**.
> Registro a ressalva: as capacidades de cada perfil ainda precisam ser validadas com usuário real.

*Emenda:* "Esse é o produto. Agora, como ele funciona por dentro." — **fim dos 5 minutos de pitch.**

---

# ATO 2 · COMO FUNCIONA

## Slide 8 — Arquitetura · ~50 s

**A · Direta**

> Três blocos, da esquerda para a direita.
> **Dados:** a gente baixa a súmula do portal da CBF todo dia, só o que mudou, e calcula um SHA-256
> de cada arquivo — é a impressão digital que prova que aquele PDF é aquele PDF. O Python lê, limpa
> e calcula os escores.
> **Serviço:** o PostgreSQL guarda escore pronto, chave de acesso e o registro de cada consulta.
> A API é só leitura, e a credencial define o que cada cliente enxerga.
> **Uso:** a aplicação em Next.js monta as quatro telas conforme o perfil.
> Um detalhe que importa: nenhum escore é calculado na hora da consulta. O pipeline calcula,
> o banco guarda, a API só lê — resposta rápida e resultado reproduzível.
> Hoje isso está no ar no Railway. A produção está desenhada na AWS.

**B · Formal**

> A arquitetura tem três blocos.
> Camada de **dados**: coleta incremental do portal da CBF, com detecção por ETag e hash SHA-256 por
> arquivo, o que estabelece cadeia de custódia do PDF de origem até o escore; o processamento em
> Python faz a leitura do PDF, a limpeza e o cálculo.
> Camada de **serviço**: o PostgreSQL armazena escores pré-calculados, credenciais e o registro de
> consultas; a API em FastAPI é de leitura apenas, e o perfil de acesso é derivado da credencial,
> nunca da requisição.
> Camada de **uso**: aplicação Next.js, com as quatro telas montadas conforme o perfil.
> A decisão de pré-calcular é deliberada: garante latência baixa e reprodutibilidade do resultado.
> A base atual tem **4.559 partidas** com minuto exato e motivo textual de cada cartão — campo que
> nenhum provedor comercial entrega estruturado.
> O ambiente está publicado no Railway; a produção está desenhada na AWS.

*Emenda:* "O bloco do meio é onde está o trabalho de ciência de dados. É o próximo slide."

---

## Slide 9 — O motor do Radar · ~2 min 30 s

**A · Direta**

> Como o Radar pontua cada atleta, sem fórmula.
> Antes da rodada ele olha **só o passado** de cada atleta relacionado: quantos cartões no 1º tempo
> ele levou, por minuto jogado.
> Por que por minuto? Porque senão o jogador que entrou aos 45 e tomou amarelo vira o mais
> indisciplinado do campeonato. Então quem jogou pouco é puxado para a média da liga, e só se
> descola dela quando tem minuto suficiente para sustentar isso.
> Essa taxa é multiplicada pelo tempo que se espera que ele jogue, e o resultado ordena a fila.
> Duas vantagens. Cada nota vira uma conta que cabe num despacho. E o sistema aprende com um evento
> que acontece toda rodada — cartão no 1º tempo.
> Do lado direito está a próxima camada, que é a IA propriamente dita.
> **Isolation Forest:** 300 árvores fazendo cortes aleatórios nos dados. O atípico se separa do grupo
> em pouquíssimos cortes — e isso funciona sem precisar de nenhum exemplo de fraude.
> **Random Forest com aprendizado PU:** aprende com os casos já confirmados pela Justiça, sem assumir
> que todo o resto é inocente. E essa premissa importa, porque a maioria dos casos reais nunca foi
> investigada.
> Por que ainda não está no produto? Porque com **14 casos confirmados**, qualquer classificador
> acerta 100% dentro da amostra de treino — e esse número não prova nada.
> O critério para entrar é ganho medido **fora** da amostra. É exatamente o que o motor atual tem,
> e é o próximo slide.

**B · Formal**

> O escore em produção é de forma fechada e auditável.
> Para cada atleta relacionado, estima-se a taxa de cartões no 1º tempo por minuto jogado,
> usando exclusivamente informação anterior à rodada.
> A estimativa usa encolhimento bayesiano empírico em direção à taxa populacional, com prior
> equivalente a **500 minutos** — cerca de cinco partidas completas.
> A razão é estatística: sem encolhimento, um atleta com um cartão em vinte minutos teria a maior
> taxa da liga por construção.
> A taxa estimada é multiplicada pelos minutos esperados, e o produto ordena a fila.
> Importa registrar que a taxa populacional também é acumulada no tempo. Estimá-la sobre a base
> inteira pareceria inofensivo, por ser um agregado de liga sem poder de discriminar atletas,
> mas seria informação do futuro entrando no escore do passado.
> À direita está a camada de aprendizado de máquina, ainda não incorporada ao produto.
> O **Isolation Forest**, com 300 árvores de cortes aleatórios, isola observações atípicas em poucas
> partições e não requer rótulo de fraude.
> O **Random Forest com aprendizado positive-unlabeled** aprende dos casos judicialmente confirmados
> sem tratar os não rotulados como negativos — premissa necessária, porque a maioria dos casos reais
> nunca foi investigada.
> O critério de entrada em produção é ganho demonstrado fora da amostra. Com 14 positivos,
> a sensibilidade de 100% medida dentro da amostra de treino não carrega informação,
> e por isso não é reportada como resultado deste trabalho.

*Emenda:* "E o motor que está em produção tem, sim, ganho medido fora da amostra. É este número."

---

## Slide 10 — O resultado · ~2 min 40 s

**A · Direta**

> Esse é o número que diz se funciona.
> A barra roxa é o Radar. A linha tracejada embaixo é o acaso: se você sortear um atleta relacionado,
> 4% das vezes ele leva cartão no 1º tempo.
> O Radar, nos dez primeiros da fila, acerta **12%**. É três vezes o acaso.
> E ele também bate a alternativa óbvia, que é simplesmente contar quem tem mais cartão na temporada —
> a barra azul. No topo da lista as duas ficam perto: 9,1% contra 9,5%.
> Mas a diferença cresce conforme a fila aumenta: no topo dez é 8,6% contra 11,9%.
> E cresce por um motivo concreto — o Radar corrige por minutos jogados, então não se engana com
> quem jogou pouco.
> Como isso foi medido: **210 rodadas**, sempre prevendo a próxima rodada só com o que já tinha
> acontecido antes dela. São 107.990 registros de atleta por partida.
> E agora a ressalva, que eu faço questão de dizer em voz alta: isso mede **atipicidade disciplinar**.
> Não mede conduta. Um atleta com estilo de falta tática precoce e um atleta aliciado produzem a mesma
> assinatura estatística. Por isso o produto prioriza atenção humana — e não acusa ninguém.

**B · Formal**

> A validação é *walk-forward*: para cada uma das **210 rodadas** avaliadas, o escore é calculado
> apenas com informação anterior àquela rodada e avaliado sobre o resultado observado nela.
> A base tem **107.990 registros** de atleta por partida, cobrindo Série A 2025 e 2026 e
> Série B de 2022 a 2026.
> A métrica é precisão no topo k da fila. Com fila de dez, **11,9%** dos alertados recebem cartão no
> 1º tempo, contra 4% da taxa basal entre relacionados — ganho de 2,9 vezes.
> O escore supera também a linha de base de referência, que é o ranqueamento por cartões acumulados
> na temporada, e a vantagem **cresce com o tamanho da fila**: de 0,4 ponto percentual no topo um
> para 3,3 pontos no topo dez. A explicação é o denominador de minutos jogados.
> Quanto ao risco de vazamento temporal, que é o maior risco técnico do trabalho: o teste adotado
> corrompe todo o alvo a partir de um corte cronológico e exige que os escores anteriores permaneçam
> idênticos. Foram **75.291 linhas comparadas, zero divergentes**.
> Registro a ressalva metodológica: o ganho mede atipicidade disciplinar, não conduta.

*Emenda:* "E é justamente porque ele não mede conduta que a próxima parte existe."

*Se perguntarem "por que não só contar cartões?":* "A contagem simples fica perto no topo 1 —
9,1% contra 9,5%. A diferença aparece quando a fila cresce: 8,6% contra 11,9% no topo dez.
O Radar corrige por minutos jogados; a contagem, não."

---

# ATO 3 · CONFIANÇA E MERCADO

## Slide 11 — Segurança e LGPD · ~80 s

**A · Direta**

> Esse sistema fala sobre pessoas identificadas. E a maioria dos atletas com perfil atípico
> **nunca foi investigada**. Nomear essas pessoas num sistema sobre integridade seria exatamente
> o dano que a gente quer evitar.
> Então a proteção não é um termo de consentimento — é a arquitetura. São três camadas.
> **Aberta:** imprensa e academia não recebem atleta nenhum, só agregado.
> **Identificada:** nome só para quem já responde por aquela pessoa — a federação, e o clube,
> e o clube só dentro do próprio elenco.
> **Nominável:** só quem tem condenação transitada em julgado. Hoje são dez atletas da Penalidade Máxima.
> Do lado técnico: a chave de acesso é guardada só como hash, o banco não conhece a chave.
> Perfil e clube vêm da credencial — se você tentar informar na URL, a API recusa.
> Tela sem permissão não aparece desabilitada: ela não aparece.
> E o escore bruto nunca é exibido, porque "0,18" seria lido como 18%. Mostramos percentil e faixa.
> Três coisas ainda em aberto, e eu prefiro dizer: a base legal do tratamento não está fixada,
> o canal formal de revisão do artigo 20 está previsto mas não implementado, e o histórico do Git
> anterior à pseudonimização ainda contém listas nominais.

**B · Formal**

> O tratamento envolve dado pessoal de pessoas identificadas e produz sobre elas inferência com
> potencial de dano reputacional.
> O escore de atipicidade não é dado sensível na definição do art. 5º, inciso II, da LGPD,
> mas o efeito prático de uma sinalização sobre a carreira de um atleta exige o mesmo nível de cuidado.
> A resposta adotada é restrição de granularidade por camada.
> Camada aberta: sem atleta na resposta.
> Camada identificada: nome apenas para quem já responde por aquelas pessoas, com registro de cada
> consulta individual.
> Nomináveis: apenas condenação transitada em julgado — hoje, dez atletas.
> Controles técnicos: credencial armazenada como hash SHA-256; perfil e clube derivados da credencial,
> com recusa explícita se informados na requisição; atletas sem condenação pseudonimizados;
> e a API não inicia em produção sem o segredo de pseudonimização configurado.
> O aviso interpretativo acompanha o dado em toda resposta, e o vocabulário é controlado —
> atípico, não suspeito; prioridade de escrutínio, não risco de fraude.
> A decisão permanece humana, o que sustenta a revisão prevista no art. 20.
> Declaro as pendências: base legal ainda não fixada, canal de revisão previsto mas não implementado,
> e histórico do repositório anterior à pseudonimização com exposição nominal.

*Emenda:* "Essa é a parte que protege quem está na base. Agora, quem paga pela conta."

---

## Slide 12 — Mercado e receita · ~80 s

**A · Direta**

> Primeiro, onde a gente **não** compete — porque isso é honesto e compra credibilidade para o resto.
> Sportradar, Genius e IBIA monitoram movimentação de odds em tempo real, no mundo inteiro.
> A gente não faz tempo real e não faz cobertura internacional.
> Sofascore e Opta têm um volume de dado esportivo que a gente não tem.
> Agora, onde a gente compete. Eles operam sobre **sinal de mercado** — odds se mexendo.
> E isso chega para a operadora.
> Nós operamos sobre **registro oficial**: o que o árbitro escreveu, com hash e carimbo de data.
> Essa é a prova que clube e federação conseguem usar num processo.
> E tem a Série B, onde a Penalidade Máxima começou e onde o provedor global cobre mal.
> A receita segue as personas: assinatura mais consulta avulsa no clube, assinatura institucional na
> federação, assinatura de dossiê na operadora, API por volume para mídia — e o panorama aberto,
> que não gera receita, gera credibilidade.

**B · Formal**

> O posicionamento é complementar, não substituto.
> Os incumbentes — Sportradar, Genius Sports e IBIA — operam sobre dado transacional de apostas,
> com monitoramento global em tempo real. Não competimos em tempo real, cobertura internacional
> nem relacionamento com operadoras. Sofascore e Opta competem em volume e amplitude de evento esportivo.
> Onde competimos: proveniência oficial auditável, motivo textual do árbitro estruturado,
> explicabilidade suficiente para instruir procedimento disciplinar, e cobertura da Série B.
> A distinção essencial é de **natureza da evidência**: um alerta de movimentação atípica de odds e
> uma anomalia disciplinar documentada em súmula são provas de naturezas diferentes,
> e é a segunda que fundamenta despacho.
> O modelo de receita acompanha as personas: assinatura mais consulta avulsa para clube,
> assinatura institucional para federação e STJD, assinatura de dossiê para integridade de operadora,
> e API por volume para mídia e pesquisa.
> O custo marginal por cliente adicional é próximo de zero; o gargalo é aquisição, não entrega.

*Emenda:* "Fecho com a frase que resume o projeto inteiro."

*Riscos a admitir se perguntarem:* nenhuma entrevista com cliente até aqui, dependência de fonte
única (portal da CBF) e apenas 14 casos confirmados.

---

## Slide 13 — Fecho · ~40 s

**A · Direta**

> O Radar não diz se houve fraude. Ele diz **onde olhar primeiro**.
> Com a súmula oficial como fonte, a justificativa aberta em cada alerta, e o PDF de origem
> anexado com hash.
> O que vem agora: validar a demanda conversando com clube e federação de verdade — porque até aqui
> a gente não entrevistou nenhum cliente, e isso está declarado no trabalho;
> ampliar a base de casos confirmados, que é o que destrava a camada de IA;
> e levar a operação para a AWS.
> Obrigado. Estamos à disposição.

**B · Formal**

> Concluo. O sistema entrega medição de atipicidade disciplinar sobre fonte oficial, com fórmula
> publicada, memória de cálculo aberta e PDF de origem anexado com hash.
> Não afirma manipulação, e essa delimitação é deliberada: é o que o dado sustenta.
> Três encaminhamentos: validação de demanda junto a clubes e federações, ainda não realizada;
> ampliação da base de casos judicialmente confirmados, condição para incorporar a camada de
> aprendizado de máquina ao produto; e migração da operação para a AWS.
> Obrigado. Ficamos à disposição para as perguntas.

*Depois de falar:* parar. Deixar a frase na tela durante a arguição.
Com <kbd>O</kbd> se salta ao slide que a pergunta pedir — **9** para a IA, **10** para o resultado,
**11** para LGPD, **8** para arquitetura, **5** para as telas.

---

## Onde já existe resposta pronta

As notas do apresentador do próprio deck (tecla <kbd>N</kbd>) trazem as respostas de arguição
slide a slide — inclusive a explicação do "2017 = 100", o porquê de a floresta de decisão ainda não
estar no produto, e as pendências de LGPD. Este documento cobre a **fala**; aquelas cobrem a **réplica**.
