.. meta::
   :description: arillso - Production-ready Ansible collections, container images, and automation tools for modern infrastructure
   :keywords: ansible, automation, devops, infrastructure, containers, kubernetes, docker, gitops, monitoring

.. _docsite_root_index:

arillso
=======

**The simple, flexible, robust and powerful automation platform**

Production-ready Ansible collections, container images, and development tools for modern infrastructure automation.

.. raw:: html

   <div class="landing-hero">
     <p class="hero-tagline">Build, Deploy, and Manage Infrastructure with Confidence</p>
     <div class="hero-badges">
       <img src="https://img.shields.io/badge/Ansible-2.15+-red.svg" alt="Ansible">
       <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
       <img src="https://img.shields.io/badge/Production-Ready-blue.svg" alt="Production Ready">
     </div>
     <div class="hero-cta">
       <a href="guide/getting-started/quickstart.html" class="cta-primary">Get Started</a>
       <a href="collections/index.html" class="cta-secondary">Explore Collections</a>
     </div>
   </div>

----

.. raw:: html

   <div class="feature-grid">
     <div class="feature-card">
       <h3>🚀 Quick Start in Minutes</h3>
       <p>Get started with arillso in under 5 minutes. Install collections, run your first playbook.</p>
       <a href="guide/getting-started/quickstart.html" class="btn-primary">Quick Start Guide →</a>
     </div>
     <div class="feature-card">
       <h3>📚 Complete Examples</h3>
       <p>Production-ready playbooks for web stacks, Kubernetes, monitoring, and more.</p>
       <a href="guide/tutorials/examples.html" class="btn-primary">View Examples →</a>
     </div>
     <div class="feature-card">
       <h3>🔒 Security First</h3>
       <p>Built-in security best practices, hardening guides, and compliance patterns.</p>
       <a href="guide/best-practices/security.html" class="btn-primary">Security Guide →</a>
     </div>
   </div>

Why Choose arillso?
-------------------

**Production-Ready & Battle-Tested**
   All components are tested in production environments with comprehensive CI/CD, security scanning, and 80%+ code coverage.

**Consistent Standards Everywhere**
   Unified development standards, CI/CD workflows, and documentation across all projects. No surprises.

**100% Open Source & MIT Licensed**
   Use freely in any project - personal, commercial, or enterprise. No restrictions.

**Active Development & Support**
   Regular updates, security patches, and new features driven by real-world production needs.

**Comprehensive Documentation**
   From quick starts to architecture guides - everything you need to succeed.

----

Quick Start
-----------

Choose Your Path
~~~~~~~~~~~~~~~~

.. raw:: html

   <div class="quickstart-grid">
     <div class="quickstart-path">
       <h4>System Administrator</h4>
       <p>Manage servers, packages, firewall, networking, system configuration</p>
       <pre><code class="language-bash">ansible-galaxy collection install arillso.system</code></pre>
       <a href="guide/getting-started/quickstart.html#path-system-admin">Learn More →</a>
     </div>
     <div class="quickstart-path">
       <h4>Container Orchestration</h4>
       <p>Deploy Docker, K3s, Kubernetes clusters, container workloads</p>
       <pre><code class="language-bash">ansible-galaxy collection install arillso.container</code></pre>
       <a href="guide/getting-started/quickstart.html#path-containers">Learn More →</a>
     </div>
     <div class="quickstart-path">
       <h4>Agent Management</h4>
       <p>Grafana Alloy, Tailscale, metrics, logs, traces, vpn</p>
       <pre><code class="language-bash">ansible-galaxy collection install arillso.agent</code></pre>
       <a href="guide/getting-started/quickstart.html#path-monitoring">Learn More →</a>
     </div>
   </div>

Installation Options
~~~~~~~~~~~~~~~~~~~~

**Ansible Collections**

.. code-block:: bash

   # Install all collections
   ansible-galaxy collection install arillso.system
   ansible-galaxy collection install arillso.container
   ansible-galaxy collection install arillso.agent

   # Or use requirements file
   cat > requirements.yml <<EOF
   ---
   collections:
     - name: arillso.system
       version: ">=1.0.0"
     - name: arillso.container
       version: ">=1.0.0"
     - name: arillso.agent
       version: ">=1.0.0"
   EOF
   ansible-galaxy collection install -r requirements.yml

