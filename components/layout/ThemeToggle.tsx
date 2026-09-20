"use client";

import { useSyncExternalStore } from "react";
import { Moon, Sun } from "@phosphor-icons/react";

function getSnapshot() {
  return document.documentElement.classList.contains("dark");
}

function getServerSnapshot() {
  return false;
}

function subscribe(callback: () => void) {
  const observer = new MutationObserver(callback);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
  return () => observer.disconnect();
}

/**
 * Alterna a classe `.dark` no `<html>` e persiste a escolha em localStorage.
 * Lê o estado atual da classe via `useSyncExternalStore` (em vez de
 * `useEffect` + `setState`) para não descasar do HTML gerado no servidor
 * nem disparar um render em cascata logo após montar — o script inline em
 * app/layout.tsx já aplicou a classe correta antes da pintura.
 */
export function ThemeToggle() {
  const escuro = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  function alternar() {
    const proximoEscuro = !document.documentElement.classList.contains("dark");
    document.documentElement.classList.toggle("dark", proximoEscuro);
    localStorage.setItem("theme", proximoEscuro ? "dark" : "light");
  }

  return (
    <button
      type="button"
      onClick={alternar}
      aria-label="Alternar tema"
      title="Alternar tema"
      className="flex size-8 items-center justify-center rounded-full border border-zinc-300 text-zinc-500 transition-colors hover:border-brand hover:bg-zinc-100 hover:text-brand dark:border-zinc-700 dark:text-zinc-400 dark:hover:border-link dark:hover:bg-zinc-800 dark:hover:text-link"
    >
      {escuro ? <Sun size={16} weight="bold" /> : <Moon size={16} weight="bold" />}
    </button>
  );
}
