# Programmatic Formatting Helper

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
list_style(300, 450)
list_style(500, 600, preset="NUMBERED_DECIMAL_ALPHA_ROMAN")
# Document-wide: set font and 1.5 line spacing on entire body
# Replace LAST_INDEX with the actual last index from the document JSON
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

## List Presets

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
