---
name: gws-docs
description: "Read and write Google Docs."
metadata:
  version: 0.22.0
  openclaw:
    category: "productivity"
    requires:
      bins:
        - gws
    cliHelp: "gws docs --help"
---

# docs (v1)

> **PREREQUISITE:** Read `../gws-shared/SKILL.md` for auth, global flags, and security rules. If missing, run `gws generate-skills` to create it.

```bash
gws docs <resource> <method> [flags]
```

## Helper Commands

| Command | Description |
|---------|-------------|
| [`+write`](../gws-docs-write/SKILL.md) | Append text to a document |
| [`+format`](../gws-docs-format/SKILL.md) | Apply rich formatting (headings, bold, colors) to a document |

## API Resources

### documents

  - `batchUpdate` — Applies one or more updates to the document. Each request is validated before being applied. If any request is not valid, then the entire request will fail and nothing will be applied. Some requests have replies to give you some information about how they are applied. Other requests do not need to return information; these each return an empty reply. The order of replies matches that of the requests.
  - `create` — Creates a blank document using the title given in the request. Other fields in the request, including any provided content, are ignored. Returns the created document.
  - `get` — Gets the latest version of the specified document.

## Reading a Document

All parameters go through `--params` as a JSON object — there are no per-field flags like `--document-id`.

```bash
# Get document (JSON output, includes body content from first tab)
gws docs documents get --params '{"documentId": "DOC_ID"}'

# Get document with all tabs content
gws docs documents get --params '{"documentId": "DOC_ID", "includeTabsContent": true}'
```

### Extracting plain text from document JSON

The API returns structured JSON, not plain text. To extract readable text:

```bash
gws docs documents get --params '{"documentId": "DOC_ID", "includeTabsContent": true}' 2>/dev/null | python3 -c "
import json, sys
doc = json.load(sys.stdin)

def extract_text(elements):
    text = ''
    for el in elements:
        if 'paragraph' in el:
            for run in el['paragraph'].get('elements', []):
                if 'textRun' in run:
                    text += run['textRun']['content']
        elif 'table' in el:
            for row in el['table'].get('tableRows', []):
                for cell in row.get('tableCells', []):
                    text += extract_text(cell.get('content', []))
    return text

for tab in doc.get('tabs', []):
    title = tab.get('tabProperties', {}).get('title', 'Main')
    body = tab.get('documentTab', {}).get('body', {})
    text = extract_text(body.get('content', []))
    print(f'=== {title} ===')
    print(text)
"
```

### Extracting document structure with character indices

To apply formatting via `batchUpdate`, you need the `startIndex` and `endIndex` of each paragraph. This script prints them alongside the text:

```bash
gws docs documents get --params '{"documentId": "DOC_ID", "includeTabsContent": true}' 2>/dev/null | python3 -c "
import json, sys
doc = json.load(sys.stdin)
body = doc['tabs'][0]['documentTab']['body']
for el in body.get('content', []):
    if 'paragraph' in el:
        p = el['paragraph']
        text = ''
        for run in p.get('elements', []):
            if 'textRun' in run:
                text += run['textRun']['content']
        start = el.get('startIndex', 0)
        end = el.get('endIndex', 0)
        preview = text.strip()[:120]
        if preview:
            print(f'{start:5d}-{end:5d} | {preview}')
"
```

### Common mistakes

- **`--params documentId=X`** — Wrong. `--params` requires JSON: `--params '{"documentId": "X"}'`
- **`--document-id X`** — Does not exist. Use `--params '{"documentId": "X"}'`
- **`--format text`** — Invalid format. Valid options: `json`, `table`, `yaml`, `csv`. Invalid formats emit a warning to stdout that breaks JSON piping.

## Formatting Documents with batchUpdate

The `batchUpdate` method applies rich formatting — headings, bold, colors, deletions — in a single atomic call. All requests are validated before any are applied; if one fails, none take effect.

```bash
gws docs documents batchUpdate \
  --params '{"documentId": "DOC_ID"}' \
  --json '{"requests": [...]}'
```

For large request payloads, write JSON to a file and use command substitution:

```bash
gws docs documents batchUpdate \
  --params '{"documentId": "DOC_ID"}' \
  --json "$(cat /tmp/format-requests.json)"
```

### Heading styles

Apply paragraph-level heading styles using `updateParagraphStyle`. Valid `namedStyleType` values: `TITLE`, `SUBTITLE`, `HEADING_1` through `HEADING_6`, `NORMAL_TEXT`.

```json
{
  "updateParagraphStyle": {
    "range": {"startIndex": 2, "endIndex": 67},
    "paragraphStyle": {"namedStyleType": "HEADING_1"},
    "fields": "namedStyleType"
  }
}
```

### Bold and italic

Apply character-level styles using `updateTextStyle`:

