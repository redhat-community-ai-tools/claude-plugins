# Skipper Plugin

Containerized development workflow using [skipper](https://github.com/Stratoscale/skipper) — build, test, and run commands inside Docker/Podman containers with reproducible toolchains.

## Skills

### skipper-dev-workflow
Build, test, lint, and run commands inside containerized environments. Covers skipper installation, configuration (`skipper.yaml`), all core commands, environment variables, volumes, port publishing, and troubleshooting.

**Prerequisites:**
- `skipper` installed via pip (`pip install strato-skipper`)
- Docker or Podman installed
- Python 3

## Installation

```bash
claude plugin marketplace add redhat-community-ai-tools/claude-plugins
claude plugin install skipper@ecosystem-claude-plugins
```
