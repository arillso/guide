// Forces every `a.reference.external` link to open in a new tab with
// `rel="noopener noreferrer"` to avoid tab-nabbing and to keep the
// docs visible.

export function initExternalLinks() {
  document.querySelectorAll("a.reference.external").forEach(function (link) {
    link.setAttribute("target", "_blank");
    link.setAttribute("rel", "noopener noreferrer");
  });
}
