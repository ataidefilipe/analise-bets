import type { Procedencia } from "@/lib/types/partida";
import { formatarData } from "@/lib/format/partida";
import { CopiarTexto } from "@/components/ui/CopiarTexto";

interface ProcedenciaPartidaProps {
  /** `null` onde não há súmula eletrônica com URL e hash registrados. */
  procedencia: Procedencia | null;
}

const LINHA = "flex flex-col gap-0.5 sm:flex-row sm:items-baseline sm:gap-2";
const ROTULO = "shrink-0 text-xs font-medium tracking-wide text-muted uppercase sm:w-32";

/**
 * "Coração da tela" (doc 03, §4): o que P3 de fato compra é procedência, não
 * predição. Precisa ser copiável e legível — por isso URL e hash têm botão
 * de copiar, em vez de virar um rodapé técnico ilegível.
 */
export function ProcedenciaPartida({ procedencia }: ProcedenciaPartidaProps) {
  if (!procedencia) {
    return (
      <div className="flex flex-col gap-1 rounded-3xl border border-line bg-surface shadow-card p-4">
        <h2 className="text-sm font-semibold text-ink">Procedência</h2>
        <p className="text-sm text-muted">
          Procedência documental não disponível para esta partida. A base registra URL e hash da súmula para a Série A
          desde 2025 e a Série B desde 2024.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2 rounded-3xl border border-line bg-surface shadow-card p-4">
      <h2 className="text-sm font-semibold text-ink">Procedência</h2>

      <div className={LINHA}>
        <span className={ROTULO}>Fonte</span>
        <span className="text-sm text-body">{procedencia.fonte}</span>
      </div>

      <div className={LINHA}>
        <span className={ROTULO}>URL da súmula</span>
        <span className="flex min-w-0 items-center gap-2">
          <span className="truncate font-mono text-sm text-body">{procedencia.urlSumula}</span>
          <CopiarTexto valor={procedencia.urlSumula} />
        </span>
      </div>

      <div className={LINHA}>
        <span className={ROTULO}>SHA-256</span>
        <span className="flex min-w-0 items-center gap-2">
          <span className="font-mono text-sm break-all text-body">{procedencia.sha256}</span>
          <CopiarTexto valor={procedencia.sha256} />
        </span>
      </div>

      <div className={LINHA}>
        <span className={ROTULO}>Download</span>
        <span className="text-sm text-body">{formatarData(procedencia.dataDownload)}</span>
      </div>

      <div className={LINHA}>
        <span className={ROTULO}>Processamento</span>
        <span className="text-sm text-body">
          {formatarData(procedencia.dataProcessamento)}
        </span>
      </div>
    </div>
  );
}
