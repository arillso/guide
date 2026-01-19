.. meta::
  :description: Go module for programmatically executing Ansible playbooks with Galaxy integration and secure file management

.. _go_ansible:

go.ansible
==========

A Go module for programmatically executing Ansible playbooks with support for Galaxy integration, temporary file management, and flexible configuration.

.. contents::
   :local:
   :depth: 2

Overview
--------

``go.ansible`` enables embedding Ansible automation within Go applications, providing a clean API for executing playbooks, managing credentials, and integrating with Ansible Galaxy.

**Repository:** https://github.com/arillso/go.ansible

**Documentation:** https://pkg.go.dev/github.com/arillso/go.ansible

**Go Version:** 1.25+

Features
--------

Playbook Execution
~~~~~~~~~~~~~~~~~~

* Execute Ansible playbooks from Go applications
* Context-based execution with cancellation support
* Command output streaming and capture
* Debug mode with command tracing

Secure File Management
~~~~~~~~~~~~~~~~~~~~~~

* Automatic temporary file creation for SSH keys
* Secure handling of Vault passwords
* Automatic cleanup of sensitive files
* File permission management (0600 for keys)

Galaxy Integration
~~~~~~~~~~~~~~~~~~

* Automatic role installation from Galaxy
* Collection installation support
* Requirements file processing (``requirements.yml``)
* Custom Galaxy server configuration

Flexible Configuration
~~~~~~~~~~~~~~~~~~~~~~

* Builder pattern for option setting
* Support for all ansible-playbook flags
* Extra variables (key=value or JSON)
* Inventory management (files or inline)
* SSH configuration and key management

Installation
------------

Install the module:

.. code-block:: bash

   go get github.com/arillso/go.ansible

Quick Start
-----------

Basic Usage
~~~~~~~~~~~

.. code-block:: go

   package main

   import (
       "context"
       "log"
       "github.com/arillso/go.ansible"
   )

   func main() {
       pb := ansible.NewPlaybook()
       pb.Config.Playbooks = []string{"site.yml"}
       pb.Config.Inventories = []string{"inventory.yml"}

       if err := pb.Exec(context.Background()); err != nil {
           log.Fatalf("Execution failed: %v", err)
       }
   }

With Extra Variables
~~~~~~~~~~~~~~~~~~~~

.. code-block:: go

   pb := ansible.NewPlaybook()
   pb.Config.Playbooks = []string{"deploy.yml"}
   pb.Config.Inventories = []string{"production"}
   pb.Config.ExtraVars = []string{
       "version=1.2.3",
       "environment=production",
   }

   err := pb.Exec(context.Background())

Using Galaxy Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: go

   pb := ansible.NewPlaybook()
   pb.Config.GalaxyFile = "requirements.yml"
   pb.Config.Playbooks = []string{"site.yml"}
   pb.Config.Inventories = []string{"hosts.yml"}

   // Galaxy roles/collections will be installed automatically
   err := pb.Exec(context.Background())

SSH Key Management
~~~~~~~~~~~~~~~~~~

.. code-block:: go

   pb := ansible.NewPlaybook()
   pb.Config.PrivateKey = `-----BEGIN RSA PRIVATE KEY-----
   MIIEpAIBAAKCAQEA...
   -----END RSA PRIVATE KEY-----`
   pb.Config.Playbooks = []string{"deploy.yml"}

   // SSH key is written to temporary file automatically
   // and cleaned up after execution
   err := pb.Exec(context.Background())

Vault Integration
~~~~~~~~~~~~~~~~~

.. code-block:: go

   pb := ansible.NewPlaybook()
   pb.Config.VaultPassword = "my-secret-password"
   pb.Config.VaultID = "production@vault-file"
   pb.Config.Playbooks = []string{"encrypted.yml"}

   err := pb.Exec(context.Background())

Advanced Usage
--------------

Context and Cancellation
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: go

   ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
   defer cancel()

   pb := ansible.NewPlaybook()
   pb.Config.Playbooks = []string{"long-running.yml"}

   // Execution will be cancelled after 5 minutes
   err := pb.Exec(ctx)

Debug Mode
~~~~~~~~~~

.. code-block:: go

   pb := ansible.NewPlaybook()
   pb.Config.Debug = true  // Print full ansible-playbook command
   pb.Config.Verbose = 4   // Maximum Ansible verbosity
   pb.Config.Playbooks = []string{"debug.yml"}

   err := pb.Exec(context.Background())

Check Mode (Dry Run)
~~~~~~~~~~~~~~~~~~~~

.. code-block:: go

   pb := ansible.NewPlaybook()
   pb.Config.Check = true  // Don't make any changes
   pb.Config.Diff = true   // Show differences
   pb.Config.Playbooks = []string{"changes.yml"}

   err := pb.Exec(context.Background())

Glob Pattern Support
~~~~~~~~~~~~~~~~~~~~

.. code-block:: go

   pb := ansible.NewPlaybook()
   pb.Config.PlaybookGlob = "playbooks/*.yml"  // Automatically resolved

   err := pb.Exec(context.Background())

Configuration Options
---------------------

