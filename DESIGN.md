---
name: arillso guide
description: Reference documentation for the arillso Ansible collections and tools, set as a technical datasheet.
colors:
  paper: "#e7f0ea"
  paper-sunk: "#d6e4db"
  paper-raised: "#f1f7f3"
  ink: "#101618"
  ink-soft: "#283236"
  mute: "#535d60"
  rule: "#101618"
  hair: "#c3d3c9"
  signal: "#00645c"
  signal-ink: "#ffffff"
  signal-wash: "#d3e6e2"
  ok: "#2b6a1f"
  warn: "#80560a"
  bad: "#b0262e"
  mark: "#f6d77a"
  dark-paper: "#0f1415"
  dark-paper-sunk: "#172022"
  dark-paper-raised: "#1f292b"
  dark-ink: "#e6ecea"
  dark-ink-soft: "#c3cdca"
  dark-mute: "#93a09d"
  dark-hair: "#303c3e"
  dark-signal: "#3fd2be"
  dark-signal-wash: "#12302d"
  dark-ok: "#8fd46a"
  dark-warn: "#e9b65a"
  dark-bad: "#ff7b7f"
  dark-mark: "#6b5310"
typography:
  display:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(2.25rem, 1.4rem + 4vw, 4rem)"
    fontWeight: 800
    lineHeight: 0.95
    fontVariation: "'wdth' 70"
  headline:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(1.75rem, 1.2rem + 2.4vw, 2.6rem)"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "-0.005em"
    fontVariation: "'wdth' 78"
  title:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.45rem"
    fontWeight: 800
    lineHeight: 1.15
    fontVariation: "'wdth' 80"
  subtitle:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.1rem"
    fontWeight: 700
    lineHeight: 1.15
    fontVariation: "'wdth' 90"
  body:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  lede:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.55
  entry:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 700
    fontVariation: "'wdth' 90"
  small:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.5
  data:
    fontFamily: "IBM Plex Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.2
  label:
    fontFamily: "IBM Plex Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "0.6875rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.12em"
  code:
    fontFamily: "IBM Plex Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.55
rounded:
  none: "0"
spacing:
  gutter-sm: "1rem"
  gutter-md: "2rem"
  measure: "46rem"
  nav-width: "17rem"
  masthead-height: "3.5rem"
components:
  code-block:
    backgroundColor: "{colors.paper-sunk}"
    textColor: "{colors.ink}"
    typography: "{typography.code}"
    rounded: "{rounded.none}"
    padding: "2.9rem 1rem 1rem 1.1rem"
  copy-button:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    height: "2.75rem"
    width: "4rem"
  copy-button-copied:
    backgroundColor: "{colors.signal}"
    textColor: "{colors.signal-ink}"
  search-input:
    backgroundColor: "{colors.paper-raised}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.35rem 0.6rem"
    height: "2.25rem"
  admonition:
    backgroundColor: "{colors.paper-raised}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.75rem 1rem 0.25rem"
  inline-code:
    backgroundColor: "{colors.paper-sunk}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.05em 0.3em"
---

<!-- DESIGN.md spec format: the frontmatter `name` and the "Do:" headings are
     required by the format, so these two rules do not apply here. -->
<!-- markdownlint-disable MD025 MD026 -->

# Design System: arillso guide

## Overview

**Creative North Star: "The Datasheet"**

The site reads like the technical datasheet of a component: pale
engineering-green paper, near-black ink, one petrol signal colour, heavy
rules between sections and a two-digit number in front of every section
heading. Information is organised by lines, numbers and tables, never by
floating cards, depth or atmosphere. The reader is writing YAML next to it;
every visual decision serves finding a role, an option or an example fast.

Density is that of a reference sheet: a 46 rem reading measure, condensed
heavy headings, monospaced labels in small caps-like tracking, and tables
that carry structure the way a spec sheet does. Light is the default; dark
mode inverts paper and ink and lifts the signal to a bright petrol.

Rejected on purpose, so the site does not drift back to a template look:
cream paper with an orange accent (reads as the Claude brand), Vercel or
Linear blue, Stripe purple, gradients, glass, large soft shadows, scroll or
fade-in motion, emoji icons, card grids, hero buttons, decorative badges.

**Key Characteristics:**

- Numbered sections: every `h2` carries `01`, `02`, … in petrol mono.
- Rules, not surfaces: 3 px ink rules for structure, 1 px hairlines for
  detail.
