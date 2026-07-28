# demo-recording

Create polished asciinema terminal recordings for documentation or demos — CLI workflows, API sequences, or any terminal task.

## What it does

Interactive workflow that helps you:
1. Analyze your current work context and propose a demo flow
2. Ask discovery questions (commands/endpoints, polish level, cleanup strategy)
3. Generate a recording script from simple or polished templates
4. Record with `asciinema` (supports dry-run and auto-cleanup)
5. Optionally upload to asciinema.org

## Skills

- **demo-recording** — End-to-end asciinema recording workflow with script generation

## Templates

| Template | Description |
|----------|-------------|
| `template-simple.sh` | Plain output, minimal formatting |
| `template-polished.sh` | ANSI colors, typing animation, headers, spinners |

Both templates include:
- `refresh_auth()` — pluggable authentication (Bearer token, API key, kubectl, etc.)
- `api()` — HTTP client wrapper with error handling
- `wait_for_state()` — async polling with configurable jq filter and timeout
- `cleanup_resources()` — reverse-order resource deletion

For pure CLI demos, strip the API helpers and use direct commands in `run_demo()`.

## Requirements

- `asciinema` — terminal session recorder ([install](https://asciinema.org/docs/installation))
- `curl` (API demos only) — HTTP client
- `jq` (optional) — JSON processor

## Install

```bash
claude plugin install demo-recording
```
