# lib

Código sem JSX: tipos de domínio, dados/mocks e formatadores.

- `types/` — tipos de domínio: `perfil.ts` (Perfil, TelaId, PersonaCodigo),
  `fila-triagem.ts` (T1), `atleta.ts` (T2 — AtletaId, AtletaResumo,
  FichaAtleta e afins) e `partida.ts` (T3 — IdentificacaoPartida,
  Procedencia, DossiePartida e afins). Os tipos de cada tela entram quando a
  tela é implementada — ver nota em `docs/arquitetura.md` sobre por que não
  foram todos antecipados.
- `mock/` — simula as respostas da API enquanto os docs 01 (API) e 02
  (regras de negócio) não chegam a este repositório. `me.ts` simula
  `GET /v1/me`; `telas.ts` guarda os metadados fixos das 4 telas;
  `personaCookie.ts` e `perfilAtual.ts` sustentam o seletor de perfil de
  demonstração; `filaTriagem.ts` simula `GET /rodadas/.../fila` (T1);
  `buscaAtletas.ts` (`listarAtletas`) simula `GET /atletas?q=` — sem
  consulta devolve a base inteira ordenada, ver
  `docs/passo-05-tabela-completa-atletas.md` — `fichaAtleta.ts` simula
  `GET /atletas/{id}` (T2) e `partidas.ts` simula
  `GET /partidas/{id}/dossie` (T3), incluindo `listarPartidas(consulta)`
  (mesmo padrão de `listarAtletas`: sem consulta devolve todas, com 3+
  caracteres filtra por clube — não há tela de fila de partidas no doc,
  existe só para navegar até um dossiê).
  Suporte compartilhado: `clubes.ts`, `nomes.ts`, `tier.ts` (vocabulário de
  tier, ainda placeholder — doc 02 §5 pendente), `avisoInterpretativo.ts`
  (texto do aviso, reusado por T1/T2/T3), `motivosCartao.ts` (sorteio do
  motivo do cartão com ~86% de chance de vir nulo, doc 03 §3, reusado por
  T2/T3), `random.ts` (gerador determinístico — o mesmo id/rodada sempre
  produz o mesmo resultado) e `opcoesRodada.ts`. **Todo arquivo aqui é
  temporário** — a intenção é que trocar por chamadas reais não exija mudar
  nenhum componente, só estes arquivos.
- `format/` — formatadores de exibição puros (sem JSX), para poderem ser
  reusados por mais de um componente ou tela. `fila.ts` monta a linha de
  justificativa da T1; `tier.ts` combina tier + percentil (usado por T1, T2
  e T3); `atleta.ts` formata a proporção de cartões no 1º tempo (T2);
  `partida.ts` formata data e placar (T3).

Cada arquivo mock tem, no topo, uma nota curta lembrando que ele é
provisório e apontando o doc que o substituirá.
