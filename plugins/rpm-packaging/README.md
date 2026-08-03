# RPM Packaging Plugin

Write RPM spec files, build with rpmbuild/mock/koji, debug build failures, and package software for Fedora/RHEL/CentOS.

## Skills

### rpm-packaging
Comprehensive guidance for RPM packaging: spec file anatomy, build lifecycle, macros, dependencies, scriptlets, subpackages, rpmlint, signing, and repository creation. Includes language-specific templates for Python, Go, and Rust, plus container-based testing patterns.

**Prerequisites (all optional — the skill provides guidance even without local tools):**
- `rpmbuild` (from `rpm-build` package)
- `mock` (chroot-based isolated builds)
- `rpmlint` (package linting)

## Installation

```bash
claude plugin marketplace add redhat-community-ai-tools/claude-plugins
claude plugin install rpm-packaging@ecosystem-claude-plugins
```
