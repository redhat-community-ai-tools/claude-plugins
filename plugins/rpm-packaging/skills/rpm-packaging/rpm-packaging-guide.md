# RPM Packaging: Comprehensive Reference Guide

This document is a verified, comprehensive reference for building RPM packages. Every claim has been adversarially verified against primary sources (RPM upstream docs, Fedora Packaging Guidelines, RHEL documentation).

## Table of Contents

1. [Spec File Anatomy](#1-spec-file-anatomy)
2. [Build Lifecycle](#2-build-lifecycle)
3. [Dependencies: BuildRequires vs Requires](#3-dependencies-buildrequires-vs-requires)
4. [Macros and Variables](#4-macros-and-variables)
5. [The %files Section](#5-the-files-section)
6. [Scriptlets](#6-scriptlets)
7. [Subpackages](#7-subpackages)
8. [Source RPMs (SRPMs)](#8-source-rpms-srpms)
9. [Build Environments: Mock, Koji, Copr](#9-build-environments-mock-koji-copr)
10. [rpmlint: Validation](#10-rpmlint-validation)
11. [Signing RPMs](#11-signing-rpms)
12. [Creating yum/dnf Repositories](#12-creating-yumdnf-repositories)
13. [Fedora and RHEL Packaging Standards](#13-fedora-and-rhel-packaging-standards)
14. [Language-Specific Patterns](#14-language-specific-patterns)
15. [Common Pitfalls and Troubleshooting](#15-common-pitfalls-and-troubleshooting)
16. [Spec File Templates](#16-spec-file-templates)
17. [RPM Removal and Querying](#17-rpm-removal-and-querying)
18. [Testing RPMs in Containers](#18-testing-rpms-in-containers)

---

## 1. Spec File Anatomy

An RPM spec file has two main parts: a **Preamble** (metadata) and a **Body** (build instructions).

### Preamble (Metadata)

The preamble defines the package identity and metadata:

```spec
Name:           mypackage
Version:        1.2.3
Release:        1%{?dist}
Summary:        Short one-line description of the package
License:        Apache-2.0
URL:            https://example.com/mypackage
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make
Requires:       glibc
```

**Key directives:**

| Directive | Purpose | Notes |
|-----------|---------|-------|
| `Name` | Package name | Lowercase, no spaces; forms NVR |
| `Version` | Upstream version | Numeric, no dashes |
| `Release` | Package revision | Always append `%{?dist}`; reset to `1` on new Version |
| `Summary` | One-line description | No period at end; max ~70 chars |
| `License` | SPDX license identifier | Use SPDX expressions (e.g., `Apache-2.0`, `MIT`, `GPL-2.0-or-later`) |
| `URL` | Upstream project URL | |
| `Source0` | Source tarball | Can use macros; multiple sources with Source1, Source2... |
| `Patch0` | Patches | Applied in %prep; multiple with Patch1, Patch2... |
| `BuildArch` | Architecture | Set to `noarch` for arch-independent packages |
| `ExclusiveArch` | Restrict architectures | e.g., `x86_64 aarch64` |
| `Epoch` | Override version ordering | Avoid unless absolutely necessary; once set, can never be removed |

The **Name-Version-Release (NVR)** triple forms the RPM filename: `name-version-release.arch.rpm`.

### Prohibited Directives (Fedora/RHEL)

Do NOT use these in spec files:
- `Copyright` (obsolete, use `License`)
- `Packager` (set by build system)
- `Vendor` (set by build system)
- `PreReq` (obsolete, use `Requires(pre)`)

### Body (Build Sections)

The body contains the build instructions organized into sections:

```spec
%description
Multi-line description of the package.
Can span multiple lines.

%prep
%autosetup -p1

%build
%configure
%make_build

%install
%make_install

%check
%make_build check

%files
%license LICENSE
%doc README.md
%{_bindir}/mypackage
%{_mandir}/man1/mypackage.1*

%changelog
* Thu Jul 03 2026 Your Name <email@example.com> - 1.2.3-1
- Initial package
```

---

## 2. Build Lifecycle

### Build Phases

RPM builds proceed through these phases in order:

| Phase | Section | Purpose |
|-------|---------|---------|
| 1 | `%prep` | Unpack sources, apply patches |
| 2 | `%conf` | Configure (RPM 4.18+, optional) |
| 3 | `%build` | Compile the software |
| 4 | `%install` | Copy artifacts to buildroot |
| 5 | `%check` | Run test suite |
| 6 | `%clean` | Clean up (obsolete in modern RPM) |

### %prep

Unpacks sources and applies patches:

```spec
%prep
%autosetup -p1
```

- `%autosetup` unpacks Source0 and applies all Patch directives automatically
- `-p1` strips one directory level from patches (standard for `git diff` output)
- `-n %{name}-%{version}` overrides the expected directory name if non-standard

Manual alternative:
```spec
%prep
%setup -q
%patch0 -p1
%patch1 -p1
```

### %build

Compiles the software:

```spec
%build
%configure
%make_build
```

Common macros:
- `%configure` — runs `./configure` with standard prefix/libdir/etc.
- `%make_build` — runs `make` with parallel jobs (`-j` flag)
- `%cmake` — runs cmake with standard options
- `%meson` — runs meson setup with standard options

### %install

**Copies build artifacts to the buildroot directory.** The buildroot mimics the target filesystem hierarchy. This section executes only during package creation, NOT during end-user installation.

```spec
%install
%make_install
```

- `%make_install` — runs `make install DESTDIR=%{buildroot}`
- All paths must be relative to `%{buildroot}`
- The buildroot is a DESTDIR prefix, not a true chroot

### %check

Runs the test suite:

```spec
%check
%make_build check
```

- Runs after %install, before packaging
- Should run the upstream test suite
- Failures here cause the build to fail

### rpmbuild Command

```bash
# Set up the build tree
rpmdev-setuptree

# Build everything (binary + source RPMs)
rpmbuild -ba mypackage.spec

# Build binary RPMs only
rpmbuild -bb mypackage.spec

# Build source RPM only
rpmbuild -bs mypackage.spec

# Build from source RPM
rpmbuild --rebuild mypackage-1.0-1.fc40.src.rpm

# Override build target architecture
rpmbuild --target x86_64 -bb mypackage.spec

# Define a macro on the command line
rpmbuild -bb --define "debug_package %{nil}" mypackage.spec
```

### rpmbuild Directory Tree

```
~/rpmbuild/
├── BUILD/       # Unpacked sources (working directory during build)
├── BUILDROOT/   # Fake install root (DESTDIR)
├── RPMS/        # Output binary RPMs
│   ├── x86_64/
│   └── noarch/
├── SOURCES/     # Source tarballs and patches
├── SPECS/       # Spec files
└── SRPMS/       # Output source RPMs
```

Create this tree with: `rpmdev-setuptree` (from `rpmdevtools` package).

---

## 3. Dependencies: BuildRequires vs Requires

### BuildRequires (Compile-Time)

- Specifies packages needed **at build time**
- **Must always be explicitly listed** — RPM cannot auto-detect build dependencies
- Installed into the build chroot before compilation
- One per line or comma-separated on a single line

```spec
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  openssl-devel
BuildRequires:  python3-devel
```

### Requires (Runtime)

- Specifies packages needed **at run time**
- **Often auto-detected** by rpmbuild for natively compiled programs (via shared library scanning with `find-requires`)
- For interpreted languages (Python, Perl, Ruby), auto-detection also works via language-specific dependency generators
- Manual Requires still needed for:
  - Programs called via `system()` or exec
  - dlopen'd libraries
  - Data files from other packages

```spec
Requires:       python3
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
```

### Version Constraints

```spec
BuildRequires:  libfoo-devel >= 2.0
Requires:       libbar < 3.0
Requires:       libbar >= 1.5
Conflicts:      otherpkg
Obsoletes:      oldname < 2.0
Provides:       oldname = %{version}-%{release}
```

### Weak Dependencies (RPM 4.12+)

```spec
Recommends:     optional-enhancement
Suggests:       nice-to-have-pkg
Supplements:    other-pkg
Enhances:       other-pkg
```

### %generate_buildrequires (RPM 4.15+ / RHEL 9+)

Programmatically generates build dependencies. Useful for language ecosystems with complex dependency trees:

```spec
%generate_buildrequires
%pyproject_buildrequires -r
```

This runs after %prep and can trigger rebuild loops until all dependencies are satisfied. Supported in RHEL 9+ (RPM 4.16.x) and Fedora 31+.

---

## 4. Macros and Variables

### Built-in Path Macros

| Macro | Value | Purpose |
|-------|-------|---------|
| `%{_prefix}` | `/usr` | Install prefix |
| `%{_bindir}` | `/usr/bin` | Executables |
| `%{_sbindir}` | `/usr/sbin` | System binaries |
| `%{_libdir}` | `/usr/lib64` (or `/usr/lib`) | Libraries |
| `%{_libexecdir}` | `/usr/libexec` | Helper executables |
| `%{_includedir}` | `/usr/include` | Header files |
| `%{_datadir}` | `/usr/share` | Architecture-independent data |
| `%{_mandir}` | `/usr/share/man` | Man pages |
| `%{_infodir}` | `/usr/share/info` | Info pages |
| `%{_sysconfdir}` | `/etc` | Configuration files |
| `%{_localstatedir}` | `/var` | Variable data |
| `%{_unitdir}` | `/usr/lib/systemd/system` | systemd unit files |
| `%{_tmpfilesdir}` | `/usr/lib/tmpfiles.d` | tmpfiles.d configs |
| `%{_sysusersdir}` | `/usr/lib/sysusers.d` | sysusers.d configs |
| `%{buildroot}` | Build root directory | DESTDIR for %install |

### Build Macros

| Macro | Purpose |
|-------|---------|
| `%{name}` | Package name |
| `%{version}` | Package version |
| `%{release}` | Package release |
| `%{?dist}` | Distribution tag (e.g., `.fc40`, `.el9`) |
| `%{_isa}` | ISA suffix (e.g., `(x86-64)`) |
| `%{optflags}` | Compiler optimization flags |
| `%{__make}` | Path to make |
| `%{__python3}` | Path to python3 |

### Defining Custom Macros

**%define vs %global — critical distinction:**

- `%define` — **declarative**: no macro expansion at definition time; scoped to current context (local inside parametric macros, otherwise global)
- `%global` — **expands the body once** at definition time; always creates global scope
- `%define -eg` is identical to `%global`

```spec
# %global: body is expanded NOW (at definition time)
%global commit abc123def
%global shortcommit %(c=%{commit}; echo ${c:0:7})

# %define: body is expanded LATER (at each use site)
%define debug_package %{nil}
```

### Macro Scoping and Stacking

- Macros are **globally scoped** (except inside parametric macros)
- Macros use a **stacking mechanism**: redefining a macro pushes the new definition on top, shadowing the previous one
- `%undefine` pops only the topmost definition

### Conditional Macros

```spec
# Conditional expansion (expands to nothing if macro undefined)
%{?with_tests: %check commands here}

# Conditional with fallback
%{?custom_prefix}%{!?custom_prefix:/usr}

# Boolean conditions
%if 0%{?fedora} >= 40
BuildRequires:  new-dep
%endif

%if 0%{?rhel}
BuildRequires:  rhel-specific-dep
%endif

# bcond (build conditionals)
%bcond_with    bootstrap     # --with bootstrap to enable
%bcond_without tests         # --without tests to disable

%if %{with tests}
%check
make test
%endif
```

### Macro Expansion in Comments

**Every spec file line undergoes macro expansion before processing, including comment lines starting with `#`.** This means:

```spec
# This comment expands %{name} to the actual package name
# Undefined macros like %{doesnotexist} will cause warnings

# Use %dnl to truly comment out content without expansion (RPM 4.15+):
%dnl This line is completely discarded, no macro expansion happens
```

**Do NOT use `%dnl` inside embedded Lua code blocks.**

### Environment Variables vs Macros in Scripts

Inside build scriptlets (%prep, %build, %install, %check), prefer environment variables over macro counterparts because **macros are evaluated at spec parse time** while **environment variables are evaluated at script execution time**:

| Use This (env var) | Not This (macro) |
|---------------------|-------------------|
| `$RPM_BUILD_ROOT` | `%{buildroot}` |
| `$RPM_OPT_FLAGS` | `%{optflags}` |
| `$RPM_LD_FLAGS` | `%{build_ldflags}` |
| `$RPM_BUILD_NCPUS` | `%{_smp_build_ncpus}` |

Note: Fedora historically favored `%{buildroot}` for stylistic consistency. Either works in practice for simple cases, but env vars are more correct for dynamic values.

### Querying Macros

```bash
# Show a macro's expanded value
rpm --eval '%{_bindir}'
rpm --eval '%{?dist}'

# Show all defined macros
rpm --showrc

# Dump macro definitions
rpm -E '%dump' 2>&1 | grep _bindir
```

---

## 5. The %files Section

### Basic Usage

The `%files` section lists every file the package installs. Files not listed here will cause a build failure ("unpackaged files found").

```spec
%files
%license LICENSE COPYING
%doc README.md CHANGELOG.md
%{_bindir}/mypackage
%{_libdir}/libmypackage.so.*
%{_mandir}/man1/mypackage.1*
%{_datadir}/mypackage/
%config(noreplace) %{_sysconfdir}/mypackage.conf
```

### File Directives

| Directive | Purpose |
|-----------|---------|
| `%license` | License files (installed to /usr/share/licenses/) |
| `%doc` | Documentation files (installed to /usr/share/doc/) |
| `%config` | Configuration file (renamed to .rpmsave on removal if modified) |
| `%config(noreplace)` | Config file preserved on update; new version saved as .rpmnew |
| `%dir` | Own the directory itself (not its contents) |
| `%attr(mode, user, group)` | Set file permissions |
| `%defattr(mode, user, group, dirmode)` | Default permissions |
| `%ghost` | File owned but not installed by the package (e.g., log files) |
| `%verify(...)` | Control verification checks |
| `%exclude` | Exclude a file from packaging |

### %config(noreplace) Behavior

When a package is updated:
- If the config file was **not locally modified**: replaced silently with the new version
- If **locally modified AND new version differs**: local file kept as-is, new version saved as `.rpmnew`
- If **locally modified AND new version is identical**: no action needed

This dual-condition trigger (local modification AND changed upstream content) is important to understand.

### Wildcards and Globs

```spec
%{_libdir}/libfoo.so.*          # Match versioned shared libraries
%{_mandir}/man1/foo.1*          # Match compressed and uncompressed man pages
%{_datadir}/%{name}/            # Own directory and all contents recursively
```

### Common Patterns

```spec
# Development subpackage files
%files devel
%{_includedir}/%{name}/
%{_libdir}/libfoo.so            # Unversioned symlink (devel only)
%{_libdir}/pkgconfig/foo.pc

# Library files
%files libs
%{_libdir}/libfoo.so.1*

# Python module files
%files -n python3-%{name}
%{python3_sitelib}/%{name}/
%{python3_sitelib}/%{name}-%{version}.dist-info/
```

---

## 6. Scriptlets

Scriptlets are shell scripts that run during package installation, upgrade, or removal.

### Scriptlet Types

| Scriptlet | When it runs | $1 value |
|-----------|-------------|----------|
| `%pretrans` | Before transaction starts | Always 0 |
| `%pre` | Before files are installed | 1=install, 2=upgrade |
| `%post` | After files are installed | 1=install, 2=upgrade |
| `%preun` | Before files are removed | 0=remove, 1=upgrade |
| `%postun` | After files are removed | 0=remove, 1=upgrade |
| `%posttrans` | After transaction completes | Always 0 |

### The $1 Argument

The `$1` argument represents the **number of installed instances of the package after the operation completes**:

- **$1=1 in %pre/%post**: Fresh install (one instance after completion)
- **$1=2 in %pre/%post**: Upgrade (two instances momentarily, but reporting post-completion count)
- **$1=0 in %preun/%postun**: Final removal
- **$1=1 in %preun/%postun**: Upgrade (one instance remains after old is removed)

For parallel-installable packages (kernels, multilib), $1 can exceed 2. Use `if [ $1 -gt 1 ]` rather than `if [ $1 -eq 2 ]`.

### Upgrade Scriptlet Ordering (14-Step Simplified View)

During an upgrade (install-new-then-erase-old), scriptlets execute in this order:

```
 1. %pretrans of new package
 2. (triggers: %triggerprein)
 3. %pre of new package
 4. (new files installed)
 5. %post of new package
 6. (triggers: %triggerin)
 7. (triggers: %triggerun of old)
 8. %preun of old package
 9. (old files removed)
10. %postun of old package
11. (triggers: %triggerpostun of old)
12. %posttrans of new package
```

The key invariant: **new files are installed before old files are removed.** Both package versions coexist briefly.

Modern RPM (4.13+) documents a full **32-step sequence** including file triggers, %sysusers, and other additions. Consult `rpm-scriptlets(7)` for the authoritative modern sequence.

### Exit Status Rules

- **All scriptlets MUST exit with zero status**
- Non-zero exit from `%pre` **blocks** package installation
- Non-zero exit from `%preun` **blocks** package uninstallation
- Non-zero exit from `%post` / `%postun` does **NOT** block the operation
- Use `|| :` to force zero exit when a command might fail:

```spec
%post
/sbin/ldconfig || :

%postun
/sbin/ldconfig || :
```

### %pretrans: Lua Required

`%pretrans` is a **dangerous slot** — during fresh system installations, even `/bin/sh` may not yet exist. The only reliable interpreter is the embedded RPM Lua interpreter:

```spec
%pretrans -p <lua>
-- Lua code here, NOT shell
```

Fedora packaging guidelines **mandate** that `%pretrans` MUST be written in Lua.

### systemd Service Scriptlets

For packages shipping systemd services, use the dedicated macros:

```spec
BuildRequires:  systemd-rpm-macros
%{?systemd_requires}

%post
%systemd_post myservice.service

%preun
%systemd_preun myservice.service

%postun
%systemd_postun_with_restart myservice.service
```

- `%systemd_post` — runs `systemctl preset <service>` on initial install (respects presets)
- `%systemd_preun` — stops and disables service before removal
- `%systemd_postun_with_restart` — restarts service after upgrade (if running)
- Use `systemd-rpm-macros` (lighter) instead of full `systemd` as BuildRequires

### Triggers

Triggers run when another package is installed/removed. **Minimize their use** — they may execute at unexpected times and are difficult to debug. Red Hat explicitly recommends minimizing trigger usage.

```spec
%triggerin -- otherpkg
# Runs when otherpkg is installed and this package is already present

%triggerun -- otherpkg
# Runs when otherpkg is about to be removed
```

---

## 7. Subpackages

Subpackages allow one spec to produce multiple RPMs.

### Defining Subpackages

```spec
Name:    mypackage
# ... preamble ...

# Subpackage inherits Name prefix: mypackage-devel
%package devel
Summary:  Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
Header files and libraries for developing with %{name}.

# Named subpackage (no Name prefix): python3-mypackage
%package -n python3-%{name}
Summary:  Python bindings for %{name}
Requires: python3

%description -n python3-%{name}
Python 3 bindings for %{name}.
```

### Build Sections Are NOT Repeated

The `%prep`, `%build`, `%install`, and `%check` sections appear **only once** in the spec. They cannot be repeated per subpackage. All subpackage build/install work must happen in these single sections.

Only `%description` and `%files` are repeated for each subpackage.

### Common Subpackage Patterns

- `%{name}-libs` — shared libraries
- `%{name}-devel` — headers, unversioned .so symlinks, pkg-config files
- `%{name}-doc` — documentation
- `python3-%{name}` — Python bindings
- `%{name}-static` — static libraries (discouraged in Fedora)

---

## 8. Source RPMs (SRPMs)

An SRPM contains everything needed to reproduce a binary build:
- The spec file
- Source tarballs
- Patches

```bash
# Build SRPM only
rpmbuild -bs mypackage.spec

# Rebuild binary from SRPM
rpmbuild --rebuild mypackage-1.0-1.fc40.src.rpm

# Install SRPM (extracts to ~/rpmbuild/{SOURCES,SPECS}/)
rpm -ivh mypackage-1.0-1.fc40.src.rpm

# Extract SRPM without installing
rpm2cpio mypackage-1.0-1.fc40.src.rpm | cpio -idmv
```

SRPMs are the standard unit of exchange for package reviews and build systems (Mock, Koji, Copr).

---

## 9. Build Environments: Mock, Koji, Copr

### Mock

Mock is a **chroot-based rpmbuild wrapper** that creates isolated build environments with minimal packages installed:

```bash
# Install mock
sudo dnf install mock
sudo usermod -aG mock $USER

# Build from SRPM
mock -r fedora-40-x86_64 --rebuild mypackage-1.0-1.fc40.src.rpm

# Build from spec + sources
mock -r fedora-40-x86_64 --buildsrpm --spec mypackage.spec --sources ~/rpmbuild/SOURCES/
mock -r fedora-40-x86_64 --rebuild /var/lib/mock/fedora-40-x86_64/result/mypackage-1.0-1.fc40.src.rpm

# Interactive shell in the chroot
mock -r fedora-40-x86_64 --shell

# Clean the chroot
mock -r fedora-40-x86_64 --clean
```

**Why use Mock:**
- Finds missing `BuildRequires` (build fails if dependency is absent)
- Ensures no host contamination
- Reproducible builds
- Cross-distribution builds (e.g., build RHEL packages on Fedora)

Modern Mock defaults to `systemd-nspawn` rather than bare `chroot(2)` but retains the chroot terminology.

### Koji

Koji is Fedora's build system, orchestrating Mock across architectures:

- **Build targets** specify where packages are built and how they are tagged
- **Tags** are collections of packages, supporting inheritance and per-tag ownership
- kojid uses Mock to build RPMs, creating a fresh buildroot for every build

```bash
# Submit a build
koji build f40-candidate mypackage-1.0-1.fc40.src.rpm

# Scratch build (not tagged, just testing)
koji build --scratch f40-candidate mypackage-1.0-1.fc40.src.rpm

# Watch a build
koji watch-task <task-id>

# List packages in a tag
koji list-tagged f40-updates
```

### Copr

Copr is a community build service — simpler than Koji, ideal for personal repos:

```bash
# Create a project
copr-cli create myproject --chroot fedora-40-x86_64

# Submit a build from SRPM
copr-cli build myproject mypackage-1.0-1.fc40.src.rpm

# Build from spec URL
copr-cli buildscm myproject --clone-url https://github.com/user/repo --subdir rpm/
```

### Relationship

Mock is the underlying build tool used by both Koji and Copr for all Fedora package builds:
- **Mock**: Local chroot builds
- **Koji**: Fedora/RHEL official builds (orchestrates Mock)
- **Copr**: Community builds (also orchestrates Mock)

---

## 10. rpmlint: Validation

rpmlint checks for common errors in RPM packages:

```bash
# Check a spec file
rpmlint mypackage.spec

# Check a binary RPM
rpmlint mypackage-1.0-1.fc40.x86_64.rpm

# Check a source RPM (broadest coverage)
rpmlint mypackage-1.0-1.fc40.src.rpm

# Check all outputs
rpmlint mypackage.spec mypackage-1.0-1.fc40.*.rpm
```

**Run rpmlint against SRPMs for best check coverage** — the SRPM check set is a superset of what plain spec file checking provides.

Fedora requires rpmlint output in package reviews.

### Suppressing Warnings

Create a `.rpmlintrc` file:

```python
# Allow specific warnings
addFilter("spelling-error")
addFilter("no-documentation")

# Set custom config
setBadness('man-page-not-gzipped', 0)
```

---

## 11. Signing RPMs

### GPG Key Setup

```bash
# Generate a GPG key (if you don't have one)
gpg --gen-key

# Export the public key
gpg --export --armor "Your Name" > RPM-GPG-KEY-yourname

# Import the key into RPM
sudo rpm --import RPM-GPG-KEY-yourname
```

### Signing Packages

```bash
# Configure in ~/.rpmmacros
echo '%_gpg_name Your Name <your@email.com>' >> ~/.rpmmacros

# Sign an RPM
rpm --addsign mypackage-1.0-1.fc40.x86_64.rpm

# Verify signature
rpm --checksig mypackage-1.0-1.fc40.x86_64.rpm
rpm -K mypackage-1.0-1.fc40.x86_64.rpm
```

The GPG signature is calculated from the RPM header and compressed CPIO archive, stored in the signature section of the RPM binary format.

---

## 12. Creating yum/dnf Repositories

### Using createrepo_c

```bash
# Install createrepo
sudo dnf install createrepo_c

# Create repository metadata
createrepo_c /path/to/your/rpms/

# Update after adding new packages
createrepo_c --update /path/to/your/rpms/
```

### Repository Configuration

Create a `.repo` file in `/etc/yum.repos.d/`:

```ini
[myrepo]
name=My Custom Repository
baseurl=https://example.com/repo/$basearch/
enabled=1
gpgcheck=1
gpgkey=https://example.com/RPM-GPG-KEY-yourname
```

### Signing Repository Metadata

```bash
# Sign the repodata
gpg --detach-sign --armor /path/to/repo/repodata/repomd.xml
```

---

## 13. Fedora and RHEL Packaging Standards

### Fedora Guidelines (Key Points)

- **BuildRequires**: MUST be explicitly listed (cannot be auto-detected)
- **Requires**: Often auto-detected; only list what RPM can't find
- **rpmlint**: MUST be run on SRPM and all binary RPMs; output posted in review
- **License**: MUST use SPDX expression; License field is mandatory
- **%check**: Strongly encouraged; run upstream test suite
- **%autosetup**: Preferred over manual %setup + %patch
- **Naming**: Must follow Fedora Naming Guidelines
- **Static linking**: Discouraged; requires justification
- **Bundling**: Discouraged; system libraries preferred

### RHEL Guidelines (Key Differences)

- More conservative than Fedora (longer support lifecycle)
- `%generate_buildrequires` available in RHEL 9+ (RPM 4.16.x)
- Some Fedora-only macros may not be available
- CRB (CodeReady Linux Builder) repository required for some devel packages
- RHEL 10 introduces additional spec file features from newer RPM versions

### Common Review Checklist

1. Spec file follows naming conventions
2. License is correctly identified (SPDX)
3. Source URL is valid and matches upstream
4. BuildRequires are complete (Mock build succeeds)
5. rpmlint output is clean (or warnings explained)
6. %files section includes %license and %doc
7. Scriptlets use || : pattern
8. No bundled libraries
9. Package builds on all target architectures

---

## 14. Language-Specific Patterns

### Python (pyproject-rpm-macros)

Modern Python packaging on RHEL 9/10 and Fedora uses `pyproject-rpm-macros`:

```spec
Name:           python-mypackage
Version:        1.0.0
Release:        1%{?dist}
Summary:        My Python package
License:        MIT
URL:            https://pypi.org/project/mypackage
Source:         %{pypi_source mypackage}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%generate_buildrequires
%pyproject_buildrequires -r

%description
%{summary}.

%package -n python3-mypackage
Summary:        %{summary}

%description -n python3-mypackage
%{summary}.

%prep
%autosetup -n mypackage-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files mypackage

%check
%pytest

%files -n python3-mypackage -f %{pyproject_files}
%doc README.md
%license LICENSE
```

The `%pyproject_*` macros replace the old `%py3_build` / `%py3_install` and use PEP 517 to work with any compliant build backend, not just setuptools.

### Go

```spec
%global goipath     github.com/user/mypackage
%global forgeurl    https://github.com/user/mypackage
%global tag         v1.0.0

%gometa -f

%global debug_package %{nil}

Name:           mypackage
Version:        %{tag}
Release:        1%{?dist}
Summary:        My Go application
License:        Apache-2.0
URL:            %{gourl}
Source:          %{gosource}

BuildRequires:  go-rpm-macros

%description
%{summary}.

%prep
%goprep -k

%build
%gobuild -o %{gobuilddir}/bin/mypackage %{goipath}

%install
install -Dpm 0755 %{gobuilddir}/bin/mypackage %{buildroot}%{_bindir}/mypackage

%check
%gocheck

%files
%license LICENSE
%doc README.md
%{_bindir}/mypackage
```

Note: `%global debug_package %{nil}` is needed because Go binaries embed debug information differently than C/C++.

### Rust

Fedora packages that build Rust code MUST use cargo-rpm-macros:

```spec
Name:           mypackage
Version:        1.0.0
Release:        1%{?dist}
Summary:        My Rust application
License:        MIT
URL:            https://crates.io/crates/mypackage
Source:         %{crates_source}

BuildRequires:  cargo-rpm-macros >= 24
BuildRequires:  rust-packaging

%description
%{summary}.

%prep
%autosetup -n mypackage-%{version}
%cargo_prep

%build
%cargo_build

%install
%cargo_install

%check
%cargo_test

%files
%license LICENSE
%doc README.md
%{_bindir}/mypackage
```

---

## 15. Common Pitfalls and Troubleshooting

### Spec File Errors

| Problem | Cause | Fix |
|---------|-------|-----|
| "Installed (but unpackaged) file(s) found" | Files in buildroot not listed in %files | Add them to %files or use `%exclude` |
| "File not found" in %files | Typo in path or file not installed | Check %install output; use `find %{buildroot}` to list |
| "%define used but never expanded" | Used %define in conditional block | Use %global instead |
| "Macro expanded in comment" | `#` comments still expand macros | Use `%dnl` for true comments |
| "Bad exit status from %scriptlet" | Scriptlet returned non-zero | Add `\|\| :` to failing commands |
| SRPM builds but binary fails | Missing BuildRequires | Build in Mock to catch missing deps |

### Macro Pitfalls

- **%define vs %global timing**: `%define` delays expansion; `%global` expands immediately. Using `%define` for version-dependent macros can produce empty values if defined before the dependency is resolved.
- **Macros in comments**: Even `# commented-out %{macro}` gets expanded. Use `%dnl` to suppress.
- **%{?macro:value}** vs **%{?macro}**: The first expands to `value` if macro is defined; the second expands to the macro's value.

### Build Environment Issues

- **"No such file or directory" in %build**: Check that %prep correctly unpacks the source and `-n` matches the directory name
- **Mock build fails but rpmbuild succeeds**: Missing BuildRequires — your host has the dependency installed but Mock's clean chroot doesn't
- **rpmlint "no-binary" warning**: Package has no architecture-specific files; consider `BuildArch: noarch`

### Scriptlet Pitfalls

- **Non-zero exit in %preun during upgrade**: Can leave duplicate rpmdb entries and stale files. Always use `|| :`
- **Using shell in %pretrans**: Will fail on fresh installs where /bin/sh doesn't exist. Must use Lua.
- **Testing $1 with -eq 2**: Breaks for parallel-installable packages. Use `-gt 1` instead.

---

## 16. Spec File Templates

### Minimal C Application

```spec
Name:           hello
Version:        1.0.0
Release:        1%{?dist}
Summary:        Hello World application
License:        GPL-3.0-or-later
URL:            https://example.com/hello
Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make

%description
A simple Hello World application.

%prep
%autosetup

%build
%configure
%make_build

%install
%make_install

%check
%make_build check

%files
%license COPYING
%doc README
%{_bindir}/hello
%{_mandir}/man1/hello.1*

%changelog
* Thu Jul 03 2026 Your Name <email@example.com> - 1.0.0-1
- Initial package
```

### systemd Service

```spec
Name:           myservice
Version:        1.0.0
Release:        1%{?dist}
Summary:        My background service
License:        MIT
URL:            https://example.com/myservice
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  systemd-rpm-macros
%{?systemd_requires}

%description
A background service that does useful things.

%prep
%autosetup

%build
%configure
%make_build

%install
%make_install
install -Dpm 0644 %{name}.service %{buildroot}%{_unitdir}/%{name}.service
install -Dpm 0644 %{name}.conf %{buildroot}%{_sysconfdir}/%{name}.conf

%check
%make_build check

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
    useradd -r -g %{name} -d /var/lib/%{name} -s /sbin/nologin \
    -c "myservice daemon" %{name}
exit 0

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%config(noreplace) %{_sysconfdir}/%{name}.conf
%dir %attr(0750, %{name}, %{name}) /var/lib/%{name}

%changelog
* Thu Jul 03 2026 Your Name <email@example.com> - 1.0.0-1
- Initial package
```

### noarch Python Package

```spec
Name:           python-example
Version:        2.0.0
Release:        1%{?dist}
Summary:        Example Python library
License:        BSD-3-Clause
URL:            https://pypi.org/project/example
Source:         %{pypi_source example}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
An example Python library that demonstrates packaging.}

%description %{_description}

%package -n python3-example
Summary:        %{summary}

%description -n python3-example %{_description}

%prep
%autosetup -n example-%{version}

%generate_buildrequires
%pyproject_buildrequires -t

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files example

%check
%pytest

%files -n python3-example -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
* Thu Jul 03 2026 Your Name <email@example.com> - 2.0.0-1
- Initial package
```

---

## 17. RPM Removal and Querying

### Removing Packages

```bash
# Remove a package
sudo rpm -e packagename
sudo dnf remove packagename

# Remove without dependency checking (dangerous)
sudo rpm -e --nodeps packagename

# Test removal (dry run)
sudo rpm -e --test packagename
```

### Querying Installed Packages

```bash
# List all installed packages
rpm -qa

# Query a specific package
rpm -qi packagename

# List files in a package
rpm -ql packagename

# Find which package owns a file
rpm -qf /usr/bin/something

# List config files
rpm -qc packagename

# List documentation files
rpm -qd packagename

# Show changelog
rpm -q --changelog packagename

# Show scriptlets
rpm -q --scripts packagename

# Show requires/provides
rpm -q --requires packagename
rpm -q --provides packagename
```

### Querying Uninstalled RPMs

```bash
# Query an RPM file (not installed)
rpm -qpi package.rpm
rpm -qpl package.rpm
rpm -qp --requires package.rpm
rpm -qp --scripts package.rpm
```

### Verifying Installed Packages

```bash
# Verify all installed packages
rpm -Va

# Verify a specific package
rpm -V packagename
```

Verification output codes: `S` (size), `M` (mode), `5` (MD5), `D` (device), `L` (link), `U` (user), `G` (group), `T` (mtime), `P` (capabilities).

---

## 18. Testing RPMs in Containers

After building an RPM, test it by installing into a clean container that matches the target OS. This catches missing dependencies, broken scriptlets, and file permission issues that your build host's pre-existing packages mask.

### Container Images

| Target OS | Image | Registry |
|-----------|-------|----------|
| Fedora (latest) | `fedora:latest` | docker.io/library/fedora |
| Fedora (specific) | `fedora:42` | docker.io/library/fedora |
| CentOS Stream 10 | `quay.io/centos/centos:stream10` | quay.io |
| CentOS Stream 9 | `quay.io/centos/centos:stream9` | quay.io |
| RHEL 10 UBI | `registry.access.redhat.com/ubi10/ubi` | registry.access.redhat.com |
| RHEL 9 UBI | `registry.access.redhat.com/ubi9/ubi` | registry.access.redhat.com |
| RHEL 9 UBI Minimal | `registry.access.redhat.com/ubi9/ubi-minimal` | registry.access.redhat.com |

UBI (Universal Base Image) images are freely redistributable RHEL-based images. Use them when you need RHEL compatibility without a subscription. UBI-minimal uses microdnf instead of full dnf.

### Quick Install Test

Mount the RPM into a container and install it:

```bash
podman run --rm \
    -v ./out:/rpms:z \
    fedora:latest \
    bash -c "
        dnf install -y /rpms/mypackage-1.0-1.fc42.noarch.rpm
        echo 'Exit code:' \$?
    "
```

The `:z` SELinux label is needed when running rootless podman on SELinux-enforcing hosts (Fedora, RHEL, CentOS). Without it, the container cannot read the mounted directory.

### What to Verify

Run these checks inside the container after installation:

```bash
podman run --rm -v ./out:/rpms:z fedora:latest bash -c "
    # 1. Install succeeds (dependencies resolve)
    dnf install -y /rpms/mypackage-*.rpm

    # 2. Package is registered
    rpm -q mypackage

    # 3. Key files exist
    ls /usr/bin/mypackage      # or /opt/mypackage, etc.

    # 4. Dependencies were pulled in
    rpm -q --requires mypackage

    # 5. Config files were created (if %post creates them)
    ls /etc/mypackage/

    # 6. No dev/test artifacts leaked in
    rpm -ql mypackage | grep -E 'test|\.github|__pycache__' && echo 'LEAK!' || echo 'Clean'

    # 7. Scriptlet output (check for errors)
    rpm -q --scripts mypackage

    # 8. Removal works cleanly
    dnf remove -y mypackage
    echo 'Removal exit code:' \$?
"
```

### Testing Scriptlets

Scriptlets (%post, %preun, %postun) deserve special attention. Test the full lifecycle:

```bash
podman run --rm -v ./out:/rpms:z fedora:latest bash -c "
    # Install — triggers %pre and %post
    dnf install -y /rpms/mypackage-*.rpm
    echo '--- post-install state ---'
    # verify %post side effects (config files created, services enabled, etc.)

    # Upgrade — triggers new %pre/%post, then old %preun/%postun
    dnf install -y /rpms/mypackage-*.rpm   # same version is a reinstall
    echo '--- post-upgrade state ---'

    # Remove — triggers %preun and %postun
    dnf remove -y mypackage
    echo '--- post-removal state ---'
    # verify %postun cleanup (directories removed, etc.)
    ls /opt/mypackage 2>/dev/null && echo 'CLEANUP FAILED' || echo 'Clean removal'
"
```

### Testing on Multiple Distros

Test on every target OS to catch differences in available packages, default Python versions, and systemd behavior:

```bash
for image in fedora:latest quay.io/centos/centos:stream10 registry.access.redhat.com/ubi10/ubi; do
    echo "=== Testing on $image ==="
    podman run --rm -v ./out:/rpms:z "$image" bash -c "
        dnf install -y /rpms/mypackage-*.rpm 2>&1 | tail -5
        rpm -q mypackage && echo 'OK' || echo 'FAILED'
    "
done
```

### Testing with rpmlint in a Container

If rpmlint is not installed locally, run it inside a container:

```bash
podman run --rm \
    -v ./out:/rpms:z \
    -v ./hack/rpm:/specs:z \
    fedora:latest \
    bash -c "
        dnf install -y rpmlint 2>/dev/null
        echo '=== Spec lint ==='
        rpmlint /specs/mypackage.spec
        echo '=== RPM lint ==='
        rpmlint /rpms/mypackage-*.rpm
    "
```

### Interactive Debugging

When tests fail, use an interactive container to investigate:

```bash
# Interactive shell with the RPM mounted
podman run --rm -it -v ./out:/rpms:z fedora:latest bash

# Inside the container:
dnf install -y /rpms/mypackage-*.rpm    # watch for errors
rpm -ql mypackage                        # check installed files
rpm -q --scripts mypackage               # view scriptlets
journalctl -xe                           # check systemd logs (if applicable)
```

### Persistent Test Container

For repeated testing during development, keep the container running:

```bash
# Create and start
podman run -d --name rpm-test -v ./out:/rpms:z fedora:latest sleep infinity

# Run tests
podman exec rpm-test dnf install -y /rpms/mypackage-*.rpm
podman exec rpm-test rpm -ql mypackage

# Reset (remove package, reinstall)
podman exec rpm-test dnf remove -y mypackage
podman exec rpm-test dnf install -y /rpms/mypackage-*.rpm

# Clean up
podman stop rpm-test && podman rm rpm-test
```

### Common Container Testing Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| "Permission denied" mounting volume | SELinux on host | Add `:z` to `-v` mount |
| dnf fails to resolve deps | Package needs repo not in base image | `dnf install -y epel-release` first (CentOS/RHEL) |
| UBI-minimal has no dnf | ubi-minimal uses microdnf | Use `microdnf install` or switch to full UBI image |
| %post fails silently | Scriptlet error swallowed by `\|\| :` | Test without `\|\| :` first, add back after fixing |
| Systemd commands fail | Container has no systemd running | Use `--privileged` or test systemd units separately |
| Different RPM behavior | RPM version differs between Fedora/RHEL | Test on the actual target distro |

---

## Sources

All claims in this document were adversarially verified against these primary sources:

- [RPM Packaging Guide](https://rpm-packaging-guide.github.io/) — beginner-oriented guide
- [RPM Spec File Format](https://rpm-software-management.github.io/rpm/manual/spec.html) — upstream reference
- [RPM Macros Manual](https://rpm-software-management.github.io/rpm/man/rpm-macros.7) — macro system docs
- [RPM Scriptlets Manual](https://rpm-software-management.github.io/rpm/man/rpm-scriptlets.7) — scriptlet reference
- [Fedora Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/) — Fedora standards
- [Fedora Scriptlets Guidelines](https://docs.pagure.org/packaging-guidelines/Packaging:Scriptlets.html) — scriptlet best practices
- [RHEL 9 Packaging Guide](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/packaging_and_distributing_software/advanced-topics) — RHEL-specific guidance
- [Mock Documentation](https://rpm-software-management.github.io/mock/) — build isolation
- [Koji Documentation](https://docs.pagure.org/koji/using_the_koji_build_system/) — build system
- [rpmlint GitHub](https://github.com/rpm-software-management/rpmlint) — package linting
