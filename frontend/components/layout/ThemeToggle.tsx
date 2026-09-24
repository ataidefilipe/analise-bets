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
      className="flex size-8 items-center justify-center rounded-full border border-line-strong text-muted transition-colors hover:border-link hover:bg-surface-muted hover:text-link"
    >
      {escuro ? <Sun size={16} weight="bold" /> : <Moon size={16} weight="bold" />}
    </button>
  );
}
