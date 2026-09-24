# Especificação do MVP — índice e acordo de escopo

**Etapa 2 do plano de trabalho.** Este conjunto de documentos é o contrato entre a
especificação e as etapas seguintes: infraestrutura (3), backend (4), front-end (5) e
automação de alimentação (6).

**Escopo declarado: protótipo / MVP.** Não é arquitetura de produção. Onde houve escolha entre
o correto-e-caro e o suficiente-e-rápido, escolheu-se o segundo, e o ponto está marcado como
**[MVP]** com a dívida explicitada. Quem for evoluir o sistema precisa saber o que foi
deliberadamente simplificado e o que foi esquecido — estes documentos só têm a primeira lista.

---

## Os documentos

| # | Documento | Destrava |
| :--- | :--- | :--- |
| 01 | [Contrato de API e modelo de autorização](01_api_e_autorizacao.md) | Etapas 4 e 5 |
| 02 | [Regras de negócio e limiares](02_regras_de_negocio.md) | Etapas 4 e 5 |
| 03 | [Especificação de telas](03_telas.md) | Etapa 5 |
| 04 | [Infraestrutura](04_infraestrutura.md) | Etapa 3 |
| 05 | [Automação de alimentação](05_automacao.md) | Etapa 6 |

Leia o 01 e o 02 antes dos demais: eles definem o vocabulário que os outros usam.

---

## Premissas assumidas, não validadas

Três premissas sustentam tudo o que vem a seguir e **nenhuma foi verificada com cliente real**.
Estão aqui para que ninguém as confunda com fato apurado.

**P-1. As personas são hipóteses.** As cinco personas de
[`docs/analise_negocio.md §6`](../analise_negocio.md) foram derivadas da estrutura do mercado,
não de entrevista. A pesquisa com usuários foi conscientemente dispensada neste ciclo. Se uma
tela não fizer sentido para o usuário real, a causa provável está aqui.

**P-2. A capacidade operacional declarada é estimada.** Os limiares de alerta por persona
partem de uma suposição de quantos casos cada perfil consegue tratar por rodada — 3 para
federação, 1 para clube, 10 para operadora. São números plausíveis, não medidos.

**P-3. O produto mede atipicidade, não fraude.** Esta não é premissa: é resultado apurado, e a
restrição mais importante do sistema. Está detalhada em
[02 — Regras de negócio](02_regras_de_negocio.md#0-a-restrição-que-precede-todas-as-outras).

---

## Quem é o cliente, em uma tabela

Derivado de `src/pipeline/perfis_de_acesso.py`, que já executa esta matriz em código.

| Perfil | Persona | Atendido | Camada de dados | Granularidade |
| :--- | :--- | :---: | :--- | :--- |
| `federacao_stjd` | P2 — analista de integridade | sim | identificada | partida + atleta |
| `clube` | P1 — compliance de clube | sim | identificada | atleta; fila só do próprio elenco, consulta a qualquer atleta |
| `operadora_integrity` | P3 — integrity officer | sim | aberta | partida |
| `imprensa_academia` | P5 — repórter de dados | sim | aberta | partida |
| `operadora_trading` | P4 — head de trading | **não** | — | — |

### Sobre a recusa ao perfil de trading

É decisão de posicionamento, registrada na tarefa F4-03 e **aplicada em tempo de execução**:
`perfil_ou_erro()` levanta `PerfilNaoAtendido` antes de qualquer dado ser projetado.

O motivo: um escore que indica "este atleta concentra cartões no 1º tempo" serve tanto para
priorizar auditoria quanto para precificar micro-mercados de cartão. Vendido à mesa de
precificação, o produto deixaria de proteger o esporte e passaria a dar vantagem competitiva
nos exatos mercados que o trabalho identifica como vetor de vulnerabilidade.

**A operadora continua sendo cliente — pela área de integrity, não pela de precificação.**
Qualquer requisito que chegue às etapas 4 ou 5 pedindo latência baixa, cobertura total pré-jogo
ou granularidade por atleta para operadora deve ser recusado no backend, não negociado na tela.

---

## O que existe hoje, e o que não existe

**Existe e está validado:**

* Base completa: Série A 2003–2025 e Série B 2022–2025, mais 2026 em curso. 11.220 partidas,
  34.248 cartões, 107.990 registros de atleta × partida.
* Escore de risco pré-jogo por atleta escalado, com ganho medido de 2,4× a 3,0× sobre seleção
  aleatória, validado em 210 rodadas de walk-forward e aprovado em teste determinístico de
  vazamento temporal.
* Escores de anomalia por partida e por atleta, com a ressalva de que **não discriminam melhor
  que sorteio no nível da partida**.
* Camadas de exposição e matriz de perfis, executáveis em código.
* Pipeline de ingestão incremental idempotente, com verificação por ETag e SHA-256.
* Feed de produto em JSON e SQLite, regenerável por um comando.

**Não existe:**

* Qualquer API. O acesso hoje é por arquivo gerado em lote.
* Qualquer autenticação ou noção de identidade do chamador.
* Qualquer modelo de tenant. `aplicar_perfil()` recebe `clube_do_cliente` como argumento — ou
  seja, **quem chama declara quem é**. No backend isso tem que vir do token.
* Qualquer interface.

Os documentos 01 a 05 especificam exatamente essa lacuna.

> **Atualização de 2026-09-23.** A API, a autenticação por chave e o modelo de perfil vindo da
> credencial foram implementados na POC da etapa 4. O que foi feito, e onde difere deste
> contrato, está em [`docs/backend.md`](../backend.md) e
> [`docs/integracao_frontend.md`](../integracao_frontend.md). A interface continua não existindo.

---

> **LGPD.** O sistema trata dado pessoal de atletas — nome, registro CBF, histórico
> disciplinar — e a camada identificada os expõe nominalmente. A avaliação de impacto e a
> definição de base legal (tarefa F4-01) **não foram feitas** e permanecem como condição para
> qualquer uso fora do ambiente acadêmico.
>
> Caso o seu projeto envolva dados pessoais ou dados pessoais sensíveis, comunique ao time de
> Segurança da Informação através do e-mail seginfo@gcb.com.br
