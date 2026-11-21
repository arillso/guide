// Adds a "Copy" button to every `.highlight` code block. Uses the
// Async Clipboard API with a hidden-textarea + `execCommand` fallback
// for browsers without clipboard access (older Safari, insecure contexts).

function copyWithFallback(text) {
  const textArea = document.createElement("textarea");
  textArea.value = text;
  textArea.style.position = "fixed";
  textArea.style.opacity = "0";
  document.body.appendChild(textArea);
  textArea.select();
  try {
    // execCommand reports failure by returning false, not by throwing.
    return document.execCommand("copy");
  } catch {
    return false;
  } finally {
    document.body.removeChild(textArea);
  }
}

export function initCopyButtons() {
  document.querySelectorAll(".highlight").forEach(function (block) {
    const pre = block.querySelector("pre");
    if (!pre) return;

    const copyButton = document.createElement("button");
    copyButton.type = "button";
    copyButton.className = "code-copy-button";
    copyButton.textContent = "Copy";
    copyButton.setAttribute("aria-label", "Copy code to clipboard");

    function showState(label, copied) {
      copyButton.textContent = label;
      copyButton.classList.toggle("copied", copied);
      setTimeout(function () {
        copyButton.textContent = "Copy";
        copyButton.classList.remove("copied");
      }, 2000);
    }

    copyButton.addEventListener("click", async function () {
      const code = pre.textContent;
      let ok;
      try {
        await navigator.clipboard.writeText(code);
        ok = true;
      } catch {
        ok = copyWithFallback(code);
      }
      showState(ok ? "Copied!" : "Failed", ok);
    });

    block.style.position = "relative";
    block.appendChild(copyButton);
  });
}
