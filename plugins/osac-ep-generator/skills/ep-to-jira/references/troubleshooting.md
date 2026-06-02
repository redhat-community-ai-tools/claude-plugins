# EP-to-Jira Troubleshooting

## Jira CLI not authenticated
**Symptom:** `jira me` fails with "Not authenticated" or "401 Unauthorized"

**Solution:** User needs to run `jira init` to configure authentication:
```bash
jira init
# Follow prompts to:
# 1. Enter Jira instance URL (e.g., https://issues.redhat.com)
# 2. Choose authentication method (usually "Browser" for SSO)
# 3. Complete authentication in browser
```

## Epic creation fails with project error
**Symptom:** `jira epic create` fails with "Project MGMT not found" or "Invalid project key"

**Solution:** Verify project key with `jira project list`. If MGMT doesn't exist, check with team for correct project key.

## Sub-task type not found
**Symptom:** `jira issue create --type Task` fails with "Issue type not found"

**Solution:** Try alternative type names:
- `--type "Sub-task"` (with hyphen and capital S)
- `--type Story` (if project doesn't support sub-tasks)
- Check available types: `jira issue types --project MGMT`

## rg type proto not recognized
**Symptom:** `rg --type proto` fails with "Type not recognized"

**Solution:** Use glob pattern as alternative:
```bash
rg --glob "*.proto" "<pattern>" --files-with-matches
```

## EP file not found
**Symptom:** Cannot find enhancement proposal at expected path

**Solution:** 
- Check if EP is in different directory structure
- Search for EP: `find enhancement-proposals/ -name "README.md" -path "*<slug>*"`
- Ask user to provide full path to EP file

## Codebase exploration returns too many results
**Symptom:** `rg` searches return hundreds of matches, overwhelming output

**Solution:**
- Use `--files-with-matches` (or `-l`) to show only filenames, not content
- Limit search to specific directories: `rg "<pattern>" osac-operator/ --type go -l`
- Use `head -20` to limit output: `rg "<pattern>" -l | head -20`

## Dependency mapping shows no results
**Symptom:** All dependency checks return empty (but EP clearly adds new resources)

**Solution:**
- This is expected for brand-new resources (no existing code to find)
- Flag as "New resource - no existing dependencies" in dependency map
- Focus on which repos WILL be affected (from EP's Proposal section)
