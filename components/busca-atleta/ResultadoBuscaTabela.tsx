"use client";

import { useState } from "react";
import Link from "next/link";
import type { AtletaResumo } from "@/lib/types/atleta";

interface ResultadoBuscaTabelaProps {
  itens: AtletaResumo[];
}

const INCREMENTO = 10;

/**
 * Tabela de atletas em ordem alfabética (já vem ordenada de
 * `listarAtletas`), 10 por vez — "Carregar mais" soma mais 10 aos já
 * exibidos, sem trocar de página. Só identificação e clubes — nunca escore
 * ou tier (doc 03, §3). Ver docs/passo-05-tabela-completa-atletas.md.
 */
export function ResultadoBuscaTabela({ itens }: ResultadoBuscaTabelaProps) {
  const [quantidadeVisivel, setQuantidadeVisivel] = useState(INCREMENTO);
  const visiveis = itens.slice(0, quantidadeVisivel);
  const temMais = quantidadeVisivel < itens.length;

  return (
    <div className="flex flex-col gap-3">
      <p className="text-sm text-zinc-500 dark:text-zinc-400">
        Mostrando {visiveis.length} de {itens.length} atletas
      </p>

      <div className="overflow-x-auto rounded-md border border-zinc-200 dark:border-zinc-800">
        <table className="w-full min-w-[480px] text-sm">
          <thead>
            <tr className="border-b border-zinc-200 text-left text-xs tracking-wide text-zinc-500 uppercase dark:border-zinc-800 dark:text-zinc-400">
              <th className="px-4 py-2 font-medium">Atleta</th>
              <th className="px-4 py-2 font-medium">Clubes</th>
              <th className="px-4 py-2 font-medium">Até</th>
            </tr>
          </thead>
          <tbody>
            {visiveis.map((atleta) => (
              <tr key={atleta.atletaId} className="border-b border-zinc-100 last:border-0 dark:border-zinc-900">
                <td className="px-4 py-2">
                  <Link
                    href={`/atletas/${atleta.atletaId}`}
                    className="font-medium text-zinc-900 hover:text-brand dark:text-zinc-50 dark:hover:text-link"
                  >
                    {atleta.nome}
                  </Link>
                </td>
                <td className="px-4 py-2 text-zinc-700 dark:text-zinc-300">
                  {atleta.clubes.map((clube) => clube.nome).join(", ")}
                </td>
                <td className="px-4 py-2 text-zinc-500 dark:text-zinc-400">{atleta.ultimoAno}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {temMais && (
        <button
          type="button"
          onClick={() => setQuantidadeVisivel((n) => n + INCREMENTO)}
          className="self-start rounded border border-zinc-300 px-3 py-1.5 text-sm text-zinc-700 transition-colors hover:border-brand hover:text-brand dark:border-zinc-700 dark:text-zinc-300 dark:hover:border-link dark:hover:text-link"
        >
          Carregar mais 10
        </button>
      )}
    </div>
  );
}
