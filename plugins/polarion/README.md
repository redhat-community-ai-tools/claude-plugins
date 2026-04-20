# Polarion Test Management Plugin

Manage Polarion test cases for OpenShift Extended Testing on Red Hat's Polarion ALM instance (polarion.engineering.redhat.com).

## Features

### Test Case Management
- Create test cases with title, description, severity, status, and optional test steps
- Search test cases using Lucene query syntax
- Update test case attributes (title, description, severity, status)
- Get test case details in JSON format

### Test Step Management
- Add/update test steps with automatic backup
- Restore test steps from backup files
- Auto-delete existing steps (handles Polarion REST API limitation)
- Preserve step ordering via numeric index extraction

### Safety Features
- Automatic backup to `/tmp/polarion-backup-OCP-XXXXX-steps.json` before modifying test steps
- Auto-delete loop that handles Polarion's step renumbering
- Restore command with step ordering preservation
- Clean error messages without SOAP API references

### CLI Wrapper
- Python-based CLI wrapping Polarion MCP server
- Commands: `test-connection`, `create`, `get`, `search`, `update`, `add-test-steps`, `restore-test-steps`
- JSON output for easy parsing with jq
- SSL warning suppression for internal Red Hat Polarion instance

## Installation

### Prerequisites

1. **polarion-mcp-server**
   ```bash
   git clone https://github.com/redhat-community-ai-tools/polarion-mcp-server.git
   cd polarion-mcp-server
   pip install -r requirements.txt
   ```

2. **Python 3** with libraries:
   - `requests`
   - `urllib3`

3. **jq** (optional, for parsing JSON output)
   ```bash
   # macOS
   brew install jq
   
   # RHEL/Fedora
   sudo dnf install jq
   ```

### Install Plugin

```bash
# Add marketplace
claude plugin marketplace add https://github.com/redhat-community-ai-tools/claude-plugins

# Install plugin
claude plugin install polarion
```

## Configuration

Set environment variables for authentication:

```bash
export POLARION_URL="https://polarion.engineering.redhat.com"
export POLARION_PROJECT="OSE"
export POLARION_TOKEN="your-personal-access-token"
```

### SSL Certificate Configuration

SSL verification is enabled by default for security. If you encounter certificate errors with self-signed certificates or internal servers:

**Option 1: Install the CA certificate (recommended)**
```bash
export POLARION_CA_CERT="/path/to/ca-cert.pem"
```

**Option 2: Disable SSL verification (development only)**
```bash
export POLARION_VERIFY_SSL="false"
```

**Note:** Disabling SSL verification should only be used in trusted development environments, never in production.

### Getting a Personal Access Token

1. Navigate to https://polarion.engineering.redhat.com/polarion/#/userSettings?settings=tokens
2. Click "Create New Token"
3. Copy the token and set it as `POLARION_TOKEN`

## Usage

### Create Test Case

```bash
# Basic test case
polarion-cli create \
  --title "Verify CAPI windows-user-data secret synchronization" \
  --description "Verify that the windows-user-data secret appears in both openshift-machine-api and openshift-cluster-api namespaces with identical content" \
  --severity should_have \
  --status draft

# With test steps
polarion-cli create \
  --title "Test case title" \
  --description "Test description" \
  --test-steps "Step 1: Setup environment
Step 2: Execute test
Step 3: Verify results
Step 4: Clean up" \
  --expected-results "Environment ready
Test executed successfully
Results match expected
Resources cleaned" \
  --severity must_have
```

### Add/Update Test Steps

```bash
# Add test steps (automatically backs up and replaces existing steps)
polarion-cli add-test-steps OCP-32615 \
  --test-steps "Step 1: Create test namespace
Step 2: Deploy test workload
Step 3: Verify functionality
Step 4: Patch secret with invalid data
Step 5: Verify secret is rejected
Step 6: Restore valid secret
Step 7: Clean up resources" \
  --expected-results "Namespace created
Workload deployed
Feature works correctly
Invalid data rejected
Secret restored
Resources removed"
```

**Automatic Features:**
- Backs up existing steps to `/tmp/polarion-backup-OCP-XXXXX-steps.json`
- Deletes existing steps (Polarion REST API requirement)
- Preserves step ordering

### Restore Test Steps

```bash
# Restore from backup
polarion-cli restore-test-steps /tmp/polarion-backup-OCP-32615-steps.json
```

### Search Test Cases

