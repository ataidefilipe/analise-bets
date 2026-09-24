import { Callout } from "@/components/ui/Callout";

interface EscoreAnomaliaPartidaProps {
  /** `null` fora da janela do escore de anomalia de partida (doc 02, §7). */
  percentil: number | null;
  tier: string | null;
  ressalva: string;
}

/**
 * Seção 4 do dossiê (doc 03, §4): sem a ressalva de que o escore no nível
 * da partida não discrimina melhor que sorteio, a tela promete o que a
 * validação não sustenta. Fora da janela, a ressalva explica a ausência.
 */
export function EscoreAnomaliaPartida({ percentil, tier, ressalva }: EscoreAnomaliaPartidaProps) {
  return (
    <div className="flex flex-col gap-2">
      <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Escore de anomalia da partida</h2>
      {percentil !== null && (
        <p className="text-sm text-zinc-700 dark:text-zinc-300">
          Percentil {percentil.toLocaleString("pt-BR", { maximumFractionDigits: 1 })}
          {tier ? ` · ${tier}` : ""}
        </p>
      )}
      <Callout>{ressalva}</Callout>
    </div>
  );
}
