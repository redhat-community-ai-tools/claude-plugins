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
- `list_jira_transitions` - Get available workflow transitions
- `search_jira_child_tickets` - Traverse 2-level Jira hierarchies
- `get_jira_project_info` / `list_jira_project_components` / `list_jira_project_versions` - Project metadata
- `search_jira_filters` / `get_jira_filter` / `list_jira_favourite_filters` - Saved filter management
- `count_jira_tickets` - Count tickets matching a JQL query
- `add_jira_weblink` - Add web links to tickets
- `list_jira_issue_types_for_project` - List issue types in a project
- `list_jira_custom_field_options` - List allowed values for custom fields

### GitHub Tools
- `search_github_issues` - Search issues and PRs
- `get_github_issue` - Get issue/PR details with comments
- `get_github_pr_diff` / `get_github_pr_checks` - PR diffs and CI status
- `get_github_repository_info` - Repository metadata
- `get_github_rate_limit` - Check API rate limit status

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

## Available Prompts

MCP prompts provide structured analysis workflows that guide the AI through multi-step investigations.

- `rca` — Root cause analysis of a failing DCI job using the 5 Whys method with log evidence gathering, adversarial verification, and confidence-rated findings
- `weekly` — Weekly DCI job analysis with failure rates, top failure reasons, and recommendations
- `biweekly` — Two-week DCI job analysis with statistics and anomaly detection
- `quarterly` — Comprehensive 3-month analysis with pipeline/topic/component statistics, trend detection, and anomaly detection

## When to Use

This plugin is designed for **DCI-centric cross-platform workflows** — CI job analysis, cross-referencing DCI results with Jira tickets, GitHub/GitLab PRs, Red Hat support cases, and Google Drive reports.

Its Jira/GitHub/GitLab tools overlap with the standalone `jira`, `jira-mcp`, and built-in GitHub plugins. For general-purpose Jira or GitHub work unrelated to DCI, prefer those dedicated plugins. Use this plugin when you need to correlate data across DCI and these platforms in a single MCP session.

## Skills

### dci-mcp-management

AI-assisted DCI and multi-platform integration through MCP. Enables searching CI jobs, querying components, managing Jira tickets, reviewing GitHub/GitLab PRs, accessing Red Hat support cases, and creating Google Drive documents.

See [skills/dci-mcp-management/SKILL.md](skills/dci-mcp-management/SKILL.md) for detailed usage patterns and query syntax.

## Links

- [GitHub Repository](https://github.com/redhat-community-ai-tools/dci-mcp-server)
- [DCI Documentation](https://doc.distributed-ci.io/)
- [MCP Protocol](https://modelcontextprotocol.io)
