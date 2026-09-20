# lib

Código sem JSX: tipos de domínio, dados/mocks e (conforme necessário)
formatadores.

- `types/` — tipos de domínio. Hoje só `perfil.ts` (Perfil, TelaId,
  PersonaCodigo). Tipos de atleta/escore entram quando a tela que os usa for
  implementada — ver nota em `docs/arquitetura.md` sobre por que não foram
  antecipados.
- `mock/` — simula as respostas da API enquanto os docs 01 (API) e 02
  (regras de negócio) não chegam a este repositório. `me.ts` simula
  `GET /v1/me`; `telas.ts` guarda os metadados fixos das 4 telas;
  `personaCookie.ts` e `perfilAtual.ts` sustentam o seletor de perfil de
  demonstração. **Todo arquivo aqui é temporário** — a intenção é que trocar
  por chamadas reais não exija mudar nenhum componente, só estes arquivos.

Cada arquivo mock tem, no topo, uma nota curta lembrando que ele é
provisório e apontando o doc que o substituirá.
