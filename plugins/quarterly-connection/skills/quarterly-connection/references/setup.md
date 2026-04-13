# Quarterly MCP Server Setup

## Installation

```bash
git clone https://github.com/redhat-community-ai-tools/quarterly-mcp-server.git
cd quarterly-mcp-server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create `~/.quarterly-mcp-config.json`:

```json
{
  "JIRA_URL": "https://your-jira-instance.atlassian.net",
  "JIRA_EMAIL": "your-email@example.com",
  "JIRA_API_TOKEN": "your-jira-api-token",
  "GITHUB_TOKEN": "your-github-personal-access-token",
  "GITLAB_URL": "https://gitlab.com",
  "GITLAB_TOKEN": "your-gitlab-token"
}
```

Environment variables override config file values:
- `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`
- `GITHUB_TOKEN`
- `GITLAB_URL`, `GITLAB_TOKEN`

## Token Acquisition

### Jira
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Create a new API token
3. Use your Atlassian email as `JIRA_EMAIL`

### GitHub
1. Go to https://github.com/settings/tokens
2. Create a Personal Access Token with `repo` scope

### GitLab
1. Go to https://gitlab.com/-/profile/personal_access_tokens
2. Create a token with `read_api` scope
3. GitLab is optional — skip if you don't use it

## Register with Claude Code

```bash
claude mcp add quarterly /path/to/quarterly-mcp-server/venv/bin/python -- /path/to/quarterly-mcp-server/server.py
```

Verify:

```bash
claude mcp list
```

You should see `quarterly` in the list of registered MCP servers.

## Troubleshooting

- **"Jira configuration missing"**: Check `JIRA_URL` and `JIRA_API_TOKEN`
  are set in config file or environment
- **"GitHub token missing"**: Set `GITHUB_TOKEN`
- **Authentication errors**: Tokens may have expired; regenerate them
- **No results**: Verify username format matches what the platform expects
  (Jira often uses email, GitHub uses the handle)
