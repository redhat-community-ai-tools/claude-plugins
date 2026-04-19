---
name: gws-gmail-triage
description: "Gmail: Show unread inbox summary (sender, subject, date). Use when the user wants to check their inbox, see what's new, find recent emails, or get an overview of unread messages. Supports custom Gmail search queries to filter by sender, subject, label, or date."
metadata:
  version: 0.22.0
  openclaw:
    category: "productivity"
    requires:
      bins:
        - gws
    cliHelp: "gws gmail +triage --help"
---

# gmail +triage

> **PREREQUISITE:** Read `../gws-shared/SKILL.md` for auth, global flags, and security rules. If missing, run `gws generate-skills` to create it.

Show unread inbox summary (sender, subject, date).

## Usage

```bash
gws gmail +triage
```

## Flags

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--max` | — | 20 | Maximum messages to show (default: 20) |
| `--query` | — | — | Gmail search query (default: is:unread) |
| `--labels` | — | — | Include label names in output |

## Examples

```bash
gws gmail +triage
gws gmail +triage --max 5 --query 'from:boss'
gws gmail +triage --format json | jq '.[].subject'
gws gmail +triage --labels
```

## Next Steps

After triage, use the message ID from the output to read, reply, or forward:

```bash
# Read the full body of a message from triage
gws gmail +read --id <ID> --headers

# Reply to a message
gws gmail +reply --message-id <ID> --body 'Thanks!'
```

## Tips

- Read-only — never modifies your mailbox.
- Defaults to table output format. Use `--format json` to get structured output with message IDs.
- The JSON output includes message IDs that can be passed directly to `+read`, `+reply`, or `+forward`.

## See Also

- [gws-shared](../gws-shared/SKILL.md) — Global flags and auth
- [gws-gmail](../gws-gmail/SKILL.md) — All Gmail commands and common workflows
- [gws-gmail-read](../gws-gmail-read/SKILL.md) — Read full message body by ID
