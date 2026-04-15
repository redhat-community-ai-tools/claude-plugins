---
name: jira-mcp-management
description: Manage JIRA issues using jira-mcp-server Model Context Protocol integration. Use this skill when you need MCP-based JIRA operations, batch processing, or when jira-cli is insufficient. Provides natural language JIRA interaction through MCP tools.
---

# JIRA MCP Management

Manage JIRA issues on Red Hat JIRA (`redhat.atlassian.net`) via **jira-mcp-server** - a Model Context Protocol server that provides comprehensive JIRA operations to AI assistants.

## Overview

jira-mcp-server is an MCP server that wraps jira-cli functionality and provides additional capabilities for AI-assisted JIRA workflows. It enables natural language interaction with JIRA while maintaining security and auditability.

## Setup

### Prerequisites

1. **jira-mcp-server** must be installed and configured:
   ```bash
   cd ~/Documents/GitHub/jira-mcp-server
   ./setup.sh
   ```

2. **jira-cli** must be configured (jira-mcp-server uses it internally):
   ```bash
   jira init --installation cloud \
     --server https://redhat.atlassian.net \
     --auth-type bearer
   ```

3. **Environment variables:**
   ```bash
   export JIRA_URL="https://redhat.atlassian.net"
   export JIRA_DEFAULT_PROJECT="WINC"
   ```

### MCP Server Configuration

Add to your MCP configuration (`.mcp.json` or Claude Desktop config):

```json
{
  "mcpServers": {
    "jira-prod": {
      "command": "python3",
      "args": ["/Users/username/Documents/GitHub/jira-mcp-server/server.py"],
      "env": {
        "JIRA_URL": "https://redhat.atlassian.net",
        "JIRA_DEFAULT_PROJECT": "WINC"
      }
    }
  }
}
```

## Available MCP Tools

The jira-mcp-server provides these tools (accessible when MCP server is running):

### Issue Operations
- `get_jira` - Get issue details by key
- `create_issue` - Create new issue (Story, Task, Bug, Epic, Sub-task)
- `edit_issue` - Update issue fields
- `transition_issue` - Move issue through workflow
- `delete_issue` - Delete an issue (use with caution)

### Search & Discovery
- `search_issues` - JQL-based issue search
- `search_users` - Find users by query

### Project Operations
- `list_projects` - List all accessible projects
- `get_project` - Get project details
- `get_project_components` - List project components
- `get_project_versions` - List project versions

### Issue Relationships
- `link_issues` - Link two issues (blocks, relates to, duplicates)
- `create_issue_link` - Create specific link types

### Comments & Attachments
- `add_comment` - Add comment to issue
- `get_comments` - Retrieve issue comments

### Batch Operations
- `close_multiple_issues` - Close multiple issues at once
- `bulk_transition` - Transition multiple issues

## Usage Patterns

### When to Use MCP vs. jira-cli

**Use jira-mcp-server (MCP) when:**
- You need AI-assisted natural language interaction
- Working in Claude Desktop or Claude Code with MCP enabled
- Batch processing multiple issues
- Complex workflows requiring decision-making

**Use jira-cli directly when:**
- Simple, one-off commands
- Shell scripting
- CI/CD pipelines
- When MCP server is not available

### Common Workflows

#### Create Issue via MCP

When MCP is available, you can use natural language:
```
"Create a Task in WINC project titled 'Fix Windows node drain issue' 
linked to epic WINC-1234 with label 'bug-fix'"
```

The MCP server translates this to appropriate API calls.

#### Search and Bulk Operations

```
"Find all open bugs in WINC assigned to me and transition them to 'In Progress'"
```

The MCP server will:
1. Search using JQL: `project = WINC AND type = Bug AND status = Open AND assignee = currentUser()`
2. Iterate through results
3. Transition each issue

#### Issue Linking

```
"Link WINC-1234 as blocked by WINC-5678"
```

Translates to: `link_issues(inward="WINC-1234", outward="WINC-5678", type="Blocks")`

## CLI Wrapper

For command-line usage without MCP client, use `jira-mcp-cli`:

```bash
# Get issue
jira-mcp-cli get WINC-1234

# Search issues
jira-mcp-cli search "project = WINC AND status = Open"

# Create issue
jira-mcp-cli create \
  --type Task \
  --summary "Fix bug in Windows node drain" \
  --description "Description here" \
  --epic WINC-1234 \
  --labels bug-fix,windows

# Update issue
jira-mcp-cli update WINC-1234 \
  --summary "Updated summary" \
  --assignee username

# Transition issue
jira-mcp-cli transition WINC-1234 "In Progress" \
  --comment "Starting work on this"

# Link issues
jira-mcp-cli link WINC-1234 WINC-5678 blocks
```

## Integration with Development Workflows

### Converting Bugs to Test Cases

When you have a JIRA bug and need to create a Polarion test case:

1. Get bug details: `get_jira(issue_key="OCPBUGS-38401")`
2. Extract relevant information
3. Create Polarion test case with the information
4. Link back to JIRA bug in test case description

### Automated Issue Management

Create issues from test failures, link to PRs, update based on CI results:

```bash
# Example: Create bug from test failure
jira-mcp-cli create \
  --type Bug \
  --summary "Test OCP-88728 failed in CI" \
  --description "Test failure details..." \
  --labels ci-failure,windows \
  --epic WINC-1650
```

## Best Practices

1. **Use JQL for complex searches** - More powerful than simple keyword search
2. **Always specify epic links** - Required for proper issue organization
3. **Use consistent labels** - Makes filtering and reporting easier
4. **Transition with comments** - Provide context for status changes
5. **Verify before bulk operations** - Test JQL queries before mass updates

## Troubleshooting

### MCP Server Not Responding

```bash
# Check if jira-cli is configured
jira me

# Verify MCP server is accessible
curl -X POST http://localhost:PORT/mcp/tools

# Check MCP logs in Claude Desktop
```

### Authentication Issues

```bash
# Verify jira-cli authentication
jira issue list --jql "project = WINC" --plain

# Check bearer token in ~/.netrc
cat ~/.netrc | grep redhat.atlassian.net
```

### JQL Errors

- Use single quotes around JQL string
- Escape double quotes in field values: `'status = "In Progress"'`
- Test JQL in JIRA web UI first

## Reference

- **jira-mcp-server**: https://github.com/redhat-community-ai-tools/jira-mcp-server
- **jira-cli**: https://github.com/ankitpokhrel/jira-cli
- **MCP Protocol**: https://modelcontextprotocol.io
- **Red Hat JIRA**: https://redhat.atlassian.net
- **JQL Reference**: https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/

## Examples

### Create Story with Full Details

```bash
jira-mcp-cli create \
  --type Story \
  --summary "Implement CAPI support for Windows nodes" \
  --description "Add Cluster API support for managing Windows worker nodes" \
  --epic WINC-1650 \
  --labels enhancement,capi \
  --assignee rrasouli
```

### Bulk Close Duplicate Issues

Via MCP natural language:
```
"Search for all issues in WINC with label 'duplicate' and status 'Open', 
then close them all as 'Duplicate' with comment 'Closing as duplicate of WINC-1234'"
```

### Weekly Status Report

```
"Find all issues in WINC that were completed this week (updated >= -7d AND status = Done)
and create a summary report"
```

The MCP server will search, aggregate, and format the results.
