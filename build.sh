#!/usr/bin/env bash
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Created with antsibull-docs 2.5.0.post0

set -e

pushd "$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Temporary file used to capture the JSON manifest emitted by
# scripts/collection_cache.py. Cleaned up alongside the pushd/popd via trap.
CACHE_MANIFEST_FILE="$(mktemp)"
trap 'rm -f "${CACHE_MANIFEST_FILE}"; popd' EXIT

# shellcheck source=versions.env
source versions.env

# 1. Build frontend artefacts (CSS + JS) from src/ into _static/
echo "Building frontend bundles..."
./scripts/build_frontend.sh

# 2. Ensure Ansible collections are present in the local cache
#    (replaces the former galaxy-install calls; see design Section 6.2).
echo "Ensuring Ansible collection cache..."
CACHE_DIR="${ARILLSO_COLLECTIONS_CACHE:-${HOME}/.cache/arillso-collections}"
CACHE_ARGS=(--versions-file versions.env --cache-dir "${CACHE_DIR}")
if [ "${ARILLSO_OFFLINE:-0}" = "1" ]; then
    CACHE_ARGS+=(--offline)
fi
python3 scripts/collection_cache.py ensure "${CACHE_ARGS[@]}" > "${CACHE_MANIFEST_FILE}"

# Export the cache root as ANSIBLE_COLLECTIONS_PATH so antsibull-docs sees
# the cached collection tree (design §4.3, §6.4).
ANSIBLE_COLLECTIONS_PATH="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['cache_root'])" "${CACHE_MANIFEST_FILE}")"
export ANSIBLE_COLLECTIONS_PATH

# 3. Create collection documentation into temporary directory
rm -rf temp-rst
mkdir -p temp-rst
chmod og-w temp-rst  # antsibull-docs wants that directory only readable by itself

antsibull-docs \
    --config-file antsibull-docs.cfg \
    collection \
    --use-current \
    --collection-version "arillso.system:${ARILLSO_SYSTEM_VERSION}" \
    --collection-version "arillso.agent:${ARILLSO_AGENT_VERSION}" \
    --collection-version "arillso.container:${ARILLSO_CONTAINER_VERSION}" \
    --dest-dir temp-rst \
    arillso.system arillso.agent arillso.container

# 4. Copy collection documentation into source directory
rsync -cprv --delete-after temp-rst/collections/ rst/collections/

# 5. Normalize collection names (token-based; see design Section 6.3).
echo "Normalizing collection names..."
python3 scripts/normalize_collections.py --root rst

# 6. Build Sphinx site
sphinx-build -M html rst build -c . -W --keep-going

# 7. Optimize CSS and JS if postcss is available
if command -v postcss &> /dev/null && [ -f build/html/_static/custom.css ]; then
    echo "Optimizing CSS with PostCSS (autoprefixer + cssnano)..."
    postcss build/html/_static/custom.css \
        --use autoprefixer --use cssnano \
        --no-map \
        -o build/html/_static/custom.css
    echo "CSS optimization complete."
fi
