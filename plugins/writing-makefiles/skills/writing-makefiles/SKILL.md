---
name: writing-makefiles
description: Use when creating or reviewing a Makefile meant as a developer command shortcut (build/test/lint/run/clean), when asked for a self-documenting `make help` target, or when debugging "missing separator", .PHONY, or unexpected variable-expansion issues in a Makefile.
---

# Writing Makefiles

## Overview

Make is the **goto** for developer command shortcuts, not a fallback: it ships with virtually every dev machine and CI image, and `make <target>` is a convention almost everyone already knows. Reach for it by default any time you'd otherwise tell teammates "run this command" in a README. Optimize the Makefile for readability and discoverability, not cleverness — it's a table of contents, not where logic lives.

This skill covers the **shortcut-Makefile** case (wrapping repeatable dev commands), not deep pattern-rule/cross-compilation build systems.

## Wrap Scripts, Don't Inline Logic

A target's job is to dispatch, not implement:

- **Trivial command** (`go build`, `pytest`, `docker build`) → inline directly in the recipe.
- **Anything with a loop, conditional, multi-step error handling, or logic you'd want to run/test without Make** → move it to `scripts/<name>.sh` (or `.py`) and have the target call it:

```makefile
.PHONY: release
release: ## Cut a release. Logic lives in scripts/release.sh.
	scripts/release.sh $(ARGS)
```

This keeps the Makefile scannable top-to-bottom as a menu of what a dev can run, and keeps the actual logic independently runnable and testable outside of Make (see Testing below). Don't reach for a different task runner (`just`, npm scripts, etc.) just because Make has quirks like tabs or `.PHONY` — those are solved once via the boilerplate below and then invisible day to day. Only consider an alternative for a brand-new project with zero file-dependency needs that specifically wants native argument-parsing into tasks; never mid-project just to dodge a quirk.

## Standard Structure

Every shortcut Makefile follows this skeleton, in order: settings → variables → `.PHONY` → `help` as default goal → targets grouped with `##@` category comments. A ready-to-copy version is at `assets/Makefile.template` in this skill — copy it in, rename the tool commands for your stack, and delete targets you don't need.

The one piece to never skip is the `help` target itself — the de-facto standard used across many real-world projects (e.g. kubebuilder-scaffolded operators):

```makefile
.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9\/-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
```

It scans every `target: ## description` line and every `##@ Category` line and pretty-prints them, so documentation can never drift out of sync with the targets themselves. **Always include this exact recipe** in shortcut Makefiles — it's copy-paste boilerplate, costs nothing to maintain, and gives every project the same `make help` entry point. Pair it with `.DEFAULT_GOAL := help` so bare `make` shows usage instead of silently running the first target.

## Standard Target Names

Use these names so any dev familiar with `make` guesses correctly without reading the file:

| Target | Purpose |
|---|---|
| `help` | List targets (default goal) |
| `build` | Compile / produce artifacts |
| `test` | Run test suite |
| `lint` | Static analysis |
| `fmt` | Auto-format code |
| `run` | Run the app locally |
| `clean` | Remove build artifacts |
| `install` / `deps` | Install dependencies |

Prefer `make test` over `make t`; if you need sub-variants, namespace with `/` (`test/unit`, `test/e2e`) — `:` breaks dependency parsing and `-` reads ambiguously.

## Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Recipe indented with spaces | `*** missing separator. Stop.` | Recipe lines must start with a literal tab. Configure your editor to insert real tabs in Makefiles. |
| Forgot `.PHONY` on a non-file target | `make: 'clean' is up to date.` even though nothing ran | Declare every command-style target `.PHONY` (group them, or one `.PHONY:` line per target next to it as shown above). |
| Used `=` instead of `:=` for a variable that shells out | Variable re-evaluates every reference, sometimes with a different (later) value or repeated side effects | Default to `:=` (simple/immediate expansion). Only use `=` when you deliberately want lazy re-evaluation. |
| Referencing a shell variable as `$VAR` in a recipe | Make tries to expand `$V` as its own (empty) variable | Escape shell variables as `$$VAR` inside recipes; single `$` is for Make variables. |
| No `@` prefix | Every command line is echoed before running, cluttering output | Prefix noisy/expected commands with `@`; leave it off while debugging a recipe. |
| Task fails but Make doesn't stop / leaves a broken output file | Partial artifact looks "built" | Add `.DELETE_ON_ERROR:` once, near the top, so Make removes a target's output file if its recipe fails. |
| No default for a config variable | `make deploy` fails cryptically without `ENV=` set | Give every variable a sane default with `?=` so `make <target>` works with zero arguments. |
| Complex multi-step logic inlined in a recipe | Unreadable, hard to test outside Make | Move it to `scripts/foo.sh` and call it from the target — see "Wrap Scripts, Don't Inline Logic" above. |

## Testing Makefiles

- **Test the logic, not the dispatcher.** Since anything non-trivial lives in `scripts/`, test those scripts with their own tooling (bats-core for bash, pytest for Python helpers, `go test` for Go helpers) instead of trying to unit-test Make syntax itself.
- **Dry-run before trusting a target.** `make -n <target>` (alias `--just-print`) prints the commands a target would run without executing them — use it after writing or editing a target to catch typos in prerequisites or recipe commands before they run for real.
- **Lint the Makefile itself.** Run [`checkmake`](https://github.com/mrtazz/checkmake) for structural issues (missing `.PHONY`, undocumented targets); pipe multi-line recipes through `shellcheck` if they contain nontrivial shell.
- **Exercise it in CI exactly like devs do.** CI should invoke `make lint`, `make test`, `make build` — the same targets developers run locally — rather than duplicating the underlying commands in CI config. That makes CI a live test of the Makefile: if a target breaks, CI catches it on every PR instead of only when a human happens to run it.
- **Verify fresh-clone behavior.** Periodically (or as a CI job) run setup → build → test against a clean checkout. A target that only works because of leftover local state (a cached venv, a stale binary) will fail for the next new contributor.

## Quick Reference

```makefile
.DEFAULT_GOAL := help      # bare `make` shows help, not the first target
.DELETE_ON_ERROR:           # remove partial output on recipe failure
VAR ?= default              # overridable default, use ?= not =
VAR := $(shell cmd)         # immediate expansion, evaluated once
target: deps | order-only   # order-only prereqs don't force rebuilds
	@echo quiet              # @ suppresses command echo
	echo $$SHELL_VAR         # $$ for shell vars, $ for Make vars
```

Sources: [Makefile Tutorial by Example](https://makefiletutorial.com/), [Cloud Posse Makefile Best Practices](https://docs.cloudposse.com/best-practices/developer-makefile/), [GNU Make manual — Phony Targets](https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html), [Self-documenting Makefile pattern (gist)](https://gist.github.com/klmr/575726c7e05d8780505a), kubebuilder-scaffolded project Makefiles.
