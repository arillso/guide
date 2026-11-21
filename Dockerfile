# Multi-stage Dockerfile for the arillso guide.
#
# Stage 1 (`builder`) installs Python and Node dependencies into the standard
# system locations using `pip install -r requirements.txt` and `npm ci`. No
# packages are installed globally (no `-g` flag).
#
# Stage 2 (`docs`) is the slim runtime that `docker-compose.yml` builds via
# `target: docs`. It carries only the minimal apt packages needed at build
# time and copies the prepared /usr/local/lib (site-packages, version-agnostic)
# plus `node_modules` from the builder. Dev dependencies (pytest) are included
# on purpose so the test suite can run inside the container. Both FROM lines
# must reference the same image; the CI job `Build Docker Image` catches drift. Antsibull is resolved exclusively via PyPI (requirements.txt);
# the previous in-image checkouts of antsibull-core, antsibull-docs-parser,
# and antsibull-docs are no longer required.

# Node runtime source. Debian's apt nodejs is too old for the frontend
# toolchain (cssnano needs Node >= 22), so node + npm come from here.
FROM node:24-slim@sha256:dc26ae92c9fb15cf6b1d63e20f0944b2efe0f115b20e00be48fb23fceb061c54 AS node

# ---------------------------------------------------------------------------
# Stage 1: Builder
# ---------------------------------------------------------------------------
FROM python:3.15@sha256:46837ed3105db0029b6d656816185c6258e3b39690532fb782428e0a5fd76182 AS builder

WORKDIR /usr/src

# Build-time dependencies. `build-essential` covers native extensions that
# some transitive Python wheels may require to compile. `git` and
# `ca-certificates` cover any VCS-backed dependencies transitively pulled in
# by pip.
RUN apt-get update && apt-get install -y --no-install-recommends \
        bash \
        rsync \
        git \
        ca-certificates \
        build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Node + npm into /usr/local, so the docs stage inherits them with the
# /usr/local copies below.
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# Python dependencies — antsibull-docs comes from PyPI (requirements.txt).
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Node dependencies — installed locally into /usr/src/node_modules; no `-g`.
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

# ---------------------------------------------------------------------------
# Stage 2: Docs runtime
# ---------------------------------------------------------------------------
FROM python:3.15@sha256:46837ed3105db0029b6d656816185c6258e3b39690532fb782428e0a5fd76182 AS docs

WORKDIR /project

# Minimal runtime apt set:
# - `bash`, `rsync`, `less`, `ca-certificates`: required by build.sh and tooling.
# Node, npm and ansible-core (pip, requirements.txt) arrive with the
# /usr/local copies from the builder.
RUN apt-get update && apt-get install -y --no-install-recommends \
        bash \
        rsync \
        less \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Carry over the Python and Node toolchains prepared in the builder stage.
# Copy all of /usr/local/lib so the site-packages path follows the base
# image's Python version instead of hardcoding it.
COPY --from=builder /usr/local/lib /usr/local/lib
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/src/node_modules /usr/src/node_modules

# Expose the locally-installed npm CLI tools (postcss, esbuild) on PATH, and
# let Node's require() (postcss.config.js plugins) resolve them from anywhere,
# including a bind-mounted /project that has no node_modules of its own.
ENV PATH=/usr/src/node_modules/.bin:$PATH \
    NODE_PATH=/usr/src/node_modules

CMD ["bash"]
