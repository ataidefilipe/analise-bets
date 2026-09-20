import { TelaPendente } from "@/components/layout/TelaPendente";
import { getTelaConfig } from "@/lib/mock/telas";

export default function AgregadosPage() {
  const tela = getTelaConfig("panorama-agregado");
  return <TelaPendente rotulo={tela.rotulo} descricaoCurta={tela.descricaoCurta} />;
}
