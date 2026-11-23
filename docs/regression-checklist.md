# Manual Regression Checklist

Manual check of the rendered site for what the CI build cannot catch:
pixel layout, browser interaction, keyboard focus, and mobile behaviour.
For whoever changes the frontend, the theme, or the doc toolchain.

## When to run

- After changes to `_theme/`, `src/styles/`, `src/scripts/` or `_static/fonts/`.
- After upgrading Sphinx or antsibull-docs.

## How to run

1. Build and serve the site. In the dde environment the container builds on
   start and serves <https://arillso-guide.test/>; rebuild without restart:

   ```bash
   docker compose exec -u "$(id -u):$(id -g)" arillso-doc-generator ./build.sh
   ```

   Without dde: `./build.sh`, then `python -m http.server -d build/html`.
   Opening `build/html/index.html` from disk works too, except search.

   After a change under `src/`, delete `build/` first. Sphinx rewrites only
   changed pages, so the others keep the old `custom.css?v=` hash and the
   browser serves the cached stylesheet. CI always builds from scratch.

2. Keep the DevTools console open (F12). Any JS console error is a fail.
3. Walk the list top to bottom, once in the light and once in the dark
   scheme (switch in the masthead, or the system setting). Report each
   failure in the PR that triggered the run (or a new issue) and fix it
   before merging. The checkboxes here stay unchecked; this file is the
   template, not a log.

---

## Layout

Current Chrome or Firefox, desktop viewport ≥ 1280 px.

- [ ] **Start page** `index.html`: masthead (logo, arillso/guide, search,
      GitHub, Galaxy, scheme switch), contents navigation left, "arillso"
      lowercase everywhere, figure strip with non-zero counts, the example
      playbook and its three run variants without horizontal scrolling,
      numbered sections 01–03, collection table shows versions from
      `versions.env`.
- [ ] **Guide page** `guide/getting-started/quickstart.html`: H1, numbered
      H2 rules, H3 in the right hierarchy, consistent paragraph spacing.
- [ ] **Role page** `collections/arillso/system/firewall_role.html`: option
      table with nested sub-options, type line under each name, defaults
      readable, "#" permalink on hover.
- [ ] **Module page** `collections/arillso/system/apt_update_info_module.html`:
      attributes table, return value table, link buttons at the end.
- [ ] **Code block** on the quickstart page: Plex Mono, sunk background,
      signal rule on the left, no overflow cut-off.
- [ ] **Collection landing** `collections/arillso/system/index.html` lists
      modules, filters, lookups and roles.
- [ ] **Search** `search.html?q=firewall` lists numbered results with
      context; the masthead search field lands there.

## Dark mode

- [ ] Scheme switch toggles light/dark; the choice survives a reload and a
      page change (stored as `arillso-theme` in `localStorage`).
- [ ] Without a stored choice the page follows the system setting.
- [ ] Code highlighting, option tables, admonitions and Mermaid diagrams
      stay readable in dark.

## Navigation

- [ ] **Contents navigation**: the current page is marked with the signal
      bar; only the current branch is expanded.
- [ ] **Breadcrumb trail** on `guide/best-practices/security.html`: every
      crumb except the last is a working link.
- [ ] **Pager** at the bottom: previous and next link to the neighbours in
      the contents order.
- [ ] **External links** (e.g. to `https://github.com/arillso/`) open in a
      new tab (`target="_blank"`).
- [ ] **Anchors**: clicking an entry of a page's contents scrolls to the
      heading without hiding it under the sticky masthead.

## Code blocks

- [ ] **Copy button** top right on every code block; copies the content
      and shows "Copied" for two seconds.
- [ ] **Language label** next to the copy button for `yaml`, `bash`,
      `python`; `none`, `text`, `default` stay unlabelled.
- [ ] **Inline code** has a sunk background and stands out from text.
- [ ] **Long lines** scroll inside the block; the page never scrolls
      horizontally.

## Mobile (360 px viewport)

Chrome DevTools → Device Toolbar → 360 × 740 px.

- [ ] **No horizontal scroll** on the start page, the quickstart and a role
      page.
- [ ] **Contents drawer**: the hamburger opens the navigation over the
      page; the button or Escape closes it and focus returns to the button.
- [ ] **Option tables** on role pages stack (antsibull narrow layout)
      instead of overflowing.
- [ ] **Tables** on the start page scroll inside their box.
- [ ] **Touch targets ≥ 44 × 44 px** for the hamburger, scheme switch and
      copy button.

## Keyboard

- [ ] **Skip link**: first Tab shows "Skip to content"; Enter moves focus
      to the main column.
- [ ] **Tab order**: skip link, masthead, contents navigation, content,
      pager, footer.
- [ ] **Visible focus**: 3 px signal outline on every interactive element.
- [ ] **No focus traps** in the navigation or the drawer.
