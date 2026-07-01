# Multi-stage Dockerfile for the arillso guide.
#
# Stage 1 (`builder`) installs Python and Node dependencies into the standard
# system locations using `pip install -r requirements.txt` and `npm ci`. No
# packages are installed globally (no `-g` flag).
#
# Stage 2 (`docs`) is the slim runtime that `docker-compose.yml` builds via
# `target: docs`. It carries only the minimal apt packages needed at build
# time and copies the prepared site-packages plus `node_modules` from the
# builder. Antsibull is resolved exclusively via PyPI (requirements.txt);
# the previous in-image checkouts of antsibull-core, antsibull-docs-parser,
# and antsibull-docs are no longer required.

# ---------------------------------------------------------------------------
# Stage 1: Builder
# ---------------------------------------------------------------------------
FROM python:3.14@sha256:09b29c360b84742bf98eba40b214f7f6b4b53286bb2c8a8b5b1afa188a8d9c0e AS builder

WORKDIR /usr/src

# Build-time dependencies. `build-essential` covers native extensions that
# some transitive Python wheels may require to compile. `npm` is needed for
# `npm ci`. `git` and `ca-certificates` cover any VCS-backed dependencies
# transitively pulled in by pip.
RUN apt-get update && apt-get install -y --no-install-recommends \
        npm \
        bash \
        rsync \
        git \
        ca-certificates \
        build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Python dependencies — antsibull-docs comes from PyPI (requirements.txt).
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Node dependencies — installed locally into /usr/src/node_modules; no `-g`.
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

# ---------------------------------------------------------------------------
# Stage 2: Docs runtime
# ---------------------------------------------------------------------------
FROM python:3.14@sha256:09b29c360b84742bf98eba40b214f7f6b4b53286bb2c8a8b5b1afa188a8d9c0e AS docs

WORKDIR /project

# Minimal runtime apt set:
# - `bash`, `rsync`, `less`, `ca-certificates`: required by build.sh and tooling.
# - `ansible-core`: provides `ansible-galaxy`, used by
#   scripts/collection_cache.py in online mode.
# - `nodejs` + `npm`: scripts/build_frontend.sh shells out to `npx`. The
#   Node binaries from this apt install drive the locally-installed
#   `node_modules` that we copy in from the builder.
RUN apt-get update && apt-get install -y --no-install-recommends \
        bash \
        rsync \
        less \
        ca-certificates \
        ansible-core \
        nodejs \
        npm \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Carry over the Python and Node toolchains prepared in the builder stage.
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/src/node_modules /usr/src/node_modules

# Expose the locally-installed npm CLI tools (postcss, esbuild, axe-core) on
# PATH so build.sh and CI scripts can invoke them without `npx`.
ENV PATH=/usr/src/node_modules/.bin:$PATH

CMD ["bash"]
