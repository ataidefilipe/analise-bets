import type { Metadata } from "next";
import { Geist_Mono, Urbanist } from "next/font/google";
import { AppShell } from "@/components/layout/AppShell";
import { getPerfilAtual } from "@/lib/api/sessao";
import "./globals.css";

const urbanist = Urbanist({
  variable: "--font-urbanist",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Análise de integridade",
  description: "Painel de monitoramento de perfil disciplinar em partidas de futebol.",
};

export default async function RootLayout({ children }: LayoutProps<"/">) {
  const perfil = await getPerfilAtual();

  return (
    <html
      lang="pt-BR"
      className={`${urbanist.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      {/* suppressHydrationWarning: o <html> ganha a classe "dark" via script antes da
          pintura (ver abaixo) e o <body> é alvo comum de extensões de navegador (ex.:
          ColorZilla injeta `cz-shortcut-listen`) — ambos os casos são descasamentos
          esperados entre servidor e cliente, não bugs deste app. */}
      <body className="min-h-full flex flex-col bg-background text-foreground" suppressHydrationWarning>
        <script
          // Evita flash de tema errado: aplica a classe antes da primeira pintura,
          // a partir da preferência salva ou, na ausência dela, do SO.
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem("theme");var d=t?t==="dark":window.matchMedia("(prefers-color-scheme: dark)").matches;document.documentElement.classList.toggle("dark",d);}catch(e){}})();`,
          }}
        />
        {perfil ? (
          <AppShell perfil={perfil}>{children}</AppShell>
        ) : (
          // Sem sessão só existe a tela de entrada — ela não tem menu nem perfil a mostrar.
          <main className="flex flex-1 items-center justify-center px-4 py-6">{children}</main>
        )}
      </body>
    </html>
  );
}
