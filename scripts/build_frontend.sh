#!/usr/bin/env bash
set -e
set -u

# Resolve repository root (parent of the directory containing this script).
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Resolve the locally-installed npm CLI tools. In the container image the
# dependencies live at /usr/src/node_modules (see Dockerfile), intentionally
# outside the bind-mounted /project so they are not shadowed by the host
# checkout. Prefer that bin dir, fall back to a project-local install (host
# dev without the image), then to whatever is already on PATH. Calling the
# binaries directly avoids `npx`, which resolves against the (empty) project
# node_modules under the bind mount and fails.
for bindir in /usr/src/node_modules/.bin "$REPO_ROOT/node_modules/.bin"; do
    if [ -d "$bindir" ]; then
        PATH="$bindir:$PATH"
    fi
done
export PATH

# Single source for the postcss/esbuild command lines; `--watch` reuses them
# for `npm run build:watch`.
css() { postcss src/styles/index.css -o _static/custom.css "$@"; }
js() { esbuild src/scripts/index.js --bundle --target=es2020 --outfile=_static/custom.js "$@"; }

if [ "${1:-}" = "--watch" ]; then
    echo "Watching CSS and JS (Ctrl-C to stop)..."
    trap 'kill 0' EXIT
    css --watch &
    js --watch &
    wait
    exit
fi

echo "Building CSS..."
css

echo "Building JS..."
js

echo "Frontend build complete."
