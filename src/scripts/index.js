import { onReady } from "./events/ready.js";
import { initTruncateDescriptions } from "./features/truncate-descriptions.js";
import { initCopyButtons } from "./features/copy-buttons.js";
import { initCodeLanguage } from "./features/code-language.js";
import { initExternalLinks } from "./features/external-links.js";
import { initThemeToggle } from "./features/theme-toggle.js";
import { initNavToggle } from "./features/nav-toggle.js";

onReady(() => {
  initTruncateDescriptions();
  initCopyButtons();
  initCodeLanguage();
  initExternalLinks();
  initThemeToggle();
  initNavToggle();
});
