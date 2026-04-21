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

### Common mistakes

- **`--params documentId=X`** — Wrong. `--params` requires JSON: `--params '{"documentId": "X"}'`
- **`--document-id X`** — Does not exist. Use `--params '{"documentId": "X"}'`
- **`--format text`** — Invalid format. Valid options: `json`, `table`, `yaml`, `csv`. Invalid formats emit a warning to stdout that breaks JSON piping.

## Discovering Commands

Before calling any API method, inspect it:

```bash
# Browse resources and methods
gws docs --help

# Inspect a method's required params, types, and defaults
gws schema docs.<resource>.<method>
```

Use `gws schema` output to build your `--params` and `--json` flags.
