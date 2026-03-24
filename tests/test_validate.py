#!/usr/bin/env python3
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import validate

SCHEMA = validate.load_json(path=REPO_ROOT / "plugin-schema.json")

GOOD_FRONTMATTER = """---
name: test-skill
description: A test skill for validation purposes
---

# Test Skill
This is a test.
"""

GOOD_MANIFEST: dict[str, Any] = {
    "name": "test-plugin",
    "version": "1.0.0",
    "description": "A test plugin for validation",
    "author": {"name": "Test Author"},
    "skills": [
        {
            "name": "test-skill",
            "path": "skills/test-skill/SKILL.md",
            "description": "A test skill for validation purposes",
            "tags": ["test"],
        }
    ],
    "license": "MIT",
    "categories": ["Developer Tools"],
}


def make_plugin(
    *,
    tmp: Path,
    name: str,
    manifest: dict[str, Any],
    skills: dict[str, str] | None = None,
    commands: dict[str, str] | None = None,
) -> Path:
    plugin_dir = tmp / "plugins" / name
    plugin_dir.mkdir(parents=True, exist_ok=True)
    (plugin_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    for files in (skills, commands):
        if not files:
            continue
        for path, content in files.items():
            full = plugin_dir / path
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content)
    return plugin_dir


class Results:
    def __init__(self) -> None:
        self.passed: int = 0
        self.failed: int = 0
        self.details: list[str] = []

    def expect_errors(self, *, name: str, errors: list[str], containing: str) -> None:
        if not errors:
            self.failed += 1
            self.details.append(f"  FAIL: {name} — expected errors but got none")
            return
        if not any(containing in e for e in errors):
            self.failed += 1
            self.details.append(f"  FAIL: {name} — expected '{containing}' in: {errors}")
            return
        self.passed += 1
        self.details.append(f"  PASS: {name} — {errors}")

    def expect_clean(self, *, name: str, errors: list[str]) -> None:
        if errors:
            self.failed += 1
            self.details.append(f"  FAIL: {name} — expected clean but got: {errors}")
            return
        self.passed += 1
        self.details.append(f"  PASS: {name}")


def test_real_plugins(*, results: Results) -> None:
    plugins_dir = REPO_ROOT / "plugins"
    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not (plugin_dir / "manifest.json").exists():
            continue
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        errors.extend(validate.validate_file_references(plugin_dir=plugin_dir))
        results.expect_clean(name=f"real:{plugin_dir.name}", errors=errors)


