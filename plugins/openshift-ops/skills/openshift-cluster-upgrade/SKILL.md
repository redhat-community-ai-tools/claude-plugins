---
name: openshift-cluster-upgrade
description: Comprehensive guide for planning, executing, and troubleshooting OpenShift cluster upgrades including pre-upgrade checks, upgrade procedures, and post-upgrade validation. Use when upgrading clusters, investigating upgrade failures, or preparing upgrade strategies.
---

# OpenShift Cluster Upgrade

This skill provides systematic guidance for upgrading OpenShift clusters safely and effectively, including preparation, execution, monitoring, and troubleshooting.

## When to Use This Skill

- Planning cluster version upgrades
- Executing cluster upgrades
- Troubleshooting stuck or failed upgrades
- Validating cluster health post-upgrade
- Upgrading operators and cluster components
- Managing upgrade channels and versions

## Upgrade Workflow

### Step 1: Pre-Upgrade Planning

**Review Release Notes**
- Check what's new in the target version
- Review known issues and breaking changes
- Verify deprecated API versions
- Check operator compatibility

**Determine Upgrade Path**
```bash
# Check current version
oc get clusterversion

# View available upgrades
oc adm upgrade

# Check upgrade graph
oc adm upgrade --to-image=<registry-url> --allow-explicit-upgrade
```

**Backup Critical Components**
```bash
# Backup etcd
oc get etcd -o yaml > etcd-backup.yaml

# Take etcd snapshot (on control plane node)
sudo /usr/local/bin/cluster-backup.sh /home/core/backup

# Backup critical configurations
oc get all -n <namespace> -o yaml > namespace-backup.yaml
oc get cm -A -o yaml > configmaps-backup.yaml
oc get secret -A -o yaml > secrets-backup.yaml
```

### Step 2: Pre-Upgrade Health Checks

```bash
# Check cluster operators
oc get clusteroperators
# Ensure all are AVAILABLE=True, PROGRESSING=False, DEGRADED=False

# Check node health
oc get nodes
# All nodes should be Ready

# Check cluster version status
oc get clusterversion -o yaml

# Check for failing pods
oc get pods -A --field-selector status.phase!=Running,status.phase!=Succeeded

# Check alerts
oc get prometheus -n openshift-monitoring
# Review any critical alerts

# Check certificate expiration
oc get csr
oc get secrets -A | grep certificate

# Verify resource availability
oc adm top nodes
oc describe nodes | grep -A 5 "Allocated resources"
```

### Step 3: Upgrade Channel Management

```bash
# View current channel
oc get clusterversion -o jsonpath='{.items[0].spec.channel}'

# Update channel if needed
oc adm upgrade channel <channel-name>
# Channels: stable-4.x, fast-4.x, eus-4.x, candidate-4.x

# Available channels
# stable-4.x: Production-ready releases
# fast-4.x: Early access to stable releases
# eus-4.x: Extended Update Support (for specific versions)
# candidate-4.x: Release candidates (testing only)
```

### Step 4: Initiate Upgrade

**Method 1: Web Console**
1. Navigate to Administration → Cluster Settings
2. Click "Update" in the Update Status section
3. Select target version
4. Click "Update"

**Method 2: CLI**
```bash
# Upgrade to latest in channel
oc adm upgrade --to-latest=true

# Upgrade to specific version
oc adm upgrade --to=<version>

# Force upgrade (use with caution)
oc adm upgrade --to=<version> --force

# Allow explicit upgrade (for non-standard paths)
oc adm upgrade --to=<version> --allow-explicit-upgrade
```

### Step 5: Monitor Upgrade Progress

```bash
# Watch cluster version status
oc get clusterversion -w

# Monitor cluster operators
watch oc get clusteroperators

# Check upgrade progress details
oc describe clusterversion

# Monitor Machine Config Operator
oc get mcp
oc get mcp -w

# Watch node updates
oc get nodes -w

# Check specific operator progress
oc get co <operator-name> -o yaml

# View upgrade events
oc get events -A --sort-by='.lastTimestamp' | grep -i upgrade
```

### Step 6: Understand Upgrade Phases

**Phase 1: Cluster Version Operator Updates**
- Downloads new release image
- Updates cluster operators

**Phase 2: Control Plane Update**
- Updates API servers
- Updates controller managers
- Updates schedulers
- One control plane node at a time

**Phase 3: Worker Node Update**
- Machine Config Operator renders new configs
- Nodes drain and reboot one by one
- Pods are rescheduled