```json
{
  "updateTextStyle": {
    "range": {"startIndex": 100, "endIndex": 115},
    "textStyle": {"bold": true},
    "fields": "bold"
  }
}
```

For italic, use `{"italic": true}` with `"fields": "italic"`. Both can be combined: `"fields": "bold,italic"`.

### Text color

Set foreground (text) or background (highlight) color using RGB values (0.0–1.0):

```json
{
  "updateTextStyle": {
    "range": {"startIndex": 200, "endIndex": 250},
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

### Font family

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

Common font families: `Red Hat Display`, `Red Hat Text`, `Roboto`, `Google Sans`, `Arial`, `Inter`.

### Bulleted and numbered lists

Convert paragraphs into native Google Docs lists using `createParagraphBullets`. Each paragraph in the range becomes a list item. Do **not** write list items with text prefixes like `- ` or `1. ` — write plain paragraphs, then apply native list formatting.

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

**Remove bullets:** use `deleteParagraphBullets` with the same range structure.

Common presets: `BULLET_DISC_CIRCLE_SQUARE` (● ○ ■), `BULLET_CHECKBOX` (☐), `NUMBERED_DECIMAL_ALPHA_ROMAN` (1. a. i.), `NUMBERED_DECIMAL_NESTED` (1. 1.1. 1.1.1.). See the [`+format`](../gws-docs-format/SKILL.md) skill for the full list.

### Line spacing

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

To apply font or line spacing to the **entire document**, use the full document range (`1` to last index).

### Deleting content

Remove text ranges with `deleteContentRange`. **Important:** deletions shift all subsequent indices, so apply them in reverse order (highest startIndex first) or separate them into a second `batchUpdate` call after formatting.

```json
{
  "deleteContentRange": {
    "range": {"startIndex": 134, "endIndex": 190}
  }
}
```

### Combining requests

A single `batchUpdate` can contain hundreds of requests. Mix different operations freely — just put deletions last and in reverse index order:

```json
{
  "requests": [
    {"updateParagraphStyle": {"range": {"startIndex": 2, "endIndex": 50}, "paragraphStyle": {"namedStyleType": "TITLE"}, "fields": "namedStyleType"}},
    {"updateParagraphStyle": {"range": {"startIndex": 100, "endIndex": 130}, "paragraphStyle": {"namedStyleType": "HEADING_1"}, "fields": "namedStyleType"}},
    {"updateTextStyle": {"range": {"startIndex": 200, "endIndex": 220}, "textStyle": {"bold": true}, "fields": "bold"}},
    {"deleteContentRange": {"range": {"startIndex": 500, "endIndex": 556}}},
    {"deleteContentRange": {"range": {"startIndex": 300, "endIndex": 356}}}
  ]
}
```

### Programmatic formatting with Python

For documents with many formatting targets, generate the requests programmatically. Use the helper functions below to build requests, then pass them to `batchUpdate`:

```python
#!/usr/bin/env python3
import json, subprocess

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

# --- Build your formatting ---
heading(2, 67, "TITLE")
heading(191, 212, 1)
bold(100, 115)
color(200, 250, 0.8, 0.0, 0.0)  # red
# Deletions in reverse index order
delete(500, 556)
delete(300, 356)

# --- Write and apply ---
with open("/tmp/format-requests.json", "w") as f:
    json.dump({"requests": requests}, f)
# Then run: gws docs documents batchUpdate --params '{"documentId": "DOC_ID"}' --json "$(cat /tmp/format-requests.json)"
```

## Recommended Workflow: Creating a Well-Formatted Document

Creating a richly formatted Google Doc is a multi-step process:

1. **Create the document:**
   ```bash
   gws docs documents create --json '{"title": "My Document Title"}'
   ```
   Save the `documentId` from the response.

2. **Write plain text content** — use `+write` with content from a file to avoid shell escaping issues with parentheses, quotes, and special characters:
   ```bash
   # Write content to a temp file first, then pipe
   gws docs +write --document DOC_ID --text "$(cat /tmp/my-content.txt)"
   ```

3. **Extract paragraph indices** — get the `startIndex`/`endIndex` for each paragraph (see "Extracting document structure with character indices" above).

4. **Apply formatting** — build a `batchUpdate` request with headings, bold, colors, and deletions. For complex documents, use the Python helper pattern above.

5. **Verify** — re-read the document to confirm formatting was applied correctly.

> [!TIP]
> Write all content as plain text first, **then** format. Formatting operations use character indices that shift when content changes — reformatting after edits requires recalculating all indices.

## Discovering Commands

Before calling any API method, inspect it:

```bash
# Browse resources and methods
gws docs --help

# Inspect a method's required params, types, and defaults
gws schema docs.<resource>.<method>
```

Use `gws schema` output to build your `--params` and `--json` flags.
