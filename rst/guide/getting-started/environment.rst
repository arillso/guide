.. meta::
  :description: Development environment setup for arillso collections
  :keywords: arillso, development, environment, setup, ide, tools

.. _environment:

Development Environment
=======================

Complete guide for setting up your development environment for arillso collections and Ansible development.

.. contents::
   :local:
   :depth: 2

Prerequisites
-------------

System Requirements
~~~~~~~~~~~~~~~~~~~

**Minimum:**

* **CPU:** 2 cores
* **RAM:** 4 GB
* **Disk:** 20 GB free space
* **OS:** Linux, macOS, or Windows with WSL2

**Recommended:**

* **CPU:** 4+ cores
* **RAM:** 8+ GB
* **Disk:** 50+ GB SSD
* **OS:** Ubuntu 22.04 or macOS

Required Software
~~~~~~~~~~~~~~~~~

**Core tools:**

.. code-block:: bash

   # Check versions
   python3 --version  # >= 3.9
   git --version      # >= 2.30
   ssh -V             # OpenSSH >= 7.0

**Install Python and pip:**

.. code-block:: bash

   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv

   # macOS
   brew install python@3.11

   # Verify
   python3 --version
   pip3 --version

Quick Start Setup
-----------------

One-Command Setup
~~~~~~~~~~~~~~~~~

**Ubuntu/Debian:**

.. code-block:: bash

   curl -sSL https://raw.githubusercontent.com/arillso/guide/main/scripts/setup-dev.sh | bash

**macOS:**

.. code-block:: bash

   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/arillso/guide/main/scripts/setup-dev-mac.sh)"

Manual Setup
~~~~~~~~~~~~

.. code-block:: bash

   # 1. Install Ansible
   pip3 install ansible>=2.15

   # 2. Install development tools
   pip3 install ansible-lint yamllint molecule pytest

   # 3. Install arillso collections
   ansible-galaxy collection install arillso.system
   ansible-galaxy collection install arillso.container
   ansible-galaxy collection install arillso.agent

   # 4. Verify installation
   ansible --version
   ansible-galaxy collection list | grep arillso

IDE Setup
---------

