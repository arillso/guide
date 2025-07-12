# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Created with antsibull-docs 2.5.0.post0

# This file only contains a selection of the most common options. For a full list see the
# documentation:
# http://www.sphinx-doc.org/en/master/config

project = 'Arillso Guide'
copyright = 'Arillso contributors'

title = 'Arillso Guide Documentation'
html_short_title = 'Arillso Guide Documentation'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx_antsibull_ext']

pygments_style = 'ansible'

highlight_language = 'YAML+Jinja'

html_theme = 'sphinx_ansible_theme'
html_show_sphinx = False

display_version = False

html_use_smartypants = True
html_use_modindex = False
html_use_index = False
html_copy_source = False

# See https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#confval-intersphinx_mapping for the syntax
intersphinx_mapping = {
    'python': ('https://docs.python.org/2/', None),
    'python3': ('https://docs.python.org/3/', None),
    'jinja2': ('https://jinja.palletsprojects.com/en/stable/', None),
    'ansible_devel': ('https://docs.ansible.com/ansible/devel/', None),
    # If you want references to resolve to a released Ansible version (say, `5`), uncomment and replace X by this version:
    # 'ansibleX': ('https://docs.ansible.com/ansible/X/', None),
}

default_role = 'any'

nitpicky = True

html_theme_options = {
    # 'canonical_url': "https://docs.ansible.com/ansible/latest/",
    'topbar_links': {
        'Home': 'https://arillso.io',
    },
    # URL to send the user to when clicking on the title link
    'documentation_home_url': '/',
}
