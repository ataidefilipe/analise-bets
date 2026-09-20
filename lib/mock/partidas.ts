import type {
  AtletaSinalizado,
  DossiePartida,
  EventoPartida,
  IdentificacaoPartida,
  Procedencia,
} from "@/lib/types/partida";
import { CLUBES_MOCK } from "@/lib/mock/clubes";
import { gerarNome } from "@/lib/mock/nomes";
import { criarGeradorAleatorio, seedFromString } from "@/lib/mock/random";
import { tierPorPercentil } from "@/lib/mock/tier";
import { sortearMotivoCartao } from "@/lib/mock/motivosCartao";
import { AVISO_INTERPRETATIVO } from "@/lib/mock/avisoInterpretativo";

const TAMANHO_POOL = 24;

const ARENAS_MOCK = [
  "Arena Exemplo Norte",
  "Estádio Municipal Exemplo",
  "Arena Exemplo Sul",
  "Estádio Exemplo Central",
];

const ARBITROS_MOCK = ["Carlos Andrade", "Marina Torres", "Eduardo Nunes", "Patrícia Lima", "Rogério Souza"];

const FONTES_MOCK = ["CBF — Súmula oficial", "Federação Estadual — Súmula oficial"];

const RESSALVA_PARTIDA =
  "No nível da partida, o escore de anomalia não discrimina melhor que sorteio aleatório. A confiabilidade estatística existe apenas na agregação por atleta, ao longo de uma amostra maior de minutos jogados.";

function somarDias(dataISO: string, dias: number): string {
  const data = new Date(dataISO);
  data.setDate(data.getDate() + dias);
  return data.toISOString().slice(0, 10);
}

function gerarHashFake(rand: () => number): string {
  const alfabeto = "0123456789abcdef";
  let hash = "";
  for (let i = 0; i < 64; i++) {
    hash += alfabeto[Math.floor(rand() * alfabeto.length)];
  }
  return hash;
}

/** Identificação determinística a partir do id — mesmo id sempre gera a mesma partida. */
function gerarIdentificacao(partidaId: string): IdentificacaoPartida {
  const rand = criarGeradorAleatorio(seedFromString(partidaId));

  const idxMandante = Math.floor(rand() * CLUBES_MOCK.length);
  const idxVisitante = (idxMandante + 1 + Math.floor(rand() * (CLUBES_MOCK.length - 1))) % CLUBES_MOCK.length;

  const diasAtras = 3 + Math.floor(rand() * 400);
  const data = somarDias(new Date().toISOString().slice(0, 10), -diasAtras);

  return {
    partidaId,
    competicao: rand() < 0.5 ? "serie-a" : "serie-b",
    ano: Number(data.slice(0, 4)),
    rodada: 1 + Math.floor(rand() * 38),
    data,
    arena: ARENAS_MOCK[Math.floor(rand() * ARENAS_MOCK.length)],
    arbitro: ARBITROS_MOCK[Math.floor(rand() * ARBITROS_MOCK.length)],
    clubeMandante: CLUBES_MOCK[idxMandante].nome,
    clubeVisitante: CLUBES_MOCK[idxVisitante].nome,
    placar: { mandante: Math.floor(rand() * 4), visitante: Math.floor(rand() * 4) },
  };
}

const POOL_PARTIDAS: IdentificacaoPartida[] = Array.from({ length: TAMANHO_POOL }, (_, i) =>
  gerarIdentificacao(`partida-${i}`),
);

/**
 * Mais recentes primeiro — não há tela de fila de partidas no doc 03; esta
 * listagem existe só para navegar até um dossiê. Sem `consulta` (ou com
 * menos de 3 caracteres) devolve todas; com 3+ caracteres, filtra pelo nome
 * de um dos dois clubes.
 */
export async function listarPartidas(consulta: string = ""): Promise<IdentificacaoPartida[]> {
  const termo = consulta.trim().toLowerCase();
  const base =
    termo.length >= 3
      ? POOL_PARTIDAS.filter(
          (partida) =>
            partida.clubeMandante.toLowerCase().includes(termo) ||
            partida.clubeVisitante.toLowerCase().includes(termo),
        )
      : POOL_PARTIDAS;

  return [...base].sort((a, b) => b.data.localeCompare(a.data));
}

/** Simula `GET /partidas/{id}/dossie` (doc 01, ainda não recebido). Qualquer id produz um dossiê plausível e estável. */
export async function getDossiePartida(partidaId: string): Promise<DossiePartida> {
  const identificacao = POOL_PARTIDAS.find((p) => p.partidaId === partidaId) ?? gerarIdentificacao(partidaId);
  const rand = criarGeradorAleatorio(seedFromString(`${partidaId}-dossie`));

  const procedencia: Procedencia = {
    fonte: FONTES_MOCK[Math.floor(rand() * FONTES_MOCK.length)],
    urlSumula: `https://cbf.com.br/sumulas/${identificacao.competicao}/${identificacao.ano}/rodada-${identificacao.rodada}/${partidaId}.pdf`,
    sha256: gerarHashFake(rand),
    dataDownload: somarDias(identificacao.data, 1),
    dataProcessamento: somarDias(identificacao.data, 2),
  };

  const numEventos = 2 + Math.floor(rand() * 6); // 2–7 cartões
  const eventos: EventoPartida[] = Array.from({ length: numEventos }, () => {
    const noPrimeiroTempo = rand() < 0.45;
    return {
      minuto: noPrimeiroTempo ? 1 + Math.floor(rand() * 45) : 46 + Math.floor(rand() * 49),
      periodo: noPrimeiroTempo ? ("1T" as const) : ("2T" as const),
      tipo: rand() < 0.9 ? ("amarelo" as const) : ("vermelho" as const),
      clubeNome: rand() < 0.5 ? identificacao.clubeMandante : identificacao.clubeVisitante,
      motivo: sortearMotivoCartao(rand),
    };
  }).sort((a, b) => a.minuto - b.minuto);

  // Doc 03, §4: no nível da partida o escore não discrimina melhor que sorteio —
  // por isso gerado uniforme, sem a cauda longa usada nos escores por atleta.
  const escoreAnomaliaPercentil = Math.round(rand() * 100);

  const numSinalizados = Math.min(3, Math.ceil(numEventos / 3));
  const atletasSinalizados: AtletaSinalizado[] = Array.from({ length: numSinalizados }, (_, i) => {
    const percentilAtleta = 70 + Math.floor(rand() * 30);
    return {
      atletaId: `${partidaId}-sinalizado-${i}`,
      atleta: gerarNome(Math.floor(rand() * 1000)),
      clubeNome: i % 2 === 0 ? identificacao.clubeMandante : identificacao.clubeVisitante,
      tier: tierPorPercentil(percentilAtleta),
      percentil: percentilAtleta,
    };
  });

  return {
    identificacao,
    procedencia,
    eventos,
    avisoInterpretativo: AVISO_INTERPRETATIVO,
    escoreAnomaliaPercentil,
    ressalvaPartida: RESSALVA_PARTIDA,
    atletasSinalizados,
  };
}
