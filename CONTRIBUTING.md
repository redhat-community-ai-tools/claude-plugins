# Contributing

## Adding a Plugin

1. Create `plugins/<your-plugin>/manifest.json` following the schema in `plugin-schema.json`
2. Add skills in `plugins/<your-plugin>/skills/<skill-name>/SKILL.md`
3. Register your plugin in `.claude-plugin/marketplace.json`
4. Run `python scripts/validate.py` — must pass with zero errors
5. Open a PR

### Plugin Structure

```
plugins/my-plugin/
  manifest.json
  skills/
    my-skill/
      SKILL.md
  agents/           # optional — for background agents
    my-agent.md
```

### manifest.json Required Fields

| Field | Type | Rules |
|-------|------|-------|
| `name` | string | Lowercase kebab-case (`^[a-z][a-z0-9-]*$`), must match directory name |
| `version` | string | Semver (`x.y.z`) |
| `description` | string | Min 10 characters |
| `skills` | array | At least one skill with `name`, `path`, `description` |

### Optional Fields

| Field | Type | Purpose |
|-------|------|---------|
| `agents` | array | Background agents with `name`, `path`, `description` |
| `commands` | array | Slash commands with `name`, `path`, `description` |
| `dependencies` | object | `tools` (external CLIs) and `plugins` (other marketplace plugins) |

### SKILL.md Format

```yaml
---
name: my-skill
description: When to trigger this skill
---

# Skill Title

Instructions for Claude Code when this skill is activated.
```

The frontmatter `name` must match the skill name in `manifest.json`.

## Versioning

Plugins use [Semantic Versioning](https://semver.org/):

- **Patch** (`0.0.x`): Fix typos, improve descriptions, clarify instructions — no behavior change
- **Minor** (`0.x.0`): Add new skills, add commands, extend functionality — backwards compatible
- **Major** (`x.0.0`): Rename/remove skills, change required tools, break existing workflows

Update the version in both `manifest.json` and `.claude-plugin/marketplace.json` in the same commit.

## Plugin Dependencies

If your plugin depends on another plugin in the marketplace, declare it:

```json
{
  "dependencies": {
    "plugins": ["jira"],
    "tools": { ... }
  }
}
```

The validator checks that declared plugin dependencies exist. Claude Code does not auto-install them — users must install dependencies manually.

## Validation

The CI pipeline runs on every PR:

```bash
# Validate all plugins
python scripts/validate.py

# Run validator tests
python tests/test_validate.py
```

### What the validator checks

- Schema compliance (required fields, types, naming)
- All skill and command file references resolve
- SKILL.md has valid frontmatter with `name` and `description`
- Frontmatter `name` matches manifest `name`
- Skill body is not empty
- Directory name matches manifest name
- No duplicate skill names across plugins
- Plugin dependencies exist in the marketplace
- `marketplace.json` is consistent with plugin directories

## Testing Locally

```bash
# Add your local clone as a marketplace, then install from it
claude plugin marketplace add /path/to/your/clone
claude plugin install my-plugin

# Or load plugins for a single session without installing
claude --plugin-dir /path/to/your/clone/plugins/my-plugin
```
