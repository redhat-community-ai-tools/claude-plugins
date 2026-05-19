# DCI MCP Server Plugin

MCP server for [DCI (Distributed CI)](https://doc.distributed-ci.io/), providing AI-powered access to CI/CD data, Jira, GitHub, GitLab, Google Drive, and Red Hat Support Cases.

## Installation

```bash
# Add marketplace
claude plugin marketplace add https://github.com/redhat-community-ai-tools/claude-plugins

# Install plugin
claude plugin install dci-mcp-server
```

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) installed
- DCI API credentials (`DCI_CLIENT_ID` and `DCI_API_SECRET`)

## Configuration

### Environment Variables

```bash
# Required: DCI authentication
export DCI_CLIENT_ID=<client_type>/<client_id>
export DCI_API_SECRET=<api_secret>

# Optional: Jira integration
export JIRA_API_TOKEN=<your_jira_api_token>
export JIRA_EMAIL=<your_email>
export JIRA_URL=https://redhat.atlassian.net
export JIRA_WRITE_ENABLED=true

# Optional: GitHub integration
export GITHUB_TOKEN=<your_github_token>

# Optional: GitLab integration
export GITLAB_TOKEN=<your_gitlab_token>
export GITLAB_URL=https://gitlab.com

# Optional: Red Hat Support Cases
export OFFLINE_TOKEN=<your_offline_token>

# Optional: Google Drive
export GOOGLE_CREDENTIALS_PATH=credentials.json
export GOOGLE_TOKEN_PATH=token.json
```

### MCP Server Configuration

Add to `.mcp.json` (Claude Code) or `claude_desktop_config.json` (Claude Desktop):

```json
{
  "mcpServers": {
    "dci": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "dci-mcp-server @ git+https://github.com/redhat-community-ai-tools/dci-mcp-server", "dci-mcp-server"]
    }
  }
}
```

## Available Tools

### DCI Tools
- `search_dci_jobs` - Search CI jobs with advanced query language
- `query_dci_components` - Query DCI components (OpenShift versions, storage, etc.)
- `query_dci_teams` - Query DCI teams
- `query_dci_remotecis` - Query DCI remotecis (labs)
- `download_dci_file` - Download job files
- `today` / `now` - Date utilities

### Jira Tools
- `get_jira_ticket` - Get ticket data with comments and changelog
- `search_jira_tickets` - Search with JQL
- `create_jira_ticket` / `update_jira_ticket` - Write operations
- `add_jira_comment` - Add comments to tickets
- `list_jira_boards` / `list_jira_sprints` - Board and sprint management
- `search_jira_child_tickets` - Traverse 2-level Jira hierarchies

### GitHub Tools
- `search_github_issues` - Search issues and PRs
- `get_github_issue` - Get issue/PR details with comments
- `get_github_pr_diff` / `get_github_pr_checks` - PR diffs and CI status
- `get_github_repository_info` - Repository metadata

### GitLab Tools
- `search_gitlab_issues` / `search_gitlab_merge_requests` - Search GitLab
- `get_gitlab_issue` / `get_gitlab_mr_diff` - Get details and diffs
- `get_gitlab_project_info` - Project metadata

### Red Hat Support Tools
- `get_support_case` - Get case data with comments and linked bugs
- `get_support_case_comments` - Get case comments with date filtering
- `list_support_case_attachments` - List case attachments
- `get_errata` - Get advisory details (RHSA, RHBA, RHEA)

### Google Drive Tools
- `create_google_doc_from_markdown` - Create Google Docs from markdown content
- `create_google_doc_from_file` - Create Google Docs from markdown files
- `convert_dci_report_to_google_doc` - Convert DCI reports to Google Docs
- `list_google_docs` / `find_folder_by_name` - Browse Google Drive

## Skills

### dci-mcp-management

AI-assisted DCI and multi-platform integration through MCP. Enables searching CI jobs, querying components, managing Jira tickets, reviewing GitHub/GitLab PRs, and accessing Red Hat support cases.

See [skills/dci-mcp-management/SKILL.md](skills/dci-mcp-management/SKILL.md) for detailed documentation.

## Links

- [GitHub Repository](https://github.com/redhat-community-ai-tools/dci-mcp-server)
- [DCI Documentation](https://doc.distributed-ci.io/)
- [MCP Protocol](https://modelcontextprotocol.io)
