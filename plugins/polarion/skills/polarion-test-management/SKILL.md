---
name: polarion-test-management
description: Manage Polarion test cases and test runs for OpenShift Extended Testing on Polarion ALM (polarion.engineering.redhat.com). Use this skill when the user mentions Polarion test cases, test runs, OCP-XXXXX IDs, creating test cases, importing test results from Excel/CSV, updating test run status, or converting bugs/features into test cases.
---

# Polarion Test Management

Manage test cases and test runs on Red Hat Polarion ALM (`polarion.engineering.redhat.com/polarion/#/project/OSE`) via `polarion-cli`. This tool is designed for OpenShift Extended Testing (OSE project).

## Setup

- **Binary:** `polarion-cli` (located in this plugin's directory)
- **Config:** Environment variables for authentication
- **Auth:** Personal Access Token in `POLARION_TOKEN` environment variable
- **Token generation:** https://polarion.engineering.redhat.com/polarion/#/userSettings?settings=tokens
- **Default project:** OSE (OpenShift Extended Testing)
- **URL pattern:** `https://polarion.engineering.redhat.com/polarion/#/project/OSE/workitem?id=OCP-12345`

## Environment Variables

```bash
export POLARION_URL="https://polarion.engineering.redhat.com"
export POLARION_PROJECT="OSE"
export POLARION_TOKEN="your-personal-access-token"
export POLARION_VERIFY_SSL="false"
```

## Command Reference

All commands use the `polarion-cli` wrapper which calls the Polarion MCP server.

### Test Connection

```bash
# Verify authentication and connectivity
polarion-cli test-connection
polarion-cli test-connection --project OSE
```

### Create Test Case

```bash
# Basic test case creation
polarion-cli create \
  --title "Verify CAPI windows-user-data secret in both namespaces" \
  --description "Verify that the windows-user-data secret appears in both openshift-machine-api and openshift-cluster-api namespaces with identical content" \
  --severity should_have \
  --status draft

# With test steps and expected results
polarion-cli create \
  --title "Test case title" \
  --description "Detailed description of what this test validates" \
  --test-steps "Step 1: Do something
Step 2: Verify result
Step 3: Clean up" \
  --expected-results "Expected outcome 1
Expected outcome 2" \
  --severity must_have \
  --status approved \
  --project OSE
```

**Severity levels:**
- `must_have` - Critical functionality, blocker
- `should_have` - Important functionality
- `nice_to_have` - Enhancement, not critical
- `will_not_have` - Deferred

**Common statuses:**
- `draft` - Initial state, not ready for review
- `approved` - Ready for automation/execution
- `inactive` - Deprecated or no longer relevant

### Get Test Case

```bash
# Retrieve test case details
polarion-cli get OCP-12345
polarion-cli get OCP-12345 --project OSE

# Output is JSON - use jq for parsing
polarion-cli get OCP-12345 | jq -r '.title'
polarion-cli get OCP-12345 | jq -r '.description'
```

### Search Test Cases

```bash
# Search by text
polarion-cli search "windows CAPI"
polarion-cli search "user-data secret" --limit 20

# Lucene query syntax examples
polarion-cli search "title:windows AND description:CAPI"
polarion-cli search "severity:must_have AND status:approved"
polarion-cli search "author:rrasouli@redhat.com"

# Parse results with jq
polarion-cli search "windows" | jq -r '.test_cases[] | .id + ": " + .title'
```

### Update Test Case

```bash
# Update title
polarion-cli update OCP-12345 --title "New title"

# Update description
polarion-cli update OCP-12345 --description "Updated description"

# Update severity
polarion-cli update OCP-12345 --severity must_have

# Update status
polarion-cli update OCP-12345 --status approved

# Multiple fields at once
polarion-cli update OCP-12345 \
  --title "Updated title" \
  --description "Updated description" \
  --severity should_have \
  --status approved
```

### Add Test Steps

Add or update test steps for a test case. This command automatically backs up existing steps and replaces them with new ones.

```bash
# Add test steps (automatically backs up and replaces existing steps)
polarion-cli add-test-steps OCP-12345 \
  --test-steps "Step 1: Create namespace
Step 2: Deploy test workload
Step 3: Verify functionality
Step 4: Clean up" \
  --expected-results "Namespace created successfully
Workload deployed
Feature works as expected
Resources cleaned up"

# Steps without expected results (defaults to empty)
polarion-cli add-test-steps OCP-12345 \
  --test-steps "Step 1: Setup
Step 2: Execute
Step 3: Verify"
```

**Automatic Features:**
- Backs up existing test steps to `/tmp/polarion-backup-OCP-XXXXX-steps.json` before modification
- Automatically deletes existing steps (Polarion REST API requirement)
- Preserves step ordering via numeric indices
- Creates backup only if test case has existing steps

**Backup File Format:**
```json
{
  "test_case_id": "OCP-12345",
  "project_id": "OSE",
  "steps": [
    {
      "id": "OSE/OCP-12345/1",
      "attributes": {
        "keys": ["step", "expectedResult"],
        "values": [
          {"type": "text/html", "value": "Step 1 text"},
          {"type": "text/html", "value": "Expected result 1"}
        ]
      }
    }
  ]
}
```

### Restore Test Steps

Restore test steps from a backup file created by `add-test-steps`.

```bash
# Restore from backup
polarion-cli restore-test-steps /tmp/polarion-backup-OCP-12345-steps.json

# Restore with explicit project
polarion-cli restore-test-steps /tmp/polarion-backup-OCP-12345-steps.json --project OSE
```

**Features:**
- Automatically deletes current test steps before restoring
- Preserves original step order from backup
- Validates backup file format
- Safe to run multiple times (idempotent)

**Recovery Workflow Example:**
```bash
# 1. Accidentally overwrote test steps
polarion-cli add-test-steps OCP-12345 --test-steps "Wrong step"

# 2. Restore from automatic backup
polarion-cli restore-test-steps /tmp/polarion-backup-OCP-12345-steps.json

# 3. Verify restoration
polarion-cli get OCP-12345
```

## Test Run Management

For test run creation, result updates, status checks, and Excel import, see `references/test-runs.md`.

## Workflow: Creating Test Cases from JIRA Bugs

When converting a JIRA bug (e.g., OCPBUGS-38401) into a Polarion test case:

1. **Extract information from JIRA:**
   - Bug summary → Test case title
   - Bug description → Test case description
   - Acceptance criteria → Expected results

2. **Create test case:**
   ```bash
   polarion-cli create \
     --title "Verify windows-user-data secret in both Machine API and CAPI" \
     --description "Verify that windows-user-data secret exists in both openshift-machine-api and openshift-cluster-api namespaces and contains identical userData content" \
     --severity should_have \
     --status draft
   ```

3. **Extract the OCP-XXXXX ID from the output:**
   ```bash
   TEST_ID=$(polarion-cli create ... | jq -r '.test_case_id')
   echo "Created test case: $TEST_ID"
   ```

4. **Update test automation code with the test case ID**

## Best Practices

1. **Test case titles** should be clear and describe what is being verified
   - Good: "Verify CAPI windows-user-data secret synchronization"
   - Bad: "Test CAPI feature"

2. **Descriptions** should include:
   - What is being tested
   - Why it's important (link to bug/feature)
   - Prerequisites (cluster configuration, features enabled)

3. **Test steps** should be:
   - Sequential and numbered
   - Actionable (commands or UI steps)
   - Reproducible by any tester

4. **Expected results** should match each test step when applicable

5. **Always link to related bugs/features:**
   - Include JIRA ticket numbers (OCPBUGS-XXXXX, WINC-XXXX)
   - Include GitHub PR links
   - Reference design documents

## Integration with OpenShift Extended Tests

When creating automated tests in `openshift-tests-private`:

1. Create Polarion test case first
2. Get the OCP-XXXXX ID
3. Use it in the test name: `g.It("Author:username-Priority-12345-Description")`
4. Link test case in PR description

Example:
```go
// Polarion test case: OCP-12345
g.It("Author:rrasouli-Critical-12345-Verify windows-user-data in CAPI and Machine API [Serial]", func() {
    // Test implementation
})
```

## Troubleshooting

```bash
# Test connection if commands fail
polarion-cli test-connection

# Verify token is set
echo $POLARION_TOKEN

# Check if token has expired
# Tokens expire after 1 year - regenerate at:
# https://polarion.engineering.redhat.com/polarion/#/userSettings?settings=tokens
```

## Common Errors

- **"POLARION_TOKEN environment variable not set"**: Export your token
- **"Authentication failed"**: Token expired or invalid - regenerate
- **"Project OSE not found"**: Check --project flag or POLARION_PROJECT env var
- **"Test case not found"**: Verify the OCP-XXXXX ID is correct
- **"REST API failed: already contains Test Steps"**: Should not occur - add-test-steps auto-deletes existing steps. If it does, check backup file and restore
- **"Backup file not found"**: add-test-steps only creates backups if test case has existing steps. For new test cases, no backup is created

## Output Format

All commands return JSON for easy parsing:

```json
{
  "status": "created",
  "test_case_id": "OCP-12345",
  "title": "Test case title",
  "url": "https://polarion.engineering.redhat.com/polarion/#/project/OSE/workitem?id=OCP-12345"
}
```

Use `jq` to extract specific fields:
```bash
TEST_ID=$(polarion-cli create ... | jq -r '.test_case_id')
URL=$(polarion-cli get OCP-12345 | jq -r '.url')
```
