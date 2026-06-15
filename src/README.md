# Frontend Source Layout

This directory holds the modular CSS and JavaScript sources. The build
pipeline aggregates the files under `src/styles/` and `src/scripts/` into
the artefacts the Sphinx theme expects (`_static/custom.css` and
`_static/custom.js`).

Entry points:

- **CSS:** `src/styles/index.css` — single PostCSS entry. All other
  stylesheets are pulled in via `@import` and resolved by
  `postcss-import`.
- **JS:** `src/scripts/index.js` — single esbuild entry. Bundled to
  `_static/custom.js` with `--target=es2020`.

## Module Map

| Path | Purpose |
|------|---------|
| `src/styles/tokens/` | CSS Custom Properties — colors, typography, spacing/radius/motion, breakpoints. Loaded first so consumers always resolve `var(--token)` lookups. |
| `src/styles/tokens/colors.css` | Color palette (primary, secondary, accent, gray scale). |
| `src/styles/tokens/typography.css` | Font families, fluid font sizes, weights, line heights. |
| `src/styles/tokens/spacing.css` | Spacing scale (8px base), border-radius, transitions/easing, z-index scale. |
| `src/styles/tokens/breakpoints.css` | Responsive breakpoints (`--bp-sm`, `--bp-md`, `--bp-lg`, `--bp-xl`). |
| `src/styles/base/` | Element-level resets and default typography. |
| `src/styles/base/reset.css` | Box-sizing, margin/padding resets, image defaults. |
| `src/styles/base/typography.css` | Heading hierarchy, link and paragraph defaults. |
| `src/styles/layout/` | Page-level layout primitives and responsive overrides. |
| `src/styles/layout/content.css` | Content area, container widths, vertical rhythm. |
| `src/styles/layout/animations.css` | Shared keyframes and animation utilities. |
| `src/styles/layout/responsive.css` | Media-query overrides — imported last so they win the cascade. |
| `src/styles/components/` | Eleven thematic component stylesheets (admonitions, breadcrumbs, buttons, code-block, feature-card, footer, mermaid, scrollbar, sidebar, tables, utilities). |
| `src/styles/index.css` | PostCSS entry point — aggregator only, no rules of its own. Defines the import order (tokens → base → layout → components → responsive). |
| `src/scripts/dom/selectors.js` | Query helpers (`$`, `$$`) used by feature modules. |
| `src/scripts/events/ready.js` | `onReady` DOM-ready helper — runs callbacks once the DOM is interactive. |
| `src/scripts/features/code-language.js` | Labels code blocks with their language. |
| `src/scripts/features/copy-buttons.js` | Wires up clipboard copy buttons on code blocks. |
| `src/scripts/features/external-links.js` | Marks external links with `target="_blank"` + `rel`. |
| `src/scripts/features/scroll-animations.js` | IntersectionObserver-driven reveal animations. |
| `src/scripts/features/smooth-scroll.js` | Smooth-scroll behaviour for in-page anchors. |
| `src/scripts/features/truncate-descriptions.js` | Truncates long descriptions in plugin/module lists. |
| `src/scripts/index.js` | JS entry point — wires every feature into `onReady`. Bundled by esbuild. |

## Token Usage

Tokens live in `src/styles/tokens/` and are exposed as CSS Custom
Properties on `:root`. Components MUST reference them via `var(--token)`;
literal colors, raw px values, or magic numbers outside `tokens/` count as
a contract violation.

| Category | Example tokens | Source |
|----------|----------------|--------|
| Colors | `--primary-color`, `--primary-dark`, `--secondary-color`, `--accent-success`, `--accent-warning`, `--accent-danger`, `--gray-50`…`--gray-900` | `tokens/colors.css` |
| Typography | `--font-sans`, `--font-mono`, `--text-base`, `--text-lg`, `--font-semibold`, `--leading-normal` | `tokens/typography.css` |
| Spacing | `--space-1`…`--space-24` (4px → 96px), `--radius-md`, `--radius-full`, `--transition-base`, `--ease-out`, `--z-modal` | `tokens/spacing.css` |
| Breakpoints | `--bp-sm` (480px), `--bp-md` (768px), `--bp-lg` (1024px), `--bp-xl` (1280px) | `tokens/breakpoints.css` |

**Convention:** Every component stylesheet under `src/styles/components/`
consumes only `var(--token)` references. If a new value is needed, add it
to the matching `tokens/*.css` file first, then consume it — never inline.

Breakpoints feed media queries; reference them as
`@media (min-width: var(--bp-md))` (mobile-first). The four `--bp-*`
values are the single source of truth — see `tokens/breakpoints.css`.

## Component Interfaces

Jinja2 macros live in `_templates/components/`. Each macro file opens
with a comment block describing parameters, slots, and A11y assumptions
— that header is the canonical contract.

| Macro | Required parameters | Optional parameters | Source |
|-------|---------------------|---------------------|--------|
| `feature_card` | `title`, `description`, `link` | `icon` | `_templates/components/feature-card.html` |
| `code_block` | `code` | `language` (default `plaintext`), `filename` | `_templates/components/code-block.html` |
| `doc_sidebar` | `items` (list of `{label, link, children?}`) | `aria_label` (default `"Documentation navigation"`) | `_templates/components/doc-sidebar.html` |

Import the macros at template scope before use:

```jinja
{% from "components/feature-card.html" import feature_card %}
{{ feature_card("Quickstart", "Install in 5 minutes.", "/quickstart/", "🚀") }}
```

## Build Commands

All commands run from the repository root.

| Command | Purpose |
|---------|---------|
| `npm run build` | Build CSS + JS once (`build:css` followed by `build:js`). |
| `npm run build:css` | PostCSS pass on `src/styles/index.css` → `_static/custom.css`. |
| `npm run build:js` | esbuild bundle of `src/scripts/index.js` → `_static/custom.js` (target ES2020). |
| `npm run build:watch:css` | Same as `build:css`, rebuild on change. |
| `npm run build:watch:js` | Same as `build:js`, rebuild on change. |
| `./scripts/build_frontend.sh` | Equivalent to `npm run build`. Used by the top-level `build.sh` as step 1. |

The PostCSS config in `postcss.config.js` enables `postcss-import` plus
`autoprefixer` and `cssnano` (the latter two are applied during the
Sphinx post-build step in `build.sh` for minification).