PlaybookConfig Structure
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: go

   type PlaybookConfig struct {
       // Playbooks and Inventory
       Playbooks     []string
       PlaybookGlob  string
       Inventories   []string

       // Galaxy
       GalaxyFile    string

       // Credentials
       PrivateKey    string
       VaultPassword string
       VaultID       string

       // Execution Options
       Check         bool
       Diff          bool
       Debug         bool
       Verbose       int
       ExtraVars     []string
       Tags          []string
       SkipTags      []string
       Limit         string

       // SSH Options
       User          string
       Connection    string
       Timeout       int
       SSHCommonArgs string

       // Privilege Escalation
       Become        bool
       BecomeMethod  string
       BecomeUser    string
   }

Common Patterns
---------------

Infrastructure Deployment
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: go

   func DeployInfrastructure(version string) error {
       pb := ansible.NewPlaybook()
       pb.Config.GalaxyFile = "requirements.yml"
       pb.Config.Playbooks = []string{"infrastructure.yml"}
       pb.Config.Inventories = []string{"production"}
       pb.Config.ExtraVars = []string{
           fmt.Sprintf("app_version=%s", version),
       }
       pb.Config.PrivateKey = os.Getenv("SSH_PRIVATE_KEY")

       return pb.Exec(context.Background())
   }

CI/CD Integration
~~~~~~~~~~~~~~~~~

.. code-block:: go

   func RunCIDeployment(ctx context.Context) error {
       pb := ansible.NewPlaybook()
       pb.Config.Playbooks = []string{"deploy.yml"}
       pb.Config.Inventories = []string{"staging"}
       pb.Config.Check = os.Getenv("DRY_RUN") == "true"
       pb.Config.Diff = true
       pb.Config.ExtraVars = []string{
           fmt.Sprintf("git_commit=%s", os.Getenv("CI_COMMIT_SHA")),
           fmt.Sprintf("git_branch=%s", os.Getenv("CI_COMMIT_BRANCH")),
       }

       return pb.Exec(ctx)
   }

Dynamic Inventory
~~~~~~~~~~~~~~~~~

.. code-block:: go

   func DeployToHosts(hosts []string) error {
       // Create inline inventory
       inventory := strings.Join(hosts, ",") + ","

       pb := ansible.NewPlaybook()
       pb.Config.Playbooks = []string{"configure.yml"}
       pb.Config.Inventories = []string{inventory}

       return pb.Exec(context.Background())
   }

Error Handling
--------------

Wrapped Errors
~~~~~~~~~~~~~~

All errors are wrapped with context using ``github.com/pkg/errors``:

.. code-block:: go

   if err := pb.Exec(ctx); err != nil {
       // Errors include context about what failed
       log.Printf("Deployment failed: %+v", err)
       // Example: "executing playbook: running command: exit status 2"
   }

Validation Errors
~~~~~~~~~~~~~~~~~

Configuration is validated before execution:

.. code-block:: go

   pb := ansible.NewPlaybook()
   // pb.Config.Playbooks not set

   err := pb.Exec(ctx)
   // Error: "no playbooks specified"

Testing
-------

The module includes comprehensive tests:

.. code-block:: bash

   # Run all tests
   go test -v ./...

   # Run with coverage
   go test -cover ./...

   # Run specific test
   go test -run TestPlaybook_Exec ./...

Example Tests
~~~~~~~~~~~~~

.. code-block:: go

   func TestPlaybookExecution(t *testing.T) {
       pb := ansible.NewPlaybook()
       pb.Config.Playbooks = []string{"test.yml"}
       pb.Config.Inventories = []string{"localhost,"}
       pb.Config.ExtraVars = []string{"test_var=value"}

       err := pb.Exec(context.Background())
       assert.NoError(t, err)
   }

Best Practices
--------------

Security
~~~~~~~~

1. **Never hardcode credentials:**

   .. code-block:: go

      // Bad
      pb.Config.VaultPassword = "my-password"

      // Good
      pb.Config.VaultPassword = os.Getenv("VAULT_PASSWORD")

2. **Use context for timeouts:**

   .. code-block:: go

      ctx, cancel := context.WithTimeout(context.Background(), 10*time.Minute)
      defer cancel()
      err := pb.Exec(ctx)

3. **Validate inputs:**

   .. code-block:: go

      if version == "" {
          return errors.New("version is required")
      }
      pb.Config.ExtraVars = []string{fmt.Sprintf("version=%s", version)}

Resource Management
~~~~~~~~~~~~~~~~~~~

The module automatically manages temporary files, but ensure proper context usage:

.. code-block:: go

   func deploy() error {
       ctx, cancel := context.WithCancel(context.Background())
       defer cancel()  // Ensure cleanup on early return

       pb := ansible.NewPlaybook()
       // ... configuration ...

       return pb.Exec(ctx)
   }

Debugging
~~~~~~~~~

Enable debug mode during development:

.. code-block:: go

   if os.Getenv("DEBUG") == "true" {
       pb.Config.Debug = true
       pb.Config.Verbose = 4
   }

Dependencies
------------

The module has minimal dependencies:

.. code-block:: go

   require (
       github.com/pkg/errors v0.9.1
   )

CI/CD Workflows
---------------

The project includes automated workflows:

* **Linting** (golangci-lint, staticcheck)
* **Testing** (Go 1.25+)
* **Security Scanning** (CodeQL, Trivy)
* **Release Builds** (automated versioning)

License
-------

MIT License - Copyright (c) 2026, arillso

.. seealso::

   * :ref:`docker.ansible <docker_ansible>` - Ansible container used for execution
   * :ref:`action.playbook <action_playbook>` - GitHub Action using similar patterns
   * Go Package Documentation: https://pkg.go.dev/github.com/arillso/go.ansible
