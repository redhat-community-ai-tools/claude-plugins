---
name: skipper-dev-workflow
description: Containerized development using skipper — build, test, lint, and run commands inside Docker/Podman containers with consistent toolchains. Use this skill whenever the user mentions skipper, skipper.yaml, or wants to run make targets, build images, run tests, or execute commands inside a containerized dev environment. Also use when troubleshooting container build failures, skipper configuration, or setting up a reproducible development workflow in a git repository.
---

# Skipper Dev Workflow

## What is Skipper

[Skipper](https://github.com/Stratoscale/skipper) is a CLI tool that lets you build and test your project in an isolated container environment. Instead of installing compilers, linters, and test tools on your host, you define them in a Dockerfile and skipper runs everything inside that container. This guarantees every developer on the team uses the exact same toolchain.

Skipper works with both **Docker** and **Podman** as container runtimes.

## Installation

Install skipper from PyPI:

```bash
pip install strato-skipper
```

Some IDEs (Cursor, VS Code, etc.) bundle their own Python which can interfere with venv creation. If you hit issues, create the venv with the system Python using a clean environment:

```bash
env -i HOME=$HOME PATH=/usr/bin:/usr/sbin:/bin:/sbin /usr/bin/python3 -m venv .venv
source .venv/bin/activate
pip install 'setuptools<81' strato-skipper
```

The `setuptools<81` cap is needed because skipper depends on `pkg_resources`, which was removed in setuptools 82+.

Enable bash completion:

```bash
echo 'source <(skipper completion)' >> ~/.bashrc
```

## Core Commands

### Build Container Images

Skipper infers images from Dockerfiles in the repo root. For `Dockerfile.myservice`:

```bash
skipper build myservice           # Build specific image
skipper build                     # Build all detected images
skipper build myservice --container-context /path/to/context
```

All images are automatically tagged with the current commit ID.

### Run Make Targets

Run makefile targets inside the build container — the most common skipper workflow:

```bash
skipper make <target>
skipper make test
skipper make lint
skipper make build
```

Use a non-standard makefile:

```bash
skipper make -f Makefile.arm32 tests
```

### Run Arbitrary Commands

```bash
skipper run gcc myprog.c -o myprog
skipper run go test ./...
```

### Interactive Shell

```bash
skipper shell
```

### Push and Manage Images

```bash
skipper --registry some-registry push myservice
skipper images                    # List local images
skipper --registry some-registry images -r   # Include remote
skipper rmi myservice <tag>       # Delete local image
```

## Configuration — `skipper.yaml`

Place `skipper.yaml` at the repo root to avoid repeating CLI flags. Once configured, commands simplify to just `skipper make test`.

```yaml
registry: some-registry
build-container-image: development
build-container-tag: latest

# Use git revision as tag — same build container unless Dockerfile changes
# build-container-tag: 'git:revision'

# Build arguments
build-arg:
  - VAR1=value1
  - VAR2=value2

# Additional build contexts
build-context:
  - context1=/path/to/dir
  - alpine=docker-image://alpine:3.15

# Custom makefile
make:
  makefile: Makefile.custom

# Container definitions (if Dockerfiles aren't at repo root)
containers:
  service1: path/to/service1/dockerfile
  service2: path/to/service2/dockerfile

# Environment variables
env:
  MY_VAR: value
  EXTERNAL_PORT: $EXTERNAL_PORT    # Shell variable substitution
  LITERAL: $$NOT_INTERPOLATED      # Double dollar for literal $

# Environment files
env_file:
  - /path/to/env_file1.env
  - /path/to/env_file2.env

# Volume mounts
volumes:
  - /tmp:/tmp:rw
  - ${HOME}/.netrc:/root/.netrc
  - ${HOME}/.gocache:/tmp/.gocache

# Override working directory (default: project directory)
workdir: /path/to/workdir
```

### Shell Interpolation in Config

Skipper evaluates shell commands in the config using `$(command)` notation:

```yaml
env:
  VAR: $(expr ${MY_NUMBER:-5} + 5)
volumes:
  - $(which myprogram):/myprogram
```

## Passing Environment Variables and Ports

### Environment Variables

Pass env vars at runtime with `-e`:

```bash
skipper make -e MY_VAR=value tests
skipper run -e DEBUG=1 ./myapp
```

Or define them in `skipper.yaml` under `env:` or via `env_file:`.

### Port Publishing

On Linux, skipper uses host networking by default (no port mapping needed). On macOS/Windows or with custom networks, publish ports with `-p`:

```bash
skipper make -p 8080:8080 serve
skipper run -p 3000:3000 -p 5432:5432 ./myapp
```

## Linux without sudo

When running skipper on Linux without sudo, skipper creates a dedicated user inside the container with root and docker groups. On Debian-based distros, `PATH` may get reset. To work around this, install `sudo` in the build container, disable `env_reset` in `/etc/sudoers`, and set:

```bash
export SKIPPER_USE_SUDO="true"
```

Or in `skipper.yaml`:

```yaml
env:
  SKIPPER_USE_SUDO: "true"
```

## Skipper Environment Variables

Skipper sets `CONTAINER_RUNTIME_COMMAND` inside the container (either `podman` or `docker`) so scripts can detect the runtime.

## Troubleshooting

### `skipper: command not found`
Skipper isn't installed or the venv isn't activated. Run `pip install strato-skipper` or `source .venv/bin/activate`.

### `pkg_resources` / `ModuleNotFoundError`
You have setuptools 82+ installed. Reinstall with the version cap:
```bash
pip install 'setuptools<81' strato-skipper
```

### Container image build failures
Common causes:
- Network issues pulling base images
- Disk space — try `docker system prune` or `podman system prune`
- Stale cache — rebuild with `skipper build --no-cache <image>`

### Permission errors (podman)
For rootless podman, ensure `XDG_RUNTIME_DIR` is set and the podman socket is running:
```bash
systemctl --user status podman.socket
```

### Skipper hangs or times out
Check that the container runtime is responsive: `docker ps` or `podman ps`. Large builds or test suites can take several minutes — this is normal.

### Python3 locale issues
If you see encoding errors, set your locale:
```bash
export LC_ALL="en_US.UTF-8"
export LANG="en_US.UTF-8"
```
