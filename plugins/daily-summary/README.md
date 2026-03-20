# Daily Summary Plugin

Generate daily status updates formatted for Slack by gathering data from Jira, GitHub PRs, and git history.

## Skills

### daily-summary
Produces a Slack-ready daily summary with accomplishments, key efforts, and risks. Items are cross-referenced across Jira, GitHub, and git to avoid duplicates. Jira ticket IDs are rendered as clickable links using Slack's native mrkdwn syntax.

**Slash command:** `/daily-summary`

**Data sources:**
- Jira issues (via `jira-cli`)
- GitHub PRs (via `gh`)
- Local git history (including submodules)
- GSD planning context (`.planning/` files)
- Session context and memory files

**Prerequisites:**
- `jira-cli` installed: `go install github.com/ankitpokhrel/jira-cli/cmd/jira@latest`
- `gh` CLI installed: https://cli.github.com/
- Both tools authenticated and configured

## Installation

```bash
claude plugin marketplace add redhat-community-ai-tools/claude-plugins
claude plugin install daily-summary@ecosystem-claude-plugins
```
