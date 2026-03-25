#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"
MARKETPLACE_FILE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
SCHEMA_FILE = REPO_ROOT / "plugin-schema.json"


def load_json(*, path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def validate_manifest_schema(*, plugin_dir: Path, schema: dict[str, Any]) -> list[str]:
    manifest = load_json(path=plugin_dir / "manifest.json")
    errors: list[str] = []
    for error in jsonschema.Draft202012Validator(schema).iter_errors(manifest):
        path_str = ".".join(str(p) for p in error.absolute_path)
        if not path_str:
            path_str = "(root)"
        errors.append(f"{plugin_dir.name}: manifest.json [{path_str}] {error.message}")
    return errors


def validate_directory_name(*, plugin_dir: Path) -> list[str]:
    manifest_name = load_json(path=plugin_dir / "manifest.json")["name"]
    if manifest_name != plugin_dir.name:
        return [f"{plugin_dir.name}: directory name '{plugin_dir.name}' does not match manifest name '{manifest_name}'"]
    return []


def validate_file_references(*, plugin_dir: Path) -> list[str]:
    manifest = load_json(path=plugin_dir / "manifest.json")
    errors: list[str] = []

    for skill in manifest["skills"]:
        skill_path = (plugin_dir / skill["path"]).resolve()
        if not skill_path.is_relative_to(plugin_dir.resolve()):
            errors.append(f"{plugin_dir.name}: skill '{skill['name']}' escapes plugin directory: {skill['path']}")
            continue
        if not skill_path.exists():
            errors.append(f"{plugin_dir.name}: skill '{skill['name']}' references missing file: {skill['path']}")
            continue
        errors.extend(validate_skill_frontmatter(
            plugin_name=plugin_dir.name,
            skill_name=skill["name"],
            skill_path=skill_path,
        ))

    if "agents" in manifest:
        for agent in manifest["agents"]:
            agent_path = (plugin_dir / agent["path"]).resolve()
            if not agent_path.is_relative_to(plugin_dir.resolve()):
                errors.append(f"{plugin_dir.name}: agent '{agent['name']}' escapes plugin directory: {agent['path']}")
                continue
            if not agent_path.exists():
                errors.append(f"{plugin_dir.name}: agent '{agent['name']}' references missing file: {agent['path']}")


    if "commands" in manifest:
        for cmd in manifest["commands"]:
            cmd_path = (plugin_dir / cmd["path"]).resolve()
            if not cmd_path.is_relative_to(plugin_dir.resolve()):
                errors.append(f"{plugin_dir.name}: command '{cmd['name']}' escapes plugin directory: {cmd['path']}")
                continue
            if not cmd_path.exists():
                errors.append(f"{plugin_dir.name}: command '{cmd['name']}' references missing file: {cmd['path']}")

    return errors


def validate_skill_frontmatter(*, plugin_name: str, skill_name: str, skill_path: Path) -> list[str]:
    content = skill_path.read_text()
    errors: list[str] = []

    if not content.startswith("---\n"):
        return [f"{plugin_name}: skill '{skill_name}' ({skill_path.name}) missing YAML frontmatter"]

    end = content.find("\n---\n", 4)
    if end == -1:
        return [f"{plugin_name}: skill '{skill_name}' ({skill_path.name}) has unclosed frontmatter"]

    frontmatter_lines = content[4:end].split("\n")

    fm_name = _frontmatter_value(lines=frontmatter_lines, field="name")
    fm_desc = _frontmatter_value(lines=frontmatter_lines, field="description")

    if not fm_name:
        errors.append(f"{plugin_name}: skill '{skill_name}' frontmatter missing 'name'")
    elif fm_name != skill_name:
        errors.append(f"{plugin_name}: skill '{skill_name}' frontmatter name mismatch: manifest says '{skill_name}', frontmatter says '{fm_name}'")

    if not fm_desc:
        errors.append(f"{plugin_name}: skill '{skill_name}' frontmatter missing 'description'")

    body = content[end + 5:].strip()
    if not body:
        errors.append(f"{plugin_name}: skill '{skill_name}' has no content after frontmatter")

    return errors


def _frontmatter_value(*, lines: list[str], field: str) -> str:
    for line in lines:
        if line.startswith(f"{field}:"):
            return line.split(":", 1)[1].strip()
    return ""


def validate_duplicate_skill_names(*, plugin_dirs: list[Path]) -> list[str]:
    seen: dict[str, str] = {}
    errors: list[str] = []
    for plugin_dir in plugin_dirs:
        manifest = load_json(path=plugin_dir / "manifest.json")
        for skill in manifest["skills"]:
            name = skill["name"]
            if name in seen:
                errors.append(f"duplicate skill name '{name}': defined in both '{seen[name]}' and '{plugin_dir.name}'")
            else:
                seen[name] = plugin_dir.name
    return errors


def validate_marketplace(*, plugin_dirs: list[Path]) -> list[str]:
    marketplace = load_json(path=MARKETPLACE_FILE)
    errors: list[str] = []

    registered = {p["name"] for p in marketplace["plugins"]}
    on_disk = {d.name for d in plugin_dirs}

    for name in sorted(on_disk - registered):
        errors.append(f"plugin '{name}' exists on disk but is not in marketplace.json")
    for name in sorted(registered - on_disk):
        errors.append(f"plugin '{name}' is in marketplace.json but has no directory")

    for entry in marketplace["plugins"]:
        name = entry["name"]
        source = entry["source"]
        expected_source = f"./plugins/{name}"
        if source != expected_source:
            errors.append(f"marketplace '{name}': source '{source}' does not match expected '{expected_source}'")
        if name not in on_disk:
            continue
        manifest = load_json(path=PLUGINS_DIR / name / "manifest.json")
        if entry["name"] != manifest["name"]:
            errors.append(f"marketplace '{name}': name mismatch with manifest")
        if entry["version"] != manifest["version"]:
            errors.append(f"marketplace '{name}': version '{entry['version']}' != manifest version '{manifest['version']}'")

    return errors


def main() -> int:
    schema = load_json(path=SCHEMA_FILE)
    plugin_dirs = sorted(
        d for d in PLUGINS_DIR.iterdir()
        if d.is_dir() and (d / "manifest.json").exists()
    )

    if not plugin_dirs:
        print("ERROR: no plugins found")
        return 1

    all_errors: list[str] = []
    for plugin_dir in plugin_dirs:
        all_errors.extend(validate_manifest_schema(plugin_dir=plugin_dir, schema=schema))
        all_errors.extend(validate_directory_name(plugin_dir=plugin_dir))
        all_errors.extend(validate_file_references(plugin_dir=plugin_dir))

    all_errors.extend(validate_duplicate_skill_names(plugin_dirs=plugin_dirs))
    all_errors.extend(validate_marketplace(plugin_dirs=plugin_dirs))

    if all_errors:
        print(f"FAILED: {len(all_errors)} error(s) found\n")
        for error in all_errors:
            print(f"  - {error}")
        return 1

    print(f"OK: {len(plugin_dirs)} plugins validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
