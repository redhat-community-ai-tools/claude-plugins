# OpenShift Operations Plugin

Opinionated diagnostic workflows for OpenShift cluster operations — decision trees, failure modes, and gotchas that complement Claude's built-in knowledge.

**Author:** Eran Cohen
**Version:** 1.0.0
**License:** MIT

## Overview

This plugin encodes the decision logic and non-obvious patterns that experienced SREs know but that aren't captured in command references. It does NOT list `oc` commands — Claude already knows those. Instead, each skill provides:

- **Decision trees**: Symptoms map to diagnosis paths
- **Priority ordering**: What to check first, second, third
- **Failure-mode classification**: What symptoms mean and how to differentiate root causes
- **Gotchas**: Non-obvious patterns that catch even experienced operators
- **Cross-skill routing**: When to hand off to a sibling skill

## Skills Included

### 1. OpenShift Debugging (`openshift-debugging`)

Layered triage and failure-mode classification for cluster issues. Identifies which layer (app/platform/infra) the problem lives in, then provides priority-ordered diagnosis for CrashLoopBackOff, Pending, ImagePullBackOff, and networking failures.

### 2. OpenShift Cluster Upgrade (`openshift-cluster-upgrade`)

Irreversibility-aware upgrade planning and stuck-upgrade diagnosis. Leads with the critical fact that upgrades cannot be rolled back, provides pre-upgrade gate checks, upgrade path decisions (standard/EUS/air-gapped/large-cluster), and a priority chain for diagnosing stuck upgrades.

### 3. OpenShift Node Operations (`openshift-node-operations`)

Safe drain procedures and automated-vs-manual node lifecycle. Centers on the automated-vs-manual infrastructure fork that affects every operation, safe drain procedures (cordon-first, PDB awareness), and node failure diagnosis priority.

### 4. OpenShift Operator Troubleshooting (`openshift-operator-troubleshooting`)

Status-triple analysis for cluster operators, CSV lifecycle for OLM. Distinguishes cluster operators (CVO-managed) from OLM operators, provides the AVAILABLE/PROGRESSING/DEGRADED status-triple interpretation table, and covers OLM infrastructure chain diagnosis.

## Installation

### Prerequisites
- Claude Code CLI installed (v2.0.0 or higher)
- OpenShift CLI (`oc`) installed and configured
- Access to OpenShift clusters

### Install from GitHub

```bash
/plugin marketplace add https://github.com/redhat-community-ai-tools/claude-plugins
```

### Verify Installation

```bash
/plugin list
/skills list
```

## Usage

Once installed, Claude automatically invokes the appropriate skill when you ask OpenShift-related questions.

### Example Prompts

- "Help me troubleshoot why my pods are in CrashLoopBackOff"
- "The cluster upgrade is stuck at 80%, what should I check?"
- "I need to drain a node for maintenance"
- "The ingress operator is degraded"

### Slash Commands

- `/debug-cluster` - Debug and troubleshoot OpenShift cluster issues
- `/upgrade-cluster` - Plan and execute OpenShift cluster upgrades
- `/node-ops` - Manage OpenShift node operations and lifecycle
- `/debug-operator` - Troubleshoot OpenShift operator issues
- `/cluster-health` - Check overall OpenShift cluster health

## Skill Relationships

The skills are designed to work together with explicit cross-routing:

- **Debugging** → May route to **Operator Troubleshooting** or **Node Operations**
- **Cluster Upgrade** → Uses **Debugging** and **Operator Troubleshooting** for issues
- **Node Operations** → Related to **Debugging** for node-level issues
- **Operator Troubleshooting** → Used by **Cluster Upgrade** and **Debugging**

## Plugin Structure

```
openshift-ops/
├── README.md
├── manifest.json
├── .claude-code/commands/
│   ├── debug-cluster.md
│   ├── upgrade-cluster.md
│   ├── node-ops.md
│   ├── debug-operator.md
│   └── cluster-health.md
└── skills/
    ├── openshift-debugging/SKILL.md
    ├── openshift-cluster-upgrade/SKILL.md
    ├── openshift-node-operations/SKILL.md
    └── openshift-operator-troubleshooting/SKILL.md
```

## Contributing

Contributions are welcome! When adding content to skills, follow this principle: **only add what Claude wouldn't know from training data.** Decision logic, gotchas, priority ordering, and failure-mode classification are valuable. Command listings are not.

1. Fork the repository at https://github.com/redhat-community-ai-tools/claude-plugins
2. Make your changes in the `plugins/openshift-ops/` directory
3. Run `python scripts/validate.py` to verify
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Eran Cohen
