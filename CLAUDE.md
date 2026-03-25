# CLAUDE.md

## Project Overview

This is a Claude Code plugin marketplace repository. It contains reusable plugins (skills, agents, commands) that can be installed into Claude Code via `/plugin marketplace add`.

## Repository Structure

```
plugins/<plugin-name>/        # Each plugin is a directory
  manifest.json               # Required: plugin metadata, skills, agents, commands
  README.md                   # Plugin documentation
  skills/<skill-name>/SKILL.md
  agents/<agent-name>.md
  .claude-code/commands/<cmd>.md
.claude-plugin/marketplace.json  # Registry of all plugins in this repo
plugin-schema.json               # JSON Schema for manifest.json validation
scripts/validate.py              # CI validation script
```

## Adding or Modifying Plugins

### Checklist (all items must be in the same commit)

1. **Plugin directory** — create `plugins/<name>/` with `manifest.json` matching the directory name
2. **marketplace.json** — add/update the entry in `.claude-plugin/marketplace.json` (name, version, source must match manifest)
3. **README.md (root)** — add/update the plugin's section in the top-level `README.md`
4. **Plugin README** — create/update `plugins/<name>/README.md`
5. **Skill files** — every skill listed in `manifest.json` must have a corresponding `SKILL.md` file at the declared path

### Validation Rules (enforced by CI)

- `manifest.json` must conform to `plugin-schema.json` (JSON Schema Draft 2020-12)
- Plugin directory name must exactly match `manifest.json` `"name"` field
- Names use lowercase kebab-case: `^[a-z][a-z0-9-]*$`
- Every file path in manifest (skills, agents, commands) must exist and stay within the plugin directory
- Every `SKILL.md` must have YAML frontmatter with `name` and `description` fields matching the manifest entry
- Skill names must be globally unique across all plugins
- Every plugin on disk must appear in `marketplace.json` and vice versa
- `version` in `marketplace.json` must match `manifest.json`
- `source` in `marketplace.json` must be `./plugins/<name>`

### Running Validation Locally

```bash
pip install 'jsonschema>=4.20,<5'
python scripts/validate.py
python tests/test_validate.py
```

## Skill File Format

```markdown
---
name: skill-name
description: One-line description matching manifest.json
---

Skill content goes here...
```

## Commit Conventions

- Prefix: `feat:` for new plugins/skills, `fix:` for corrections, `docs:` for documentation-only changes
- Keep marketplace.json, README, and manifest.json changes in the same commit as the skill/agent files they reference
