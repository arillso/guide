// Contents drawer below 64rem: the button opens the toctree as a full-height
// panel; Escape or a second press closes it and returns focus to the button.

export function initNavToggle() {
  const button = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");
  if (!button || !nav) return;

  function setOpen(open) {
    nav.classList.toggle("is-open", open);
    button.setAttribute("aria-expanded", String(open));
    document.body.style.overflow = open ? "hidden" : "";
    // Content behind the full-screen drawer must not take focus.
    document.querySelectorAll(".page, .colophon").forEach(function (el) {
      el.inert = open;
    });
  }

  button.addEventListener("click", function () {
    const open = !nav.classList.contains("is-open");
    setOpen(open);
    if (open) {
      const target = nav.querySelector("a.current") || nav.querySelector("a");
      if (target) target.focus();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && nav.classList.contains("is-open")) {
      setOpen(false);
      button.focus();
    }
  });

  // Desktop layout shows the nav permanently; drop drawer state when crossing.
  window.matchMedia("(min-width: 64rem)").addEventListener("change", function () {
    setOpen(false);
  });
}
