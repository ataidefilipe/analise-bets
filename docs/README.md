# Documentação do front

Índice da documentação deste projeto. Cada passo do desenvolvimento (ver
`03_telas.md` do projeto de análise) ganha um registro aqui descrevendo o que
foi entregue, para revisão antes de avançar para o próximo.

- [`arquitetura.md`](./arquitetura.md) — estrutura de pastas, convenções e
  como o front lida com permissão por perfil. Documento vivo: atualizado a
  cada passo que muda uma convenção.
- [`passo-01-base-do-projeto.md`](./passo-01-base-do-projeto.md) — primeiro
  passo: estrutura base, tipos de perfil, menu dinâmico e páginas placeholder
  das 4 telas.
- [`passo-02-fila-triagem.md`](./passo-02-fila-triagem.md) — segundo passo:
  T1 (fila de triagem da rodada) implementada por completo.
- [`passo-03-busca-e-ficha-atleta.md`](./passo-03-busca-e-ficha-atleta.md) —
  terceiro passo: T2 (busca e ficha do atleta) implementada por completo.
- [`passo-04-paginacao-busca.md`](./passo-04-paginacao-busca.md) — quarto
  passo: paginação na busca de atleta. **Superado pelo passo 5**, mantido
  como histórico.
- [`passo-05-tabela-completa-atletas.md`](./passo-05-tabela-completa-atletas.md) —
  quinto passo: a tela de busca virou uma tabela com todos os atletas por
  padrão, ordenada alfabeticamente — diverge do doc 03 §3 (que descreve só
  busca, sem listagem prévia), registrado como decisão deliberada do
  usuário. Navegação por "carregar mais" **superada pelo passo 6**.
- [`passo-06-paginacao-classica-atletas.md`](./passo-06-paginacao-classica-atletas.md) —
  sexto passo: troca o "carregar mais" por paginação Anterior/Próxima de 10
  em 10, mantendo a tabela completa e a busca como filtro do passo 5.
- [`passo-07-dossie-partida.md`](./passo-07-dossie-partida.md) — sétimo
  passo: T3 (dossiê de partida) implementada por completo, com exportação
  em PDF via impressão.
- [`passo-08-busca-e-paginacao-partidas.md`](./passo-08-busca-e-paginacao-partidas.md) —
  oitavo passo: busca e paginação na listagem de partidas, no mesmo padrão
  da T2 — e generalização de `BuscaForm`/`Pager` para `components/ui`.

## Convenção de componentes

Cada pasta de componentes (`components/ui`, `components/layout`, e as que
forem criadas por tela) tem seu próprio `README.md` descrevendo o que existe
ali e por quê. Comentários no código explicam decisões não óbvias; a
descrição do "o que é isso e para que serve" fica nesses READMEs.
