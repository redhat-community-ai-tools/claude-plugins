---
name: gws-docs-format
description: "Google Docs: Apply rich formatting (headings, bold, colors) to a document via batchUpdate."
metadata:
  version: 0.22.0
  openclaw:
    category: "productivity"
    requires:
      bins:
        - gws
    cliHelp: "gws schema docs.documents.batchUpdate"
---

# docs +format

> **PREREQUISITE:** Read `../gws-shared/SKILL.md` for auth, global flags, and security rules. If missing, run `gws generate-skills` to create it.

Apply rich formatting to a Google Doc using the `batchUpdate` API. This skill covers headings, bold/italic, text colors, and content deletion.

## Quick Start

Formatting requires character indices. The workflow is always:

1. Get the document structure with indices
2. Build formatting requests targeting those indices
3. Apply via `batchUpdate`

### Step 1 — Get paragraph indices

```bash
gws docs documents get --params '{"documentId": "DOC_ID", "includeTabsContent": true}' 2>/dev/null | python3 -c "
import json, sys
doc = json.load(sys.stdin)
body = doc['tabs'][0]['documentTab']['body']
for el in body.get('content', []):
    if 'paragraph' in el:
        text = ''
        for run in el['paragraph'].get('elements', []):
            if 'textRun' in run:
                text += run['textRun']['content']
        start = el.get('startIndex', 0)
        end = el.get('endIndex', 0)
        preview = text.strip()[:120]
        if preview:
            print(f'{start:5d}-{end:5d} | {preview}')
"
```

### Step 2 — Build and apply formatting

```bash
gws docs documents batchUpdate \
  --params '{"documentId": "DOC_ID"}' \
  --json '{"requests": [
    {"updateParagraphStyle": {"range": {"startIndex": 2, "endIndex": 50}, "paragraphStyle": {"namedStyleType": "TITLE"}, "fields": "namedStyleType"}},
    {"updateParagraphStyle": {"range": {"startIndex": 100, "endIndex": 130}, "paragraphStyle": {"namedStyleType": "HEADING_1"}, "fields": "namedStyleType"}},
    {"updateTextStyle": {"range": {"startIndex": 200, "endIndex": 220}, "textStyle": {"bold": true}, "fields": "bold"}}
  ]}'
```

For large payloads, write JSON to a file:

```bash
gws docs documents batchUpdate \
  --params '{"documentId": "DOC_ID"}' \
  --json "$(cat /tmp/format-requests.json)"
```

## Request Types

### Headings

Valid `namedStyleType` values: `TITLE`, `SUBTITLE`, `HEADING_1` through `HEADING_6`, `NORMAL_TEXT`.

```json
{
  "updateParagraphStyle": {
    "range": {"startIndex": START, "endIndex": END},
    "paragraphStyle": {"namedStyleType": "HEADING_1"},
    "fields": "namedStyleType"
  }
}
```

### Bold / Italic

```json
{
  "updateTextStyle": {
    "range": {"startIndex": START, "endIndex": END},
    "textStyle": {"bold": true},
    "fields": "bold"
  }
}
```

Use `"italic": true` with `"fields": "italic"` for italics. Combine: `"fields": "bold,italic"`.

### Text Color

RGB values are floats from 0.0 to 1.0.

```json
{
  "updateTextStyle": {
    "range": {"startIndex": START, "endIndex": END},
    "textStyle": {
      "foregroundColor": {
        "color": {"rgbColor": {"red": 0.8, "green": 0.0, "blue": 0.0}}
      }
    },
    "fields": "foregroundColor"
  }
}
```

Replace `foregroundColor` with `backgroundColor` for highlighting.

Common colors:
| Color | RGB |
|-------|-----|
| Red | `0.8, 0.0, 0.0` |
| Gray | `0.4, 0.4, 0.4` |
| Blue | `0.0, 0.0, 0.8` |
| Green | `0.0, 0.5, 0.0` |

### Deleting Content

```json
{
  "deleteContentRange": {
    "range": {"startIndex": START, "endIndex": END}
  }
}
```

**Critical:** Deletions shift all subsequent indices. Always apply deletions in **reverse index order** (highest `startIndex` first).

## Programmatic Formatting

For documents with many formatting targets, use Python to generate requests:

```python
#!/usr/bin/env python3
import json

DOC_ID = "YOUR_DOC_ID"
requests = []

def heading(start, end, level):
    style_map = {"TITLE": "TITLE", 1: "HEADING_1", 2: "HEADING_2", 3: "HEADING_3"}
    requests.append({
        "updateParagraphStyle": {
            "range": {"startIndex": start, "endIndex": end},
            "paragraphStyle": {"namedStyleType": style_map[level]},
            "fields": "namedStyleType"
        }
    })

def bold(start, end):
    requests.append({
        "updateTextStyle": {
            "range": {"startIndex": start, "endIndex": end},
            "textStyle": {"bold": True},
            "fields": "bold"
        }
    })

def color(start, end, r, g, b):
    requests.append({
        "updateTextStyle": {
            "range": {"startIndex": start, "endIndex": end},
            "textStyle": {"foregroundColor": {"color": {"rgbColor": {"red": r, "green": g, "blue": b}}}},
            "fields": "foregroundColor"
        }
    })

def delete(start, end):
    requests.append({"deleteContentRange": {"range": {"startIndex": start, "endIndex": end}}})

# Build formatting
heading(2, 67, "TITLE")
heading(191, 212, 1)
heading(500, 540, 2)
bold(100, 115)
color(200, 250, 0.8, 0.0, 0.0)
# Deletions MUST be in reverse index order
delete(600, 656)
delete(400, 456)

with open("/tmp/format-requests.json", "w") as f:
    json.dump({"requests": requests}, f)
```

Then apply:

```bash
gws docs documents batchUpdate \
  --params '{"documentId": "DOC_ID"}' \
  --json "$(cat /tmp/format-requests.json)"
```

## Tips

- **Write content first, format second.** Formatting uses character indices that shift when content changes.
- **One batchUpdate can hold hundreds of requests.** Mix headings, bold, colors, and deletions in a single call — just put deletions last in reverse order.
- **Formatting-only operations (headings, bold, color) do not shift indices.** Only insertions and deletions move things around — so you can safely apply all non-delete operations in any order.
- **Verify formatting** by re-reading the document structure after applying.

> [!CAUTION]
> This is a **write** command — confirm with the user before executing.

## See Also

- [gws-docs](../gws-docs/SKILL.md) — Full docs API reference including batchUpdate details
- [gws-docs-write](../gws-docs-write/SKILL.md) — Append plain text
- [gws-shared](../gws-shared/SKILL.md) — Global flags and auth
