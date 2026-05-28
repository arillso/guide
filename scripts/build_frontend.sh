#!/usr/bin/env bash
set -e
set -u

# Resolve repository root (parent of the directory containing this script).
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "Building CSS..."
npx postcss src/styles/index.css -o _static/custom.css

echo "Building JS..."
npx esbuild src/scripts/index.js --bundle --target=es2020 --outfile=_static/custom.js

echo "Frontend build complete."
