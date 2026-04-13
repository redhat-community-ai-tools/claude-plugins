# Configure

Verify and set up the quarterly MCP server and its platform credentials.

## Steps

### 1. Check MCP Server Registration

Verify the `quarterly-mcp-server` is registered:

```bash
claude mcp list
```

Look for a `quarterly` entry. If missing, guide the user through registration
(see `references/setup.md`).

### 2. Check Configuration File

The server reads from `~/.quarterly-mcp-config.json`. Check if it exists:

```bash
cat ~/.quarterly-mcp-config.json 2>/dev/null
```

If missing, help the user create it. The expected format:

```json
{
  "JIRA_URL": "https://your-jira.atlassian.net",
  "JIRA_EMAIL": "your-email@example.com",
  "JIRA_API_TOKEN": "your-token",
  "GITHUB_TOKEN": "your-github-pat",
  "GITLAB_URL": "https://gitlab.com",
  "GITLAB_TOKEN": "your-gitlab-token"
}
```

**Important:** Do NOT display tokens in output. When showing the config,
mask token values (e.g., `"JIRA_API_TOKEN": "****"`).

### 3. Verify Each Platform

Test each configured platform by making a small query:

**Jira** — call `get_jira_summary` with the user's username and a narrow
recent date range (last 7 days). Success = JSON with a `total` field.
Error = JSON with an `error` field.

**GitHub** — call `get_github_summary` similarly. Look for `total_count`.

**GitLab** — call `get_gitlab_summary`. Look for `total`.

### 4. Report Status

Present a clear status table:

```
Platform  | Status  | Notes
----------|---------|---------------------------
Jira      | OK      | Connected to redhat.atlassian.net
GitHub    | OK      | Token valid, 42 PRs found
GitLab    | MISSING | No token configured
```

### 5. Fix Issues

For each failing platform, provide specific guidance:

- **Jira**: Check `JIRA_URL` format (must include `https://`), verify email
  matches the Jira account, confirm API token is current
- **GitHub**: Token needs `repo` scope; generate at
  github.com/settings/tokens
- **GitLab**: Token needs `read_api` scope; GitLab config is optional if
  the user doesn't use GitLab
