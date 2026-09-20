import { TelaPendente } from "@/components/layout/TelaPendente";
import { getTelaConfig } from "@/lib/mock/telas";

export default function TriagemPage() {
  const tela = getTelaConfig("fila-triagem");
  return <TelaPendente rotulo={tela.rotulo} descricaoCurta={tela.descricaoCurta} />;
}
