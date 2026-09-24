import type { Condicao, FilaTriagemItem } from "@/lib/types/fila-triagem";

const ROTULO_CONDICAO: Record<Condicao, string> = {
  titular: "titular",
  reserva: "reserva",
};

/**
 * Linha de justificativa (doc 03, §2): "montar a partir de `componentes`, em
 * linguagem natural" — a transparência do escore como conta aberta é o que
 * torna a fila útil para fundamentar um despacho.
 */
export function formatarJustificativa(item: FilaTriagemItem): string {
  const { cartoes1T, minutosJogados, taxaAjustada } = item.componentes;
  const minutos = minutosJogados.toLocaleString("pt-BR");
  const taxa = taxaAjustada.toLocaleString("pt-BR", {
    minimumFractionDigits: 5,
    maximumFractionDigits: 5,
  });
  return `${cartoes1T} cartões no 1º tempo em ${minutos} minutos jogados · ${ROTULO_CONDICAO[item.condicao]} · taxa ajustada ${taxa}`;
}
