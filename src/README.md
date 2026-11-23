# Frontend Sources

CSS and JavaScript for the site theme. The templates live in
`_theme/arillso/`; this directory holds what they load. The build bundles
everything into two files the theme references:

| Entry point            | Tool                                              | Output               |
| ---------------------- | ------------------------------------------------- | -------------------- |
| `src/styles/index.css` | PostCSS (`postcss-import`, autoprefixer, cssnano) | `_static/custom.css` |
| `src/scripts/index.js` | esbuild, `--target=es2020`                        | `_static/custom.js`  |

Both outputs are git-ignored and overwritten on every build.

## Design

The site reads like a technical datasheet: pale engineering-green paper
(`#e7f0ea`, like graph paper), near-black
ink, one petrol signal colour (`--signal`, `#00645c` light, `#3fd2be` dark),
heavy rules between sections and a two-digit number in front of every `h2`.
Cream paper with an orange accent was dropped because it reads as the Claude
brand; keep away from it, and from Vercel/Linear blue and Stripe purple.
"arillso" is always lowercase, so no `text-transform: uppercase` on text that
can contain the name (headings, navigation captions, wordmark); only fixed
labels such as table heads use it. No shadows, gradients, rounded cards or
motion. Scrollbars are thin and square in the `--mute` colour.

| Element    | Choice                                                                                                |
| ---------- | ----------------------------------------------------------------------------------------------------- |
| Text font  | Archivo (variable, width axis used for condensed headings)                                            |
| Code font  | IBM Plex Mono                                                                                         |
| Font files | `_static/fonts/*.woff2`, latin subset, self-hosted; SIL OFL licences next to them                     |
| Colours    | `src/styles/tokens.css`; light by default, dark via `prefers-color-scheme` or the masthead switch     |
| Logo       | `_static/logo.svg` (signal block with a ring-and-stem "a"); `_static/favicon.ico` is its 32 px raster |

Banned on purpose, so the site does not drift back to a template look:
gradients, glass effects, large soft shadows, scroll or fade-in
animations, emoji icons, card grids, hero buttons, decorative badges.

## Module Map

| Path                                            | Purpose                                                                                               |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `src/styles/index.css`                          | Aggregator only; defines the import order.                                                            |
| `src/styles/fonts.css`                          | `@font-face` rules; URLs are relative to `_static/custom.css`.                                        |
| `src/styles/tokens.css`                         | Colour and type tokens; the dark palette is declared for the media query and for `data-theme="dark"`. |
| `src/styles/base.css`                           | Box model, body type, links, focus ring, skip link.                                                   |
| `src/styles/layout.css`                         | Masthead, contents navigation (drawer below 64rem), breadcrumb trail, pager, colophon.                |
| `src/styles/content.css`                        | Headings with section numbers, lists, tables, admonitions, figures.                                   |
| `src/styles/code.css`                           | Inline code, code blocks, language label, copy button, Pygments token colours.                        |
| `src/styles/antsibull.css`                      | Remaps the `--antsibull-*` variables of `antsibull-minimal.css` and styles option tables.             |
| `src/styles/home.css`                           | Start page (`body.page-index`) and `index-table` lists.                                               |
| `src/styles/search.css`                         | Search page and results.                                                                              |
| `src/styles/print.css`                          | Hides navigation chrome when printing.                                                                |
| `src/scripts/index.js`                          | Wires every feature into `onReady`.                                                                   |
| `src/scripts/events/ready.js`                   | `onReady` DOM-ready helper.                                                                           |
| `src/scripts/features/copy-buttons.js`          | Copy button on every `.highlight` block.                                                              |
| `src/scripts/features/code-language.js`         | Sets `data-language` on code blocks for the label.                                                    |
| `src/scripts/features/external-links.js`        | `target="_blank"` and `rel` on external links.                                                        |
| `src/scripts/features/truncate-descriptions.js` | Cuts " – description" tails from navigation, trail and pager labels.                                  |
| `src/scripts/features/theme-toggle.js`          | Light/dark switch; choice stored in `localStorage` under `arillso-theme`.                             |
| `src/scripts/features/nav-toggle.js`            | Opens and closes the contents drawer; Escape closes and returns focus.                                |

## Rules

- Colours only through tokens. A new colour goes into `tokens.css` for both
  palettes; check WCAG AA contrast against `--paper` in light and dark.
- Pygments colours are mapped in `code.css` onto the tokens, so code blocks
  follow dark mode without a second Pygments stylesheet. New token classes
  belong there.
- Generated collection pages are styled through the classes antsibull-docs
  emits (`ansible-option-*`); never post-process the generated RST.
- Mobile first: base rules target 360 px, `min-width` queries add the wide
  layout (`48rem` tables, `64rem` sidebar).

## Build Commands

| Command                       | Purpose                                                 |
| ----------------------------- | ------------------------------------------------------- |
| `npm run build`               | Build CSS + JS once (runs `scripts/build_frontend.sh`). |
| `npm run build:watch`         | Rebuild on change.                                      |
| `./scripts/build_frontend.sh` | Same as `npm run build`; step 1 of `build.sh`.          |
