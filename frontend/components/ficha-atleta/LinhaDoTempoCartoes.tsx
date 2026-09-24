import type { CartaoEvento } from "@/lib/types/atleta";

interface LinhaDoTempoCartoesProps {
  eventos: CartaoEvento[];
}

const ROTULO_TIPO: Record<CartaoEvento["tipo"], string> = {
  amarelo: "Amarelo",
  vermelho: "Vermelho",
};

/**
 * Doc 03, §3: onde `motivo_completo` for nulo (~86% da Série A), mostrar que
 * é limitação da fonte, não falha do sistema — nunca um campo vazio que
 * parece bug.
 */
export function LinhaDoTempoCartoes({ eventos }: LinhaDoTempoCartoesProps) {
  if (eventos.length === 0) {
    return <p className="text-sm text-muted">Nenhum cartão registrado.</p>;
  }

  const porAno = new Map<number, CartaoEvento[]>();
  for (const evento of eventos) {
    const lista = porAno.get(evento.ano) ?? [];
    lista.push(evento);
    porAno.set(evento.ano, lista);
  }
  const anos = [...porAno.keys()].sort((a, b) => b - a);

  return (
    <div>
      <h2 className="mb-2 text-sm font-semibold text-ink">Linha do tempo de cartões</h2>
      <div className="flex flex-col gap-4">
        {anos.map((ano) => (
          <div key={ano}>
            <p className="mb-1 text-xs font-medium tracking-wide text-muted uppercase">
              {ano}
            </p>
            <ul className="divide-y divide-line overflow-hidden rounded-2xl border border-line bg-surface shadow-card">
              {porAno.get(ano)!.map((evento, i) => (
                <li key={i} className="flex flex-col gap-0.5 px-4 py-2 text-sm">
                  <span className="text-body">
                    {evento.minuto}&apos; · {evento.periodo} · {ROTULO_TIPO[evento.tipo]}
                    {evento.categoria ? ` · ${evento.categoria}` : ""}
                  </span>
                  <span className="text-xs text-muted italic">
                    {evento.motivoCompleto ?? "Motivo não registrado na súmula desta temporada."}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
