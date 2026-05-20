---
name: gws-docs-write
description: "Google Docs: Append text to a document."
metadata:
  version: 0.22.0
  openclaw:
    category: "productivity"
    requires:
      bins:
        - gws
    cliHelp: "gws docs +write --help"
---

# docs +write

> **PREREQUISITE:** Read `../gws-shared/SKILL.md` for auth, global flags, and security rules. If missing, run `gws generate-skills` to create it.

Append text to a document

## Usage

```bash
gws docs +write --document <ID> --text <TEXT>
```

## Flags

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--document` | ✓ | — | Document ID |
| `--text` | ✓ | — | Text to append (plain text) |

## Examples

```bash
gws docs +write --document DOC_ID --text 'Hello, world!'
```

## Tips

- Text is inserted at the end of the document body.
- For rich formatting, use the [`+format`](../gws-docs-format/SKILL.md) helper or the raw `batchUpdate` API.
- **Long or complex text:** Write content to a temp file first, then use command substitution. Passing long strings directly via `--text '...'` often breaks due to shell interpretation of parentheses, quotes, backticks, and other special characters.
  ```bash
  # Write content to file, then pass via command substitution
  gws docs +write --document DOC_ID --text "$(cat /tmp/my-content.txt)"
  ```
- **Lists:** Do not write bullet or numbered list items with text prefixes like `- ` or `1. `. Write each item as a plain line, then use [`+format`](../gws-docs-format/SKILL.md) to apply native Google Docs bulleted/numbered list formatting via `createParagraphBullets`.

> [!CAUTION]
> This is a **write** command — confirm with the user before executing.

## See Also

- [gws-shared](../gws-shared/SKILL.md) — Global flags and auth
- [gws-docs](../gws-docs/SKILL.md) — All read and write google docs commands
