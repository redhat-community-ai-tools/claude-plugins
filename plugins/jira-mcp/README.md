# JIRA MCP Plugin

AI-assisted JIRA issue management via Model Context Protocol (MCP) for Red Hat JIRA (redhat.atlassian.net).

## Overview

This plugin provides **natural language JIRA interaction** through the jira-mcp-server Model Context Protocol implementation. It's designed for AI-assisted workflows, batch operations, and complex decision-making scenarios.

### When to Use This Plugin

**Use `jira-mcp` when:**
- Working with Claude Desktop or Claude Code with MCP server enabled
- Need AI-assisted natural language interaction ("Find all open bugs assigned to me and close them")
- Batch processing multiple issues with decision logic
- Complex workflows requiring context and decision-making
- Real-time MCP-based JIRA integration

**Use `jira` plugin instead when:**
- Simple, one-off CLI commands
- Shell scripting and automation
- CI/CD pipelines
- MCP server is not available
- Traditional command-line workflows

## Key Differences: jira vs jira-mcp

| Feature | jira (CLI-based) | jira-mcp (MCP-based) |
|---------|------------------|----------------------|
| **Approach** | Direct jira-cli commands | MCP server + AI integration |
| **Best for** | Scripts, CI/CD, one-off commands | Interactive AI workflows |
| **Setup** | jira-cli only | jira-cli + jira-mcp-server |
| **Natural Language** | No | Yes (via MCP) |
| **Batch Operations** | Manual loops | AI-assisted batch processing |
| **Context Awareness** | None | Full conversation context |
| **Skills** | 5 advanced skills (status reports, triage, etc.) | 1 core skill (MCP management) |

**Both plugins can coexist** - install the one that matches your workflow, or install both for different use cases.

## Features

### MCP Server Integration
- Natural language JIRA interaction
- Context-aware issue management
- AI-assisted decision-making for bulk operations
- Real-time MCP tool invocation

### CLI Wrapper
- `jira-mcp-cli` for command-line usage without MCP client
- Direct REST API calls with basic auth
- Same commands available in both MCP and CLI modes

### Issue Operations
- Create, read, update, delete issues
- Transition issues through workflow
- Link issues with various relationship types
- Add comments and manage attachments

### Search & Discovery
- JQL-based issue search
- User lookup and project browsing
- Component and version management

### Batch Operations
- Close multiple issues at once
- Bulk transition workflows
- AI-guided mass updates

## Installation

### Prerequisites

1. **jira-mcp-server**
   ```bash
   git clone https://github.com/redhat-community-ai-tools/jira-mcp-server.git
   cd jira-mcp-server
   ./setup.sh
   ```

2. **jira-cli** (required by jira-mcp-server)
   ```bash
   go install github.com/ankitpokhrel/jira-cli/cmd/jira@latest
   
   # Configure for Red Hat JIRA
   jira init --installation cloud \
     --server https://redhat.atlassian.net \
     --auth-type bearer
   ```

3. **Python 3** with libraries (for jira-mcp-cli)

### Install Plugin

```bash
# Add marketplace
claude plugin marketplace add https://github.com/redhat-community-ai-tools/claude-plugins

# Install plugin
claude plugin install jira-mcp
```

## Configuration

### Environment Variables

```bash
export JIRA_URL="https://redhat.atlassian.net"
export JIRA_DEFAULT_PROJECT="WINC"
export JIRA_USER="your-email@redhat.com"
export JIRA_API_TOKEN="your-api-token"
```

Get your API token from: https://id.atlassian.com/manage-profile/security/api-tokens

### MCP Server Configuration

Add to `.mcp.json` (Claude Code) or `claude_desktop_config.json` (Claude Desktop):

```json
{
  "mcpServers": {
    "jira-prod": {
      "command": "python3",
      "args": ["/path/to/jira-mcp-server/server.py"],
      "env": {
        "JIRA_URL": "https://redhat.atlassian.net",
        "JIRA_DEFAULT_PROJECT": "WINC",
        "JIRA_USER": "your-email@redhat.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Usage

### Natural Language (via MCP)

When MCP server is running, use natural language:

```
"Create a Task in WINC project titled 'Fix Windows node drain issue' 
linked to epic WINC-1234 with label bug-fix"

"Find all open bugs in WINC assigned to me and transition them to In Progress"

"Link WINC-1234 as blocked by WINC-5678"
```

Claude will translate these to appropriate MCP tool calls.

### CLI Commands (jira-mcp-cli)

For direct command-line usage:

```bash
# Get issue details
jira-mcp-cli get WINC-1234

# Search issues
jira-mcp-cli search "project = WINC AND status = Open"