def test_good_plugin(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        plugin_dir = make_plugin(tmp=Path(tmp), name="test-plugin", manifest=GOOD_MANIFEST,
                                 skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        errors.extend(validate.validate_file_references(plugin_dir=plugin_dir))
        results.expect_clean(name="good-plugin", errors=errors)


def test_missing_name(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {k: v for k, v in GOOD_MANIFEST.items() if k != "name"}
        plugin_dir = make_plugin(tmp=Path(tmp), name="no-name", manifest=manifest,
                                 skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        results.expect_errors(name="missing-name", errors=errors, containing="'name' is a required property")


def test_missing_version(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {k: v for k, v in GOOD_MANIFEST.items() if k != "version"}
        plugin_dir = make_plugin(tmp=Path(tmp), name="no-version", manifest=manifest,
                                 skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        results.expect_errors(name="missing-version", errors=errors, containing="'version' is a required property")


def test_missing_skills(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {k: v for k, v in GOOD_MANIFEST.items() if k != "skills"}
        plugin_dir = make_plugin(tmp=Path(tmp), name="no-skills", manifest=manifest)
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        results.expect_errors(name="missing-skills", errors=errors, containing="'skills' is a required property")


def test_empty_skills(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {**GOOD_MANIFEST, "skills": []}
        plugin_dir = make_plugin(tmp=Path(tmp), name="empty-skills", manifest=manifest)
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        results.expect_errors(name="empty-skills", errors=errors, containing="non-empty")


def test_bad_version_format(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {**GOOD_MANIFEST, "version": "v1.0"}
        plugin_dir = make_plugin(tmp=Path(tmp), name="bad-version", manifest=manifest,
                                 skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        results.expect_errors(name="bad-version-format", errors=errors, containing="does not match")


def test_bad_name_uppercase(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {**GOOD_MANIFEST, "name": "MyPlugin"}
        plugin_dir = make_plugin(tmp=Path(tmp), name="bad-name", manifest=manifest,
                                 skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        results.expect_errors(name="bad-name-uppercase", errors=errors, containing="does not match")


def test_bad_name_underscore(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {**GOOD_MANIFEST, "name": "my_plugin"}
        plugin_dir = make_plugin(tmp=Path(tmp), name="bad-name-underscore", manifest=manifest,
                                 skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        results.expect_errors(name="bad-name-underscore", errors=errors, containing="does not match")


def test_author_as_string(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {**GOOD_MANIFEST, "author": "Some Author"}
        plugin_dir = make_plugin(tmp=Path(tmp), name="author-string", manifest=manifest,
                                 skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        results.expect_errors(name="author-as-string", errors=errors, containing="is not of type 'object'")


def test_short_description(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {**GOOD_MANIFEST, "description": "hi"}
        plugin_dir = make_plugin(tmp=Path(tmp), name="short-desc", manifest=manifest,
                                 skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        results.expect_errors(name="short-description", errors=errors, containing="too short")


def test_extra_unknown_fields(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {**GOOD_MANIFEST, "banana": True, "secret_config": {"x": 1}}
        plugin_dir = make_plugin(tmp=Path(tmp), name="extra-fields", manifest=manifest,
                                 skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        results.expect_errors(name="extra-unknown-fields", errors=errors, containing="Additional properties")


def test_skill_missing_path(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {**GOOD_MANIFEST, "skills": [{"name": "x", "description": "A skill without a path field"}]}
        plugin_dir = make_plugin(tmp=Path(tmp), name="skill-no-path", manifest=manifest)
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        results.expect_errors(name="skill-missing-path", errors=errors, containing="'path' is a required property")


def test_skill_path_not_md(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {**GOOD_MANIFEST, "skills": [
            {"name": "test-skill", "path": "skills/test.txt", "description": "A test skill with wrong extension"}
        ]}
        plugin_dir = make_plugin(tmp=Path(tmp), name="skill-bad-ext", manifest=manifest,
                                 skills={"skills/test.txt": "content"})
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        results.expect_errors(name="skill-path-not-md", errors=errors, containing="does not match")


def test_skill_name_uppercase(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {**GOOD_MANIFEST, "skills": [
            {"name": "TestSkill", "path": "skills/test/SKILL.md", "description": "A test skill with uppercase name"}
        ]}
        plugin_dir = make_plugin(tmp=Path(tmp), name="skill-upper", manifest=manifest,
                                 skills={"skills/test/SKILL.md": GOOD_FRONTMATTER})
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        results.expect_errors(name="skill-name-uppercase", errors=errors, containing="does not match")


def test_skill_file_missing(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        plugin_dir = make_plugin(tmp=Path(tmp), name="skill-missing-file", manifest=GOOD_MANIFEST)
        errors = validate.validate_file_references(plugin_dir=plugin_dir)
        results.expect_errors(name="skill-file-missing", errors=errors, containing="references missing file")


def test_command_file_missing(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {**GOOD_MANIFEST, "commands": [
            {"name": "test-cmd", "path": ".claude-code/commands/test.md", "description": "test"}
        ]}
        plugin_dir = make_plugin(tmp=Path(tmp), name="cmd-missing-file", manifest=manifest,
                                 skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})
        errors = validate.validate_file_references(plugin_dir=plugin_dir)
        results.expect_errors(name="command-file-missing", errors=errors, containing="references missing file")


def test_frontmatter_missing(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        plugin_dir = make_plugin(tmp=Path(tmp), name="no-frontmatter", manifest=GOOD_MANIFEST,
                                 skills={"skills/test-skill/SKILL.md": "# Just a heading\nNo frontmatter here."})
        errors = validate.validate_file_references(plugin_dir=plugin_dir)
        results.expect_errors(name="frontmatter-missing", errors=errors, containing="missing YAML frontmatter")


def test_frontmatter_no_name(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        plugin_dir = make_plugin(tmp=Path(tmp), name="fm-no-name", manifest=GOOD_MANIFEST,
                                 skills={"skills/test-skill/SKILL.md": "---\ndescription: some description\n---\n# Skill"})
        errors = validate.validate_file_references(plugin_dir=plugin_dir)
        results.expect_errors(name="frontmatter-no-name", errors=errors, containing="frontmatter missing 'name'")


def test_frontmatter_no_description(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        plugin_dir = make_plugin(tmp=Path(tmp), name="fm-no-desc", manifest=GOOD_MANIFEST,
                                 skills={"skills/test-skill/SKILL.md": "---\nname: test-skill\n---\n# Skill"})
        errors = validate.validate_file_references(plugin_dir=plugin_dir)
        results.expect_errors(name="frontmatter-no-description", errors=errors, containing="frontmatter missing 'description'")


def test_frontmatter_unclosed(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        plugin_dir = make_plugin(tmp=Path(tmp), name="fm-unclosed", manifest=GOOD_MANIFEST,
                                 skills={"skills/test-skill/SKILL.md": "---\nname: test\ndescription: test\n# No closing ---"})
        errors = validate.validate_file_references(plugin_dir=plugin_dir)
        results.expect_errors(name="frontmatter-unclosed", errors=errors, containing="unclosed frontmatter")


def test_skill_name_mismatch(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        fm = "---\nname: completely-different-name\ndescription: A mismatched skill\n---\n# Skill"
        plugin_dir = make_plugin(tmp=Path(tmp), name="name-mismatch", manifest=GOOD_MANIFEST,
                                 skills={"skills/test-skill/SKILL.md": fm})
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        errors.extend(validate.validate_file_references(plugin_dir=plugin_dir))
        results.expect_errors(name="skill-name-mismatch", errors=errors, containing="mismatch")


def test_skill_extra_fields(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {**GOOD_MANIFEST, "skills": [
            {"name": "test-skill", "path": "skills/test-skill/SKILL.md",
             "description": "A test skill for validation purposes",
             "descrption": "typo field that should be caught"}
        ]}
        plugin_dir = make_plugin(tmp=Path(tmp), name="skill-extra", manifest=manifest,
                                 skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        results.expect_errors(name="skill-extra-fields", errors=errors, containing="Additional properties")


def test_path_traversal(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {**GOOD_MANIFEST, "skills": [
            {"name": "evil", "path": "../../etc/passwd.md", "description": "A skill with path traversal attack"}
        ]}
        plugin_dir = make_plugin(tmp=Path(tmp), name="path-traversal", manifest=manifest)
        errors = validate.validate_manifest_schema(plugin_dir=plugin_dir, schema=SCHEMA)
        errors.extend(validate.validate_file_references(plugin_dir=plugin_dir))
        results.expect_errors(name="path-traversal", errors=errors, containing="escapes plugin directory")


def test_directory_name_mismatch(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {**GOOD_MANIFEST, "name": "totally-different"}
        plugin_dir = make_plugin(tmp=Path(tmp), name="my-plugin", manifest=manifest,
                                 skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})
        errors = validate.validate_directory_name(plugin_dir=plugin_dir)
        results.expect_errors(name="directory-name-mismatch", errors=errors, containing="does not match manifest name")


def test_directory_name_matches(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        plugin_dir = make_plugin(tmp=Path(tmp), name="test-plugin", manifest=GOOD_MANIFEST,
                                 skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})
        errors = validate.validate_directory_name(plugin_dir=plugin_dir)
        results.expect_clean(name="directory-name-matches", errors=errors)


def test_duplicate_skill_names(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest_a = {**GOOD_MANIFEST, "name": "plugin-a"}
        manifest_b = {**GOOD_MANIFEST, "name": "plugin-b"}
        make_plugin(tmp=tmp_path, name="plugin-a", manifest=manifest_a,
                    skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})
        dir_b = make_plugin(tmp=tmp_path, name="plugin-b", manifest=manifest_b,
                            skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})
        plugin_dirs = [dir_b.parent / "plugin-a", dir_b]
        errors = validate.validate_duplicate_skill_names(plugin_dirs=plugin_dirs)
        results.expect_errors(name="duplicate-skill-names", errors=errors, containing="duplicate skill name")


def test_no_duplicate_skill_names(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest_a = {**GOOD_MANIFEST, "name": "plugin-a", "skills": [
            {"name": "skill-a", "path": "skills/a/SKILL.md", "description": "First skill for testing"}
        ]}
        manifest_b = {**GOOD_MANIFEST, "name": "plugin-b", "skills": [
            {"name": "skill-b", "path": "skills/b/SKILL.md", "description": "Second skill for testing"}
        ]}
        make_plugin(tmp=tmp_path, name="plugin-a", manifest=manifest_a,
                    skills={"skills/a/SKILL.md": "---\nname: skill-a\ndescription: First skill\n---\n# A"})
        dir_b = make_plugin(tmp=tmp_path, name="plugin-b", manifest=manifest_b,
                            skills={"skills/b/SKILL.md": "---\nname: skill-b\ndescription: Second skill\n---\n# B"})
        plugin_dirs = [dir_b.parent / "plugin-a", dir_b]
        errors = validate.validate_duplicate_skill_names(plugin_dirs=plugin_dirs)
        results.expect_clean(name="no-duplicate-skill-names", errors=errors)


def test_marketplace_source_wrong(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        marketplace = {
            "plugins": [{"name": "my-plugin", "source": "./plugins/wrong-dir", "version": "1.0.0"}]
        }
        marketplace_path = tmp_path / ".claude-plugin" / "marketplace.json"
        marketplace_path.parent.mkdir(parents=True)
        marketplace_path.write_text(json.dumps(marketplace))
        plugin_dir = make_plugin(tmp=tmp_path, name="my-plugin", manifest=GOOD_MANIFEST,
                                 skills={"skills/test-skill/SKILL.md": GOOD_FRONTMATTER})

        old_mf = validate.MARKETPLACE_FILE
        old_pd = validate.PLUGINS_DIR
        validate.MARKETPLACE_FILE = marketplace_path
        validate.PLUGINS_DIR = tmp_path / "plugins"
        errors = validate.validate_marketplace(plugin_dirs=[plugin_dir])
        validate.MARKETPLACE_FILE = old_mf
        validate.PLUGINS_DIR = old_pd
        results.expect_errors(name="marketplace-source-wrong", errors=errors, containing="does not match expected")


def test_empty_skill_body(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        plugin_dir = make_plugin(tmp=Path(tmp), name="empty-body", manifest=GOOD_MANIFEST,
                                 skills={"skills/test-skill/SKILL.md": "---\nname: test-skill\ndescription: A skill with no body content\n---\n"})
        errors = validate.validate_file_references(plugin_dir=plugin_dir)
        results.expect_errors(name="empty-skill-body", errors=errors, containing="no content after frontmatter")


def test_skill_body_whitespace_only(*, results: Results) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        plugin_dir = make_plugin(tmp=Path(tmp), name="whitespace-body", manifest=GOOD_MANIFEST,
                                 skills={"skills/test-skill/SKILL.md": "---\nname: test-skill\ndescription: A skill with whitespace only body\n---\n\n   \n\n"})
        errors = validate.validate_file_references(plugin_dir=plugin_dir)
        results.expect_errors(name="skill-body-whitespace-only", errors=errors, containing="no content after frontmatter")


ALL_TESTS = [
    test_real_plugins,
    test_good_plugin,
    test_missing_name,
    test_missing_version,
    test_missing_skills,
    test_empty_skills,
    test_bad_version_format,
    test_bad_name_uppercase,
    test_bad_name_underscore,
    test_author_as_string,
    test_short_description,
    test_extra_unknown_fields,
    test_skill_missing_path,
    test_skill_path_not_md,
    test_skill_name_uppercase,
    test_skill_file_missing,
    test_command_file_missing,
    test_frontmatter_missing,
    test_frontmatter_no_name,
    test_frontmatter_no_description,
    test_frontmatter_unclosed,
    test_skill_name_mismatch,
    test_skill_extra_fields,
    test_path_traversal,
    test_directory_name_mismatch,
    test_directory_name_matches,
    test_duplicate_skill_names,
    test_no_duplicate_skill_names,
    test_marketplace_source_wrong,
    test_empty_skill_body,
    test_skill_body_whitespace_only,
]


def main() -> int:
    results = Results()
    for test in ALL_TESTS:
        test(results=results)

    for d in results.details:
        print(d)
    print(f"\n{results.passed} passed, {results.failed} failed")
    return 1 if results.failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
