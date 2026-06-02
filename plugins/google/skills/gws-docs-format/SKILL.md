---
name: gws-docs-format
description: "Google Docs: Apply rich formatting (headings, bold, colors, links, lists) to a document via batchUpdate."
metadata:
  version: 0.2.0
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
3. **Always include 1.5 line spacing** (`lineSpacing: 150`) across the full document range (`1` to last index) — Google Docs defaults to 1.15 which is too tight for most documents
4. Apply via `batchUpdate`

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

### Links

Make text a clickable hyperlink:

```json
{
  "updateTextStyle": {
    "range": {"startIndex": START, "endIndex": END},
    "textStyle": {
      "link": {"url": "https://example.com"}
    },
    "fields": "link"
  }
}
```

To remove a link while keeping the text, set `"link": null`.

To insert new linked text (e.g., `[label](url)` style), use `insertText` to add the label text, then apply the link style to that range:

```json
{
  "requests": [
    {"insertText": {"location": {"index": INSERT_AT}, "text": "Click here"}},
    {"updateTextStyle": {
      "range": {"startIndex": INSERT_AT, "endIndex": INSERT_AT_PLUS_TEXT_LEN},
      "textStyle": {"link": {"url": "https://example.com"}},
      "fields": "link"
    }}
  ]
}
```

**Note:** `insertText` shifts all subsequent indices. If inserting multiple links, work in reverse index order or calculate offsets.

### Font Family

Set the font for a text range. The font must be available in Google Docs (installed or from Google Fonts).

```json
{
  "updateTextStyle": {
    "range": {"startIndex": START, "endIndex": END},
    "textStyle": {
      "weightedFontFamily": {"fontFamily": "Red Hat Display"}
    },
    "fields": "weightedFontFamily"
  }
}
```

To set the font for the **entire document**, use the full document range (`1` to last index). To change the default font for all named styles at once, use `updateDocumentStyle` (see "Document-Wide Defaults" below).

### Bulleted and Numbered Lists

Convert paragraphs into native Google Docs lists using `createParagraphBullets`. The range should cover all paragraphs to include in the list. Each paragraph in the range becomes a list item.

**Bulleted list:**

```json
{
  "createParagraphBullets": {
    "range": {"startIndex": START, "endIndex": END},
    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
  }
}
```

**Numbered list:**

```json
{
  "createParagraphBullets": {
    "range": {"startIndex": START, "endIndex": END},
    "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN"
  }
}
```

**Remove bullets/numbering:**

```json
{
  "deleteParagraphBullets": {
    "range": {"startIndex": START, "endIndex": END}
  }
}
```

**Note:** Do not write list items with text prefixes like `- ` or `1. ` when the intent is to create a native list. Write each item as a plain paragraph (one per line), then apply `createParagraphBullets` to the range. Native lists give proper indentation, numbering, and nesting — text prefixes are just plain text with no list behavior.

**Note:** If converting existing text that has `- ` or `1. ` prefixes, you must strip the prefixes in a **separate** `batchUpdate` call **after** applying `createParagraphBullets`. The `createParagraphBullets` operation shifts character indices, so prefix deletions in the same batch will target wrong positions. Apply list formatting first, then re-read the document to get updated indices, then delete prefixes.

Common bullet presets:
| Preset | Style |
|--------|-------|
| `BULLET_DISC_CIRCLE_SQUARE` | ● ○ ■ (standard) |
| `BULLET_DIAMONDX_ARROW3D_SQUARE` | ◆ ➤ ■ |
| `BULLET_CHECKBOX` | ☐ ☐ ☐ |
| `BULLET_ARROW_DIAMOND_DISC` | ➔ ◆ ● |

Common numbered presets:
| Preset | Style |
|--------|-------|
| `NUMBERED_DECIMAL_ALPHA_ROMAN` | 1. a. i. (standard) |
| `NUMBERED_DECIMAL_ALPHA_ROMAN_PARENS` | 1) a) i) |
| `NUMBERED_DECIMAL_NESTED` | 1. 1.1. 1.1.1. |
| `NUMBERED_UPPERALPHA_ALPHA_ROMAN` | A. a. i. |

