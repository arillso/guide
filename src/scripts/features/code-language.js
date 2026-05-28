// Detects the Pygments highlight language of a `.highlight` code block
// from its CSS classes. Exports both an init hook (badge-rendering will
// be wired in a later task) and the bare detection helper so other
// feature modules can reuse it without duplicating the parsing logic.

export function detectCodeLanguage(block) {
  const classes = block.className.split(" ");
  for (const className of classes) {
    if (className.startsWith("highlight-")) {
      return className.replace("highlight-", "");
    }
  }
  return "unknown";
}

export function initCodeLanguage() {
  const codeBlocks = document.querySelectorAll(".highlight");

  codeBlocks.forEach(function (block) {
    const language = detectCodeLanguage(block);
    if (language && language !== "unknown") {
      block.setAttribute("data-language", language);
    }
  });
}
