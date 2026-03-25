# Claude Code Plugins

A collection of Claude Code plugins for various operations and workflows.

**License:** MIT

## Available Plugins

### OpenShift Operations (`openshift-ops`)

Comprehensive skills for OpenShift cluster management, troubleshooting, and operations.

**Skills Included:**
- OpenShift Debugging - Troubleshoot pods, nodes, operators, networking, and storage
- Cluster Upgrade - Plan, execute, and troubleshoot cluster upgrades
- Node Operations - Manage node lifecycle, cordoning, draining, and maintenance
- Operator Troubleshooting - Debug cluster operators, OLM, and subscription issues

**[Documentation →](plugins/openshift-ops/README.md)**

### Jira (`jira`)

Manage Jira issues on Red Hat Jira using `jira-cli`.

**Skills Included:**
- Jira Task Management - Create, search, update, transition, and comment on issues, epics, and sprints

**[Documentation →](plugins/jira/README.md)**

### Skipper (`skipper`)

Containerized development using skipper — build, test, and run commands inside Docker/Podman containers with reproducible toolchains.

**Skills Included:**
- Skipper Dev Workflow - Build, test, lint, and run commands inside containerized environments

**[Documentation →](plugins/skipper/README.md)**

### Daily Summary (`daily-summary`)

Generate daily status updates formatted for Slack from Jira, GitHub, and git activity.

**Skills Included:**
- Daily Summary - Cross-references Jira, GitHub PRs, and git history to produce a Slack-ready standup update with clickable Jira links

**[Documentation →](plugins/daily-summary/README.md)**

### OSAC Dev (`osac-dev`)

OSAC development workflows: bug fix and bug reporting with Jira integration.

**Agents:**
- Fix Bug - Background agent that runs end-to-end: opens a Jira bug, writes the fix with tests, verifies build/format/tests pass, commits, posts a PR, and moves the ticket to Code Review

**Skills Included:**
- Fix Bug (launcher) - Gathers inputs and launches the fix-bug agent in the background
- Report Bug - Report a bug in Jira without fixing it — creates a Bug ticket with proper description, links it to an epic, and assigns it

### Google Workspace (`google`)

Google Workspace integration via the [`gws` CLI](https://github.com/googleworkspace/cli) — Gmail, Docs, Slides, Sheets, Calendar, and Drive.

**Skills Included:**
- Gmail - Send, read, reply, reply-all, forward, triage inbox, and watch for new emails
- Google Docs - Read and write documents
- Google Slides - Read and write presentations
- Google Sheets - Read values and append rows to spreadsheets
- Google Calendar - View agenda, create events with Meet links
- Google Drive - Manage files/folders, upload files

---

## Installation

### Install from Marketplace

```bash
# Add the plugin repository to Claude Code
/plugin marketplace add https://github.com/redhat-community-ai-tools/claude-plugins

# Verify installation
/plugin list
```

### Install from Local Development

```bash
# Clone the repository
git clone https://github.com/redhat-community-ai-tools/claude-plugins.git
cd claude-plugins/plugins/openshift-ops

# Install locally
/plugin install .
```

## Repository Structure

```
claude-plugins/
├── README.md                    # This file
├── .claude-plugin/
│   └── marketplace.json        # Repository marketplace metadata
└── plugins/
    ├── openshift-ops/          # OpenShift Operations
    │   ├── manifest.json
    │   ├── README.md
    │   └── skills/
    │       ├── openshift-debugging/
    │       ├── openshift-cluster-upgrade/
    │       ├── openshift-node-operations/
    │       └── openshift-operator-troubleshooting/
    ├── jira/                   # Jira Task Management
    │   ├── manifest.json
    │   ├── README.md
    │   └── skills/
    │       └── jira-task-management/
    ├── skipper/                # Skipper Dev Workflow
    │   ├── manifest.json
    │   ├── README.md
    │   └── skills/
    │       └── skipper-dev-workflow/
    ├── daily-summary/          # Daily Summary for Slack
    │   ├── manifest.json
    │   ├── README.md
    │   ├── .claude-code/commands/
    │   └── skills/
    │       └── daily-summary/
    ├── osac-dev/               # OSAC Dev Workflows
    │   ├── manifest.json
    │   ├── .claude-code/commands/
    │   ├── agents/
    │   │   └── fix-bug.md
    │   └── skills/
    │       ├── fix-bug/
    │       └── report-bug/
    └── google/                 # Google Workspace
        ├── manifest.json
        └── skills/
            ├── gws-shared/
            ├── gws-gmail/
            ├── gws-gmail-send/
            ├── gws-gmail-read/
            ├── gws-gmail-reply/
            ├── gws-gmail-reply-all/
            ├── gws-gmail-forward/
            ├── gws-gmail-triage/
            ├── gws-gmail-watch/
            ├── gws-docs/
            ├── gws-docs-write/
            ├── gws-slides/
            ├── gws-sheets/
            ├── gws-sheets-read/
            ├── gws-sheets-append/
            ├── gws-calendar/
            ├── gws-calendar-agenda/
            ├── gws-calendar-insert/
            ├── gws-drive/
            └── gws-drive-upload/
```

## Contributing

Contributions are welcome! To add a new plugin or improve existing ones:

1. Fork the repository
2. Create a new branch for your changes
3. Add your plugin in a new subdirectory
4. Ensure proper `manifest.json` and documentation
5. Test your plugin locally
6. Submit a pull request

## Plugin Development

Each plugin should follow this structure:

```
plugin-name/
├── manifest.json          # Plugin metadata and configuration
├── marketplace.json       # Marketplace submission metadata
├── README.md             # Plugin documentation
├── LICENSE               # License file
└── skills/               # Skill definitions
    └── skill-name/
        └── SKILL.md
```

### Creating a New Plugin

1. Create a new directory with your plugin name
2. Add required files (manifest.json, README.md, etc.)
3. Follow the structure of existing plugins
4. Test locally before submitting

## Support

For issues, questions, or suggestions:
- Open an issue in this repository
- Reference the specific plugin in your issue title

## License

Each plugin is licensed under MIT unless otherwise specified in its directory.

Copyright (c) 2025 Eran Cohen
