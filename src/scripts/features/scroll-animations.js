// Fades in feature cards, admonitions, and other surfaced blocks as
// they enter the viewport. Skipped entirely for prefers-reduced-motion;
// print stays readable through the `@media print` override in
// layout/animations.css.

export function initScrollAnimations() {
  if (
    typeof IntersectionObserver === "undefined" ||
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  ) {
    return;
  }

  const observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.opacity = "1";
          entry.target.style.transform = "translateY(0)";
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: "0px 0px -50px 0px" },
  );

  document
    .querySelectorAll(
      ".feature-card, .admonition, .quickstart-path, .community-card, .stat-card",
    )
    .forEach(function (element) {
      element.style.opacity = "0";
      element.style.transform = "translateY(20px)";
      element.style.transition = "opacity 0.6s ease, transform 0.6s ease";
      observer.observe(element);
    });
}