**Container Image**

.. code-block:: bash

   # Pull optimized Ansible image (with Mitogen)
   docker pull arillso/ansible:latest

   # Run playbook in container
   docker run --rm \
     -v $(pwd):/workspace \
     -v ~/.ssh:/root/.ssh:ro \
     arillso/ansible ansible-playbook site.yml

**Go Library**

.. code-block:: bash

   # Programmatic Ansible execution
   go get github.com/arillso/go.ansible

**GitHub Actions**

.. code-block:: yaml

   # .github/workflows/deploy.yml
   - name: Deploy Infrastructure
     uses: arillso/action.playbook@v1.2.0
     with:
       playbook: deploy.yml
       inventory: production.yml
       private_key: ${{ secrets.SSH_PRIVATE_KEY }}

----

Popular Use Cases
-----------------

Real-world scenarios with complete, working examples:

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Use Case
     - What You Get
     - Guide
   * - **Docker Server**
     - Docker with firewall and Tailscale VPN
     - :ref:`usecase-docker-server`
   * - **K3s Cluster**
     - Lightweight Kubernetes cluster setup
     - :ref:`usecase-k3s-cluster`
   * - **Developer Workstation**
     - Python, Docker, and dev tools
     - :ref:`usecase-dev-workstation`
   * - **System Hardening**
     - Firewall, SSH rate limiting, kernel tuning
     - :ref:`usecase-system-hardening`

:doc:`View All Use Cases → <guide/tutorials/use-cases>`

----

Platform Components
-------------------

Ansible Collections
~~~~~~~~~~~~~~~~~~~

Production-ready roles, modules, and plugins.

.. list-table::
   :header-rows: 1
   :widths: 25 50 25

   * - Collection
     - Features
     - Documentation
   * - **arillso.system**
     - Packages, firewall, network, logging, tuning, access control
     - :ref:`plugins_in_arillso.system`
   * - **arillso.container**
     - Docker, K3s, Helm, Fleet GitOps, Tailscale mesh
     - :ref:`plugins_in_arillso.container`
   * - **arillso.agent**
     - Grafana Alloy, DigitalOcean agent, Tailscale VPN
     - :ref:`plugins_in_arillso.agent`

**Total:** 24+ roles, 10+ plugins, 5+ modules

Container Images
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Image
     - Features
   * - **arillso/ansible**
     - Alpine-based • Mitogen (2-7x faster) • K8s tools • Multi-platform (amd64, arm64)

**Pull:** ``docker pull arillso/ansible:latest``

Go Libraries
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Library
     - Features
   * - **go.ansible**
     - Programmatic playbook execution • Galaxy integration • Context-aware

**Install:** ``go get github.com/arillso/go.ansible``

GitHub Actions
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Action
     - Features
   * - **action.playbook**
     - Run playbooks in CI/CD • SSH key normalization • Vault support

**Use:** ``arillso/action.playbook@v1.2.0``

----

Architecture & Design
---------------------

.. mermaid::

   mindmap
     root((arillso Platform))
       Ansible Collections
         arillso.system
         arillso.container
         arillso.agent
       Container Images
         arillso/ansible
         Mitogen optimized
         Multi-platform
       Go Libraries
         go.ansible
         Programmatic API
         Context-aware
       GitHub Actions
         action.playbook
         CI/CD ready
         Vault support

**Key Design Principles:**

* **Modularity** - Independent but composable components
* **Production-Ready** - Battle-tested with comprehensive testing
* **Security First** - SHA-pinned deps, CodeQL, Trivy scanning
* **Consistency** - Unified standards across all projects

:doc:`Read Architecture Guide → <guide/getting-started/architecture>`

----

Features & Quality
------------------

