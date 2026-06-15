# Contributing to the Arillso Guide

Thank you for your interest in contributing! This document provides guidelines
and instructions. This repository builds the documentation site published at
<https://guide.arillso.io>.

## Prerequisites

- Python >= 3.12
- Git
- Docker (optional, for a containerised build via `docker-compose.yml`)

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/guide.git
cd guide
git remote add upstream https://github.com/arillso/guide.git
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install git hooks

```bash
lefthook install
```

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

## Building

```bash
./build.sh
```

The rendered site lands in `build/html`. Generated artefacts (`build/`,
`temp-rst/`, `rst/collections/`) are git-ignored and must not be committed.

## Coding Standards

### YAML

- Use 4 spaces for indentation (no tabs)
- Keep lines under 160 characters
- Require `---` document start

### Markdown

- Follows `.markdownlint.json`

### Editor

- `.editorconfig` defines indentation, charset, and line endings

Run the hooks locally with `lefthook install`; they run prettier, yamllint,
markdownlint, actionlint, and gitleaks on commit.

## Submitting Changes

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```text
type(scope): brief summary

- Detailed description with bullet points
- Reference related issues

Fixes #123
```

### Pull Request Process

1. Ensure your branch is up to date with `main`
2. Run the build and the hooks; fix all issues
3. Update relevant documentation
4. Create a PR using our [PR template](.github/pull_request_template.md)
5. Fill out all template sections and link related issues

### PR Review

- A maintainer will review your PR
- Address any requested changes
- All CI checks must pass
- At least one maintainer approval required

## Getting Help

- **Issues**: Use GitHub issues for bugs and feature requests
- **Templates**: Use our issue templates for structured reports

---

**Thank you for contributing!**
