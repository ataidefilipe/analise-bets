# Decisão sobre o histórico do Git — exposição nominal de atletas

**Tarefa:** F4-02, item "decisão registrada sobre o repositório"
**Data:** 2026-09-18
**Status:** **Decisão pendente do responsável pelo projeto.** Nenhuma reescrita foi executada.

---

## O fato

A pseudonimização aplicada nesta tarefa corrige o estado **atual** da árvore de trabalho. Ela
não alcança o histórico: o repositório está publicado em
`github.com/ataidefilipe/analise-bets`, e os commits anteriores continuam contendo os nomes.

| Item | Situação |
| :--- | :--- |
| Commits publicados no remoto | 15, com `origin/main` em `876f9c7` |
| Commits que tocam tabelas nominais | 3 |
| Atletas nominados na Tabela 16 publicada | 50, dos quais 10 são condenados e **40 nunca foram investigados** |
| Outras tabelas afetadas no histórico | Tabela 03 (17 atletas) e Tabela 20 (41 atletas) |

Qualquer pessoa com acesso ao repositório consegue recuperar as listas nominais com um
`git show`, mesmo depois de a versão atual estar pseudonimizada.

## As opções

### A — Reescrever o histórico
Remover os arquivos dos commits antigos com `git filter-repo` e forçar o push.

* **A favor:** elimina a exposição de fato. É o único caminho que realmente remove o dado.
* **Contra:** reescreve todos os hashes a partir do primeiro commit afetado; quebra qualquer
  clone ou fork existente; exige coordenação com quem já clonou. Se o repositório for público,
  **não garante remoção**: o GitHub mantém objetos órfãos acessíveis por hash durante um
  período, e forks já criados permanecem intactos. Exige abrir chamado de suporte ao GitHub
  para purga completa.

### B — Tornar o repositório privado e reescrever
Fechar o acesso público, reescrever o histórico e só então reabrir, se for o caso.

* **A favor:** resolve a exposição e a limitação técnica da opção A ao mesmo tempo.
* **Contra:** o repositório deixa de ser publicamente verificável, o que é parte do argumento
  de reprodutibilidade do trabalho acadêmico.

### C — Aceitar e documentar
Manter o histórico, registrar a limitação e garantir que nada novo seja publicado nominalmente.

* **A favor:** custo zero, sem quebrar clones.
* **Contra:** a exposição permanece acessível. Uma eventual reclamação de atleta não é
  respondida por "corrigimos daqui em diante".

## Recomendação

**Opção B**, se o repositório for público hoje. A exposição de 40 atletas nunca investigados,
associados a um ranking rotulado "atletas anômalos" num projeto sobre manipulação de
resultados, é o risco mais concreto do trabalho — e é exatamente o que a tarefa F4-02 existe
para eliminar.

Se o repositório já for privado e restrito à equipe, a **opção C** é defensável: o público
exposto se limita a quem já tem acesso autorizado, e o custo de reescrever supera o ganho.

## O que não foi feito, e por quê

Reescrever histórico publicado é destrutivo e irreversível para terceiros. É decisão de quem
responde pelo projeto, não de quem executa a tarefa. O tratamento fica registrado aqui para
ser decidido e executado conscientemente.

Enquanto a decisão não for tomada, vale a ressalva já registrada no termo de uso: **o termo não
pode ser oposto a terceiros** com base na proteção da árvore atual, porque o histórico continua
acessível.

## Se a opção A ou B for escolhida

```bash
# Requer git-filter-repo (pip install git-filter-repo)
git filter-repo --path reports/tables/tabela_03_atletas_outliers_1T.csv \
                --path reports/tables/tabela_16_ranking_atletas_anomalos.csv \
                --path reports/tables/tabela_20_classificacao_atletas_ml.csv \
                --invert-paths
```

Depois: recriar as tabelas pseudonimizadas a partir dos geradores, forçar o push, avisar quem
tiver clone e, no caso de repositório público, abrir chamado ao suporte do GitHub pedindo a
purga dos objetos órfãos.

> Caso o seu projeto envolva dados pessoais ou dados pessoais sensíveis, comunique ao time de
> Segurança da Informação através do e-mail seginfo@gcb.com.br
