# Arquitetura do front

Base: Next.js 16 (App Router), React 19, TypeScript, Tailwind v4. Fonte da
especificação de produto: `03_telas.md`, que por sua vez depende de
`01_api_e_autorizacao.md` e `02_regras_de_negocio.md` — nenhum dos dois está
neste repositório ainda, então tudo que hoje é "mock" está marcado como tal e
isolado para ser trocado sem tocar em componente de tela.

## Estrutura de pastas

```
app/            Só roteamento (page/layout por rota) — sem lógica de negócio.
components/
  ui/           Primitivos genéricos, sem conhecimento de domínio (Callout, EmptyState...).
  layout/       Casca da aplicação: AppShell, menu, seletor de perfil de demonstração.
  <tela>/       Uma pasta por tela (T1, T2...), criada quando a tela é implementada.
lib/
  types/        Tipos de domínio (Perfil, TelaId...).
  mock/         Camada que hoje simula a API (docs 01/02 pendentes). Único lugar
                a trocar quando a API real existir.
  format/       Formatadores de exibição (criado conforme necessário).
docs/           Esta pasta.
```

## Decisões

**Perfil e menu dinâmico (doc 03, §0).** `GET /v1/me` retorna quais telas o
perfil pode ver; o front nunca decide isso sozinho. `lib/types/perfil.ts`
define o formato (`Perfil`, `TelaId`), `lib/mock/me.ts` simula a resposta e
`components/layout/NavMenu.tsx` filtra os links por `perfil.telasPermitidas`.
Uma tela fora da lista não vira link desabilitado — não existe no DOM.

**Perfil mock trocável por cookie.** Sem doc 01, não há autenticação real.
`components/layout/PersonaSwitcher.tsx` grava a persona escolhida em um
cookie (`mock_persona`) só para permitir demonstrar/testar o menu com as 5
personas do doc 03 (P1 a P5). Isso desaparece quando a autenticação real
entrar — a origem do perfil passa a ser a sessão, não uma escolha manual.

**Tiers e escores ainda não modelados.** O doc 03 é explícito que o front
nunca recalcula tier a partir do escore (§1.3) e nunca mostra o escore bruto
do pré-jogo (§1.4) — ambos vêm prontos do backend. Como o formato exato
desses campos depende do doc 01 (contrato da API) e do doc 02 (vocabulário de
tier, §5), esses tipos só serão adicionados quando a tela que os usa (T1)
for implementada, para não inventar um contrato que pode não bater com o
real.

**Persona P4.** Aparece na numeração do doc 03 mas não é citada em nenhuma
das 4 telas (§0). Está modelada em `lib/mock/me.ts` sem nenhuma tela
permitida, até o doc 02 esclarecer seu papel.

## Pendências conhecidas

- Trocar `lib/mock/*` por chamadas reais assim que os docs 01/02 chegarem.
- Vocabulário de tier (doc 02, §5) precisa validar os rótulos usados nas
  telas quando forem implementadas.
