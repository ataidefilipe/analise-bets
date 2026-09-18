# 03 — Especificação de telas

**Destrava:** etapa 5 (front-end).
**Escopo:** protótipo / MVP.

Leia antes: [01 — API](01_api_e_autorizacao.md) e
[02 — Regras de negócio](02_regras_de_negocio.md). O vocabulário de §5 do documento 02 é
obrigatório em todo rótulo de tela.

---

## 0. Quatro telas

| # | Tela | Endpoint | Personas |
| :---: | :--- | :--- | :--- |
| T1 | Fila de triagem da rodada | `/rodadas/.../fila` | P2 federação, P1 clube |
| T2 | Ficha do atleta | `/atletas/{id}` | P2, P1 |
| T3 | Dossiê de partida | `/partidas/.../dossie` | P3 operadora, P2 |
| T4 | Panorama agregado | `/agregados/...` | P5 imprensa, P3 |

O menu é montado a partir de `GET /v1/me`: o front só oferece o que a granularidade do perfil
permite. Uma tela negada **não aparece desabilitada** — não aparece.

---

## 1. Regras que valem em todas as telas

1. **O aviso interpretativo aparece na tela onde o escore aparece.** Não em rodapé, não em
   modal que se fecha e não volta, não em tooltip. Texto vem de `aviso_interpretativo` na
   resposta — nunca hard-coded, para que mudar o texto não exija deploy do front.
2. **`atleta_id` é opaco.** O front não deriva nada dele nem assume formato.
3. **`tier` vem do backend.** O front nunca recalcula tier a partir do escore.
4. **O escore bruto do pré-jogo nunca é exibido.** É contagem esperada de cartões, não
   probabilidade, e um usuário lendo "0,18" vai interpretar como 18%. Exibir percentil e tier.
5. **Nome de atleta só quando a resposta traz.** Ausência não é erro nem campo a preencher.
6. **Toda tela que lista escore tem estado vazio explicativo**, não uma lista em branco.

---

## 2. T1 — Fila de triagem da rodada

A tela principal. Responde à pergunta de P2: *"da rodada inteira, quais casos eu mando para
revisão?"*

### Estrutura

```
┌────────────────────────────────────────────────────────────┐
│ Triagem da rodada                                          │
│ [Série A ▾] [2026 ▾] [Rodada 28 ▾]                         │
├────────────────────────────────────────────────────────────┤
│ ⓘ Este escore mede ATIPICIDADE ESTATÍSTICA do perfil        │
│   disciplinar do atleta, e não probabilidade de fraude.     │
│   A finalidade é priorizar atenção humana.                  │
├────────────────────────────────────────────────────────────┤
│ Corte: percentil [70] ──────●───────  3 de 920 relacionados │
├────────────────────────────────────────────────────────────┤
│ ATLETA              CLUBE      CONFRONTO      TIER          │
│ ─────────────────────────────────────────────────────────── │
│ Nome do Atleta      Exemplo    EXE x OUT      Extrema (p99) │
│   └ 7 cartões no 1ºT em 2.430 min · titular · [ver ficha]   │
│ ...                                                         │
└────────────────────────────────────────────────────────────┘
```

### Colunas

| Campo | Origem | Nota |
| :--- | :--- | :--- |
| Atleta | `atleta` + `num_camisa` | Só camada identificada |
| Clube | `clube_slug` | Exibir nome legível, não o slug |
| Confronto | `confronto` | |
| Condição | `condicao` | Titular / Reserva |
| Tier | `tier` + `percentil` | Rótulo do documento 02 §2 |
| Justificativa | `componentes` | **Obrigatória.** Ver abaixo |

### A linha de justificativa é requisito, não enfeite

P2 precisa fundamentar em despacho por que abriu ou arquivou. Uma fila que diz "este atleta
está no Top 1%" sem dizer por quê é inútil para essa pessoa.

Montar a partir de `componentes`, em linguagem natural:

> *7 cartões no 1º tempo em 2.430 minutos jogados · titular · taxa ajustada 0,00205*

O escore é uma conta aberta — `taxa_1t_ajustada × minutos_esperados` — e essa transparência é
uma das poucas vantagens defensáveis do produto. Escondê-la desperdiça-a.

### O controle de corte

O slider de percentil é **a funcionalidade mais importante desta tela**, porque a decisão de
produto é a carga de alerta, não o algoritmo.

* Inicia no `limiar_padrao` de `/v1/me`.
* Ao mover, mostra em tempo real quantos itens entram na fila.
* Texto de apoio fixo: *"Baixar o corte captura mais casos conhecidos e também mais alarme
  falso."*

### Ordenação e paginação

Ordem padrão: `percentil` decrescente. Sem paginação no MVP — o corte já limita a fila a
poucas dezenas. `limite` máximo de 200.

### Perfil `clube`

Mesma tela, já filtrada pelo backend para o próprio elenco. O cabeçalho deve dizer
explicitamente *"Elenco do [clube]"*, para que o usuário não interprete uma fila curta como
ausência de casos na rodada.