Visual Studio Code (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Install VS Code:**

.. code-block:: bash

   # Ubuntu/Debian
   wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
   sudo install -o root -g root -m 644 packages.microsoft.gpg /usr/share/keyrings/
   sudo sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
   sudo apt update
   sudo apt install code

   # macOS
   brew install --cask visual-studio-code

**Essential VS Code Extensions:**

1. **Ansible** (redhat.ansible)

   .. code-block:: bash

      code --install-extension redhat.ansible

   * Syntax highlighting
   * IntelliSense for Ansible
   * Snippet support
   * Integrated linting

2. **YAML** (redhat.vscode-yaml)

   .. code-block:: bash

      code --install-extension redhat.vscode-yaml

   * YAML validation
   * Schema support
   * Auto-formatting

3. **Python** (ms-python.python)

   .. code-block:: bash

      code --install-extension ms-python.python

   * Python IntelliSense
   * Debugging
   * Linting (Pylint, Flake8)

4. **GitLens** (eamodio.gitlens)

   .. code-block:: bash

      code --install-extension eamodio.gitlens

   * Git blame annotations
   * Repository insights
   * Commit history

5. **Docker** (ms-azuretools.vscode-docker)

   .. code-block:: bash

      code --install-extension ms-azuretools.vscode-docker

   * Dockerfile syntax
   * Container management
   * Compose file support

**Install all at once:**

.. code-block:: bash

   code --install-extension redhat.ansible \
        --install-extension redhat.vscode-yaml \
        --install-extension ms-python.python \
        --install-extension eamodio.gitlens \
        --install-extension ms-azuretools.vscode-docker

**VS Code Settings:**

Create ``.vscode/settings.json`` in your project:

.. code-block:: json

   {
     "ansible.python.interpreterPath": "/usr/bin/python3",
     "ansible.validation.enabled": true,
     "ansible.validation.lint.enabled": true,
     "ansible.validation.lint.path": "ansible-lint",

     "yaml.schemas": {
       "https://json.schemastore.org/ansible-playbook.json": [
         "playbooks/**/*.yml",
         "playbooks/**/*.yaml"
       ]
     },

     "files.associations": {
       "*.yml": "ansible",
       "*.yaml": "ansible"
     },

     "editor.rulers": [120],
     "editor.formatOnSave": true,

     "python.linting.enabled": true,
     "python.linting.pylintEnabled": true
   }

JetBrains IDEs (PyCharm, IntelliJ)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Install:**

.. code-block:: bash

   # Download from https://www.jetbrains.com/pycharm/

**Recommended Plugins:**

1. **Ansible**
2. **YAML/Ansible support**
3. **Docker**
4. **Kubernetes**

**Configure:**

1. File → Settings → Languages & Frameworks → Ansible
2. Enable Ansible support
3. Set Python interpreter
4. Configure ansible-lint

Vim/Neovim
~~~~~~~~~~

**For Vim users:**

.. code-block:: bash

   # Install vim-plug
   curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
       https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

**Add to `.vimrc`:**

.. code-block:: vim

   call plug#begin('~/.vim/plugged')

   " Ansible syntax
   Plug 'pearofducks/ansible-vim'

   " YAML support
   Plug 'stephpy/vim-yaml'

   " Linting
   Plug 'dense-analysis/ale'

   call plug#end()

   " ALE configuration
   let g:ale_linters = {
   \   'ansible': ['ansible-lint'],
   \   'yaml': ['yamllint'],
   \}

**Install plugins:**

.. code-block:: bash

   vim +PlugInstall +qall

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

Project Configuration
---------------------

Create these configuration files in your project root:

**.editorconfig**

Maintains consistent coding style across editors and IDEs:

.. code-block:: bash

   # Create .editorconfig
   cat > .editorconfig <<EOF
   root = true

   [*]
   charset = utf-8
   indent_style = space
   indent_size = 4
   end_of_line = lf
   trim_trailing_whitespace = true
   insert_final_newline = true

   [*.{yml,yaml}]
   indent_size = 2

   [*.md]
   trim_trailing_whitespace = false

   [Makefile]
   indent_style = tab
   EOF

**.yamllint.yml**

YAML linting configuration:

.. code-block:: bash

   cat > .yamllint.yml <<EOF
   ---
   extends: default
   rules:
     braces:
       max-spaces-inside: 1
     new-lines:
       type: unix
     line-length:
       max: 500
     comments:
       min-spaces-from-content: 1
     truthy:
       allowed-values: ["true", "false", "on"]
   EOF

**.ansible-lint**

Ansible linting configuration:

.. code-block:: bash

   cat > .ansible-lint <<EOF
   ---
   profile: production
   strict: true
   offline: false

   skip_list:
     - yaml[line-length]
     - name[casing]

   warn_list:
     - experimental

   exclude_paths:
     - .github/
     - .ansible/
     - molecule/
     - tests/
   EOF

Development Tools
-----------------

Linters and Formatters
~~~~~~~~~~~~~~~~~~~~~~~

**Install linting tools:**

.. code-block:: bash

   # Python tools
   pip3 install \
     ansible-lint \
     yamllint \
     pylint \
     black \
     isort

   # Verify installation
   ansible-lint --version
   yamllint --version
   pylint --version

**Usage:**

.. code-block:: bash

   # Lint Ansible code
   ansible-lint playbooks/

   # Lint YAML files
   yamllint .

   # Format Python code
   black plugins/modules/

   # Sort Python imports
   isort plugins/modules/

Testing Tools
~~~~~~~~~~~~~

**Install testing frameworks:**

.. code-block:: bash

   # Molecule for role testing
   pip3 install molecule molecule-plugins[docker]

   # Pytest for unit tests
   pip3 install pytest pytest-ansible pytest-cov

**Create molecule scenario:**

.. code-block:: bash

   cd roles/myrole
   molecule init scenario default

**Run tests:**

.. code-block:: bash

   # Molecule tests
   molecule test

   # Pytest
   pytest tests/unit/

   # With coverage
   pytest --cov=plugins tests/

Docker Development Environment
-------------------------------

Use Docker for isolated development:

**Method 1: arillso Container**

.. code-block:: bash

   # Pull arillso/ansible image
   docker pull arillso/ansible:latest

   # Run interactive shell
   docker run -it --rm \
     -v $(pwd):/workspace \
     -w /workspace \
     arillso/ansible bash

   # Run playbook in container
   docker run --rm \
     -v $(pwd):/workspace \
     -v ~/.ssh:/root/.ssh:ro \
     -w /workspace \
     arillso/ansible \
     ansible-playbook site.yml

**Method 2: Dev Container**

Create ``.devcontainer/devcontainer.json``:

.. code-block:: json

   {
     "name": "Ansible Development",
     "image": "arillso/ansible:latest",
     "customizations": {
       "vscode": {
         "extensions": [
           "redhat.ansible",
           "redhat.vscode-yaml",
           "ms-python.python"
         ]
       }
     },
     "mounts": [
       "source=${localEnv:HOME}/.ssh,target=/root/.ssh,type=bind,consistency=cached"
     ],
     "postCreateCommand": "ansible-galaxy collection install -r requirements.yml"
   }

**Open in VS Code:**

1. Install "Remote - Containers" extension
2. Open folder in VS Code
3. Click "Reopen in Container"

Virtual Environments
--------------------

Python venv
~~~~~~~~~~~

Create isolated Python environments:

.. code-block:: bash

   # Create venv
   python3 -m venv ~/.venv/ansible

   # Activate
   source ~/.venv/ansible/bin/activate

   # Install packages
   pip install ansible ansible-lint molecule

   # Deactivate
   deactivate

**Auto-activate in project:**

.. code-block:: bash

   # Add to .bashrc or .zshrc
   cd() {
     builtin cd "$@"
     if [[ -f .venv/bin/activate ]]; then
       source .venv/bin/activate
     fi
   }

pipx for Tools
~~~~~~~~~~~~~~

Install Ansible tools in isolated environments:

.. code-block:: bash

   # Install pipx
   pip3 install --user pipx
   pipx ensurepath

   # Install Ansible
   pipx install ansible

   # Install additional tools
   pipx install ansible-lint
   pipx install molecule

   # Inject packages
   pipx inject ansible argcomplete

Git Configuration
-----------------

Git Hooks
~~~~~~~~~

**Pre-commit hooks:**

.. code-block:: bash

   # Install pre-commit
   pip3 install pre-commit

   # Create .pre-commit-config.yaml
   cat > .pre-commit-config.yaml <<EOF
   ---
   repos:
     - repo: https://github.com/pre-commit/pre-commit-hooks
       rev: v4.5.0
       hooks:
         - id: trailing-whitespace
         - id: end-of-file-fixer
         - id: check-yaml
         - id: check-merge-conflict
         - id: check-added-large-files

     - repo: https://github.com/adrienverge/yamllint
       rev: v1.33.0
       hooks:
         - id: yamllint

     - repo: https://github.com/ansible/ansible-lint
       rev: v6.22.1
       hooks:
         - id: ansible-lint
           files: \.(yaml|yml)$
   EOF

   # Install hooks
   pre-commit install

   # Run manually
   pre-commit run --all-files

Git Aliases
~~~~~~~~~~~

Add to ``~/.gitconfig``:

.. code-block:: ini

   [alias]
     # Shortcuts
     st = status
     co = checkout
     br = branch
     ci = commit

     # Pretty log
     lg = log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit

     # Amend last commit
     amend = commit --amend --no-edit

CI/CD Local Testing
-------------------

Test GitHub Actions Locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install act
   # macOS
   brew install act

   # Ubuntu/Debian
   curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

   # Run workflows
   act -l  # List workflows
   act     # Run default workflow
   act pull_request  # Run PR workflow

GitLab CI Local Testing
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install gitlab-runner
   brew install gitlab-runner  # macOS
   curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
   sudo apt-get install gitlab-runner  # Ubuntu

   # Run locally
   gitlab-runner exec docker test

Performance Optimization
------------------------

Ansible Configuration
~~~~~~~~~~~~~~~~~~~~~

Create ``ansible.cfg`` for better performance:

.. code-block:: ini

   [defaults]
   inventory = inventory/
   remote_user = ubuntu
   host_key_checking = False
   retry_files_enabled = False

   # Performance
   forks = 20
   gathering = smart
   fact_caching = jsonfile
   fact_caching_connection = /tmp/ansible_facts
   fact_caching_timeout = 86400

   # Plugins
   callback_whitelist = profile_tasks, timer

   [ssh_connection]
   pipelining = True
   control_path = ~/.ssh/cm-%r@%h:%p
   control_master = auto
   control_persist = 60s

Mitogen Strategy
~~~~~~~~~~~~~~~~

Install Mitogen for 2-7x performance improvement:

.. code-block:: bash

   # Install Mitogen
   pip3 install mitogen

   # Configure in ansible.cfg
   cat >> ansible.cfg <<EOF
   [defaults]
   strategy_plugins = /path/to/mitogen/ansible_mitogen/plugins/strategy
   strategy = mitogen_linear
   EOF

Troubleshooting Setup
---------------------

Common Issues
~~~~~~~~~~~~~

**Python not found:**

.. code-block:: bash

   # Set Python interpreter
   export ANSIBLE_PYTHON_INTERPRETER=/usr/bin/python3

   # Or in inventory
   [all:vars]
   ansible_python_interpreter=/usr/bin/python3

**Collection not found:**

.. code-block:: bash

   # Check collection path
   ansible-config dump | grep COLLECTIONS_PATHS

   # Add to ansible.cfg
   [defaults]
   collections_paths = ./collections:~/.ansible/collections

**Permission errors:**

.. code-block:: bash

   # Install to user directory
   pip3 install --user ansible

   # Or use venv
   python3 -m venv ~/.venv/ansible
   source ~/.venv/ansible/bin/activate

Environment Checklist
---------------------

Verify your setup:

.. code-block:: bash

   # Create verification script
   cat > verify-setup.sh <<'EOF'
   #!/bin/bash

   echo "=== Ansible Development Environment Check ==="

   # Python
   echo -n "Python 3: "
   python3 --version || echo "❌ Not found"

   # Ansible
   echo -n "Ansible: "
   ansible --version | head -1 || echo "❌ Not found"

   # Collections
   echo "arillso Collections:"
   ansible-galaxy collection list 2>/dev/null | grep arillso || echo "❌ Not installed"

   # Tools
   echo -n "ansible-lint: "
   ansible-lint --version 2>/dev/null || echo "❌ Not found"

   echo -n "yamllint: "
   yamllint --version 2>/dev/null || echo "❌ Not found"

   echo -n "molecule: "
   molecule --version 2>/dev/null || echo "❌ Not found"

   echo "=== Check Complete ==="
   EOF

   chmod +x verify-setup.sh
   ./verify-setup.sh

✅ **Setup checklist:**

* [ ] Python 3.9+ installed
* [ ] Ansible 2.15+ installed
* [ ] arillso collections installed
* [ ] IDE configured with extensions
* [ ] Linters installed (ansible-lint, yamllint)
* [ ] Git hooks configured (pre-commit)
* [ ] Testing tools installed (molecule, pytest)
* [ ] SSH keys configured
* [ ] ansible.cfg created

Next Steps
----------

Now that your environment is set up:

1. **Try the quick start:** :ref:`quickstart`
2. **Clone example project:** :ref:`examples`
3. **Read standards:** :ref:`standards`
4. **Contribute:** :ref:`contributing`

Additional Resources
--------------------

Documentation
~~~~~~~~~~~~~

* `Ansible Documentation <https://docs.ansible.com/>`_
* `VS Code Ansible Extension <https://marketplace.visualstudio.com/items?itemName=redhat.ansible>`_
* `Pre-commit Documentation <https://pre-commit.com/>`_

Community
~~~~~~~~~

* `arillso GitHub <https://github.com/arillso>`_
* `Ansible Community <https://www.ansible.com/community>`_

.. seealso::

   * :ref:`quickstart` - Quick Start Guide
   * :ref:`standards` - Repository Standards
   * :ref:`contributing` - Contributing Guidelines
   * :ref:`troubleshooting` - Troubleshooting Guide
