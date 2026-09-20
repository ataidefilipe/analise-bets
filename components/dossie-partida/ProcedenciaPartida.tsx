import type { Procedencia } from "@/lib/types/partida";
import { formatarData } from "@/lib/format/partida";
import { CopiarTexto } from "@/components/ui/CopiarTexto";

interface ProcedenciaPartidaProps {
  procedencia: Procedencia;
}

const LINHA = "flex flex-col gap-0.5 sm:flex-row sm:items-baseline sm:gap-2";
const ROTULO = "shrink-0 text-xs font-medium tracking-wide text-zinc-500 uppercase dark:text-zinc-400 sm:w-32";

/**
 * "Coração da tela" (doc 03, §4): o que P3 de fato compra é procedência, não
 * predição. Precisa ser copiável e legível — por isso URL e hash têm botão
 * de copiar, em vez de virar um rodapé técnico ilegível.
 */
export function ProcedenciaPartida({ procedencia }: ProcedenciaPartidaProps) {
  return (
    <div className="flex flex-col gap-2 rounded-md border border-zinc-200 p-4 dark:border-zinc-800">
      <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Procedência</h2>

      <div className={LINHA}>
        <span className={ROTULO}>Fonte</span>
        <span className="text-sm text-zinc-700 dark:text-zinc-300">{procedencia.fonte}</span>
      </div>

      <div className={LINHA}>
        <span className={ROTULO}>URL da súmula</span>
        <span className="flex min-w-0 items-center gap-2">
          <span className="truncate font-mono text-sm text-zinc-700 dark:text-zinc-300">{procedencia.urlSumula}</span>
          <CopiarTexto valor={procedencia.urlSumula} />
        </span>
      </div>

      <div className={LINHA}>
        <span className={ROTULO}>SHA-256</span>
        <span className="flex min-w-0 items-center gap-2">
          <span className="font-mono text-sm break-all text-zinc-700 dark:text-zinc-300">{procedencia.sha256}</span>
          <CopiarTexto valor={procedencia.sha256} />
        </span>
      </div>

      <div className={LINHA}>
        <span className={ROTULO}>Download</span>
        <span className="text-sm text-zinc-700 dark:text-zinc-300">{formatarData(procedencia.dataDownload)}</span>
      </div>

      <div className={LINHA}>
        <span className={ROTULO}>Processamento</span>
        <span className="text-sm text-zinc-700 dark:text-zinc-300">
          {formatarData(procedencia.dataProcessamento)}
        </span>
      </div>
    </div>
  );
}
