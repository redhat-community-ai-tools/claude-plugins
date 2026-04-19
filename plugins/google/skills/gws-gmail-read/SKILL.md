---
name: gws-gmail-read
description: "Gmail: Read a message and extract its body or headers. Use this to get the full content of an email after finding its ID via +triage or a threads/messages search. Handles base64 decoding, HTML-to-text conversion, and multipart messages automatically — prefer this over raw messages.get for reading email bodies."
metadata:
  version: 0.22.0
  openclaw:
    category: "productivity"
    requires:
      bins:
        - gws
    cliHelp: "gws gmail +read --help"
---

# gmail +read

> **PREREQUISITE:** Read `../gws-shared/SKILL.md` for auth, global flags, and security rules. If missing, run `gws generate-skills` to create it.

Read a message and extract its body or headers.

## Usage

```bash
gws gmail +read --id <ID>
```

## Finding Message IDs

You need a message ID before calling `+read`. Here's how to get one:

```bash
# From triage (shows IDs in output)
gws gmail +triage --format json | jq '.[0].id'

# From a thread search
gws gmail users threads list --params '{"userId": "me", "q": "from:alice subject:report", "maxResults": 1}'
# Then read the message ID from the response's messages array

# From a message search
gws gmail users messages list --params '{"userId": "me", "q": "subject:quarterly review", "maxResults": 5}'
```

## Flags

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--id` | ✓ | — | The Gmail message ID to read |
| `--headers` | — | — | Include headers (From, To, Subject, Date) in the output |
| `--format` | — | text | Output format (text, json) |
| `--html` | — | — | Return HTML body instead of plain text |
| `--dry-run` | — | — | Show the request that would be sent without executing it |

## Examples

```bash
gws gmail +read --id 18f1a2b3c4d
gws gmail +read --id 18f1a2b3c4d --headers
gws gmail +read --id 18f1a2b3c4d --format json | jq '.body'
```

## Tips

- Converts HTML-only messages to plain text automatically.
- Handles multipart/alternative and base64 decoding.
- Use `--headers` to include From, To, Subject, Date alongside the body — helpful for summarization tasks.
- For thread summarization, call `+read --headers` on each message ID in the thread.

## See Also

- [gws-shared](../gws-shared/SKILL.md) — Global flags and auth
- [gws-gmail](../gws-gmail/SKILL.md) — All Gmail commands and common workflows
