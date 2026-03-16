# OpenShift Operations Plugin

A comprehensive Claude Code plugin providing expert-level skills for OpenShift cluster management, troubleshooting, and operations.

**Author:** Eran Cohen
**Version:** 1.0.0
**License:** MIT

## Overview

This plugin equips Claude with deep knowledge of OpenShift operational procedures, best practices, and troubleshooting workflows. It's designed for platform engineers, SREs, and administrators who manage OpenShift clusters.

## Skills Included

### 1. OpenShift Debugging (`openshift-debugging`)

Comprehensive troubleshooting and debugging skill for OpenShift clusters covering:
- Pod failures and crashes
- Deployment and rollout issues
- Networking problems
- Storage and PVC issues
- Operator failures
- Node health problems
- Cluster resource constraints

**Use when:** Investigating cluster problems, diagnosing failed deployments, or resolving operational issues.

### 2. OpenShift Cluster Upgrade (`openshift-cluster-upgrade`)

Complete guide for planning, executing, and troubleshooting OpenShift cluster upgrades:
- Pre-upgrade planning and health checks
- Upgrade channel management
- Upgrade execution and monitoring
- Post-upgrade validation
- Troubleshooting stuck or failed upgrades
- EUS-to-EUS upgrades
- Air-gapped upgrade procedures

**Use when:** Upgrading clusters, investigating upgrade failures, or preparing upgrade strategies.

### 3. OpenShift Node Operations (`openshift-node-operations`)

Node lifecycle management covering:
- Adding and removing nodes
- Cordoning and draining procedures
- Node maintenance and reboots
- Machine and MachineSet management
- Node troubleshooting
- Auto-scaling configuration
- Label and taint management

**Use when:** Managing cluster capacity, performing node maintenance, or resolving node-level problems.

### 4. OpenShift Operator Troubleshooting (`openshift-operator-troubleshooting`)

Deep dive into operator issues including:
- Cluster operator degradation
- OLM operator installation failures
- Subscription and InstallPlan issues
- CSV (ClusterServiceVersion) errors
- CRD conflicts and issues
- Operator upgrade problems
- RBAC and permission issues

**Use when:** Operators are degraded, failing to install/upgrade, or causing cluster issues.

## Installation

### Prerequisites
- Claude Code CLI installed (v2.0.0 or higher)
- OpenShift CLI (`oc`) installed and configured
- Access to OpenShift clusters
- Optional: `jq` for enhanced JSON parsing

### Install from GitHub

```bash
# Install directly from GitHub
/plugin marketplace add https://github.com/redhat-community-ai-tools/claude-plugins

# Or clone and install locally
git clone https://github.com/redhat-community-ai-tools/claude-plugins.git
cd claude-plugins/plugins/openshift-ops
/plugin install .
```

### Verify Installation

```bash
# List installed plugins
/plugin list

# View available skills
/skill list
```

## Usage

Once installed, Claude will automatically invoke the appropriate skill when you ask OpenShift-related questions or request operations.

### Example Prompts

**Debugging:**
- "Help me troubleshoot why my pods are in CrashLoopBackOff"
- "My deployment is stuck, can you help debug it?"
- "Network connectivity is broken between services"

**Cluster Upgrades:**
- "I need to upgrade my cluster from 4.12 to 4.13"
- "The cluster upgrade is stuck at 80%, what should I check?"
- "Help me prepare for an upgrade to the latest version"

**Node Operations:**
- "I need to drain a node for maintenance"
- "How do I add more worker nodes to my cluster?"
- "One of my nodes is NotReady, help me troubleshoot"

**Operator Issues:**
- "The ingress operator is degraded"
- "My operator installation is failing"
- "How do I troubleshoot OLM subscription issues?"

### Slash Commands

The plugin provides convenient slash commands for common operations:

