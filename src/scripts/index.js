import { onReady } from "./events/ready.js";
import { initTruncateDescriptions } from "./features/truncate-descriptions.js";
import { initCopyButtons } from "./features/copy-buttons.js";
import { initCodeLanguage } from "./features/code-language.js";
import { initSmoothScroll } from "./features/smooth-scroll.js";
import { initScrollAnimations } from "./features/scroll-animations.js";
import { initExternalLinks } from "./features/external-links.js";

onReady(() => {
  initTruncateDescriptions();
  initCopyButtons();
  initCodeLanguage();
  initSmoothScroll();
  initScrollAnimations();
  initExternalLinks();
});
