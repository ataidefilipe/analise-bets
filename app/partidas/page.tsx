import { TelaPendente } from "@/components/layout/TelaPendente";
import { getTelaConfig } from "@/lib/mock/telas";

export default function PartidasPage() {
  const tela = getTelaConfig("dossie-partida");
  return <TelaPendente rotulo={tela.rotulo} descricaoCurta={tela.descricaoCurta} />;
}
