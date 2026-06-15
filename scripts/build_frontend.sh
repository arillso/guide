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

echo "Building CSS..."
postcss src/styles/index.css -o _static/custom.css

echo "Building JS..."
esbuild src/scripts/index.js --bundle --target=es2020 --outfile=_static/custom.js

echo "Frontend build complete."
