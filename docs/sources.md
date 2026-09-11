# Mapeamento de Fontes de Dados e Auditoria Documental

**Projeto:** Impacto das Apostas Esportivas no Futebol Brasileiro  
**Documento de Governança de Fontes:** `docs/sources.md`  
**Última Atualização:** 2026-09-10  

---

## 1. Visão Geral das Fontes

Em conformidade com a Seção 29 do [`README.md`](file:///d:/Python%20Projetos/analise-bets/README.md) e as seções 4, 5 e 16 do [`.agent.md`](file:///d:/Python%20Projetos/analise-bets/.agent.md), nenhum dado é incorporado às bases analíticas processadas sem o registro explícito de sua origem primária, método de extração, período de cobertura, nível de confiabilidade e processo de auditoria.

O projeto opera com **cinco pilares documentais e de dados**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             ARQUITETURA DE FONTES                           │
├───────────────────────────────┬─────────────────────────────────────────────┤
│ 1. DADOS ESPORTIVOS           │ 2. EXPOSIÇÃO ECONÔMICA & PATROCÍNIOS        │
│ • Adão Duque (2003–2024)      │ • IBOPE Repucom (Mapa do Patrocínio)        │
│ • Súmulas Eletrônicas CBF     │ • Balanços Patrimoniais Oficiais dos Clubes │
│ • Sofascore (Validação)       │ • Imprensa Especializada de Negócios (GE/MKT)│
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 3. DEMANDA DIGITAL MACRO      │ 4. REGULAÇÃO & INTEGRIDADE                  │
│ • Google Trends Brasil        │ • Ministério da Fazenda (SPA / SIGAP)       │
│   (2015–2025)                 │ • Autos Judiciais (Op. Penalidade Máxima)   │
│                               │ • Alertas de Integridade (IBIA / Sportradar)│
├───────────────────────────────┴─────────────────────────────────────────────┤
│ 5. LITERATURA CIENTÍFICA & FUNDAMENTAÇÃO TEÓRICA                            │
│ • Econometria Forense (AER / JLE): Duggan & Levitt (2002), Wolfers (2006)   │
│ • Micro-Apostas & Spot-Fixing: Carpenter (2012), Forrest (2012), Hill (2010)│
│ • Governança Global: ONU/UNODC (2021), Convenção de Macolin (2014)          │
│ • Inferência Causal: Callaway & Sant'Anna (2021), Goodman-Bacon (2021)      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. De Onde Vem a Informação de que "Time Tem Bet"?

A compilação histórica dos patrocínios de casas de apostas nos 34 clubes que disputaram a Série A entre 2015 e 2024 (totalizando 200 registros de clube $\times$ temporada) foi estruturada no arquivo [`data/raw/betting/serie_a_patrocinios_2015_2024.csv`](file:///d:/Python%20Projetos/analise-bets/data/raw/betting/serie_a_patrocinios_2015_2024.csv) pelo script [`src/ingestion/build_betting_data.py`](file:///d:/Python%20Projetos/analise-bets/src/ingestion/build_betting_data.py).

Essa informação decorre do cruzamento de três fontes documentais independentes:

### 2.1 Censo do IBOPE Repucom (*Mapa do Patrocínio do Futebol Brasileiro*)
* **O que é:** Estudo censitário publicado anualmente pela consultoria multinacional IBOPE Repucom, considerada o padrão ouro da indústria para auditoria de mídia e marketing esportivo no Brasil.
* **Metodologia do IBOPE:** Monitoramento contínuo de 100% das partidas da Série A, catalogando todas as propriedades dos uniformes dos 20 clubes:
  * Espaço Máster (peito/barriga frontal);
  * Mangas;
  * Omoplata;
  * Costas (superior e inferior);
  * Barra frontal e traseira;
  * Calção (frontal e traseiro) e meiões.
* **Classificação Setorial:** O IBOPE Repucom categoriza os patrocinadores pelo setor econômico *"Apostas / Loterias"*, permitindo quantificar o salto de marcas ativas:
  * 2018: 0 marcas
  * 2019: 5 marcas
  * 2021: 11 marcas
  * 2023: 12 marcas
  * 2024: 15 marcas ativas e 18 clubes com bet máster.

### 2.2 Balanços Patrimoniais e Demonstrações Contábeis dos Clubes
* **O que é:** Demonstrações financeiras anuais obrigatórias por força da Lei Pelé (Lei nº 9.615/1998) e da Lei da SAF (Lei nº 14.193/2021), auditadas por auditorias externas independentes (ex.: PwC, EY, KPMG, BDO).
* **Evidência Contábil:** As notas explicativas da rubrica *"Receitas de Patrocínio e Publicidade"* discriminam os patrocinadores contratuais e valores auferidos:
  * *Exemplo 1 (Flamengo):* Balanços oficiais registram contratos com *Sportsbet.io* (2020–2021), transição para *Pixbet* (2022–2023 nas costas/mangas) e novo contrato máster em 2024 (R$ 105 milhões anuais).
  * *Exemplo 2 (Atlético-MG):* Balanços detalham o patrocínio máster contínuo da *Betano* desde 2021.
  * *Exemplo 3 (Palmeiras):* Demonstrações financeiras comprovam contrato exclusivo com a *Crefisa / Faculdade das Américas (FAM)* até dezembro de 2024, atestando ausência total de marcas de apostas no uniforme durante o período analisado.

### 2.3 Marco Legal e Registro de Negócios Esportivos
A presença das marcas segue estritamente a cronologia legal do Brasil:
1. **2015–2017 (Proibição Legal):** Apostas de quota fixa eram qualificadas como contravenção penal (Decreto-Lei nº 3.688/1941, art. 50). Nenhuma empresa de apostas podia operar legalmente ou estampar marcas no futebol brasileiro. `tem_patrocinio_bet = False` para todos os clubes.
2. **2018 (Sanção Tardia da Lei 13.756/2018):** Sancionada pelo presidente Michel Temer em **12 de dezembro de 2018**, autorizando a modalidade no país. O Brasileirão 2018 teve sua última rodada em **02 de dezembro de 2018** (dez dias antes). Portanto, nenhum jogo da Série A 2018 teve patrocínio de apostas em campo.
3. **2019 (Abertura de Mercado):** Início dos primeiros patrocínios na Série A catalogados pela imprensa de negócios (*Máquina do Esporte*, *MKT Esportivo*, *GE/Globo Esporte*):
   * *Marjosports:* máster em Goiás e Fortaleza; mangas no Corinthians.
   * *NetBet:* máster no Fortaleza e Vasco da Gama.
   * *Dafabet:* máster na Chapecoense.
   * *Casa de Apostas:* propriedades secundárias no Bahia, Botafogo, Cruzeiro e Santos.
4. **2021–2024 (Saturação e Megacontratos):**
   * Entrada de multinacionais (*Betano*, *Superbet*, *Parimatch*, *Betfair*, *Stake*) e operadores nacionais (*Pixbet*, *Esportes da Sorte*, *EstrelaBet*, *Blaze*).

---

## 3. Fontes de Dados de Partidas e Disciplina (MVP 1)

### 3.1 Dataset Adão Duque (Brasileirão Dataset)
* **Repositório:** `https://github.com/adaoduque/Brasileirao_Dataset`
* **Localização Bruta:** [`data/raw/adaoduque/`](file:///d:/Python%20Projetos/analise-bets/data/raw/adaoduque/)
* **Integridade Criptográfica:** Hashes SHA-256 documentados em [`data/raw/adaoduque/manifest.json`](file:///d:/Python%20Projetos/analise-bets/data/raw/adaoduque/manifest.json).
* **Cobertura Auditada:**
  * `campeonato-brasileiro-full.csv`: 8.785 partidas (2003 a 2024).
  * `campeonato-brasileiro-cartoes.csv`: 20.953 cartões individuais com atleta, clube, posição e minuto contínuo (2014 a 2024).
  * `campeonato-brasileiro-gols.csv`: 9.861 gols com tipo (normal, pênalti, contra) e minuto (2014 a 2024).
  * `campeonato-brasileiro-estatisticas-full.csv`: 17.570 registros de scouts (2003 a 2024).
### 3.2 Dataset Sofascore (Scouts da Série A 2024)
* **Repositório:** `https://github.com/leeofernandes1980/brasileirao-dataset` (camada `datalake/silver/`)
* **Localização Bruta:** [`data/raw/sofascore/`](file:///d:/Python%20Projetos/analise-bets/data/raw/sofascore/)
* **Integridade Criptográfica:** Hashes SHA-256 em [`manifest.json`](file:///d:/Python%20Projetos/analise-bets/data/raw/sofascore/manifest.json).
* **Cobertura:** 380 partidas da Série A de 2024 (760 registros clube-partida).
* **Finalidade Metodológica:** Fechamento da lacuna de scouts agregados (faltas, escanteios, chutes, passes, posse) da Série A de 2024 deixada zerada na raspagem do Google do dataset do Adão Duque.
* **Volume:** 9.585 faltas registradas em 2024, permitindo o cálculo definitivo da taxa de conversão $\tau_{\text{CF}}$ para 2024.

### 3.3 Súmulas Eletrônicas da CBF (Divisões de Acesso: Séries B, C e D)
* **Fonte Primária Oficial:** Confederação Brasileira de Futebol (CDN: `https://conteudo.cbf.com.br/sumulas/{ano}/{codigo}{jogo}se.pdf`)
* **Códigos Canônicos Identificados:**
  * Série A: `142`
  * Série B: `242`
  * Série C: `342`
  * Série D: `542`
* **Localização Bruta Ingerida:** 
  * [`data/raw/cbf/sumulas_serie_b_2022/`](file:///d:/Python%20Projetos/analise-bets/data/raw/cbf/sumulas_serie_b_2022/): 380 PDFs oficiais (100% da edição de 2022) com manifesto SHA-256.
  * [`data/raw/cbf/sumulas_serie_b_2023/`](file:///d:/Python%20Projetos/analise-bets/data/raw/cbf/sumulas_serie_b_2023/): 380 PDFs oficiais (100% da edição de 2023) com manifesto SHA-256.
* **Volume Processado:** 760 partidas, 3.671 cartões e 2.137 gols estruturados em [`data/processed/serie_b/`](file:///d:/Python%20Projetos/analise-bets/data/processed/serie_b/).
* **Achado Crítico de Governança:** Árbitros **não** registram contagem corrida de faltas ou escanteios nas súmulas (função delegada a data providers como Opta/Sofascore). Contudo, as súmulas fornecem com 100% de autenticidade oficial:
  * Cabeçalho completo, arbitragem (campo e VAR) e cronologia com acréscimos;
  * Gols com autoria, minuto e tipo;
  * Todos os cartões amarelos e vermelhos com jogador, minuto e o **texto literal do motivo da infração**, viabilizando a categorização de infrações (faltas temerárias, reclamação, cera/retardamento, conduta antidesportiva).

---

## 4. Fontes de Demanda Digital Macro e Integridade Judicial

### 4.1 Google Trends Brasil
* **Termos Consolidados:** `bet`, `bets`, `apostas esportivas`, `betano`, `bet365`, `sportingbet`.
* **Âmbito Geográfico:** Brasil (`geo='BR'`).
* **Série Histórica:** 2015–2025 em periodicidade mensal (132 registros) e anual (11 registros).
* **Localização Processada:** [`data/processed/betting/trends_mensal.parquet`](file:///d:/Python%20Projetos/analise-bets/data/processed/betting/trends_mensal.parquet) e `trends_anual.parquet`.
* **Papel Metodológico:** Atua como *proxy* contínuo de atenção pública e penetração digital da atividade apostadora, alimentando a variável $S_{\text{macro}}$ do índice `BET_EXPOSURE`.

### 4.2 Autos Judiciais e Acórdãos Desportivos — Operação Penalidade Máxima (MP-GO e STJD)
* **Origem Documental:**
  * **Ministério Público do Estado de Goiás (MP-GO / GAECO):** Denúncias criminais das Fases 1, 2 e 3 da Operação Penalidade Máxima (Autos dos Processos nº 5174836-81.2023.8.09.0051 e conexos da 2ª Vara Estadual dos Feitos Relativos a Delitos Praticados por Organização Criminosa).
  * **Superior Tribunal de Justiça Desportiva (STJD):** Processos Disciplinares nº 003/2023, 052/2023, 085/2023 e Acórdãos do Tribunal Pleno.
* **Conteúdo Probatório Auditado:** Conversas periciadas de WhatsApp entre apostadores e atletas, transferências bancárias via PIX comprovando sinais e quitações financeiras, termos de colaboração premiada e confissões formais em juízo.
* **Localização Processada:** [`data/processed/integrity/casos_penalidade_maxima.parquet`](file:///d:/Python%20Projetos/analise-bets/data/processed/integrity/casos_penalidade_maxima.parquet) e `.csv` (14 casos catalogados).
* **Papel Metodológico:** Constitui a base empírica de *ground truth* (eventos ilícitos comprovados). Utilizada para:
  1. Calibrar thresholds estatísticos de anomalia temporal (concentração no 1º tempo);
  2. Contrastar o perfil de jogadores aliciados com a população geral de atletas;
  3. Validar a sensibilidade dos filtros de detecção desenvolvidos no projeto sem incorrer em acusações infundadas.

---

## 5. Matriz Resumo de Confiabilidade das Fontes

| Dimensão de Dados | Fonte Primária | Período Auditado | Nível de Confiabilidade | Papel no Pipeline |
| :--- | :--- | :---: | :---: | :--- |
| **Resultados e Jogos (Série A)** | Adão Duque / CBF | 2003–2024 | **Alto** (100% verificado) | Base do MVP 1 |
| **Cartões Individuais (Série A)**| Adão Duque / Súmulas | 2014–2024 | **Excelente** (20.953 cartões) | Testes de integridade (MVP 1 e 4) |
| **Scouts e Faltas (Série A)** | Adão Duque (2015–23) + Sofascore (2024) | 2015–2024 | **Alto** (100% preenchido) | Taxa de conversão cartão/falta |
| **Partidas e Cartões (Série B)** | Súmulas Eletrônicas CBF | 2022–2023 | **Oficial Máxima** (760 PDFs autenticados)| Comparação Séries A vs. B |
| **Casos Judiciais de Integridade**| MP-GO (GAECO) / STJD | 2022 | **Jurídica Plena** (Denúncias e Acórdãos)| Ground Truth de calibração |
| **Patrocínios Clubes** | IBOPE Repucom / Balanços | 2015–2024 | **Alto** (200 registros auditados)| Cálculo do `BET_EXPOSURE` (MVP 2) |
| **Interesse Público** | Google Trends Brasil | 2015–2025 | **Alto** (Normalizado [0, 100]) | Efeito macro e transbordamento |
| **Volume de Apostas** | Sigiloso (Operadoras) | Não público | **Fora do Caminho Crítico** | Substituído por proxies públicas |
| **Literatura & Integridade** | Artigos Peer-Reviewed / ONU / Macolin | 2002–2024 | **Científica / Tratados** | Fundamentação teórica e causal (`docs/revisao_bibliografica.md`) |

---

## 6. Literatura Científica e Documentos Institucionais de Referência

A fundamentação teórica completa, catalogação de artigos e matriz de vinculação aos módulos do projeto encontram-se sistematizados em [`docs/revisao_bibliografica.md`](file:///d:/Python%20Projetos/analise-bets/docs/revisao_bibliografica.md).

* **Econometria Forense:** Duggan & Levitt (2002, AER), Wolfers (2006, AER), Preston & Szymanski (2003).
* **Micro-Apostas & Spot-Fixing:** Carpenter (2012), Forrest (2012), Hill (2010), Haberfeld & Sheehan (2013).
* **Economia do Esporte & Patrocínio:** Lopez-Gonzalez & Griffiths (2018), Buning & Palmer (2020), Szymanski (2003).
* **Comportamento Arbitral:** Garicano et al. (2005, JLE), Buraimo et al. (2010, JRSS), Pettersson-Lidbom & Priks (2010).
* **Governança & Tratados Internacionais:** UNODC/IOC (2021), Convenção de Macolin (Conselho da Europa, 2014), Sportradar (2023, 2024), IBIA (2024).
* **Inferência Causal:** Callaway & Sant'Anna (2021), Goodman-Bacon (2021), Cameron & Miller (2015).

