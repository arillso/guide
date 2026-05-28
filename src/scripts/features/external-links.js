// Forces every `a.reference.external` link to open in a new tab with
// `rel="noopener noreferrer"` to avoid tab-nabbing and to keep the
// docs visible. Click-tracking is dispatched through the global
// `trackEvent` analytics helper when present; the link's destination
// category (GitHub, Docker Hub, …) is classified locally.

export function initExternalLinks() {
  const externalLinks = document.querySelectorAll("a.reference.external");

  externalLinks.forEach(function (link) {
    link.setAttribute("target", "_blank");
    link.setAttribute("rel", "noopener noreferrer");

    link.addEventListener("click", function () {
      const destination = getExternalLinkDestination(link.href);
      trackExternalClick(destination, link.href);
    });
  });
}

function getExternalLinkDestination(url) {
  if (url.includes("github.com/marketplace")) return "GitHub Actions";
  if (url.includes("github.com")) return "GitHub";
  if (url.includes("hub.docker.com")) return "Docker Hub";
  if (url.includes("galaxy.ansible.com")) return "Ansible Galaxy";
  if (url.includes("arillso.io")) return "Arillso Website";
  return "Other";
}

function trackExternalClick(destination, url) {
  if (typeof window !== "undefined" && typeof window.trackEvent === "function") {
    window.trackEvent("external-link-click", { destination, url });
  }
}
