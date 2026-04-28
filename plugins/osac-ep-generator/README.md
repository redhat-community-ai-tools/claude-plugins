# OSAC Enhancement Proposal Generator

A Claude Code plugin for generating OSAC enhancement proposals from high-level requirements and decomposing them into Jira work items.

## Skills

### generate-ep

Generate a structured OSAC enhancement proposal from:
- Conversational requirements (describe what you want to build)
- Meeting notes or requirements documents (point to a file)
- Jira tickets (provide a ticket number like MGMT-XXXXX)

The skill explores the codebase, asks clarifying questions, drafts a full EP following the osac-project/enhancement-proposals template, and submits it as a PR.

**Usage:**
- "Draft an enhancement proposal for a storage network API"
- "Turn these meeting notes into an EP" (with file path)
- "Create an enhancement proposal from MGMT-24100"

### ep-to-jira

Convert an approved enhancement proposal into a Jira epic with linked sub-tasks. Includes:
- **Dependency mapping**: Identifies cross-repo impacts and breaking changes using codebase analysis
- **Complexity assessment**: Rates architectural impact on 5 dimensions (repos, API, data, dependencies, testing)
- **Task ordering**: Sequences tasks (proto -> backend -> controller -> tests -> docs)

**Usage:**
- "Create Jira tasks from the networking EP"
- "Decompose the storage-network enhancement proposal"
- "What's the complexity of implementing the bare-metal-fulfillment EP?"

## Prerequisites

| Tool | Required | Purpose |
|------|----------|---------|
| gh | Yes | GitHub CLI for PR operations |
| jira | Yes | Jira CLI for epic/task creation |
| rg | Yes | ripgrep for codebase search |
| jq | No | JSON parsing |

## Installation

### From marketplace
(After publication)

### Local testing
```bash
claude --plugin-dir /path/to/plugins/osac-ep-generator
```

## License

MIT
