"use client";

import { useMemo, useState } from "react";
import { CaretUp, CaretDown } from "@phosphor-icons/react";
import { formatarProporcao } from "@/lib/format/proporcao";
import { formatarMedia } from "@/lib/format/agregado";

export interface LinhaAgregado {
  chave: string;
  rotulo: string;
  partidas: number;
  cartoesTotais: number;
  cartoes1T: number;
}

interface AgregadoTabelaProps {
  linhas: LinhaAgregado[];
  /** "Clube" ou "Rodada" — só muda o rótulo da primeira coluna. */
  rotuloColuna: string;
}

type Campo = "rotulo" | "partidas" | "cartoesTotais" | "cartoes1T" | "proporcao" | "media";

const COLUNAS: { campo: Campo; alinhamento: "left" | "right" }[] = [
  { campo: "rotulo", alinhamento: "left" },
  { campo: "partidas", alinhamento: "right" },
  { campo: "cartoesTotais", alinhamento: "right" },
  { campo: "cartoes1T", alinhamento: "right" },
  { campo: "proporcao", alinhamento: "right" },
  { campo: "media", alinhamento: "right" },
];

function valorOrdenacao(linha: LinhaAgregado, campo: Campo): number | string {
  switch (campo) {
    case "rotulo":
      return linha.rotulo;
    case "partidas":
      return linha.partidas;
    case "cartoesTotais":
      return linha.cartoesTotais;
    case "cartoes1T":
      return linha.cartoes1T;
    case "proporcao":
      return linha.cartoesTotais === 0 ? 0 : linha.cartoes1T / linha.cartoesTotais;
    case "media":
      return linha.partidas === 0 ? 0 : linha.cartoesTotais / linha.partidas;
  }
}

/** Tabela ordenável (doc 03, §5) — clicar num cabeçalho alterna a ordenação por aquela coluna. */
export function AgregadoTabela({ linhas, rotuloColuna }: AgregadoTabelaProps) {
  const [ordenacao, setOrdenacao] = useState<{ campo: Campo; direcao: "asc" | "desc" }>({
    campo: "cartoesTotais",
    direcao: "desc",
  });

  const ordenadas = useMemo(() => {
    const copia = [...linhas];
    copia.sort((a, b) => {
      const va = valorOrdenacao(a, ordenacao.campo);
      const vb = valorOrdenacao(b, ordenacao.campo);
      const comparacao = typeof va === "string" ? va.localeCompare(vb as string, "pt-BR") : va - (vb as number);
      return ordenacao.direcao === "asc" ? comparacao : -comparacao;
    });
    return copia;
  }, [linhas, ordenacao]);

  function alternar(campo: Campo) {
    setOrdenacao((atual) =>
      atual.campo === campo
        ? { campo, direcao: atual.direcao === "asc" ? "desc" : "asc" }
        : { campo, direcao: campo === "rotulo" ? "asc" : "desc" },
    );
  }

  const rotulos: Record<Campo, string> = {
    rotulo: rotuloColuna,
    partidas: "Partidas",
    cartoesTotais: "Cartões",
    cartoes1T: "1º tempo",
    proporcao: "Proporção",
    media: "Média/partida",
  };

  return (
    <div className="overflow-x-auto rounded-2xl border border-line bg-surface shadow-card">
      <table className="w-full min-w-120 text-sm">
        <thead>
          <tr className="border-b border-line text-xs tracking-wide text-muted uppercase">
            {COLUNAS.map(({ campo, alinhamento }) => (
              <th key={campo} className={`px-4 py-2 font-medium ${alinhamento === "right" ? "text-right" : "text-left"}`}>
                <button
                  type="button"
                  onClick={() => alternar(campo)}
                  className={`inline-flex items-center gap-1 hover:text-ink ${
                    alinhamento === "right" ? "flex-row-reverse" : ""
                  }`}
                >
                  {rotulos[campo]}
                  {ordenacao.campo === campo &&
                    (ordenacao.direcao === "asc" ? (
                      <CaretUp size={12} weight="bold" />
                    ) : (
                      <CaretDown size={12} weight="bold" />
                    ))}
                </button>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ordenadas.map((linha) => (
            <tr key={linha.chave} className="border-b border-line-soft last:border-0">
              <td className="px-4 py-2 text-ink">{linha.rotulo}</td>
              <td className="px-4 py-2 text-right text-body">{linha.partidas}</td>
              <td className="px-4 py-2 text-right text-body">{linha.cartoesTotais}</td>
              <td className="px-4 py-2 text-right text-body">{linha.cartoes1T}</td>
              <td className="px-4 py-2 text-right text-body">
                {formatarProporcao(linha.cartoes1T, linha.cartoesTotais)}
              </td>
              <td className="px-4 py-2 text-right text-body">
                {formatarMedia(linha.cartoesTotais, linha.partidas)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
