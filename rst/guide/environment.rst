
:orphan:

.. meta::
  :antsibull-docs: 2.5.0.post0

.. contents::
   :local:
   :depth: 1

.. _vs_code_setup_for_ansible:

VS Code Setup for Ansible
=========================

This guide outlines the steps and recommended plugins for setting up Visual Studio Code for developing Ansible Collections.

Recommended Plugins
--------------------

1. `Ansible Extension by Red Hat <https://marketplace.visualstudio.com/items?itemName=redhat.ansible>`_: Provides support for Ansible syntax, autocompletion, snippets, and linting.

2. `YAML <https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml>`_: Supports YAML syntax, essential for Ansible files.

3. `Python Extension <https://marketplace.visualstudio.com/items?itemName=ms-python.python>`_: Useful for Python scripting in Ansible modules.

4. `GitLens <https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens>`_: Enhances Git functionalities in VS Code, useful for version control.

5. `Docker <https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker>`_: If working with Docker containers, this extension offers handy features.

.editorconfig for Ansible Collections
--------------------------------------

The .editorconfig file helps maintain a consistent coding style. Below is an example configuration:

.. code-block:: ini

    # EditorConfig: http://editorconfig.org

    # This entry designates this configuration as being at the root of the project and should be used by EditorConfig.
    root = true

    # These settings apply to all file types.
    [*]
    # Sets the character encoding to UTF-8 for all files.
    charset = utf-8
    # Specifies that indentation should use spaces.
    indent_style = space
    # Sets the indentation size to 4 spaces.
    indent_size = 4
    # Ensures that line endings are marked with LF (Line Feed), typical for Unix/Linux systems.
    end_of_line = lf
    # Automatically removes trailing whitespace at the end of lines.
    trim_trailing_whitespace = true
    # Automatically adds a new line at the end of every file.
    insert_final_newline = true

    # Specific settings for YAML files.
    [*.yml]
    # Sets the indentation size for YAML files to 2 spaces.
    indent_size = 2

.pre-commit-config.yaml for Ansible
-----------------------------------

The .pre-commit-config.yaml file ensures that committed changes adhere to certain guidelines. Here's an example configuration:

.. code-block:: yaml

    # Defines repositories for pre-commit hooks.
    repos:
      # First repository: Ansible Lint
      - repo: https://github.com/ansible/ansible-lint
        # Specifies the version of the Ansible Lint tool to use. Here, v5.0.0 is specified.
        rev: v5.0.0  # Use the latest version
        # Defines which hooks to use from this repository.
        hooks:
          # Uses the ansible-lint hook for linting Ansible playbooks and roles.
          - id: ansible-lint
      
      # Second repository: pre-commit common hooks
      - repo: https://github.com/pre-commit/pre-commit-hooks
        # Specifies the version of the pre-commit common hooks to use. Here, v3.0.0 is specified.
        rev: v3.0.0  # Use the latest version
        # Defines which hooks to use from this repository.
        hooks:
          # This hook removes trailing whitespace from lines in files.
          - id: trailing-whitespace
          # This hook ensures that a file ends with a newline (end-of-file fix).
          - id: end-of-file-fixer
          # This hook checks the syntax of YAML files.
          - id: check-yaml

Environment Setup Steps
-----------------------

1. Install Visual Studio Code and the extensions mentioned above.

2. Create the .editorconfig file in the root directory of the project.

3. Install Pre-Commit on the system if not already done. More information about Pre-Commit can be found at `Pre-Commit <https://pre-commit.com/>`_.

4. Create the .pre-commit-config.yaml file. Run the following command in the terminal to activate the hooks:

.. code-block:: console

    pre-commit install

5. Begin developing the Ansible Collection, with the configuration files ensuring that the code remains consistent and clean.