- One accent colour, used for links, numbers, keywords and focus only.
- Square everything: radius 0 throughout.
- No motion beyond the browser's own anchor scrolling.

## Colors

Green-tinted paper and ink with a single petrol signal; status colours
exist only for admonitions and syntax.

### Primary

- **Petrol Signal** (`signal`, dark `dark-signal`): links, section numbers,
  ordered-list markers, YAML keys and keywords, the left edge of code
  blocks, the current navigation entry, focus rings and text selection.
  Never a fill for large areas; the only filled use is the "copied" state of
  the copy button and `::selection`.
- **Signal Wash** (`signal-wash`): background of highlighted code lines
  only.

### Neutral

- **Graph Paper** (`paper`): page background, masthead, copy button at rest.
- **Sunk Paper** (`paper-sunk`): code blocks and inline code, the one
  recessed surface.
- **Raised Paper** (`paper-raised`): admonitions, search input, table row
  hover, Mermaid diagram frames.
- **Ink** (`ink`, same value as `rule`): body text, headings and every
  structural rule.
- **Soft Ink** (`ink-soft`): lede paragraphs, code punctuation.
- **Mute** (`mute`): captions, breadcrumb trail, table and topic labels,
  comments in code, scrollbars.
- **Hairline** (`hair`): table row lines, `h3` rules, nav nesting lines.

### Status

- **Ok Green** (`ok`): tip and hint admonitions.
- **Amber** (`warn`): warning admonitions and string literals in code, so
  strings stay apart from petrol keys.
- **Alarm Red** (`bad`): danger, error and important admonitions, syntax
  errors.
- **Marker Yellow** (`mark`): search-term highlighting.

### Named Rules

**The One Signal Rule.** Petrol is the only accent. A second hue appears
only as a status (ok, warn, bad) or the search marker, never as decoration.

**The Same-Ink Rule.** Rules are drawn in text ink (`rule` equals `ink`).
Structure is as dark as the words it separates.

## Typography

**Display Font:** Archivo variable (with Helvetica Neue, Arial)
**Body Font:** Archivo variable, normal width
**Label/Mono Font:** IBM Plex Mono 400 and 600 (with ui-monospace, Menlo)

**Character:** A grotesk whose width axis carries the hierarchy:
headings are condensed (70–90 % width) and heavy, body text runs at normal
width. Plex Mono does every label, caption, number and code line, which is
what makes the pages read as a spec sheet. Fonts are self-hosted from
`_static/fonts/` (latin subset, SIL OFL).

### Hierarchy

- **Display** (800, 70 % width, clamp 2.25–4 rem, line height 0.95): the
  start page title only.
- **Headline** (800, 78 % width, clamp 1.75–2.6 rem): `h1` of every page.
- **Title** (800, 80 % width, 1.45 rem): `h2`, under a 3 px ink rule and
  after its mono section number.
- **Subtitle** (700, 90 % width, 1.1 rem): `h3`, under a hairline.
- **Body** (400, 1 rem, line height 1.6): running text in a 46 rem column.
- **Lede** (400, 1.125 rem, soft ink): the opening paragraph of the start
  page, max 40 rem.
- **Entry** (700, 90 % width, 1.0625 rem): first column of index tables.
- **Small** (400, 0.9375 rem): tables, contents navigation, topic boxes,
  antsibull option tables.
- **Data** (Plex Mono 400, 0.875 rem): versions and counts in index tables,
  search input and results, antsibull option metadata.
- **Label** (Plex Mono 600, 0.6875 rem, tracking 0.08–0.12 em, uppercase):
  table heads, admonition titles, topic titles, language tags, copy button.
- **Code** (Plex Mono 400, 0.8125 rem, line height 1.55): code blocks;
  inline code at 0.875 em.

### Named Rules

**The Lowercase Name Rule.** "arillso" is always lowercase. No
`text-transform: uppercase` on anything that can contain the name
(headings, navigation captions, wordmark); only fixed labels such as table
heads are uppercased.

**The Width-Not-Size Rule.** Heading rank is expressed through weight and
width as much as size; never introduce a second display family.

## Layout

A sticky masthead (3.5 rem, 3 px ink rule below) holds wordmark, search,
external links and the light/dark switch. Below 64 rem the contents
navigation is a drawer behind a toggle; from 64 rem the frame is a two-column
grid: a 17 rem navigation column separated by a hairline, and the page
column with the document at a 46 rem measure. The gutter is 1 rem on small
screens and 2 rem from 48 rem up.

