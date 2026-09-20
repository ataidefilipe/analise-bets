# lib

Código sem JSX: tipos de domínio, dados/mocks e formatadores.

- `types/` — tipos de domínio: `perfil.ts` (Perfil, TelaId, PersonaCodigo),
  `fila-triagem.ts` (T1) e `atleta.ts` (T2 — AtletaId, AtletaResumo,
  FichaAtleta e afins). Os tipos de cada tela entram quando a tela é
  implementada — ver nota em `docs/arquitetura.md` sobre por que não foram
  todos antecipados.
- `mock/` — simula as respostas da API enquanto os docs 01 (API) e 02
  (regras de negócio) não chegam a este repositório. `me.ts` simula
  `GET /v1/me`; `telas.ts` guarda os metadados fixos das 4 telas;
  `personaCookie.ts` e `perfilAtual.ts` sustentam o seletor de perfil de
  demonstração; `filaTriagem.ts` simula `GET /rodadas/.../fila` (T1);
  `buscaAtletas.ts` (`listarAtletas`) simula `GET /atletas?q=` — sem
  consulta devolve a base inteira ordenada, ver
  `docs/passo-05-tabela-completa-atletas.md` — e `fichaAtleta.ts` simula
  `GET /atletas/{id}` (T2, ambos apoiados no mesmo pool de nomes). Suporte
  compartilhado: `clubes.ts`, `nomes.ts`, `tier.ts` (vocabulário de tier,
  ainda placeholder — doc 02 §5 pendente), `random.ts` (gerador
  determinístico — o mesmo id/rodada sempre produz o mesmo resultado) e
  `opcoesRodada.ts`. **Todo arquivo aqui é temporário** — a intenção é que
  trocar por chamadas reais não exija mudar nenhum componente, só estes
  arquivos.
- `format/` — formatadores de exibição puros (sem JSX), para poderem ser
  reusados por mais de um componente ou tela. `fila.ts` monta a linha de
  justificativa da T1; `tier.ts` combina tier + percentil (usado por T1 e
  T2); `atleta.ts` formata a proporção de cartões no 1º tempo (T2).

Cada arquivo mock tem, no topo, uma nota curta lembrando que ele é
provisório e apontando o doc que o substituirá.
