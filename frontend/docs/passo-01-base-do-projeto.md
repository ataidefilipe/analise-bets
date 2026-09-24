# Passo 1 — Base do projeto

Status: pronto para avaliação.

## O que foi entregue

- Estrutura de pastas (`components/ui`, `components/layout`, `lib/types`,
  `lib/mock`, `docs`) — ver [`arquitetura.md`](./arquitetura.md).
- Tipos de perfil e permissão (`lib/types/perfil.ts`): `Perfil`, `TelaId`,
  `PersonaCodigo`, `Granularidade`.
- Mock de `GET /v1/me` (`lib/mock/me.ts`) com os 5 perfis citados no doc 03,
  cada um com as telas que a tabela do §0 permite.
- Menu dinâmico (`components/layout/NavMenu.tsx`): só lista as telas
  permitidas ao perfil ativo; perfil sem nenhuma tela mostra aviso, não uma
  lista vazia silenciosa.
- Seletor de perfil de demonstração (`components/layout/PersonaSwitcher.tsx`)
  no cabeçalho, para trocar entre P1–P5 e comparar o menu — ferramenta de
  QA, não parte do produto final.
- Página inicial (`app/page.tsx`): saudação e cards das telas acessíveis ao
  perfil ativo.
- 4 rotas placeholder (`/triagem`, `/atletas`, `/partidas`, `/agregados`),
  uma por tela do doc 03 §0, mostrando que a navegação e a permissão já
  funcionam de ponta a ponta antes de qualquer tela ter conteúdo real.
- Primitivos de UI que várias telas vão reusar: `Callout` (aviso
  interpretativo, doc 03 §1.1) e `EmptyState` (estado vazio explicativo,
  doc 03 §1.6/§6). Ainda não estão em uso nas páginas — entram na
  implementação de T1/T2/T3.
- Botão de voltar (`components/layout/BackButton.tsx`), presente em toda
  tela exceto a home, embutido no `AppShell`. Ícone `ArrowLeft` da
  [phosphor-icons/react](https://github.com/phosphor-icons/react), primeira
  dependência de ícones do projeto. Usa o histórico do navegador em vez de
  sempre linkar para "/", para já se comportar bem quando telas futuras
  tiverem navegação mais profunda (ex.: da busca para a ficha do atleta).
- Paleta de marca extraída de [pe.senac.br](https://www.pe.senac.br/)
  (azul-marinho + acento azul claro) com versão dedicada para tema escuro, e
  botão (`ThemeToggle`) para alternar entre os dois manualmente. Detalhes e
  os hex exatos em [`arquitetura.md`](./arquitetura.md#paleta-de-cores). O
  item de menu da tela atual agora usa essa cor para indicar onde o usuário
  está.

## Como conferir

1. `pnpm dev` e abrir a home.
2. Trocar o perfil no seletor do cabeçalho e observar o menu mudando —
   P1 (Clube Exemplo FC) só vê triagem e busca de atleta; P5 (Imprensa) só
   vê o panorama agregado; P4 não vê nenhuma tela.
3. Abrir cada rota placeholder pelo menu e conferir o item ativo destacado.
4. Clicar no botão de sol/lua no cabeçalho e conferir o tema escuro.

## O que fica para os próximos passos

- Construir uma tela por vez (T1 a T4), começando pela que você indicar.
- Modelar os tipos de escore/atleta quando a tela que os usa for
  implementada (ver nota em `arquitetura.md`).
- Substituir a camada mock por chamadas reais quando os docs 01/02 chegarem.

## Assunções registradas (a confirmar quando os docs 01/02 chegarem)

- Mapeamento perfil → telas seguiu literalmente a coluna "Personas" da
  tabela do doc 03 §0.
- `limiarPadrao` usado nos mocks (70 para a maioria, 80 para o perfil clube)
  é um valor de exemplo, não uma regra de negócio confirmada.
