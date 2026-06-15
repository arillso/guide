// Adds a "Copy" button to every `.highlight` code block. Uses the
// Async Clipboard API with a hidden-textarea + `execCommand` fallback
// for browsers without clipboard access. The detected language is
// reused from `code-language.js` so the analytics payload stays
// consistent across features.

import { detectCodeLanguage } from "./code-language.js";

export function initCopyButtons() {
  const codeBlocks = document.querySelectorAll(".highlight");

  codeBlocks.forEach(function (block) {
    const copyButton = document.createElement("button");
    copyButton.className = "code-copy-button";
    copyButton.textContent = "Copy";
    copyButton.setAttribute("aria-label", "Copy code to clipboard");

    copyButton.addEventListener("click", async function () {
      const code = block.querySelector("pre").textContent;
      const codeLanguage = detectCodeLanguage(block);

      try {
        await navigator.clipboard.writeText(code);

        copyButton.textContent = "Copied!";
        copyButton.classList.add("copied");

        trackCopyEvent(codeLanguage, code.length);

        setTimeout(function () {
          copyButton.textContent = "Copy";
          copyButton.classList.remove("copied");
        }, 2000);
      } catch (err) {
        // Fallback for browsers without Clipboard API access (older
        // Safari, insecure contexts).
        const textArea = document.createElement("textarea");
        textArea.value = code;
        textArea.style.position = "fixed";
        textArea.style.opacity = "0";
        document.body.appendChild(textArea);
        textArea.select();

        try {
          document.execCommand("copy");
          copyButton.textContent = "Copied!";
          copyButton.classList.add("copied");

          trackCopyEvent(codeLanguage, code.length);

          setTimeout(function () {
            copyButton.textContent = "Copy";
            copyButton.classList.remove("copied");
          }, 2000);
        } catch (fallbackErr) {
          copyButton.textContent = "Failed";
          setTimeout(function () {
            copyButton.textContent = "Copy";
          }, 2000);
        }

        document.body.removeChild(textArea);
      }
    });

    block.style.position = "relative";
    block.appendChild(copyButton);
  });
}

function trackCopyEvent(language, length) {
  if (typeof window !== "undefined" && typeof window.trackEvent === "function") {
    window.trackEvent("code-copied", { language, length });
  }
}