```bash
# Text search
polarion-cli search "windows CAPI"

# Lucene query syntax
polarion-cli search "title:windows AND description:secret" --limit 20
polarion-cli search "severity:must_have AND status:approved"
```

### Get Test Case Details

```bash
# Get full details
polarion-cli get OCP-32615

# Parse with jq
polarion-cli get OCP-32615 | jq -r '.title'
polarion-cli get OCP-32615 | jq -r '.url'
```

### Update Test Case

```bash
# Update multiple fields
polarion-cli update OCP-32615 \
  --title "Updated title" \
  --description "Updated description" \
  --severity must_have \
  --status approved
```

## Workflow: Converting JIRA Bugs to Test Cases

1. Get JIRA bug details
2. Create Polarion test case
3. Extract test case ID (OCP-XXXXX)
4. Add test steps
5. Update automation code with test case ID

Example:

```bash
# Create test case from JIRA bug
TEST_ID=$(polarion-cli create \
  --title "$(jira issue view OCPBUGS-38401 --plain | grep Summary)" \
  --description "Test for OCPBUGS-38401" \
  --severity should_have | jq -r '.test_case_id')

# Add test steps
polarion-cli add-test-steps $TEST_ID \
  --test-steps "Step 1: Verify secret in Machine API namespace
Step 2: Verify secret in CAPI namespace
Step 3: Compare secret content" \
  --expected-results "Secret exists in Machine API
Secret exists in CAPI
Content is identical"

# Use in automation
echo "Created test case: $TEST_ID"
```

## Skills

This plugin provides one skill:

### polarion-test-management

Manage test cases on Polarion ALM — create, search, update test cases and test steps. Includes guidance for OpenShift Extended Testing workflow.

See [skills/polarion-test-management/SKILL.md](skills/polarion-test-management/SKILL.md) for detailed documentation.

## Technical Details

### Polarion REST API Limitations

Polarion's REST API can only POST test steps to test cases that have NO existing steps. The plugin handles this by:

1. Auto-backing up existing steps before modification
2. Auto-deleting existing steps in a loop (handles step renumbering)
3. Adding new steps via POST
4. Preserving order via index extraction from step IDs

### Step Ordering

Step IDs in Polarion have format `OSE/OCP-32615/1` where the last number is the index. The restore command:
1. Extracts numeric index from each step ID
2. Sorts steps by index
3. Restores in correct order

### Auto-Delete Loop

Polarion renumbers steps after each deletion (1,2,3,4 → delete 1 → remaining become 1,2,3). The plugin loops up to 20 times to ensure all steps are removed before adding new ones.

## Troubleshooting

```bash
# Test connection
polarion-cli test-connection

# Verify token
echo $POLARION_TOKEN

# Check if token expired (tokens expire after 1 year)
# Regenerate at: https://polarion.engineering.redhat.com/polarion/#/userSettings?settings=tokens
```

## Security Considerations

- Never commit `POLARION_TOKEN` to version control
- Use environment variables or secure vaults
- SSL verification is enabled by default for secure connections
- Limit token permissions to minimum required

## Common Errors

- **"POLARION_TOKEN environment variable not set"**: Export your token
- **"Authentication failed"**: Token expired or invalid — regenerate
- **"SSL certificate verify failed"**: Configure POLARION_CA_CERT or POLARION_VERIFY_SSL (see SSL Certificate Configuration)
- **"REST API failed: already contains Test Steps"**: Should not occur with add-test-steps auto-delete. If it does, use restore-test-steps
- **"Backup file not found"**: Backup is only created if test case has existing steps

## Output Format

All commands return JSON:

```json
{
  "status": "success",
  "test_case_id": "OCP-32615",
  "title": "Test case title",
  "url": "https://polarion.engineering.redhat.com/polarion/#/project/OSE/workitem?id=OCP-32615"
}
```

Use jq to parse:
```bash
TEST_ID=$(polarion-cli create ... | jq -r '.test_case_id')
URL=$(polarion-cli get OCP-32615 | jq -r '.url')
```

## Dependencies

- [polarion-mcp-server](https://github.com/redhat-community-ai-tools/polarion-mcp-server) — REST API client library
- Python 3 — Runtime for polarion-cli
- requests, urllib3 — HTTP client libraries

## Related

- Polarion MCP Server: https://github.com/redhat-community-ai-tools/polarion-mcp-server
- OpenShift Extended Tests: https://github.com/openshift/openshift-tests-private
- Red Hat Polarion: https://polarion.engineering.redhat.com
