import { Callout } from "@/components/ui/Callout";

interface EscoreAnomaliaPartidaProps {
  percentil: number;
  ressalva: string;
}

/**
 * Seção 4 do dossiê (doc 03, §4): sem a ressalva de que o escore no nível
 * da partida não discrimina melhor que sorteio, a tela promete o que a
 * validação não sustenta.
 */
export function EscoreAnomaliaPartida({ percentil, ressalva }: EscoreAnomaliaPartidaProps) {
  return (
    <div className="flex flex-col gap-2">
      <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Escore de anomalia da partida</h2>
      <p className="text-sm text-zinc-700 dark:text-zinc-300">Percentil {percentil}</p>
      <Callout>{ressalva}</Callout>
    </div>
  );
}
