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
  padrão, ordenada alfabeticamente, com "carregar mais" — diverge do doc 03
  §3 (que descreve só busca, sem listagem prévia), registrado como decisão
  deliberada do usuário.

## Convenção de componentes

Cada pasta de componentes (`components/ui`, `components/layout`, e as que
forem criadas por tela) tem seu próprio `README.md` descrevendo o que existe
ali e por quê. Comentários no código explicam decisões não óbvias; a
descrição do "o que é isso e para que serve" fica nesses READMEs.
