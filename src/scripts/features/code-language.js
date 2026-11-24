// Labels each `.highlight` code block with its Pygments language. Sphinx
// puts the language class on the wrapper, not on the inner block:
//   <div class="highlight-yaml notranslate"><div class="highlight"><pre>
// The label is set as `data-language` and rendered by code.css.

const UNLABELLED = new Set(["none", "text", "default"]);

export function detectCodeLanguage(block) {
  const wrapper = block.parentElement;
  if (!wrapper) return null;
  for (const className of wrapper.classList) {
    if (className.startsWith("highlight-")) {
      const language = className.slice("highlight-".length);
      return UNLABELLED.has(language) ? null : language;
    }
  }
  return null;
}

export function initCodeLanguage() {
  document.querySelectorAll(".highlight").forEach(function (block) {
    const language = detectCodeLanguage(block);
    if (language) block.setAttribute("data-language", language);
  });
}
