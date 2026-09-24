# lib

Código sem JSX: cliente da API, tipos de domínio e formatadores.

- `api/` — **só servidor.** `cliente.ts` faz a chamada HTTP com a chave do
  cookie `httpOnly` e traduz 401/403/404 em navegação; `sessao.ts` monta o
  `Perfil` a partir de `GET /v1/me` e expõe `exigirAcessoTela`; `acoes.ts`
  tem as Server Actions `entrar` e `sair`. Os demais são adaptadores, um por
  recurso, que convertem a resposta da API para os tipos de `types/`:
  `cobertura.ts` (temporadas e rodadas para os filtros), `fila.ts` (T1),
  `atletas.ts` (T2, busca e ficha), `partidas.ts` (T3, listagem e dossiê) e
  `agregados.ts` (T4).
- `types/` — tipos de domínio que os componentes consomem: `perfil.ts`
  (Perfil, Camada, TelaId), `fila-triagem.ts` (T1), `atleta.ts` (T2),
  `partida.ts` (T3) e `agregado.ts` (T4 — nenhum campo de atleta, nunca;
  doc 03 §5). Campos que a API pode devolver nulos são `| null` aqui.
- `format/` — formatadores de exibição puros (sem JSX). `fila.ts` monta a
  linha de justificativa da T1; `tier.ts` combina tier + percentil, com "—"
  quando não há tier; `proporcao.ts` formata proporção como percentual;
  `partida.ts` formata data (sem deslocamento de fuso em data pura) e placar;
  `agregado.ts` formata a média de cartões por partida.
- `opcoes.ts` — séries (`A`/`B`), total de rodadas e leitura de parâmetros de
  URL. Temporadas disponíveis não ficam aqui: vêm de `/v1/cobertura`.
- `telas.ts` — metadados fixos das 4 telas, usados pelo menu e pela home.