---

## 3. T2 — Ficha do atleta

Responde: *"este atleta tem histórico?"*

### Seções

**Cabeçalho** — nome, clubes por onde passou, identificador.

**Histórico por temporada** — uma linha por temporada: partidas jogadas, minutos, cartões
totais, cartões no 1º tempo, proporção, tier. É onde o padrão aparece: proporção de 1º tempo
consistentemente alta ao longo de temporadas diz mais que um escore isolado.

**Linha do tempo de cartões** — cada cartão com minuto, período, tipo, categoria e o motivo
textual do árbitro.

Onde `motivo_completo` for nulo — 86% da Série A — exibir *"motivo não registrado na súmula
desta temporada"*. É limitação da fonte, não falha do sistema, e a tela deve deixar isso claro
em vez de mostrar um campo vazio que parece bug.

**Aviso interpretativo** — visível, junto ao histórico.

### Cuidado de design

Esta é a tela com maior potencial de dano do sistema: uma ficha individual, nominada, num
produto sobre integridade. O enquadramento visual precisa ser **neutro e factual** — uma ficha
de dados disciplinares, não um dossiê de investigação. Sem vermelho, sem ícone de alerta, sem
selo. Percentil alto é informação estatística, não acusação.

---

## 4. T3 — Dossiê de partida

Responde à pergunta de P3: *"se a SPA me perguntar, consigo provar que monitorei esta
partida?"*

Esta persona **compra papel, não predição**. O valor está na procedência, não no escore.

### Seções

1. **Identificação** — partida, data, arena, árbitro, placar.
2. **Procedência** — fonte, URL da súmula, SHA-256, data de download, data de processamento.
   **É o coração da tela.** Deve ser copiável e legível, não um rodapé técnico.
3. **Eventos** — cartões com minuto, período e motivo.
4. **Escore de anomalia da partida** — com a ressalva obrigatória de que, no nível da partida,
   o escore **não discrimina melhor que sorteio**. Sem essa nota, a tela promete o que a
   validação não sustenta.
5. **Atletas sinalizados** — só camada identificada.

### Exportação [MVP]

Botão "Exportar PDF" — impressão da própria página via `window.print()` com folha de estilo
para impressão. Basta para o MVP.

> **[MVP] Dívida.** O dossiê em PDF assinado e arquivável (tarefa F3-03) é o que P3 de fato
> compraria. Impressão de página não é registro auditável.

---

## 5. T4 — Panorama agregado

Camada aberta. Serve P5 e a visão macro de P3.

Agregados por clube ou por rodada: partidas, cartões, cartões no 1º tempo, proporção, média por
partida. Tabela ordenável, com um gráfico de barras de proporção de 1º tempo por clube.

**Nenhum atleta, em nenhuma circunstância.** Se um dia aparecer um campo de atleta nesta tela,
é vazamento de camada e o backend está com defeito.

---

## 6. Estados

Todas as telas precisam tratar estes casos. Vários são normais, não erros.

| Estado | Quando | Mensagem |
| :--- | :--- | :--- |
| **Sem escalação** (422) | Rodada futura, súmula ainda não publicada | *"A escalação desta rodada ainda não foi publicada pela CBF. A fila fica disponível após a publicação da súmula."* — **não é erro** |
| **Fila vazia** | Corte alto demais, nenhum atleta acima | *"Nenhum atleta acima do corte atual. Reduza o percentil para ampliar a fila."* |
| **Base rasa** | Rodadas 1 a 5 | Faixa informativa: *"Histórico insuficiente nas primeiras rodadas; os escores são dominados pela média da liga."* |
| **Sem permissão** (403) | Perfil sem acesso | *"Seu perfil não tem acesso a esta consulta."* Sem detalhe técnico |
| **Fora do escopo** (403, clube) | Atleta de outro elenco | *"Seu perfil acessa apenas atletas do próprio elenco."* |
| **Não encontrado** (404) | Partida ou atleta inexistente | |
| **Erro interno** (500) | | Mensagem genérica. Nunca stack trace |

---

## 7. Fora do MVP

Registrado para não ser confundido com esquecimento:

* **Due diligence pré-contratação** — o caso de uso mais concreto de P1. Exige fluxo de
  declaração de finalidade e prazo, que depende da F4-01. Ver
  [01 §5](01_api_e_autorizacao.md#o-escopo-do-perfil-clube-mvp).
* **Relatório semanal por e-mail** — formato que P1 declara preferir. *"Documento, não API."*
* **Dossiê em PDF assinado** (F3-03).
* **Alertas ativos** (push, e-mail) quando um atleta cruza o limiar.
* **Gestão de usuários** — chaves são cadastradas manualmente.

> Caso o seu projeto envolva dados pessoais ou dados pessoais sensíveis, comunique ao time de
> Segurança da Informação através do e-mail seginfo@gcb.com.br
