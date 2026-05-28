// `onReady` is the single entry point for "run this once the DOM is
// parsed". If the document already passed the `DOMContentLoaded`
// milestone (readyState === 'interactive' | 'complete'), we still
// schedule the callback asynchronously via `queueMicrotask` so callers
// observe a consistent "always async" contract — no surprise sync
// re-entrancy when scripts load late.

/**
 * Invoke `callback` once the DOM is ready.
 *
 * @param {() => void} callback - Initialisation routine to run.
 */
export function onReady(callback) {
  if (typeof callback !== "function") return;

  if (document.readyState === "interactive" || document.readyState === "complete") {
    if (typeof queueMicrotask === "function") {
      queueMicrotask(callback);
    } else {
      setTimeout(callback, 0);
    }
    return;
  }

  document.addEventListener("DOMContentLoaded", callback, { once: true });
}