# Create issue
jira-mcp-cli create \
  --type Task \
  --summary "Fix bug in Windows node drain" \
  --description "Detailed description" \
  --labels bug-fix,windows \
  --assignee username

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

## Skills

This plugin provides one skill:

### jira-mcp-management

AI-assisted JIRA issue management through MCP integration. Enables natural language interaction, batch operations, and context-aware workflows.

See [skills/jira-mcp-management/SKILL.md](skills/jira-mcp-management/SKILL.md) for detailed documentation.

## Workflows

### Bug to Test Case Conversion

```
1. Get bug details: "Show me details of OCPBUGS-38401"
2. Create test case in Polarion with extracted information
3. Link back to JIRA bug in test case description
```

### Bulk Issue Management

```
"Find all issues in WINC with label 'duplicate' and status 'Open', 
then close them all as Duplicate with comment 'Closing as duplicate of WINC-1234'"
```

### Weekly Status Report

```
"Find all issues in WINC completed this week (updated >= -7d AND status = Done) 
and create a summary report"
```

## MCP Tools Available

When MCP server is running, these tools are available to Claude:

- `get_jira` - Get issue details
- `create_issue` - Create new issue
- `edit_issue` - Update issue fields
- `transition_issue` - Move through workflow
- `delete_issue` - Delete issue
- `search_issues` - JQL search
- `search_users` - User lookup
- `list_projects` - Project browsing
- `get_project_components` - Component listing
- `get_project_versions` - Version listing
- `link_issues` - Issue linking
- `add_comment` - Comment management
- `close_multiple_issues` - Bulk close
- `bulk_transition` - Bulk status change

## Troubleshooting

### MCP Server Not Responding

```bash
# Check jira-cli is configured
jira me

# Verify bearer token in ~/.netrc
cat ~/.netrc | grep redhat.atlassian.net

# Test jira-cli directly
jira issue list --jql "project = WINC" --plain
```

### CLI Authentication Issues

```bash
# Verify environment variables
echo $JIRA_USER
echo $JIRA_API_TOKEN

# Test API access
curl -u "$JIRA_USER:$JIRA_API_TOKEN" \
  https://redhat.atlassian.net/rest/api/2/myself
```

### JQL Query Errors

- Use single quotes around JQL string
- Escape double quotes in field values: `'status = "In Progress"'`
- Test JQL in JIRA web UI first: https://redhat.atlassian.net

## Best Practices

1. **Use JQL for complex searches** - More powerful than keyword search
2. **Always specify epic links** - Required for proper issue organization (WINC team standard)
3. **Use consistent labels** - Makes filtering and reporting easier
4. **Transition with comments** - Provide context for status changes
5. **Verify before bulk operations** - Test JQL queries before mass updates
6. **Prefer natural language with MCP** - Let AI handle the API complexity

## Common Errors

- **"JIRA_USER environment variable not set"**: Export your Red Hat email
- **"JIRA_API_TOKEN environment variable not set"**: Export your API token
- **"MCP server not responding"**: Check MCP configuration and server logs
- **"JQL syntax error"**: Test query in JIRA web UI first
- **"Authentication failed"**: Verify API token hasn't expired (regenerate at id.atlassian.com)

## Dependencies

- [jira-mcp-server](https://github.com/redhat-community-ai-tools/jira-mcp-server) - MCP server implementation
- [jira-cli](https://github.com/ankitpokhrel/jira-cli) - Underlying JIRA CLI tool
- Python 3 - Runtime for jira-mcp-cli
- curl - REST API calls

## Related

- JIRA MCP Server: https://github.com/redhat-community-ai-tools/jira-mcp-server
- JIRA CLI: https://github.com/ankitpokhrel/jira-cli
- Red Hat JIRA: https://redhat.atlassian.net
- MCP Protocol: https://modelcontextprotocol.io
- JQL Reference: https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/

## Comparison with jira Plugin

If you're unsure which plugin to use, here's a decision guide:

**Choose `jira-mcp` if:**
- ✅ You use Claude Desktop or Claude Code regularly
- ✅ You want to describe tasks in natural language
- ✅ You need AI to make decisions across multiple issues
- ✅ You prefer interactive, conversational workflows

**Choose `jira` if:**
- ✅ You write shell scripts for automation
- ✅ You use JIRA in CI/CD pipelines
- ✅ You need advanced skills (status reports, triage, spec-to-backlog)
- ✅ You prefer traditional command-line tools

**Install both if:**
- ✅ You use both interactive and scripted workflows
- ✅ You want maximum flexibility
- ✅ Different team members have different preferences

Both plugins target the same Red Hat JIRA instance and can be used together without conflict.