### Line Spacing

Set line spacing on paragraphs using `lineSpacing` as a percentage (100 = single, 150 = 1.5, 200 = double):

```json
{
  "updateParagraphStyle": {
    "range": {"startIndex": START, "endIndex": END},
    "paragraphStyle": {"lineSpacing": 150},
    "fields": "lineSpacing"
  }
}
```

To apply to the **entire document**, use the full document range (`1` to last index).

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
    style_map = {
        "TITLE": "TITLE", "SUBTITLE": "SUBTITLE",
        1: "HEADING_1", 2: "HEADING_2", 3: "HEADING_3",
        4: "HEADING_4", 5: "HEADING_5", 6: "HEADING_6",
    }
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

def link(start, end, url):
    requests.append({
        "updateTextStyle": {
            "range": {"startIndex": start, "endIndex": end},
            "textStyle": {"link": {"url": url}},
            "fields": "link"
        }
    })

def list_style(start, end, preset="BULLET_DISC_CIRCLE_SQUARE"):
    requests.append({
        "createParagraphBullets": {
            "range": {"startIndex": start, "endIndex": end},
            "bulletPreset": preset
        }
    })

def font(start, end, family):
    requests.append({
        "updateTextStyle": {
            "range": {"startIndex": start, "endIndex": end},
            "textStyle": {"weightedFontFamily": {"fontFamily": family}},
            "fields": "weightedFontFamily"
        }
    })

def line_spacing(start, end, pct):
    """pct: 100 = single, 150 = 1.5, 200 = double."""
    requests.append({
        "updateParagraphStyle": {
            "range": {"startIndex": start, "endIndex": end},
            "paragraphStyle": {"lineSpacing": pct},
            "fields": "lineSpacing"
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
# Convert paragraphs to native lists (range covers all items)
list_style(300, 450)
list_style(500, 600, preset="NUMBERED_DECIMAL_ALPHA_ROMAN")
# Document-wide: set font and 1.5 line spacing on entire body
# Replace LAST_INDEX with the actual last index from the document JSON
# (see "Document-Wide Defaults" section below for how to get it)
font(1, last_index, "Red Hat Display")
line_spacing(1, last_index, 150)
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

## Document-Wide Defaults

To set font and line spacing across the entire document body, apply `updateTextStyle` and `updateParagraphStyle` with a range covering the full content (`1` to the last index). Get the last index from the document JSON:

```bash
gws docs documents get --params '{"documentId": "DOC_ID", "includeTabsContent": true}' 2>/dev/null | python3 -c "
import json, sys
doc = json.load(sys.stdin)
body = doc['tabs'][0]['documentTab']['body']
last = body['content'][-1].get('endIndex', 1)
print(last)
"
```

Then apply both in one `batchUpdate`:

```json
{
  "requests": [
    {
      "updateTextStyle": {
        "range": {"startIndex": 1, "endIndex": LAST_INDEX},
        "textStyle": {"weightedFontFamily": {"fontFamily": "Red Hat Display"}},
        "fields": "weightedFontFamily"
      }
    },
    {
      "updateParagraphStyle": {
        "range": {"startIndex": 1, "endIndex": LAST_INDEX},
        "paragraphStyle": {"lineSpacing": 150},
        "fields": "lineSpacing"
      }
    }
  ]
}
```

Common font families: `Red Hat Display`, `Red Hat Text`, `Roboto`, `Google Sans`, `Arial`, `Inter`.

Line spacing values: `100` (single), `115` (1.15), `150` (1.5), `200` (double).

## Tips

- **Always apply 1.5 line spacing** (`lineSpacing: 150`) to the full document range as part of every formatting pass. Google Docs defaults to 1.15 which produces cramped output. Include `line_spacing(1, last_index, 150)` in every programmatic formatting script, or add the `updateParagraphStyle` request manually.
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
