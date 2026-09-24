# Passo 11 — Integração com a API real

**Objetivo:** trocar `lib/mock/` pela API da POC (`src/api/`, na raiz do
monólito), sem reescrever as telas. Contrato: `docs/integracao_frontend.md`
na raiz.

## O que mudou

### Sessão

- O seletor de persona (`PersonaSwitcher`, cookie `mock_persona`) saiu. A
  entrada agora é por **chave de API**, em `/entrar`.
- A Server Action `entrar` valida a chave em `GET /v1/me` e só então grava o
  cookie `ab_api_key` (`httpOnly`, `sameSite=lax`, 8 horas). "Sair" apaga o cookie.
- O perfil vem de `/v1/me`. O menu sai da `camada`, porque a API não devolve
  lista de telas: `identificada` → 4 telas; `aberta` → dossiê e panorama.

**Correção de permissão herdada dos mocks.** O mock tratava a operadora (P3)
como camada identificada, o que exporia nome de atleta a um perfil de camada
aberta. Também escondia dossiê e panorama da federação e do clube, e tinha um
perfil P4 (trading) que o produto recusa. Agora vale a matriz do doc 01 §5.

### Por tela

| Tela | Mudança |
| :--- | :--- |
| T1 Fila | Filtros de série/ano vêm de `/v1/cobertura`; abre na última rodada com escalação. **O corte passou para o backend:** o slider grava `?percentil=` e a página busca de novo (a API limita a 200 itens, e filtrar no navegador perderia atletas). O contador usa `total_sinalizados`. 422 vira "escalação ainda não publicada" |
| T2 Busca | **A tabela completa com paginação (passos 5 e 6) saiu.** A API só responde a busca de 3+ caracteres, com até 20 resultados e sem escore — regra de governança (doc 01 §5), não limitação técnica. Sem busca, a tela mostra orientação |
| T2 Ficha | Tier e percentil podem vir nulos (fora da janela do escore retrospectivo) e aparecem como "—", com nota explicativa. Coluna de série no histórico |
| T3 Dossiê | Rota nova: `/partidas/[serie]/[temporada]/[id]` — `partida_id` sozinho repete entre séries e anos. Procedência e escore podem faltar; a tela explica em vez de mostrar campo vazio |
| T3 Listagem | Sobre `GET /v1/partidas`: filtro de série e temporada, busca por clube e paginação no backend |
| T4 Panorama | Série e temporada obrigatórias (a API agrega uma de cada vez); abre na temporada mais recente |

### Estrutura

- `lib/mock/` removido. No lugar: `lib/api/` (cliente, sessão, Server Actions
  e um adaptador por recurso), `lib/opcoes.ts` e `lib/telas.ts`.
- Tipos de `lib/types/` ajustados para o que a API devolve, incluindo `| null`
  nos campos que podem faltar.
- Novos: `app/entrar/`, `app/error.tsx`, `app/not-found.tsx`,
  `components/layout/EntrarForm.tsx`, `components/ui/SerieTemporadaFiltros.tsx`.
- `BuscaForm` e `Pager` aceitam `parametros`, para manter série e temporada na URL.
- `formatarData` não desloca mais data pura (`2026-04-05` virava 04/04 no fuso de Brasília).

## Como rodar

```bash
# na raiz do monólito
python -m src.api.carga
ANALISE_BETS_AMBIENTE=dev uvicorn src.api.main:app --port 8000

# em frontend/
cp .env.example .env.local     # ajuste ANALISE_BETS_API_URL se preciso
pnpm install
pnpm dev
```

As chaves de demonstração (uma por perfil) ficam em
`data/restrito/chaves_api_poc.json`, na raiz, fora do Git.

## Verificado

- `pnpm build` e `pnpm lint` sem erros.
- Com o backend real, por perfil: tela de entrada sem sessão; fila da
  federação (p70: 125 de 459 relacionados na rodada 27 de 2026); fila do clube
  restrita ao elenco; 422 na rodada 38; redirecionamento da imprensa ao abrir
  `/triagem`; busca e ficha; dossiê com e sem procedência; sinalizados só na
  camada identificada; panorama por clube e por rodada.
- **Não verificado no navegador:** o envio do formulário de entrada, que exige
  digitar uma chave. Foi testado o caminho equivalente (cookie enviado direto).
