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
| **openshift-ops** | Diagnostic workflows for cluster operations — decision trees, failure modes, gotchas | `claude plugin install openshift-ops` | `oc` |
| **jira** | CLI-based JIRA management with advanced skills | `claude plugin install jira` | `jira` (jira-cli) |
| **jira-mcp** | AI-assisted JIRA management via MCP server | `claude plugin install jira-mcp` | `jira-mcp-server`, `jira-cli` |
| **polarion** | Manage Polarion test cases for OpenShift Extended Testing | `claude plugin install polarion` | `python3`, `polarion-mcp-server` |
| **skipper** | Build and test inside Docker/Podman containers | `claude plugin install skipper` | `skipper`, `python3` |
| **daily-summary** | Generate Slack-formatted daily standup updates | `claude plugin install daily-summary` | `jira`, `gh` |
| **osac-dev** | Bug fix and bug reporting workflows with Jira+PR | `claude plugin install osac-dev` | `jira`, `gh` |
| **google** | Google Workspace — Gmail, Docs, Slides, Sheets, Calendar, Drive | `claude plugin install google` | `gws` |
| **quarterly-connection** | Red Hat Quarterly Connection reports from Jira, GitHub, Google Workspace, GitLab | `claude plugin install quarterly-connection` | `jira`, `gh`, `gws` |
| **skill-scanner** | Scan plugins for security vulnerabilities | `claude plugin install skill-scanner` | — |

### openshift-ops

4 skills for OpenShift cluster management:
- **openshift-debugging** — Layered triage and failure-mode classification for cluster issues
- **openshift-cluster-upgrade** — Irreversibility-aware upgrade planning and stuck-upgrade diagnosis
- **openshift-node-operations** — Safe drain procedures and automated-vs-manual node lifecycle
- **openshift-operator-troubleshooting** — Status-triple analysis for cluster operators, CSV lifecycle for OLM

### jira

5 skills for Jira issue management on Red Hat Jira (CLI-based):
- **jira-task-management** — Create, search, update, transition issues and sprints
- **capture-tasks-from-meeting-notes** — Extract action items from meeting notes into Jira
- **generate-status-report** — Generate project status reports from Jira data
- **spec-to-backlog** — Transform spec documents into structured Jira backlogs
- **triage-issue** — Triage bug reports, check for duplicates, create well-structured tickets

**Best for:** Shell scripts, CI/CD, one-off commands, advanced workflow skills

### jira-mcp

AI-assisted JIRA management via Model Context Protocol:
- **jira-mcp-management** — Natural language JIRA interaction, batch operations, context-aware workflows through MCP server integration

**Best for:** Interactive AI workflows, natural language commands, batch processing with decision logic, Claude Desktop/Code with MCP

**Key Difference:** `jira` uses jira-cli directly (traditional CLI). `jira-mcp` uses MCP server for AI-assisted natural language interaction. Both can coexist.

See [plugins/jira-mcp/README.md](plugins/jira-mcp/README.md)

### polarion

Polarion ALM test case management for OpenShift Extended Testing:
- **polarion-test-management** — Create, search, update test cases and test steps on Red Hat's Polarion instance (polarion.engineering.redhat.com). Includes automatic backup/restore for test steps, auto-delete handling for Polarion REST API limitations, and step ordering preservation. Integrates with openshift-tests-private workflow for converting JIRA bugs into automated test cases.

See [plugins/polarion/README.md](plugins/polarion/README.md)

### skipper

- **skipper-dev-workflow** — Build, test, lint inside containerized environments with consistent toolchains

### daily-summary

- **daily-summary** — Cross-references Jira, GitHub PRs, and git history for a Slack-ready standup update

### osac-dev

- **fix-bug** — Background agent: end-to-end bug fix from Jira ticket to merged PR
- **report-bug** — Create a well-structured Jira bug ticket with links and assignment

### google

Google Workspace integration via the [`gws`](https://github.com/googleworkspace/cli) CLI:
- **Gmail** — Send, read, reply, reply-all, forward, triage inbox, watch for new emails
- **Google Docs** — Read and write documents
- **Google Slides** — Read and write presentations
- **Google Sheets** — Read values and append rows
- **Google Calendar** — View agenda, create events with Meet links
- **Google Drive** — Manage files/folders, upload files

**Requires setup:** GCP project with OAuth credentials. See [plugins/google/README.md](plugins/google/README.md) for step-by-step instructions.

### quarterly-connection

- **quarterly-connection** — Generates Red Hat Quarterly Connection reports by aggregating data from Jira, GitHub, Google Docs/Slides/Calendar, and GitLab. Includes `/quarterly` for official Red Hat QC format and `/quarterly-report` for enhanced analysis with cycle time ranking, achievement analysis by multiple metrics, and AI-powered narrative refinement (business impact, technical depth, leadership frameworks)

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
