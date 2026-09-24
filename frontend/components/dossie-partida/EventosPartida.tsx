import type { EventoPartida as EventoPartidaType } from "@/lib/types/partida";

interface EventosPartidaProps {
  eventos: EventoPartidaType[];
}

const ROTULO_TIPO: Record<EventoPartidaType["tipo"], string> = {
  amarelo: "Amarelo",
  vermelho: "Vermelho",
};

/** Seção 3 do dossiê (doc 03, §4): cartões com minuto, período e motivo. */
export function EventosPartida({ eventos }: EventosPartidaProps) {
  if (eventos.length === 0) {
    return <p className="text-sm text-zinc-500 dark:text-zinc-400">Nenhum cartão registrado nesta partida.</p>;
  }

  return (
    <div>
      <h2 className="mb-2 text-sm font-semibold text-zinc-900 dark:text-zinc-50">Eventos</h2>
      <ul className="divide-y divide-zinc-200 rounded-md border border-zinc-200 dark:divide-zinc-800 dark:border-zinc-800">
        {eventos.map((evento, i) => (
          <li key={i} className="flex flex-col gap-0.5 px-4 py-2 text-sm">
            <span className="text-zinc-700 dark:text-zinc-300">
              {evento.minuto}&apos; · {evento.periodo} · {ROTULO_TIPO[evento.tipo]} · {evento.clubeNome}
            </span>
            <span className="text-xs text-zinc-500 italic dark:text-zinc-400">
              {evento.motivo ?? "Motivo não registrado na súmula desta partida."}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
