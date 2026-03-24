# Claude Code Plugins

A marketplace of Claude Code plugins for OpenShift operations, Jira workflows, CI/CD, and developer productivity.

## Quick Start

```bash
# Add this marketplace to Claude Code
claude plugin marketplace add https://github.com/redhat-community-ai-tools/claude-plugins

# Install a plugin
claude plugin install jira

# List installed plugins
claude plugin list

# Update a plugin
claude plugin update jira
```

## Available Plugins

| Plugin | Description | Install | Requires |
|--------|-------------|---------|----------|
| **openshift-ops** | Cluster management, debugging, upgrades, node ops | `claude plugin install openshift-ops` | `oc` |
| **jira** | Create, search, update, and track Jira issues | `claude plugin install jira` | `jira` (jira-cli) |
| **skipper** | Build and test inside Docker/Podman containers | `claude plugin install skipper` | `skipper`, `python3` |
| **daily-summary** | Generate Slack-formatted daily standup updates | `claude plugin install daily-summary` | `jira`, `gh` |
| **osac-dev** | Bug fix and bug reporting workflows with Jira+PR | `claude plugin install osac-dev` | `jira`, `gh` |
| **google** | Google Workspace — Gmail, Docs, Slides, Sheets, Calendar, Drive | `claude plugin install google` | `gws` |
| **skill-scanner** | Scan plugins for security vulnerabilities | `claude plugin install skill-scanner` | — |

### openshift-ops

4 skills for OpenShift cluster management:
- **openshift-debugging** — Troubleshoot pods, nodes, operators, networking, storage
- **openshift-cluster-upgrade** — Plan, execute, and troubleshoot cluster upgrades
- **openshift-node-operations** — Add/remove nodes, cordoning, draining, maintenance
- **openshift-operator-troubleshooting** — Debug cluster operators, OLM, subscriptions

### jira

5 skills for Jira issue management on Red Hat Jira:
- **jira-task-management** — Create, search, update, transition issues and sprints
- **capture-tasks-from-meeting-notes** — Extract action items from meeting notes into Jira
- **generate-status-report** — Generate project status reports from Jira data
- **spec-to-backlog** — Transform spec documents into structured Jira backlogs
- **triage-issue** — Triage bug reports, check for duplicates, create well-structured tickets

### skipper

- **skipper-dev-workflow** — Build, test, lint inside containerized environments with consistent toolchains

### daily-summary

- **daily-summary** — Cross-references Jira, GitHub PRs, and git history for a Slack-ready standup update

### osac-dev

- **fix-bug** — Background agent: end-to-end bug fix from Jira ticket to merged PR
- **report-bug** — Create a well-structured Jira bug ticket with links and assignment

### google

Google Workspace integration via the `gws` CLI:
- **Gmail** — Send, read, reply, reply-all, forward, triage inbox, watch for new emails
- **Google Docs** — Read and write documents
- **Google Slides** — Read and write presentations
- **Google Sheets** — Read values and append rows
- **Google Calendar** — View agenda, create events with Meet links
- **Google Drive** — Manage files/folders, upload files

### skill-scanner

- **skill-scanner** — Scan installed plugins for prompt injection, malicious instructions, and security issues

## Managing Plugins

```bash
# Uninstall a plugin
claude plugin uninstall jira

# Install for current project only (not globally)
claude plugin install jira --scope project

# Update all marketplace data
claude plugin marketplace update

# Remove this marketplace
claude plugin marketplace remove ecosystem-claude-plugins
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to create plugins, versioning rules, and the review process.

## License

MIT. See individual plugin directories for any exceptions.
