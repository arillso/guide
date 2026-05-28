// Intercepts in-page anchor clicks (`a[href^="#"]`) and replaces the
// browser default jump with a `scrollIntoView({ behavior: "smooth" })`.
// The URL hash is updated via `history.pushState` so the address bar
// reflects the target without re-triggering a navigation.

export function initSmoothScroll() {
  const anchorLinks = document.querySelectorAll('a[href^="#"]');

  anchorLinks.forEach(function (link) {
    link.addEventListener("click", function (e) {
      const targetId = this.getAttribute("href");

      if (targetId === "#") return;

      const targetElement = document.querySelector(targetId);

      if (targetElement) {
        e.preventDefault();
        targetElement.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });

        if (history.pushState) {
          history.pushState(null, null, targetId);
        }
      }
    });
  });
}
