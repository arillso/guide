// Strips " – " (em dash) or " - " (long hyphen-dash) descriptions from
// breadcrumbs, vertical-menu links, and headings. Original text is kept
// on the `title` attribute so hover still reveals the full label.

export function initTruncateDescriptions() {
  const elements = document.querySelectorAll(
    ".wy-breadcrumbs li a, " +
      ".wy-breadcrumbs li, " +
      ".breadcrumb-item, " +
      ".wy-menu-vertical a, " +
      "h1, h2, h3, h4, h5, h6",
  );

  elements.forEach(function (element) {
    const text = element.textContent;

    // Em dash: always treated as a description separator.
    if (text.includes(" – ")) {
      const parts = text.split(" – ");
      const shortName = parts[0].trim();
      element.setAttribute("title", text);
      element.textContent = shortName;
    } else if (text.includes(" - ")) {
      // Hyphen-dash: only split when the tail looks like a description
      // (> 20 chars) so we don't mangle compound names.
      const parts = text.split(" - ");
      if (parts.length === 2 && parts[1].length > 20) {
        const shortName = parts[0].trim();
        element.setAttribute("title", text);
        element.textContent = shortName;
      }
    }
  });
}