Pages end with a pager (previous/next, 3 px rule above, one column below
40 rem, two above) and a colophon in mono under another 3 px rule. The
start page widens the document to 60 rem and uses a ruled figures strip
(2 columns, 4 from 48 rem) and a two-column "hook" of playbook and run
commands.

Tables scroll inside their own box on narrow screens; antsibull option
tables keep antsibull's own stacking below 1200 px. Index tables on
the start page stack each row below 48 rem: the entry and its short second
column (version, kind) on one line, the rest full width. Role links there
are set in mono, because they are the names written in YAML. On generated
role and plugin pages the install note is a compact block and a contents
box with a single entry point is hidden. The start page leads with
coverage (lede, figures, collections table) before the run examples.

## Elevation & Depth

Flat. There are no shadows anywhere. Depth is expressed only by three
paper tones: sunk (code), base (page) and raised (admonitions, inputs,
hovered rows), and by rule weight.

**The Flat Sheet Rule.** If something needs to stand out, give it a rule
or a paper tone, never a shadow, blur or gradient.

## Shapes

Every corner is square (radius 0): inputs, buttons, code blocks,
admonitions, scrollbar thumbs. Form comes from rules: 3 px ink rules for
section structure (masthead, `h2`, pager, colophon, figures strip), 1 px
hairlines for detail, a 3 px petrol left edge on code blocks and a 6 px
coloured left edge on admonitions. Scrollbars are thin and square in mute.

## Components

All components are ruled and exact: they are delimited by lines and frames,
not by fills or depth; states change only colour and line weight.

### Code Blocks

- **Shape:** square, sunk paper, 3 px petrol left edge.
- **Top strip:** a reserved 2.9 rem strip holds the uppercase language tag
  (mute) and the copy button, so they never cover code.
- **Copy button:** square, 4 × 2.75 rem, paper background with hairline
  left and bottom edges, mono label; hover turns the label petrol; after
  copying the button fills petrol with white text.
- **Syntax:** keys and keywords petrol 600, strings amber, numbers and
  names ink 600, comments mute italic.

### Tables

- **Head:** mono label, uppercase, 2 px ink rule below.
- **Rows:** hairline between rows, raised paper on hover.
- **Index tables:** first column larger (700, 90 % width), linked in ink
  with a 2 px petrol underline; version and count columns in mono, counts
  right-aligned.

### Admonitions

- **Shape:** 1 px ink frame, 6 px coloured left edge, raised paper.
- **Title:** mono label in the status colour (petrol for note, amber for
  warning, red for danger, green for tip).

### Inputs (search)

- **Style:** 1 px ink frame, raised paper, mono text, radius 0, min height
  2.25 rem.
- **Focus:** 3 px petrol outline, 2 px offset (global focus ring).

### Navigation

- **Contents nav:** mono captions over a 1 px ink rule; nested levels
  indented behind a hairline; hover petrol; the current page bold petrol.
- **Trail:** mono 0.75 rem breadcrumb in mute, hover petrol.
- **Mobile:** below 64 rem the nav opens as a full-width drawer on paper.

### Section Numbers (signature)

Every `h2` is preceded by its two-digit counter (`01`, `02` …) in Plex Mono
600 at 0.8125 rem, petrol, on a 2.25 rem slot.

### Figures Strip (signature, start page)

Large condensed numbers (800, 70 % width, 2.75 rem) over mono captions,
between a 3 px rule above and a 1 px rule below, columns split by 1 px
rules in mute (the hairline was too faint). Each caption links to its
index.

## Do's and Don'ts

### Do:

- **Do** take every colour from `src/styles/tokens.css`; define dark values
  for both the media query and `data-theme="dark"`.
- **Do** separate sections with rules: 3 px `rule` for structure, 1 px
  `hair` for detail.
- **Do** set labels, captions, numbers and code in IBM Plex Mono.
- **Do** keep "arillso" lowercase everywhere.
- **Do** keep a visible 3 px petrol focus ring and WCAG AA contrast in both
  themes.

### Don't:

- **Don't** use gradients, glass effects, blur or box shadows.
- **Don't** add scroll, fade-in or reveal animations.
- **Don't** use emoji icons, card grids, hero buttons or decorative badges.
- **Don't** introduce cream paper with orange, Vercel/Linear blue or
  Stripe purple.
- **Don't** round corners.
- **Don't** uppercase text that can contain the name "arillso".
