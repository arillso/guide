#!/usr/bin/env bash
# Run @axe-core/cli WCAG audit against representative built HTML pages.
# Exits non-zero on serious/critical findings per WCAG 2.1 AA (Requirements 4.5, 5.5, 5.6).

set -e
set -u

# Resolve repository root (parent of the directory containing this script).
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Representative pages: landing, getting-started guide, collection index.
# Non-existent pages are skipped with a warning so the script remains robust
# during early build phases (per design §6.12 and task 6.3 Observable Done).
PAGES=(
  "build/html/index.html"
  "build/html/guide/getting-started/quickstart.html"
  "build/html/collections/index.html"
)

for page in "${PAGES[@]}"; do
  if [ ! -f "$page" ]; then
    echo "WARNING: $page does not exist, skipping."
    continue
  fi
  echo "Auditing $page..."
  npx @axe-core/cli "file://$(realpath "$page")" \
      --exit \
      --tags wcag2a,wcag2aa,wcag21a,wcag21aa
done

echo "axe-core audit complete."
