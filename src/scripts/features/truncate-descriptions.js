// Strips " – " (en dash, U+2013, what Sphinx smartquotes makes of "--") and
// long " - " descriptions from breadcrumb and sidebar labels, e.g.
// "arillso.system.users role – Manage users" -> "arillso.system.users role".
// Only direct text nodes are touched, so child links and the theme's
// toctree-expand buttons survive. Headings are left alone on purpose: the
// page title keeps its full description. The original label stays on `title`.

export function initTruncateDescriptions() {
  const elements = document.querySelectorAll(
    ".trail li a, .trail li, .site-nav a, .pager a",
  );

  elements.forEach(function (element) {
    element.childNodes.forEach(function (node) {
      if (node.nodeType !== Node.TEXT_NODE) return;
      const text = node.nodeValue;
      let head = null;

      if (text.includes(" – ")) {
        head = text.split(" – ")[0];
      } else if (text.includes(" - ")) {
        // Only split when the tail looks like a description (> 20 chars),
        // so compound names stay intact.
        const parts = text.split(" - ");
        if (parts.length === 2 && parts[1].length > 20) head = parts[0];
      }

      // Inside the contents navigation the collection prefix repeats the
      // parent entry: "arillso.system.firewall role" -> "firewall role".
      const label = head !== null ? head : text;
      if (element.closest(".site-nav")) {
        const short = label.replace(/^(\s*)arillso\.(system|container|agent)\.(?=\S)/, "$1");
        if (short !== label) head = short;
      }

      if (head !== null) {
        element.setAttribute("title", text.trim());
        node.nodeValue = head.trimEnd();
      }
    });
  });
}
