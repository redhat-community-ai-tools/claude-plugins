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
| [`+format`](../gws-docs-format/SKILL.md) | Apply rich formatting (headings, bold, colors, links, lists) to a document |

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

The `batchUpdate` method applies rich formatting — headings, bold/italic, colors, links, lists, font, line spacing, and content deletion — in a single atomic call. For the **full formatting guide**, request types, Python helpers, and examples, see [`+format`](../gws-docs-format/SKILL.md).

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

Key rules:
- **Write content first, format second.** Formatting uses character indices that shift when content changes.
- **Formatting-only operations** (headings, bold, color) do not shift indices — only insertions and deletions do.
- **Deletions must be in reverse index order** (highest `startIndex` first).
- A single `batchUpdate` can hold hundreds of requests.

### Recommended workflow

1. **Create** the document with `documents create`
2. **Write** plain text content with `+write`
3. **Extract** paragraph indices (see "Extracting document structure with character indices" above)
4. **Format** using `batchUpdate` — see [`+format`](../gws-docs-format/SKILL.md) for all request types and a reusable Python helper
5. **Verify** by re-reading the document

## Discovering Commands

Before calling any API method, inspect it:

```bash
# Browse resources and methods
gws docs --help

# Inspect a method's required params, types, and defaults
gws schema docs.<resource>.<method>
```

Use `gws schema` output to build your `--params` and `--json` flags.