```bash
# Monitor MCP status during worker updates
oc get mcp
# UPDATED=True, UPDATING=False, DEGRADED=False indicates completion

# Check which nodes are updating
oc get nodes -o wide
# Look for SchedulingDisabled and version changes
```

### Step 7: Post-Upgrade Validation

```bash
# Verify new version
oc get clusterversion
oc get nodes

# Check all operators are healthy
oc get clusteroperators

# Verify critical workloads
oc get pods -A
oc get deployments -A
oc get statefulsets -A

# Check for deprecated APIs
oc get apiservices
oc api-resources

# Run cluster diagnostics
oc adm must-gather

# Test application functionality
# - Access applications through routes
# - Verify database connections
# - Check persistent storage
# - Test CI/CD pipelines
```

### Step 8: Operator Upgrades

```bash
# Check operator subscriptions
oc get subscription -A

# View available operator updates
oc get csv -A

# Update operator via subscription
oc patch subscription <subscription-name> -n <namespace> \
  --type='merge' -p '{"spec":{"channel":"<new-channel>"}}'

# Manual approval for operator upgrades
oc patch installplan <install-plan-name> -n <namespace> \
  --type='merge' -p '{"spec":{"approved":true}}'

# Check operator upgrade status
oc get csv -n <namespace>
oc describe csv <csv-name> -n <namespace>
```

## Troubleshooting Upgrades

### Stuck Upgrade

```bash
# Check cluster version for errors
oc describe clusterversion

# Check failing operator
oc get co
oc describe co <degraded-operator>

# Check operator logs
oc logs -n <operator-namespace> deployment/<operator-deployment>

# Check machine config pools
oc get mcp
oc describe mcp <mcp-name>

# Check nodes that won't drain
oc get nodes
oc describe node <node-name>

# Force drain if necessary (use with caution)
oc adm drain <node-name> --ignore-daemonsets --delete-emptydir-data --force
```

### Failed Cluster Operator

```bash
# Get operator details
oc describe co <operator-name>

# Check related resources
oc get all -n <operator-namespace>

# Review operator logs
oc logs -n <operator-namespace> -l app=<operator-app>

# Check for resource constraints
oc describe nodes
oc adm top nodes

# Restart operator pods if needed
oc delete pod -n <operator-namespace> -l app=<operator-app>
```

### Node Not Updating

```bash
# Check MCP status
oc get mcp
oc describe mcp worker

# Check machine config daemon logs
oc logs -n openshift-machine-config-operator -l k8s-app=machine-config-daemon

# Check node cordoning
oc get nodes
oc uncordon <node-name>

# Check PDBs preventing drain
oc get pdb -A
oc describe pdb <pdb-name> -n <namespace>

# Check for stuck pods
oc get pods -A --field-selector spec.nodeName=<node-name>
```

### Rollback Considerations

**Important**: OpenShift upgrades cannot be automatically rolled back. Prevention is critical.

```bash
# If upgrade fails, investigate and fix
# Do NOT attempt to change version backward

# Restore from etcd backup only as last resort
# This is a destructive operation requiring cluster downtime

# For critical failures:
1. Open Red Hat support case
2. Provide must-gather data
3. Follow support guidance
```

## Best Practices

### Before Upgrading

1. **Test in Non-Production**: Upgrade dev/staging clusters first
2. **Review Compatibility**: Check application and operator compatibility
3. **Backup Everything**: etcd, PVs, configurations, and application data
4. **Check Resources**: Ensure sufficient CPU, memory, and storage
5. **Review Maintenance Window**: Plan for 2-4 hours minimum
6. **Notify Stakeholders**: Inform teams of maintenance window
7. **Verify Health**: Ensure cluster is completely healthy

### During Upgrade

1. **Monitor Actively**: Watch cluster operators and nodes
2. **Don't Interrupt**: Let upgrade complete naturally
3. **Check Alerts**: Monitor for new critical alerts
4. **Document Issues**: Record any problems for investigation
5. **Be Patient**: Worker node updates take time (one node at a time)

### After Upgrade

1. **Validate Functionality**: Test critical applications
2. **Check Deprecations**: Review and address API deprecation warnings
3. **Update Documentation**: Record new version and any issues encountered
4. **Monitor for Days**: Watch for delayed issues
5. **Update Operators**: Upgrade operators to compatible versions

For upgrade strategies (EUS-to-EUS, large clusters, air-gapped) and quick commands, see `references/upgrade-strategies.md`.

## Related Skills

- `openshift-debugging` - For troubleshooting upgrade-related issues
- `openshift-operator-troubleshooting` - For operator-specific upgrade problems
- `openshift-node-operations` - For node management during upgrades
