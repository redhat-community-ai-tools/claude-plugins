---
name: rpm-packaging
description: Use when writing RPM spec files, building RPMs with rpmbuild/mock/koji, debugging build failures, packaging software for Fedora/RHEL/CentOS, or working with rpm macros, scriptlets, dependencies (BuildRequires/Requires), subpackages, SRPMs, rpmlint, signing, or yum/dnf repositories. Also use when packaging Python, Go, or Rust projects as RPMs.
---

# RPM Packaging

## Overview

RPM packages are built from spec files containing a Preamble (metadata: Name, Version, Release, License) and a Body (build phases: %prep, %build, %install, %check). The Name-Version-Release (NVR) triple forms the package filename.

## Quick Reference

### Build Commands

```bash
rpmdev-setuptree                              # Create ~/rpmbuild tree
rpmbuild -ba package.spec                     # Build binary + source RPM
rpmbuild -bb package.spec                     # Binary RPM only
rpmbuild -bs package.spec                     # Source RPM only
rpmbuild --rebuild package.src.rpm            # Rebuild from SRPM
mock -r fedora-40-x86_64 --rebuild pkg.src.rpm  # Isolated chroot build
rpmlint package.spec *.rpm                    # Lint check (run on SRPM for best coverage)
rpm --addsign package.rpm                     # Sign a package
```

### Key Macros

| Macro | Value | Macro | Value |
|-------|-------|-------|-------|
| `%{_bindir}` | /usr/bin | `%{_libdir}` | /usr/lib64 |
| `%{_sysconfdir}` | /etc | `%{_datadir}` | /usr/share |
| `%{_unitdir}` | systemd unit dir | `%{_mandir}` | /usr/share/man |
| `%{name}` | Package name | `%{version}` | Package version |

### Dependencies

- **BuildRequires**: compile-time, always list explicitly (no auto-detect)
- **Requires**: runtime, often auto-detected for native code via shared lib scanning
- **%generate_buildrequires**: programmatic deps (RHEL 9+ / RPM 4.15+)

### Scriptlet $1 Values

| Scriptlet | $1=1 | $1=0 | Upgrade |
|-----------|------|------|---------|
| %pre/%post | install | n/a | $1=2 |
| %preun/%postun | upgrade remains | removal | n/a |

Use `if [ $1 -gt 1 ]` not `-eq 2` (parallel-installable packages).

### Critical Rules

- `%pretrans` requires Lua (`-p <lua>`), not shell
- All scriptlets require zero exit status — use `|| :` for fallible commands
- `%define` = no expansion at definition time; `%global` = expand once immediately
- Every spec line is macro-expanded INCLUDING `#` comments — use `%dnl` for true comments
- Prefer env vars ($RPM_BUILD_ROOT) over macros (%{buildroot}) inside scripts
- Use `%config(noreplace)` for config files users may edit
- Build in Mock to catch missing BuildRequires

## Full Reference

See @rpm-packaging-guide.md for the complete guide covering:
- Spec file anatomy and all preamble directives
- Build lifecycle phases and rpmbuild directory tree
- Macros: built-in paths, %define vs %global, conditionals, bcond
- %files section: directives, wildcards, config handling
- Scriptlets: ordering during upgrades (14/32-step), exit status rules, systemd macros
- Subpackages: defining, naming conventions, file splitting
- SRPMs: building, rebuilding, extracting
- Build environments: Mock, Koji, Copr (relationship and usage)
- rpmlint: validation and suppressing warnings
- Signing RPMs and creating yum/dnf repositories
- Fedora and RHEL packaging standards and review checklist
- Language-specific templates: Python (pyproject), Go, Rust
- Common pitfalls table and troubleshooting guide
- RPM querying and removal commands
- Testing RPMs in containers: images (Fedora, CentOS Stream, RHEL UBI), install tests, scriptlet lifecycle, multi-distro testing, rpmlint in containers, debugging
