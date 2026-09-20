import { BuscaForm } from "@/components/ui/BuscaForm";
import { Pager } from "@/components/ui/Pager";
import { ResultadoPartidasTabela } from "@/components/dossie-partida/ResultadoPartidasTabela";
import { EmptyState } from "@/components/ui/EmptyState";
import { listarPartidas } from "@/lib/mock/partidas";
import { exigirAcessoTela } from "@/lib/mock/acesso";

const POR_PAGINA = 10;

function primeiro(valor: string | string[] | undefined): string | undefined {
  return Array.isArray(valor) ? valor[0] : valor;
}

function lerPagina(valor: string | string[] | undefined): number {
  const n = Number(primeiro(valor));
  return Number.isInteger(n) && n >= 1 ? n : 1;
}

/**
 * O doc 03 não descreve uma tela de listagem para a T3 — assume que P3
 * chega numa partida específica por referência externa. Esta lista existe
 * só para permitir navegar até um dossiê durante o desenvolvimento/demo,
 * agora com busca e paginação equivalentes às da T2 (a pedido do usuário).
 */
export default async function PartidasPage({ searchParams }: PageProps<"/partidas">) {
  await exigirAcessoTela("dossie-partida");
  const sp = await searchParams;
  const consulta = (primeiro(sp.q) ?? "").trim();
  const buscaCurta = consulta.length > 0 && consulta.length < 3;

  const todas = buscaCurta ? [] : await listarPartidas(consulta);
  const totalPaginas = Math.max(1, Math.ceil(todas.length / POR_PAGINA));
  const pagina = Math.min(lerPagina(sp.pagina), totalPaginas);
  const itensDaPagina = todas.slice((pagina - 1) * POR_PAGINA, pagina * POR_PAGINA);

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4">
      <div className="flex flex-col gap-2">
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Partidas monitoradas</h1>
        <BuscaForm basePath="/partidas" valorInicial={consulta} placeholder="nome de um dos clubes..." />
      </div>

      {buscaCurta ? (
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Digite ao menos 3 caracteres para buscar.</p>
      ) : todas.length === 0 ? (
        <EmptyState
          titulo="Nenhuma partida encontrada."
          descricao="Tente buscar pelo nome de um dos clubes."
        />
      ) : (
        <>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">{todas.length} partidas no total</p>
          <ResultadoPartidasTabela itens={itensDaPagina} />
          <Pager basePath="/partidas" consulta={consulta} pagina={pagina} totalPaginas={totalPaginas} />
        </>
      )}
    </div>
  );
}
