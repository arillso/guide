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

| Path                                            | Purpose                                                                                                                                                      |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `src/styles/tokens/`                            | CSS Custom Properties — colors, typography, spacing/radius/motion, breakpoints. Loaded first so consumers always resolve `var(--token)` lookups.             |
| `src/styles/tokens/colors.css`                  | Color palette (primary, secondary, accent, gray scale).                                                                                                      |
| `src/styles/tokens/typography.css`              | Font families, fluid font sizes, weights, line heights.                                                                                                      |
| `src/styles/tokens/spacing.css`                 | Spacing scale (8px base), border-radius, transitions/easing, z-index scale.                                                                                  |
| `src/styles/tokens/breakpoints.css`             | Responsive breakpoints (`--bp-sm`, `--bp-md`, `--bp-lg`, `--bp-xl`).                                                                                         |
| `src/styles/base/`                              | Element-level resets and default typography.                                                                                                                 |
| `src/styles/base/reset.css`                     | Box-sizing, margin/padding resets, image defaults.                                                                                                           |
| `src/styles/base/typography.css`                | Heading hierarchy, link and paragraph defaults.                                                                                                              |
| `src/styles/layout/`                            | Page-level layout primitives and responsive overrides.                                                                                                       |
| `src/styles/layout/content.css`                 | Content area, container widths, vertical rhythm.                                                                                                             |
| `src/styles/layout/animations.css`              | Keyframes, smooth anchor scrolling, print override.                                                                                                          |
| `src/styles/layout/responsive.css`              | Media-query overrides — imported last so they win the cascade.                                                                                               |
| `src/styles/components/`                        | Eleven thematic component stylesheets (admonitions, breadcrumbs, buttons, code-block, feature-card, footer, mermaid, scrollbar, sidebar, tables, utilities). |
| `src/styles/index.css`                          | PostCSS entry point — aggregator only, no rules of its own. Defines the import order (tokens → base → layout → components → responsive).                     |
| `src/scripts/events/ready.js`                   | `onReady` DOM-ready helper — runs callbacks once the DOM is interactive.                                                                                     |
| `src/scripts/features/code-language.js`         | Labels code blocks with their language.                                                                                                                      |
| `src/scripts/features/copy-buttons.js`          | Wires up clipboard copy buttons on code blocks.                                                                                                              |
| `src/scripts/features/external-links.js`        | Marks external links with `target="_blank"` + `rel`.                                                                                                         |
| `src/scripts/features/scroll-animations.js`     | IntersectionObserver-driven reveal animations.                                                                                                               |
| `src/scripts/features/truncate-descriptions.js` | Strips descriptions from sidebar and breadcrumb labels.                                                                                                      |
| `src/scripts/index.js`                          | JS entry point — wires every feature into `onReady`. Bundled by esbuild.                                                                                     |

## Token Usage

Tokens live in `src/styles/tokens/` and are exposed as CSS Custom
Properties on `:root`. Components MUST reference them via `var(--token)`;
literal colors, raw px values, or magic numbers outside `tokens/` count as
a contract violation.

| Category    | Example tokens                                                                                                                                | Source                   |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| Colors      | `--primary-color`, `--primary-dark`, `--secondary-color`, `--accent-success`, `--accent-warning`, `--accent-danger`, `--gray-50`…`--gray-900` | `tokens/colors.css`      |
| Typography  | `--font-sans`, `--font-mono`, `--text-base`, `--text-lg`, `--font-semibold`, `--leading-normal`                                               | `tokens/typography.css`  |
| Spacing     | `--space-1`…`--space-24` (4px → 96px), `--radius-md`, `--radius-full`, `--transition-base`, `--ease-out`, `--z-modal`                         | `tokens/spacing.css`     |
| Breakpoints | `--bp-sm` (480px), `--bp-md` (768px), `--bp-lg` (1024px), `--bp-xl` (1280px)                                                                  | `tokens/breakpoints.css` |

**Convention:** Every component stylesheet under `src/styles/components/`
consumes only `var(--token)` references. If a new value is needed, add it
to the matching `tokens/*.css` file first, then consume it — never inline.

Breakpoints feed media queries; reference them as
`@media (min-width: var(--bp-md))` (mobile-first). The four `--bp-*`
values are the single source of truth — see `tokens/breakpoints.css`.

## Build Commands

All commands run from the repository root.

| Command                       | Purpose                                                                    |
| ----------------------------- | -------------------------------------------------------------------------- |
| `npm run build`               | Build CSS + JS once (runs `scripts/build_frontend.sh`).                    |
| `npm run build:watch`         | CSS + JS, rebuild on change (`build_frontend.sh --watch`).                 |
| `./scripts/build_frontend.sh` | Equivalent to `npm run build`. Used by the top-level `build.sh` as step 1. |

The PostCSS config in `postcss.config.js` enables `postcss-import`,
`autoprefixer` and `cssnano`, so the frontend build already emits the final
minified CSS.
