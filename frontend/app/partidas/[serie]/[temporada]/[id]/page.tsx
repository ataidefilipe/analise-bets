import { notFound } from "next/navigation";
import { Callout } from "@/components/ui/Callout";
import { IdentificacaoPartida } from "@/components/dossie-partida/IdentificacaoPartida";
import { ProcedenciaPartida } from "@/components/dossie-partida/ProcedenciaPartida";
import { EventosPartida } from "@/components/dossie-partida/EventosPartida";
import { EscoreAnomaliaPartida } from "@/components/dossie-partida/EscoreAnomaliaPartida";
import { AtletasSinalizados } from "@/components/dossie-partida/AtletasSinalizados";
import { ExportarPdfButton } from "@/components/dossie-partida/ExportarPdfButton";
import { exigirAcessoTela } from "@/lib/api/sessao";
import { getDossiePartida } from "@/lib/api/partidas";
import { lerInteiro } from "@/lib/opcoes";

export default async function DossiePartidaPage({ params }: PageProps<"/partidas/[serie]/[temporada]/[id]">) {
  const perfil = await exigirAcessoTela("dossie-partida");
  const { serie, temporada, id } = await params;
  const ano = lerInteiro(temporada);
  const partidaId = lerInteiro(id);
  if ((serie !== "A" && serie !== "B") || !ano || !partidaId) notFound();

  const dossie = await getDossiePartida(serie, ano, partidaId);

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <IdentificacaoPartida identificacao={dossie.identificacao} />
        <ExportarPdfButton />
      </div>

      <Callout>{dossie.avisoInterpretativo}</Callout>

      <ProcedenciaPartida procedencia={dossie.procedencia} />
      <EventosPartida eventos={dossie.eventos} />
      <EscoreAnomaliaPartida
        percentil={dossie.escoreAnomaliaPercentil}
        tier={dossie.tierPartida}
        ressalva={dossie.ressalvaPartida}
      />

      {/* A camada decide no backend: na aberta a seção nem vem na resposta (doc 03, §4). */}
      {perfil.camada === "identificada" && dossie.atletasSinalizados && (
        <AtletasSinalizados atletas={dossie.atletasSinalizados} />
      )}

      <p className="text-xs text-subtle italic print:hidden">
        [MVP] Este PDF é gerado por impressão de página — não é um registro auditável assinado (dívida registrada no
        doc 03, §4).
      </p>
    </div>
  );
}
