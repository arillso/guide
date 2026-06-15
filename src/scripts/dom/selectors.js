// Thin wrappers around the native DOM query APIs. Centralising them
// here lets feature modules stay declarative and gives us a single
// place to bolt on test stubs or telemetry later. The helpers
// intentionally do NOT eagerly materialise the NodeList (no Array.from)
// so callers can keep using `forEach` without paying for an extra
// allocation.

/**
 * Query all elements matching `selector` within `root`.
 *
 * @param {string} selector - Any valid CSS selector.
 * @param {ParentNode} [root=document] - Optional scoping root.
 * @returns {NodeListOf<Element>}
 */
export function qsa(selector, root = document) {
  return root.querySelectorAll(selector);
}

/**
 * Query the first element matching `selector` within `root`.
 *
 * @param {string} selector - Any valid CSS selector.
 * @param {ParentNode} [root=document] - Optional scoping root.
 * @returns {Element | null}
 */
export function qs(selector, root = document) {
  return root.querySelector(selector);
}
