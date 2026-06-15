#!/usr/bin/env bash
# Run @axe-core/cli WCAG audit against representative built HTML pages.
# Exits non-zero on serious/critical findings per WCAG 2.1 AA.

set -e
set -u

# Resolve repository root (parent of the directory containing this script).
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Resolve the locally-installed axe binary the same way build_frontend.sh does:
# prefer the image-baked node_modules, fall back to a project-local install,
# then to PATH. Calling the binary directly avoids `npx`, which resolves against
# the (empty) project node_modules under the container bind mount and fails.
for bindir in /usr/src/node_modules/.bin "$REPO_ROOT/node_modules/.bin"; do
    if [ -d "$bindir" ]; then
        PATH="$bindir:$PATH"
    fi
done
export PATH

# Representative pages: landing, getting-started guide, collection index.
# Non-existent pages are skipped with a warning so the script remains robust
# during early build phases.
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
  axe "file://$(realpath "$page")" \
      --exit \
      --tags wcag2a,wcag2aa,wcag21a,wcag21aa
done

echo "axe-core audit complete."
