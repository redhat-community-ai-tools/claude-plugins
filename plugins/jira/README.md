# Jira Plugin

Manage Jira issues from Claude Code using `jira-cli`.

## Skills

### jira-task-management
View, create, update, transition, comment on, and search Jira issues, epics, and sprints.

**Slash command:** `/jira`

**Prerequisites:**
- `jira-cli` installed: `go install github.com/ankitpokhrel/jira-cli/cmd/jira@latest`
- Configured for local Jira Server with bearer token auth
- Token stored in `~/.netrc`

## Installation

```bash
claude plugin marketplace add redhat-community-ai-tools/claude-plugins
claude plugin install jira@ecosystem-claude-plugins
```
