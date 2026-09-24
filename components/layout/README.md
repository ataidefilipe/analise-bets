# components/layout

Casca da aplicação — cabeçalho, menu e o que é comum a toda tela.

| Componente | Para quê |
| :--- | :--- |
| `AppShell` | Envolve toda página autenticada: cabeçalho com perfil ativo, botão Sair, `NavMenu` e `HomeButton`. Usado uma vez, no `app/layout.tsx` — sem sessão, o layout não o renderiza. |
| `NavMenu` | Lista as telas permitidas ao perfil (`perfil.telasPermitidas`). Uma tela fora da lista não gera link. |
| `HomeButton` | Botão circular com ícone `House` ([phosphor-icons/react](https://github.com/phosphor-icons/react)) em toda tela exceto a home — link fixo para `/`. |
| `EntrarForm` | Formulário da chave de API em `/entrar`. Chama a Server Action `entrar`, que valida a chave em `/v1/me` e grava o cookie `httpOnly`. |
| `ThemeToggle` | Alterna entre tema claro e escuro (classe `.dark` no `<html>`, persistida em `localStorage`). Ícones `Sun`/`Moon` da phosphor-icons. |
| `TelaPendente` | Stub das telas ainda não implementadas. Some conforme cada tela (T1–T4) é construída. |

Ver [`docs/arquitetura.md`](../../docs/arquitetura.md) para o raciocínio por
trás do menu dinâmico, da sessão por chave e da paleta de cores/tema escuro.
