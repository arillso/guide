#!/usr/bin/env bash
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Created with antsibull-docs 2.5.0.post0

set -e

pushd "$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
trap "{ popd; }" EXIT

# renovate: datasource=galaxy-collection depName=arillso.system
ARILLSO_SYSTEM_VERSION="1.0.5"
# renovate: datasource=galaxy-collection depName=arillso.agent
ARILLSO_AGENT_VERSION="1.0.3"
# renovate: datasource=galaxy-collection depName=arillso.container
ARILLSO_CONTAINER_VERSION="1.0.2"

# Install Ansible Collections
echo "Installing Ansible Collections..."
ansible-galaxy collection install "arillso.system:${ARILLSO_SYSTEM_VERSION}" --force
ansible-galaxy collection install "arillso.agent:${ARILLSO_AGENT_VERSION}" --force
ansible-galaxy collection install "arillso.container:${ARILLSO_CONTAINER_VERSION}" --force

# Create collection documentation into temporary directory
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

# Copy collection documentation into source directory
rsync -cprv --delete-after temp-rst/collections/ rst/collections/

# Fix collection names to lowercase in all RST files
echo "Converting collection names to lowercase..."
find rst/collections/arillso -type f -name "*.rst" | while read -r file; do
    sed -i 's/Arillso/arillso/g; s/\.Agent/\.agent/g; s/\.System/\.system/g; s/\.Container/\.container/g' "$file"
done

find rst -type f -name "*.rst" | while read -r file; do
    sed -i 's/Arillso/arillso/g' "$file"
done


# Build Sphinx site
sphinx-build -M html rst build -c . -W --keep-going
