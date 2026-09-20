# components/layout

Casca da aplicação — cabeçalho, menu e o que é comum a toda tela.

| Componente | Para quê |
| :--- | :--- |
| `AppShell` | Envolve toda página: cabeçalho com perfil ativo + `NavMenu` + `BackButton`. Usado uma vez, no `app/layout.tsx`. |
| `NavMenu` | Lista as telas permitidas ao perfil (`perfil.telasPermitidas`). Uma tela fora da lista não gera link. |
| `BackButton` | Botão circular com ícone `ArrowLeft` ([phosphor-icons/react](https://github.com/phosphor-icons/react)) em toda tela exceto a home. Usa o histórico do navegador (`router.back()`), não um link fixo, para voltar ao ponto de origem real (ex.: resultado de busca, não sempre a home). |
| `PersonaSwitcher` | Troca a persona mock ativa (cookie `mock_persona`) para testar o menu com os 5 perfis. **Ferramenta de demonstração/QA — não existe em produção**, onde o perfil vem da sessão autenticada. |
| `TelaPendente` | Stub das telas ainda não implementadas. Some conforme cada tela (T1–T4) é construída. |

Ver [`docs/arquitetura.md`](../../docs/arquitetura.md) para o raciocínio por
trás do menu dinâmico e do perfil mock.
