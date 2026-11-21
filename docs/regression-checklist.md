# Manual Regression Checklist

Manual check of the rendered site for what the CI build cannot catch:
pixel layout, browser interaction, keyboard focus, and mobile behaviour.
For whoever changes the frontend, the theme, or the doc toolchain.

## When to run

- After changes to `_templates/`, `src/styles/`, or `src/scripts/`.
- After upgrading Sphinx, `sphinx-ansible-theme`, or antsibull-docs.

## How to run

1. Build the site:

   ```bash
   ./build.sh
   ```

2. Open the output in a browser:

   ```bash
   xdg-open build/html/index.html   # Linux
   open build/html/index.html       # macOS
   ```

3. Keep the DevTools console open (F12). Any JS console error is a fail.
4. Walk the list top to bottom. Report each failure in the PR that
   triggered the run (or a new issue) and fix it before merging. The
   checkboxes here stay unchecked; this file is the template, not a log.

---

## Layout

Current Chrome or Firefox, desktop viewport ≥ 1280 px.

- [ ] **Index page** `build/html/index.html` loads fully: logo top left,
      main heading, sidebar visible, content area filled, footer at the
      bottom.
- [ ] **Guide page** `build/html/guide/getting-started/quickstart.html`
      shows H1, H2, H3 in the right hierarchy with consistent paragraph
      spacing.
- [ ] **Code block** on the quickstart page or
      `build/html/containers/docker_ansible.html`: monospaced font,
      background matching the theme, no overflow cut-off.
- [ ] **Collection landing** `build/html/collections/arillso/system/index.html`
      lists modules and roles with the description table intact.
- [ ] **404 page** (if the theme provides one — open
      `build/html/does-not-exist.html`): shows an error page with
      navigation back to the index, not a broken skeleton.

## Navigation

- [ ] **Sidebar expand/collapse** on `build/html/index.html`: open and
      close expandable entries under the toctree captions (e.g. Getting
      Started, Ansible Collections) — children appear without layout jumps.
- [ ] **Breadcrumbs** on `build/html/guide/best-practices/security.html`
      are visible and every crumb is a working link.
- [ ] **Internal links**: from `build/html/index.html` open at least three
      internal targets (e.g. Quickstart, Architecture, Troubleshooting) —
      all load without 404 at the right scroll position.
- [ ] **Active sidebar entry** on the quickstart page is visually
      highlighted (bold, accent colour, or indicator bar).
- [ ] **External links** (e.g. to `https://github.com/arillso/`) show the
      external-link icon and open in a new tab (`target="_blank"`).
- [ ] **Anchors**: on `build/html/guide/best-practices/standards.html`,
      clicking a TOC entry scrolls to the right H2/H3 without hiding it
      under the sticky header.

## Code blocks

- [ ] **Copy button appears** on every code block of the quickstart page
      (on hover, or always on mobile), top right.
- [ ] **Copy button works**: the block content lands in the clipboard
      (paste to verify) and the button shows short feedback ("Copied").
- [ ] **Syntax highlighting**: YAML blocks on
      `build/html/github/action_playbook.html` colour keys, values,
      strings, and comments.
- [ ] **Language badge**: every code block with a real language (`yaml`,
      `bash`, `python`) shows it as a small label; `none`, `text`, and
      `default` blocks stay unlabelled.
- [ ] **Inline code** on `build/html/guide/reference/troubleshooting.html`
      has a subtle background and stands out from body text.
- [ ] **Long lines** (> 100 characters) scroll horizontally inside the
      block or wrap — the page itself never scrolls horizontally.

## Mobile (375 px viewport)

Chrome DevTools → Device Toolbar → iPhone SE / 375 × 667 px.

- [ ] **No horizontal scroll** on `build/html/index.html`.
- [ ] **Hamburger menu** (if present): below 768 px the sidebar hides
      behind the icon, opens as overlay or drawer, and closes via X or a
      backdrop click.
- [ ] **Code blocks** on the quickstart page wrap or scroll internally; the
      body stays 375 px wide.
- [ ] **Touch targets ≥ 44 × 44 px** for sidebar links, copy button, and
      hamburger.
- [ ] **Typography**: body text ≥ 14 px effective, H1 does not fill the
      first view, line length roughly 30–75 characters.
- [ ] **Tables** on `build/html/collections/arillso/system/index.html` wrap,
      scroll internally, or stack — no broken page layout.

## Keyboard

- [ ] **Tab order** from `build/html/index.html`: logo, sidebar
      items, content links, footer links, in a visible, logical order.
- [ ] **Visible focus** on every interactive element (outline, underline,
      or background change).
- [ ] **No focus traps** in the sidebar, including expandable entries:
      Tab and Shift+Tab always move on.
- [ ] **Enter activates** a focused sidebar link; Enter or Space on a
      focused copy button copies.
- [ ] **Escape closes overlays** (mobile drawer, modal) and returns focus
      to the trigger.
