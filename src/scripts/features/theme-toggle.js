// Light/dark switch. The stored choice is applied before first paint by an
// inline script in layout.html; this only wires the button. Without a stored
// choice the page follows prefers-color-scheme.

const KEY = "arillso-theme";

function current() {
  const forced = document.documentElement.dataset.theme;
  if (forced === "dark" || forced === "light") return forced;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function initThemeToggle() {
  const button = document.querySelector(".theme-toggle");
  if (!button) return;

  function label() {
    const next = current() === "dark" ? "light" : "dark";
    button.setAttribute("aria-label", `Switch to ${next} colour scheme`);
    button.title = `Switch to ${next} colour scheme`;
  }

  button.addEventListener("click", function () {
    const next = current() === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem(KEY, next);
    } catch {
      // Storage blocked (private mode): the switch still applies to this page.
    }
    label();
  });

  label();
}
