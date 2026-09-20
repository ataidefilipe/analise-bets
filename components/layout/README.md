# components/layout

Casca da aplicação — cabeçalho, menu e o que é comum a toda tela.

| Componente | Para quê |
| :--- | :--- |
| `AppShell` | Envolve toda página: cabeçalho com perfil ativo + `NavMenu` + `HomeButton`. Usado uma vez, no `app/layout.tsx`. |
| `NavMenu` | Lista as telas permitidas ao perfil (`perfil.telasPermitidas`). Uma tela fora da lista não gera link. |
| `HomeButton` | Botão circular com ícone `House` ([phosphor-icons/react](https://github.com/phosphor-icons/react)) em toda tela exceto a home — link fixo para `/`. |
| `PersonaSwitcher` | Troca a persona mock ativa (cookie `mock_persona`) para testar o menu com os 5 perfis. **Ferramenta de demonstração/QA — não existe em produção**, onde o perfil vem da sessão autenticada. |
| `ThemeToggle` | Alterna entre tema claro e escuro (classe `.dark` no `<html>`, persistida em `localStorage`). Ícones `Sun`/`Moon` da phosphor-icons. |
| `TelaPendente` | Stub das telas ainda não implementadas. Some conforme cada tela (T1–T4) é construída. |

Ver [`docs/arquitetura.md`](../../docs/arquitetura.md) para o raciocínio por
trás do menu dinâmico, do perfil mock e da paleta de cores/tema escuro.
