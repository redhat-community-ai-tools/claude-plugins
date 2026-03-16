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
    └── skipper/                # Skipper Dev Workflow
        ├── manifest.json
        ├── README.md
        └── skills/
            └── skipper-dev-workflow/
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
