---
name: dci-mcp-management
description: Manage DCI jobs, components, Jira tickets, GitHub/GitLab issues, and Red Hat support cases via the dci-mcp-server Model Context Protocol integration
---

# DCI MCP Management

Manage DCI (Distributed CI) jobs, components, teams, and remotecis, plus Jira, GitHub, GitLab, Google Drive, and Red Hat Support Cases via the **dci-mcp-server** Model Context Protocol integration.

## Overview

dci-mcp-server is an MCP server that provides comprehensive access to DCI CI/CD data and integrates with multiple platforms. It enables AI-assisted workflows for CI monitoring, issue tracking, PR review, and support case management.

## Setup

### Prerequisites

1. **Python 3.14+** and **uv** package manager
2. **DCI API credentials**

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

Add to `.mcp.json`:

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

## Available MCP Tools

### DCI Tools

- `search_dci_jobs` - Search CI jobs with advanced query language supporting nested boolean queries, date ranges, and component filtering
- `query_dci_components` - Query DCI components (OpenShift versions, storage solutions) with tag filtering (build:ga, build:dev, etc.)
- `query_dci_teams` - Query DCI teams
- `query_dci_remotecis` - Query DCI remotecis (labs)
- `download_dci_file` - Download job files (logs, JUnit results, etc.)
- `today` / `now` - Date utilities for building time-based queries

### Jira Tools

- `get_jira_ticket` - Get ticket data with comments, changelog, and custom fields
- `search_jira_tickets` - Search with JQL queries
- `create_jira_ticket` / `update_jira_ticket` - Create and update tickets
- `add_jira_comment` - Add comments to tickets
- `list_jira_boards` / `list_jira_sprints` - Board and sprint management
- `list_jira_transitions` - Get available workflow transitions
- `search_jira_child_tickets` - Traverse 2-level Jira hierarchies (e.g., requirements to test tickets)
- `get_jira_project_info` / `list_jira_project_components` / `list_jira_project_versions` - Project metadata
- `search_jira_filters` / `get_jira_filter` / `list_jira_favourite_filters` - Saved filter management

### GitHub Tools

- `search_github_issues` - Search issues and PRs with GitHub query syntax
- `get_github_issue` - Get issue/PR details with comments
- `get_github_pr_diff` - Get unified diffs for PR file changes
- `get_github_pr_checks` - Get CI check runs and commit statuses
- `get_github_repository_info` - Repository metadata
- `get_github_rate_limit` - Check API rate limit status

### GitLab Tools

- `search_gitlab_issues` / `search_gitlab_merge_requests` - Search with state and label filters
- `get_gitlab_issue` - Get issue details with notes
- `get_gitlab_mr_diff` - Get MR diffs with configurable context
- `get_gitlab_project_info` - Project metadata

### Red Hat Support Tools

- `get_support_case` - Get case data with comments and linked Bugzilla bugs
- `get_support_case_comments` - Get case comments with date filtering
- `list_support_case_attachments` - List case attachments
- `get_errata` - Get advisory details (RHSA, RHBA, RHEA) with CVEs and affected products

### Google Drive Tools

- `create_google_doc_from_markdown` - Create Google Docs from markdown content
- `create_google_doc_from_file` - Create Google Docs from local markdown files
- `convert_dci_report_to_google_doc` - Convert DCI reports with proper formatting
- `list_google_docs` / `find_folder_by_name` - Browse Google Drive

## Usage Patterns

### Search DCI Jobs

```
"Find all failed daily jobs for OCP 4.19 in the last week"
```

The MCP server uses the advanced query language:
```
(((tags in ['daily']) and (status='failure')) and (created_at>='2025-01-01'))
```

### Query Components

```
"List all GA OpenShift components"
```

Uses: `and(eq(type,ocp),contains(tags,build:ga))`

### Cross-Platform Workflows

```
"Find the failing DCI job, get the related Jira ticket, and check if there's a GitHub PR fixing it"
```

The MCP server provides tools across all platforms, enabling AI to correlate data from DCI, Jira, GitHub, and GitLab in a single workflow.

### Support Case Investigation

```
"Get the details of support case 03619625 and check if there's a related errata"
```

## Reference

- **dci-mcp-server**: https://github.com/redhat-community-ai-tools/dci-mcp-server
- **DCI Documentation**: https://doc.distributed-ci.io/
- **MCP Protocol**: https://modelcontextprotocol.io
