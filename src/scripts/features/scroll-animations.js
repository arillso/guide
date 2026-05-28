// Fades in feature cards, admonitions, and other surfaced blocks as
// they enter the viewport. Uses `IntersectionObserver` so we don't
// burn cycles on scroll-event listeners; inline-styles are used to
// keep the initial paint hidden without a CSS dependency.

export function initScrollAnimations() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      }
    });
  }, observerOptions);

  const animatedElements = document.querySelectorAll(
    ".feature-card, .admonition, .quickstart-path, .community-card, .stat-card",
  );

  animatedElements.forEach(function (element) {
    element.style.opacity = "0";
    element.style.transform = "translateY(20px)";
    element.style.transition = "opacity 0.6s ease, transform 0.6s ease";
    observer.observe(element);
  });
}
