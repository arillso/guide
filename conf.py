# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Created with antsibull-docs 2.5.0.post0

# This file only contains a selection of the most common options. For a full list see the
# documentation:
# http://www.sphinx-doc.org/en/master/config

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

from security_txt import write_security_txt  # noqa: E402

# Render .well-known/security.txt here, at config-read time, rather than from a
# builder-inited handler: Sphinx validates html_extra_path while reading this
# file, so a directory created later would still warn — and build.sh runs with
# -W, which turns that warning into a failed build on a clean checkout.
write_security_txt(datetime.now(timezone.utc))

project = "arillso"

# Homepage facts, computed instead of typed so they cannot drift: collection
# versions from versions.env (Renovate bumps them), plugin counts from the
# pages antsibull-docs generated into rst/collections/ (build.sh step 4).
_ROOT = Path(__file__).resolve().parent
_versions = dict(
    line.split("=", 1)
    for line in (_ROOT / "versions.env").read_text(encoding="utf-8").splitlines()
    if line.startswith("ARILLSO_")
)
_subs = []
for _name in ("system", "container", "agent"):
    _version = _versions[f"ARILLSO_{_name.upper()}_VERSION"].strip('"')
    _subs.append(f".. |{_name}_version| replace:: {_version}")
    _dir = _ROOT / "rst" / "collections" / "arillso" / _name
    for _kind in ("role", "module", "filter", "lookup"):
        _count = len(list(_dir.glob(f"*_{_kind}.rst")))
        _subs.append(f".. |{_name}_{_kind}s| replace:: {_count}")
_gen = _ROOT / "rst" / "collections" / "arillso"
_subs.append(f".. |total_roles| replace:: **{len(list(_gen.glob('*/*_role.rst')))}**")
_plugins = [p for p in _gen.glob("*/*.rst") if not p.name.endswith("_role.rst") and p.name != "index.rst"]
_subs.append(f".. |total_plugins| replace:: **{len(_plugins)}**")
rst_epilog = "\n".join(_subs) + "\n"
copyright = "arillso contributors"

html_title = "arillso guide"
html_short_title = "arillso guide"

extensions = [
    "sphinx.ext.intersphinx",
    "sphinx_antsibull_ext",
    "sphinxcontrib.mermaid",
    "sphinx_sitemap",
]

# Mermaid configuration - use default light theme. Pinned: "latest" would let
# a Mermaid major release change every diagram without a repo change. Renovate
# bumps it (custom manager in .github/renovate.json).
mermaid_version = "12.3.0"
mermaid_init_js = "mermaid.initialize({startOnLoad:true,theme:'neutral'});"

pygments_style = "ansible"

highlight_language = "YAML+Jinja"

# Own theme under _theme/arillso (inherits Sphinx's basic templates only).
html_theme = "arillso"
html_theme_path = ["_theme"]
# "#" instead of the pilcrow: the latin subset of the vendored fonts has no ¶.
html_permalinks_icon = "#"
html_show_sphinx = False

html_use_index = False
html_copy_source = False

# Static files (CSS, JavaScript, Images)
html_static_path = ["_static"]

# Rendered just above; the contents are copied into the root of build/html,
# which is what puts security.txt under /.well-known/.
html_extra_path = ["_well_known_build"]
html_css_files = ["custom.css"]
html_js_files = ["custom.js"]

# Favicon (the logo is placed by _theme/arillso/layout.html)
html_favicon = "_static/favicon.ico"

# See https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#confval-intersphinx_mapping for the syntax
intersphinx_mapping = {
    "python3": ("https://docs.python.org/3/", None),
    "jinja2": ("https://jinja.palletsprojects.com/en/stable/", None),
    "ansible_devel": ("https://docs.ansible.com/ansible/devel/", None),
    # If you want references to resolve to a released Ansible version (say, `5`), uncomment and replace X by this version:
    # 'ansibleX': ('https://docs.ansible.com/ansible/X/', None),
}

default_role = "any"

nitpicky = True

# Link checking (sphinx-build -b linkcheck). Internal :ref:/:doc: references are
# validated by the regular html build (nitpicky); these options harden the
# external HTTP checks against flaky endpoints so CI fails only on genuinely
# broken links.
linkcheck_retries = 2
linkcheck_timeout = 15
linkcheck_workers = 5
# Treat anchor-only failures as warnings, not errors: many sites render anchors
# client-side, so a missing #fragment is not a broken page.
linkcheck_anchors = False
# Hosts that rate-limit or block automated HEAD/GET requests but are known-good.
linkcheck_ignore = [
    # galaxy.ansible.com / hub.docker.com return 403 to non-browser clients.
    r"https://galaxy\.ansible\.com/.*",
    r"https://hub\.docker\.com/.*",
    # Non-HTTP URI schemes that appear in generated collection RST (e.g. the
    # tailscale_role "tag:" ACL tags) and that linkcheck cannot resolve.
    r"^tag:.*",
]

# Sitemap configuration
html_baseurl = "https://guide.arillso.io/"
sitemap_url_scheme = "{link}"
