import { Callout } from "@/components/ui/Callout";
import { FichaCabecalho } from "@/components/ficha-atleta/FichaCabecalho";
import { HistoricoTemporadas } from "@/components/ficha-atleta/HistoricoTemporadas";
import { LinhaDoTempoCartoes } from "@/components/ficha-atleta/LinhaDoTempoCartoes";
import { getFichaAtleta } from "@/lib/api/atletas";
import { exigirAcessoTela } from "@/lib/api/sessao";

export default async function FichaAtletaPage({ params }: PageProps<"/atletas/[id]">) {
  await exigirAcessoTela("busca-atleta");
  const { id } = await params;
  const ficha = await getFichaAtleta(id);

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <FichaCabecalho ficha={ficha} />
      <Callout>{ficha.avisoInterpretativo}</Callout>
      <HistoricoTemporadas temporadas={ficha.historicoPorTemporada} />
      <LinhaDoTempoCartoes eventos={ficha.linhaDoTempoCartoes} />
    </div>
  );
}
