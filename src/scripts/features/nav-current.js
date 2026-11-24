// Scroll the contents navigation (not the page) so the current entry is in
// view; on deep collection pages it otherwise sits below the nav's fold.
export function initNavCurrent() {
  const nav = document.getElementById("site-nav");
  const current = nav?.querySelector("a.current");
  if (!nav || !current || nav.scrollHeight <= nav.clientHeight) return;
  const navTop = nav.getBoundingClientRect().top;
  const itemTop = current.getBoundingClientRect().top;
  nav.scrollTop += itemTop - navTop - nav.clientHeight / 3;
}