- `/debug-cluster` - Debug and troubleshoot OpenShift cluster issues
- `/upgrade-cluster` - Plan and execute OpenShift cluster upgrades
- `/node-ops` - Manage OpenShift node operations and lifecycle
- `/debug-operator` - Troubleshoot OpenShift operator issues
- `/cluster-health` - Check overall OpenShift cluster health

**Example:**
```bash
# Quick cluster health check
/cluster-health

# Start debugging a cluster issue
/debug-cluster

# Plan an upgrade
/upgrade-cluster
```

## Skills Structure

```
openshift-ops/
├── README.md
├── .claude-code/
│   └── commands/
│       ├── debug-cluster.md
│       ├── upgrade-cluster.md
│       ├── node-ops.md
│       ├── debug-operator.md
│       └── cluster-health.md
└── skills/
    ├── openshift-debugging/
    │   └── SKILL.md
    ├── openshift-cluster-upgrade/
    │   └── SKILL.md
    ├── openshift-node-operations/
    │   └── SKILL.md
    └── openshift-operator-troubleshooting/
        └── SKILL.md
```

## Best Practices

1. **Use Specific Skills:** Reference skill names when you need specialized help
2. **Provide Context:** Share error messages, cluster version, and relevant output
3. **Follow Procedures:** The skills provide step-by-step workflows - follow them sequentially
4. **Test in Non-Production:** Always test procedures in dev/staging first
5. **Backup First:** Create backups before making significant changes
6. **Document Findings:** Keep notes of troubleshooting steps and resolutions

## Skill Relationships

The skills are designed to work together:

- **Debugging** → May lead to **Operator Troubleshooting** or **Node Operations**
- **Cluster Upgrade** → Uses **Debugging** and **Operator Troubleshooting** for issues
- **Node Operations** → Related to **Debugging** for node-level issues
- **Operator Troubleshooting** → Used by **Cluster Upgrade** and **Debugging**

## Common Workflows

### Troubleshooting a Cluster Issue
1. Start with `openshift-debugging` for general investigation
2. Drill down to specific skills based on findings:
   - Operator issues → `openshift-operator-troubleshooting`
   - Node issues → `openshift-node-operations`
   - Upgrade issues → `openshift-cluster-upgrade`

### Planning a Cluster Upgrade
1. Use `openshift-cluster-upgrade` for planning
2. Reference `openshift-debugging` for pre-upgrade health checks
3. Use `openshift-operator-troubleshooting` if operators are degraded

### Performing Node Maintenance
1. Use `openshift-node-operations` for drain/cordon procedures
2. Reference `openshift-debugging` if workloads don't reschedule properly
3. Use `openshift-operator-troubleshooting` if Machine API issues occur

## Advanced Usage

### Manual Skill Invocation

```bash
# In Claude Code, you can explicitly request a skill
"Use the openshift-debugging skill to help me troubleshoot this pod issue"
```

### Combining Skills

```bash
# Ask Claude to use multiple skills
"I need to drain a node and troubleshoot why pods aren't rescheduling"
# Claude will use openshift-node-operations + openshift-debugging
```

## Troubleshooting

If skills or commands aren't working:
1. Verify plugin is installed: `/plugin list`
2. Check available skills: `/skill list`
3. Try explicitly requesting the skill by name or using slash commands
4. Ensure `oc` CLI is installed and configured

## Contributing

Contributions are welcome! To enhance this plugin:

1. Fork the repository at https://github.com/redhat-community-ai-tools/claude-plugins
2. Make your changes in the `plugins/openshift-ops/` directory
3. Test your changes thoroughly
4. Submit a pull request with a clear description of improvements

## License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Eran Cohen

## Support

For issues, questions, or suggestions:
- Open an issue in the repository
- Reference official OpenShift documentation
- Consult Red Hat support for production clusters

## Related Resources

- [OpenShift Documentation](https://docs.openshift.com/)
- [Red Hat Knowledgebase](https://access.redhat.com/support)
- [OpenShift CLI Reference](https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html)

## Acknowledgments

Inspired by the Kubernetes Operations plugin structure and the Claude Skills framework by Anthropic.
