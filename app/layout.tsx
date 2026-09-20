import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { AppShell } from "@/components/layout/AppShell";
import { getPerfilAtual } from "@/lib/mock/perfilAtual";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
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
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <script
          // Evita flash de tema errado: aplica a classe antes da primeira pintura,
          // a partir da preferência salva ou, na ausência dela, do SO.
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem("theme");var d=t?t==="dark":window.matchMedia("(prefers-color-scheme: dark)").matches;document.documentElement.classList.toggle("dark",d);}catch(e){}})();`,
          }}
        />
        <AppShell perfil={perfil}>{children}</AppShell>
      </body>
    </html>
  );
}