.. raw:: html

   <div class="features-quality-grid">
     <div class="quality-card quality-security">
       <div class="quality-icon">🔒</div>
       <h3>Security</h3>
       <ul class="quality-features">
         <li>SHA-pinned GitHub Actions</li>
         <li>CodeQL & Trivy Scanning</li>
         <li>Non-root Containers</li>
         <li>Vault & Bitwarden Integration</li>
         <li>CIS, PCI-DSS, GDPR Ready</li>
       </ul>
       <a href="guide/best-practices/security.html" class="quality-link">Security Guide →</a>
     </div>

     <div class="quality-card quality-testing">
       <div class="quality-icon">🧪</div>
       <h3>Testing</h3>
       <ul class="quality-features">
         <li>pytest with 80%+ coverage</li>
         <li>ansible-test end-to-end</li>
         <li>Molecule multi-platform</li>
         <li>Ubuntu, Debian, RHEL, Alpine</li>
         <li>amd64, arm64 tested</li>
       </ul>
     </div>

     <div class="quality-card quality-cicd">
       <div class="quality-icon">⚙️</div>
       <h3>CI/CD</h3>
       <ul class="quality-features">
         <li>CHANGELOG-driven releases</li>
         <li>Renovate dependency automation</li>
         <li>Consolidated workflows</li>
         <li>GitHub Rulesets protection</li>
         <li>Quality gates enforced</li>
       </ul>
       <a href="guide/development/cicd.html" class="quality-link">CI/CD Standards →</a>
     </div>

     <div class="quality-card quality-code">
       <div class="quality-icon">✨</div>
       <h3>Code Quality</h3>
       <ul class="quality-features">
         <li>ansible-lint production profile</li>
         <li>yamllint validation</li>
         <li>golangci-lint for Go</li>
         <li>Pre-commit hooks</li>
         <li>EditorConfig consistency</li>
       </ul>
     </div>
   </div>

----

Documentation Hub
-----------------

.. raw:: html

   <div class="doc-hub-grid">
     <!-- Getting Started Section -->
     <div class="doc-hub-section">
       <h3>🚀 Getting Started</h3>
       <div class="doc-links">
         <a href="guide/getting-started/quickstart.html" class="doc-link">
           <span class="doc-title">Quick Start Guide</span>
           <span class="doc-description">Get up and running in 5 minutes</span>
         </a>
         <a href="guide/getting-started/environment.html" class="doc-link">
           <span class="doc-title">Development Environment</span>
           <span class="doc-description">Set up your development environment</span>
         </a>
         <a href="guide/getting-started/architecture.html" class="doc-link">
           <span class="doc-title">Platform Architecture</span>
           <span class="doc-description">Understand the platform design</span>
         </a>
       </div>
     </div>

     <!-- Working with arillso Section -->
     <div class="doc-hub-section">
       <h3>📚 Working with arillso</h3>
       <div class="doc-links">
         <a href="guide/tutorials/use-cases.html" class="doc-link">
           <span class="doc-title">Use Cases</span>
           <span class="doc-description">10+ real-world scenarios</span>
         </a>
         <a href="guide/tutorials/examples.html" class="doc-link">
           <span class="doc-title">Complete Examples</span>
           <span class="doc-description">Complete playbook examples</span>
         </a>
         <a href="guide/best-practices/security.html" class="doc-link">
           <span class="doc-title">Security Best Practices</span>
           <span class="doc-description">Security best practices</span>
         </a>
       </div>
     </div>

     <!-- Reference Section -->
     <div class="doc-hub-section">
       <h3>📖 Reference</h3>
       <div class="doc-links">
         <a href="guide/reference/compatibility.html" class="doc-link">
           <span class="doc-title">Compatibility Matrix</span>
           <span class="doc-description">Version compatibility matrix</span>
         </a>
         <a href="guide/reference/troubleshooting.html" class="doc-link">
           <span class="doc-title">Troubleshooting</span>
           <span class="doc-description">FAQ and debugging guide</span>
         </a>
         <a href="guide/best-practices/standards.html" class="doc-link">
           <span class="doc-title">Repository Standards</span>
           <span class="doc-description">Repository standards</span>
         </a>
         <a href="guide/development/contributing.html" class="doc-link">
           <span class="doc-title">Contributing Guide</span>
           <span class="doc-description">Contribution guidelines</span>
         </a>
       </div>
     </div>
   </div>

----

Community & Support
-------------------

