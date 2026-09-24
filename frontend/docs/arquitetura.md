# Arquitetura do front

Base: Next.js 16 (App Router), React 19, TypeScript, Tailwind v4. Fonte da
especificação de produto: `docs/especificacao/` na raiz do monólito
(01 — API e autorização, 02 — regras de negócio, 03 — telas). O contrato da
API implementada está em `docs/integracao_frontend.md`, também na raiz.

Este front vive em `frontend/` do repositório `analise-bets`, ao lado do
backend (`src/api/`). Veio de `rennegomes/front-analise-bets`, incorporado com
`git subtree` — o histórico original está preservado.

Desde o passo 11, o front consome a API real; não há mais dado simulado.

## Estrutura de pastas

```
app/            Só roteamento (page/layout por rota) — sem lógica de negócio.
  entrar/       Tela de entrada pela chave de API.
components/
  ui/           Primitivos genéricos, sem conhecimento de domínio (Callout, EmptyState...).
  layout/       Casca da aplicação: AppShell, menu, formulário de entrada.
  <tela>/       Uma pasta por tela (T1, T2...).
lib/
  api/          Cliente HTTP e adaptadores da API (só servidor). Único lugar que
                conhece o formato de resposta da API.
  types/        Tipos de domínio que os componentes consomem.
  format/       Formatadores de exibição.
  opcoes.ts     Séries e leitura de parâmetros de URL.
  telas.ts      Metadados das 4 telas.
docs/           Esta pasta.
```

## Decisões

**A chave de API nunca chega ao navegador.** Toda chamada à API acontece em
componente de servidor ou Server Action (`lib/api/`). A chave fica num cookie
`httpOnly` (`ab_api_key`), gravado por `lib/api/acoes.ts::entrar` só depois de
validada em `GET /v1/me`. O JavaScript do navegador não consegue lê-la.
`ANALISE_BETS_API_URL` aponta para a API (padrão `http://localhost:8000`).

**Adaptadores isolam o formato da API.** Cada arquivo de `lib/api/` converte a
resposta (`snake_case`, campos nulos) para os tipos de `lib/types/`. Os
componentes de tela não conhecem a API: mudou o contrato, muda o adaptador.

**Perfil e menu dinâmico (doc 03, §0).** A API não devolve lista de telas: o
menu sai da `camada` de `/v1/me` (`lib/api/sessao.ts::montarPerfil`) —
`identificada` vê as 4 telas; `aberta` vê só dossiê e panorama.
`components/layout/NavMenu.tsx` filtra os links por `perfil.telasPermitidas`.
Uma tela fora da lista não vira link desabilitado — não existe no DOM. Cada
`page.tsx` protegida também chama `exigirAcessoTela(tela)` antes de buscar
qualquer dado: sem sessão vai para `/entrar`, sem acesso vai para `/`. O
backend recusa com 403 de qualquer forma — o front é só a primeira camada.

**Estados de erro vêm do status HTTP** (`lib/api/cliente.ts::apiGet`): 401 →
`/entrar`; 403 → `/`; 404 → `app/not-found.tsx`; 422 na fila → "escalação
ainda não publicada", tratado como estado normal; resto → `app/error.tsx`,
com mensagem genérica.

**Tier nunca é recalculado no front.** O doc 03 é explícito que o front
nunca recalcula tier a partir do escore (§1.3) e nunca mostra o escore bruto
do pré-jogo (§1.4) — ambos vêm prontos do backend. Fora da janela do escore
retrospectivo, tier e percentil chegam nulos e a tela mostra "—".

**O corte da fila é do backend.** A API devolve no máximo 200 itens e uma
rodada tem ~450 relacionados; filtrar no navegador perderia gente. O slider
grava `?percentil=` na URL e a página busca de novo (passo 11).

**Rotas espelham o formato do endpoint, não decisão de UI.** `/atletas/[id]`
(ficha) é uma rota dinâmica própria, não um parâmetro de query em `/atletas`
— assim como a API separa `/atletas` de `/atletas/{id}`. O dossiê é
`/partidas/[serie]/[temporada]/[id]`, porque `partida_id` sozinho repete entre
séries e anos.

## Paleta de cores

Tema inspirado no template [Astrolus](https://themewagon.github.io/astrolus/)
(só visual: cores, tipografia e formas — nenhuma mudança de comportamento).
Substituiu a paleta anterior, extraída de pe.senac.br. Os tokens ficam em
`app/globals.css`, registrados no `@theme` do Tailwind, e viram utilitários
normais (`bg-brand`, `text-muted`, `border-line`, `shadow-card` etc.). Todos
trocam de valor sozinhos no modo escuro — os componentes não repetem pares
`dark:`; as cores fixas do Tailwind (zinc, gray...) não são usadas direto.

| Token | Uso pretendido | Claro | Escuro |
| :--- | :--- | :--- | :--- |
| `brand` / `brand-strong` | Preenchimento sólido (item de menu ativo, botão primário, barra da marca), sempre com texto branco. | `#4f46e5` / `#4338ca` | `#4f46e5` / `#6366f1` |
| `link` / `link-strong` | Texto/ícone interativo sobre o fundo (hover, foco). No escuro usa indigo-400: o indigo-600 não tem contraste como texto sobre preto. | `#4f46e5` / `#4338ca` | `#818cf8` / `#a5b4fc` |
| `accent` | Destaque decorativo (borda do `Callout`, barras do gráfico). | `#6366f1` | `#818cf8` |
| `ink` / `body` / `muted` / `subtle` / `faint` | Texto: título, corpo, secundário, terciário, desativado. | gray 900/700/500/400/300 | branco, gray 300/400/500/700 |
| `line-soft` / `line` / `line-strong` | Bordas e divisórias, da mais leve à mais marcada. | gray 100/200/300 | gray 900/800/700 |
| `surface` / `surface-muted` / `track` | Card e campo; fundo alternado, cabeçalho de tabela e hover; trilho de barra/skeleton. | branco, gray 50, gray 200 | gray 900, gray 800, gray 800 |
| `background` | Fundo da página. | branco | `#030712` (gray-950) |

Formas: cards `rounded-2xl`/`rounded-3xl` com `shadow-card` (sombra suave
só no claro), botões, campos e itens de menu em pílula (`rounded-full`).
Fonte Urbanist (`next/font`), Geist Mono para trechos monoespaçados.
`components/ui/FundoDecorativo.tsx` desenha as manchas em degradê do
Astrolus apenas na home e na entrada.

**Fora do escopo desta paleta:** cor de severidade/tier nas telas de escore.
O doc 03 (§3, "Cuidado de design") exige tom neutro e factual na ficha do
atleta — sem vermelho, ícone de alarme ou selo — e isso não muda com a marca
visual do site. A paleta acima é para a interface (navegação, botões,
links), não para comunicar risco.

## Tema claro/escuro

Modo escuro por classe (`.dark` no `<html>`, via `@custom-variant dark` no
Tailwind), não só `prefers-color-scheme` — permite alternância manual.
`components/layout/ThemeToggle.tsx` alterna a classe e salva a escolha em
`localStorage`; um script inline em `app/layout.tsx` aplica a classe certa
antes da primeira pintura (evita flash de tema errado) a partir da
preferência salva ou, na ausência dela, da preferência do sistema
operacional.

## Pendências conhecidas

- Semântica do percentil da fila (pendência D1 do guia de integração): o p70
  padrão coloca ~30% da rodada na fila. Decisão de produto em aberto.
- Sem rate limiting nem expiração de chave na API: não expor fora de rede local.
