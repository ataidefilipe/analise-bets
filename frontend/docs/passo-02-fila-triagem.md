# Passo 2 — T1: Fila de triagem da rodada

Status: pronto para avaliação.

## O que foi entregue

- Rota `/triagem` funcional, substituindo o placeholder do passo 1.
- Filtros de competição/ano/rodada (`RodadaFiltros`) via query string —
  trocar um filtro navega para a mesma rota com a nova query e o servidor
  busca a fila correspondente.
- Aviso interpretativo (`Callout`) sempre visível junto à fila, com o texto
  vindo da resposta simulada (`avisoInterpretativo`), nunca hard-coded no
  componente (doc 03, §1.1).
- Slider de corte por percentil (`FilaTriagemPainel`), iniciando no
  `limiarPadrao` do perfil ativo, com contagem "X de Y relacionados" em
  tempo real e o texto de apoio fixo do doc.
- Tabela (`FilaTriagemTabela`) com atleta, clube, confronto, condição e
  tier — cada atleta com a linha de justificativa obrigatória (doc 03, §2)
  montada a partir dos componentes do escore, e link "ver ficha" para
  `/atletas?atletaId=...` (a T2 vai ler esse parâmetro quando for
  implementada).
- Estados tratados: sem escalação (rodada futura, não é erro), fila vazia
  (corte alto demais), base rasa (rodadas 1–5) e fila escopada por clube
  para o perfil P1, com o cabeçalho dizendo "Elenco do [clube]" como o doc
  exige.

## Como conferir

1. `pnpm dev`, entrar em Triagem pelo menu (perfil padrão P2 já tem acesso).
2. Mexer no slider de corte e ver a contagem e a tabela mudarem na hora.
3. Trocar a rodada para um número alto (ex.: 35) e ver o estado "sem
   escalação" (não parece erro).
4. Trocar a rodada para 1–5 e ver o aviso extra de base rasa.
5. Trocar o perfil (seletor do cabeçalho) para P1 (Clube) e ver a fila já
   escopada ao elenco, com o cabeçalho "Elenco do Exemplo A FC".

## Assunções registradas (a confirmar quando os docs 01/02 chegarem)

- **Filtragem do corte no cliente.** O doc pede resposta "em tempo real" ao
  mover o slider; implementei buscando a rodada inteira (todos os
  relacionados) uma vez e filtrando por percentil no navegador, em vez de
  refazer a chamada à API a cada movimento. Se a API real não puder
  devolver a rodada inteira de uma vez (por volume ou por design), isso
  precisa virar uma busca com debounce.
- **Vocabulário de tier** (`Extrema`, `Muito alta`, `Alta`, `Moderada`,
  `Baixa`) inventado só para o mock ter algo plausível para exibir — o doc
  02 §5, que define o vocabulário real, ainda não chegou.
- **Rodada "atual"** fixada em 30 (das 38) só para o mock ter rodadas
  futuras demonstráveis (estado "sem escalação"). Não existe noção real de
  calendário ainda.
- Confronto e clube são todos fictícios ("Exemplo A FC" ... "Exemplo T
  FC"), na mesma convenção que o próprio doc 03 usa (`exemplo_fc`).

## O que fica para os próximos passos

- T2 (busca e ficha do atleta) — o link "ver ficha" desta tela já aponta
  para lá.
- T3 e T4.
- Trocar `getFilaTriagem` por uma chamada real quando o doc 01 chegar.
