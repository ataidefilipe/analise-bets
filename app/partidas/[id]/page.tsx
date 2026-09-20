import { Callout } from "@/components/ui/Callout";
import { IdentificacaoPartida } from "@/components/dossie-partida/IdentificacaoPartida";
import { ProcedenciaPartida } from "@/components/dossie-partida/ProcedenciaPartida";
import { EventosPartida } from "@/components/dossie-partida/EventosPartida";
import { EscoreAnomaliaPartida } from "@/components/dossie-partida/EscoreAnomaliaPartida";
import { AtletasSinalizados } from "@/components/dossie-partida/AtletasSinalizados";
import { ExportarPdfButton } from "@/components/dossie-partida/ExportarPdfButton";
import { getDossiePartida } from "@/lib/mock/partidas";
import { getPerfilAtual } from "@/lib/mock/perfilAtual";

export default async function DossiePartidaPage({ params }: PageProps<"/partidas/[id]">) {
  const { id } = await params;
  const [dossie, perfil] = await Promise.all([getDossiePartida(id), getPerfilAtual()]);

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <IdentificacaoPartida identificacao={dossie.identificacao} />
        <ExportarPdfButton />
      </div>

      <Callout>{dossie.avisoInterpretativo}</Callout>

      <ProcedenciaPartida procedencia={dossie.procedencia} />
      <EventosPartida eventos={dossie.eventos} />
      <EscoreAnomaliaPartida percentil={dossie.escoreAnomaliaPercentil} ressalva={dossie.ressalvaPartida} />

      {perfil.granularidade === "identificada" && dossie.atletasSinalizados && (
        <AtletasSinalizados atletas={dossie.atletasSinalizados} />
      )}

      <p className="text-xs text-zinc-400 italic print:hidden dark:text-zinc-600">
        [MVP] Este PDF é gerado por impressão de página — não é um registro auditável assinado (dívida registrada no
        doc 03, §4).
      </p>
    </div>
  );
}