.. raw:: html

   <div class="community-section">
     <div class="community-links">
       <div class="community-card">
         <h4>🐙 GitHub</h4>
         <p>Browse source code, report issues, contribute</p>
         <a href="https://github.com/arillso" target="_blank">github.com/arillso</a>
       </div>
       <div class="community-card">
         <h4>🌟 Ansible Galaxy</h4>
         <p>Download collections, view stats</p>
         <a href="https://galaxy.ansible.com/ui/namespaces/arillso/" target="_blank">galaxy.ansible.com/arillso</a>
       </div>
       <div class="community-card">
         <h4>🐳 Docker Hub</h4>
         <p>Pull container images</p>
         <a href="https://hub.docker.com/r/arillso/ansible" target="_blank">hub.docker.com/r/arillso</a>
       </div>
     </div>

     <div class="support-cta">
       <h3>Need Help?</h3>
       <p>Choose the best option for your needs:</p>
       <div class="support-options">
         <a href="https://github.com/orgs/arillso/discussions" target="_blank" class="support-btn support-discussions">
           <span class="support-icon">💬</span>
           <span class="support-text">
             <strong>GitHub Discussions</strong>
             <small>Ask questions, share ideas, get community support</small>
           </span>
         </a>
         <a href="https://github.com/arillso" target="_blank" class="support-btn support-issues">
           <span class="support-icon">🐛</span>
           <span class="support-text">
             <strong>Report Issue</strong>
             <small>Found a bug? Report it in the project repository</small>
           </span>
         </a>
         <a href="mailto:hello@arillso.io" class="support-btn support-email">
           <span class="support-icon">✉️</span>
           <span class="support-text">
             <strong>Email Support</strong>
             <small>hello@arillso.io</small>
           </span>
         </a>
       </div>
     </div>
   </div>

**Get Help:**

* **Documentation Issues?** Open an issue on `guide repository <https://github.com/arillso/guide>`_
* **Bug Reports?** Use the issue tracker in the respective project repository
* **Questions?** Check :doc:`guide/reference/troubleshooting` first
* **Contributing?** Read :doc:`guide/development/contributing`

----

Statistics
----------

.. raw:: html

   <div class="stats-grid">
     <div class="stat-card">
       <h3>24+</h3>
       <p>Production Roles</p>
     </div>
     <div class="stat-card">
       <h3>10+</h3>
       <p>Plugins & Filters</p>
     </div>
     <div class="stat-card">
       <h3>80%+</h3>
       <p>Code Coverage</p>
     </div>
     <div class="stat-card">
       <h3>100%</h3>
       <p>Open Source</p>
     </div>
   </div>

----

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Getting Started

   guide/getting-started/quickstart
   guide/getting-started/environment
   guide/getting-started/architecture

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Working with arillso

   guide/tutorials/use-cases
   guide/tutorials/examples
   guide/best-practices/security

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Reference

   guide/reference/compatibility
   guide/reference/troubleshooting
   guide/best-practices/standards
   guide/development/cicd
   guide/development/contributing

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Ansible Collections

   collections/index

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Container Images

   containers/index

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Go Libraries

   libraries/index

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: GitHub Actions

   github/index

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Plugin References
   :glob:

   collections/index_*

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Additional Resources

   collections/environment_variables

License
-------

All arillso projects are released under the **MIT License**.

Copyright (c) 2022-2026, arillso

----

.. raw:: html

   <div class="landing-footer">
     <div class="footer-cta">
       <h3>Ready to Get Started?</h3>
       <p>Choose your path and start automating your infrastructure today.</p>
       <div class="cta-buttons">
         <a href="guide/getting-started/quickstart.html" class="btn-primary-lg">Quick Start Guide</a>
         <a href="guide/tutorials/examples.html" class="btn-secondary-lg">View Examples</a>
         <a href="collections/index.html" class="btn-secondary-lg">Browse Collections</a>
       </div>
     </div>
     <div class="footer-links">
       <p>
         <a href="guide/development/contributing.html">Contributing</a> •
         <a href="guide/reference/troubleshooting.html">FAQ</a> •
         <a href="https://github.com/arillso">GitHub</a> •
         <a href="https://galaxy.ansible.com/ui/namespaces/arillso/">Ansible Galaxy</a>
       </p>
     </div>
   </div>
