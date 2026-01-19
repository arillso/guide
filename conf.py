# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Created with antsibull-docs 2.5.0.post0

# This file only contains a selection of the most common options. For a full list see the
# documentation:
# http://www.sphinx-doc.org/en/master/config

project = "arillso"
copyright = "arillso contributors"

title = "arillso Guide Documentation"
html_short_title = "arillso Documentation"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_antsibull_ext",
    "sphinxcontrib.mermaid",
    "sphinx_sitemap",
]

# Mermaid configuration - use default light theme
mermaid_version = "latest"
mermaid_params = ["--theme", "default", "--backgroundColor", "white"]
mermaid_init_js = "mermaid.initialize({startOnLoad:true,theme:'default'});"

pygments_style = "ansible"

highlight_language = "YAML+Jinja"

html_theme = "sphinx_ansible_theme"
html_show_sphinx = False

display_version = False

html_use_smartypants = True
html_use_modindex = False
html_use_index = False
html_copy_source = False

# Static files (CSS, JavaScript, Images)
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_js_files = ["custom.js"]

# Logo and Favicon
html_logo = "_static/logo.svg"
html_favicon = "_static/favicon.ico"

# See https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#confval-intersphinx_mapping for the syntax
intersphinx_mapping = {
    "python": ("https://docs.python.org/2/", None),
    "python3": ("https://docs.python.org/3/", None),
    "jinja2": ("https://jinja.palletsprojects.com/en/stable/", None),
    "ansible_devel": ("https://docs.ansible.com/ansible/devel/", None),
    # If you want references to resolve to a released Ansible version (say, `5`), uncomment and replace X by this version:
    # 'ansibleX': ('https://docs.ansible.com/ansible/X/', None),
}

default_role = "any"

nitpicky = True

# Sitemap configuration
html_baseurl = "https://guide.arillso.io/"
sitemap_url_scheme = "{link}"

html_theme_options = {
    # URLs and canonical settings
    "canonical_url": "https://guide.arillso.io/",
    "documentation_home_url": "/",
    # Topbar navigation links
    "topbar_links": {
        "GitHub": "https://github.com/arillso",
        "Discussions": "https://github.com/orgs/arillso/discussions",
        "Collections": "https://galaxy.ansible.com/ui/namespaces/arillso/",
        "Docker Hub": "https://hub.docker.com/r/arillso/ansible",
        "GitHub Actions": "https://github.com/marketplace/actions/play-ansible-playbook",
    },
    # Branding and logo
    "logo_only": True,
    "display_version": False,
    # Navigation behavior
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
    # Page navigation
    "prev_next_buttons_location": "both",
    # Styling
    "style_external_links": True,
    "style_nav_header_background": "#2c3e50",
    # Tracking and analytics (disabled)
    "analytics_id": "",
    "analytics_anonymize_ip": False,
    # Additional features
    "vcs_pageview_mode": "",
    "show_rtd_ethical_ads": False,
}
