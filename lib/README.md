# lib

Código sem JSX: tipos de domínio, dados/mocks e formatadores.

- `types/` — tipos de domínio: `perfil.ts` (Perfil, TelaId, PersonaCodigo) e
  `fila-triagem.ts` (FilaTriagemItem/Response, introduzidos junto com a T1).
  Os tipos de cada tela entram quando a tela é implementada — ver nota em
  `docs/arquitetura.md` sobre por que não foram todos antecipados.
- `mock/` — simula as respostas da API enquanto os docs 01 (API) e 02
  (regras de negócio) não chegam a este repositório. `me.ts` simula
  `GET /v1/me`; `telas.ts` guarda os metadados fixos das 4 telas;
  `personaCookie.ts` e `perfilAtual.ts` sustentam o seletor de perfil de
  demonstração; `filaTriagem.ts` simula `GET /rodadas/.../fila` (T1),
  apoiado por `clubes.ts`, `nomes.ts`, `random.ts` (gerador determinístico —
  mesma rodada sempre produz a mesma fila) e `opcoesRodada.ts`. **Todo
  arquivo aqui é temporário** — a intenção é que trocar por chamadas reais
  não exija mudar nenhum componente, só estes arquivos.
- `format/` — formatadores de exibição puros (sem JSX), para poderem ser
  reusados por mais de um componente ou tela. `fila.ts` monta a linha de
  justificativa e o rótulo de tier da T1.

Cada arquivo mock tem, no topo, uma nota curta lembrando que ele é
provisório e apontando o doc que o substituirá.
