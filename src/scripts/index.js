import { onReady } from "./events/ready.js";
import { initTruncateDescriptions } from "./features/truncate-descriptions.js";
import { initCopyButtons } from "./features/copy-buttons.js";
import { initCodeLanguage } from "./features/code-language.js";
import { initScrollAnimations } from "./features/scroll-animations.js";
import { initExternalLinks } from "./features/external-links.js";

// Smooth in-page scrolling is plain CSS (`scroll-behavior` in
// layout/animations.css), so `:target` and ids with `/` or `.` keep working.
onReady(() => {
  initTruncateDescriptions();
  initCopyButtons();
  initCodeLanguage();
  initScrollAnimations();
  initExternalLinks();
});
