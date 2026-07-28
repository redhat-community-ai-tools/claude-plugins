---
name: demo-recording
description: Create asciinema terminal recordings for documentation or demos — CLI workflows, API sequences, or any terminal task
---

# Demo Recording

## Overview

Interactive workflow for creating polished asciinema terminal recordings. Works for any demo that runs in a terminal — API sequences, CLI tool workflows, kubectl operations, build pipelines, or interactive scripts.

## When to Use

- Recording a terminal workflow for documentation, a README, or a presentation
- Multi-step sequences where you want reproducible, scripted playback
- Any demo that benefits from typing animation, colored output, or async wait indicators

## Workflow

**1. Analyze Context**
- Read recent files, CLAUDE.md, git history to understand current work
- Identify what the user wants to demo
- Propose a demo flow based on context (e.g., "I see you're working on the CLI — shall we demo the create → list → delete flow?")

**2. Discovery Questions**
- Confirm/refine proposed workflow steps
- For API demos: base URL and auth method
- For CLI demos: which commands, what order
- Polish level: simple (plain) or polished (colors/animations)
- Cleanup strategy: keep created resources or delete with `--cleanup` flag

**3. Generate Script**
- Use `template-simple.sh` or `template-polished.sh` from this directory
- Fill in the demo steps in `run_demo()`
- For API demos: configure `API_BASE`, `refresh_auth()`, and `api()` calls
- For CLI demos: replace the API helpers with direct commands
- Add `wait_for_state()` calls if any step requires async polling
- Track created resources for cleanup

**4. Record**
- Test without recording: `./demo.sh --no-record` (runs the demo live without asciinema)
- Record: `./demo.sh` or `./demo.sh --cleanup`
- Playback: `asciinema play <file>.cast`

**5. Publish**
- Ask: "Upload to asciinema.org?"
- If yes: `asciinema upload <file>.cast`
- Provide shareable URL

## Templates

- `template-simple.sh` - Plain output, minimal formatting
- `template-polished.sh` - ANSI colors, typing animation, headers, spinners

Both include: `refresh_auth()`, `api()`, `wait_for_state()`, cleanup tracking. For pure CLI demos, strip the API helpers and use direct commands in `run_demo()`.

## Quick Reference

| Task | Command/Pattern |
|------|-----------------|
| Auth | `refresh_auth()` — call before API requests, in wait loops |
| API call | `api GET/POST/DELETE "<path>" [-d '{"json"}']` |
| Async wait | `wait_for_state "<url>" "<jq_filter>" "READY" <timeout>` |
| Track resource | `CREATED_RESOURCES+=("resourcetype/${id}")` |
| Test (no recording) | `./demo.sh --no-record` |
| Record+cleanup | `./demo.sh --cleanup` |

## Common Issues

- **Token expires**: Short-lived tokens need refresh. Call `refresh_auth()` inside polling loops.
- **Timeout**: Tune per resource — fast operations may need 30s, slow provisioning may need 600s.
- **Cleanup order**: Delete children before parents to avoid dependency errors.
- **Terminal size**: Set a consistent terminal size before recording (`stty cols 120 rows 35`) for uniform playback.

## Example

A minimal CLI demo — no API helpers needed:

```bash
run_demo() {
  type_cmd "myctl create widget --name demo-widget"
  myctl create widget --name demo-widget
  CREATED_RESOURCES+=("widget/demo-widget")

  type_cmd "myctl list widgets"
  myctl list widgets

  if [[ "${CLEANUP}" == "true" ]]; then
    cleanup_resources
  fi
}
```

For API demos, adapt `refresh_auth()` and `api()` to your auth mechanism (Bearer token, API key, basic auth, OAuth, etc.) and set `API_BASE`.
