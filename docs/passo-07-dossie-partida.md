# Passo 7 — T3: Dossiê de partida

Status: pronto para avaliação.

## O que foi entregue

- Rota `/partidas/[id]` com as 5 seções do doc 03, §4:
  1. **Identificação** — confronto, placar, data, arena, árbitro, competição/rodada.
  2. **Procedência** — "o coração da tela": fonte, URL da súmula e SHA-256
     (ambos com botão de copiar), datas de download e processamento.
  3. **Eventos** — cartões com minuto, período, tipo e motivo (ou a nota de
     que a súmula não registrou, mesmo padrão da T2).
  4. **Escore de anomalia da partida** — percentil + a ressalva obrigatória
     de que, neste nível, o escore não discrimina melhor que sorteio (sem
     essa nota, a tela prometeria o que a validação não sustenta).
  5. **Atletas sinalizados** — só aparece para perfil de granularidade
     identificada (`perfil.granularidade === "identificada"`), linkando
     para a ficha do atleta (T2).
- Botão "Exportar PDF" = `window.print()`, exatamente o que o doc pede para
  o MVP. Uma nota discreta na tela (oculta na impressão) registra a dívida
  que o próprio doc já cita: isso não é um registro auditável assinado.
- Impressão limpa: cabeçalho, menu e botão de voltar somem ao imprimir
  (`print:hidden`), sobrando só o conteúdo do dossiê.
- Rota `/partidas` (listagem): **não existe no doc 03** — a T3 assume que
  P3 chega numa partida específica por referência externa. Criei essa
  listagem só para haver como navegar até um dossiê durante o
  desenvolvimento/demo; documentando para não parecer invenção de escopo
  não pedida.
- Refactor de apoio: o texto do aviso interpretativo e o sorteio do motivo
  do cartão (~86% nulo) — antes duplicados entre T1/T2 — viraram módulos
  compartilhados (`lib/mock/avisoInterpretativo.ts`,
  `lib/mock/motivosCartao.ts`), agora reusados também pela T3.

## Como conferir

1. `pnpm dev`, ir em "Dossiê de partida" pelo menu (perfil padrão P2 ou
   perfil P3 têm acesso).
2. Abrir uma partida da lista: conferir as 5 seções, o hash SHA-256 e os
   botões de copiar.
3. Clicar em "Exportar PDF": abre o diálogo de impressão do navegador só
   com o conteúdo do dossiê (sem cabeçalho/menu).
4. Reparar a ressalva na seção de escore — sem ela a tela estaria
   prometendo mais do que o modelo sustenta no nível de partida.

## Assunções registradas (a confirmar quando os docs 01/02 chegarem)

- **Listagem `/partidas`** é uma adição não prevista no doc 03, feita por
  necessidade de navegação (ver acima).
- **Categoria do evento**: ao contrário da T2, o doc 03 §4 lista só
  "minuto, período e motivo" para os eventos da T3 — não incluí campo de
  categoria aqui, só na ficha do atleta.
- **Escore de partida gerado uniforme** (não com a distribuição de cauda
  longa usada nos escores por atleta): o próprio doc diz que, neste nível,
  o escore não discrimina melhor que sorteio, então gerar um valor uniforme
  é a escolha mock mais fiel a essa afirmação.
- Não há, entre os perfis mock atuais, uma combinação com acesso à T3 e
  granularidade agregada — a ocultação da seção "Atletas sinalizados"
  está implementada, mas não há como demonstrá-la com os perfis de
  demonstração de hoje.

## O que fica para os próximos passos

- T4 (panorama agregado) — última tela do MVP.
- Trocar `getDossiePartida`/`listarPartidas` por chamadas reais quando o
  doc 01 chegar.
