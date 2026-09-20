import { TelaPendente } from "@/components/layout/TelaPendente";
import { getTelaConfig } from "@/lib/mock/telas";

export default function AtletasPage() {
  const tela = getTelaConfig("busca-atleta");
  return <TelaPendente rotulo={tela.rotulo} descricaoCurta={tela.descricaoCurta} />;
}
