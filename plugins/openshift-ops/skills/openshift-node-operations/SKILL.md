---
name: openshift-node-operations
description: Comprehensive guide for OpenShift node lifecycle management including adding/removing nodes, cordoning/draining, machine management, node maintenance, and troubleshooting node issues. Use when managing cluster capacity, performing node maintenance, or resolving node-level problems.
---

# OpenShift Node Operations

This skill provides guidance for managing OpenShift nodes throughout their lifecycle, from provisioning to decommissioning, including maintenance and troubleshooting.

## When to Use This Skill

- Adding or removing nodes from the cluster
- Performing node maintenance or reboots
- Troubleshooting node health issues
- Managing node capacity and scaling
- Handling node failures or replacements
- Cordoning and draining nodes safely
- Managing machine and machine sets (for automated infrastructure)

## Node Lifecycle Operations

### Step 1: Viewing Node Information

```bash
# List all nodes
oc get nodes
oc get nodes -o wide

# Get detailed node information
oc describe node <node-name>

# View node labels
oc get nodes --show-labels

# Check node resource usage
oc adm top nodes

# Get node allocatable resources
oc describe nodes | grep -A 5 "Allocatable:"

# View nodes with specific roles
oc get nodes -l node-role.kubernetes.io/worker
oc get nodes -l node-role.kubernetes.io/master
```

### Step 2: Adding Nodes to Cluster

**For Automated Infrastructure (AWS, Azure, GCP, OpenStack)**

```bash
# View existing machine sets
oc get machinesets -n openshift-machine-api

# Scale machine set to add nodes
oc scale machineset <machineset-name> -n openshift-machine-api --replicas=<new-count>

# Create new machine set (for different instance types/zones)
oc get machineset <existing-machineset> -n openshift-machine-api -o yaml > new-machineset.yaml
# Edit new-machineset.yaml (change name, replicas, instance type, etc.)
oc create -f new-machineset.yaml

# Monitor machine creation
oc get machines -n openshift-machine-api -w

# Verify nodes join cluster
oc get nodes -w
```

**For Bare Metal/Manual Infrastructure**

1. Prepare the node with RHCOS
2. Configure bootstrap ignition
3. Start the node
4. Approve pending CSRs:

```bash
# Watch for pending CSRs
oc get csr

# Approve CSRs
oc adm certificate approve <csr-name>

# Approve all pending CSRs (use with caution)
oc get csr -o name | xargs oc adm certificate approve

# Verify node joined
oc get nodes
```

### Step 3: Node Labeling and Taints

**Labels**

```bash
# Add label to node
oc label node <node-name> <key>=<value>

# Remove label from node
oc label node <node-name> <key>-

# Update existing label
oc label node <node-name> <key>=<new-value> --overwrite

# Label multiple nodes
oc label nodes -l <selector> <key>=<value>

# Common labels
oc label node <node-name> node-role.kubernetes.io/infra=""
oc label node <node-name> node-role.kubernetes.io/storage=""
oc label node <node-name> environment=production
```

**Taints and Tolerations**

```bash
# Add taint to node
oc adm taint node <node-name> <key>=<value>:<effect>
# Effects: NoSchedule, PreferNoSchedule, NoExecute

# Remove taint from node
oc adm taint node <node-name> <key>:<effect>-

# Examples
oc adm taint node <node-name> dedicated=gpu:NoSchedule
oc adm taint node <node-name> maintenance=true:NoExecute
oc adm taint node <node-name> special=true:PreferNoSchedule

# View node taints
oc describe node <node-name> | grep Taints
```

### Step 4: Cordoning Nodes

Cordoning prevents new pods from being scheduled on a node:

```bash
# Cordon a node (mark as unschedulable)
oc adm cordon <node-name>

# Uncordon a node (mark as schedulable)
oc adm uncordon <node-name>

# Cordon multiple nodes
oc adm cordon <node1> <node2> <node3>

# Verify node status
oc get nodes
# Look for "SchedulingDisabled" in STATUS column
```

### Step 5: Draining Nodes

Draining safely evicts pods from a node:

```bash
# Drain a node (standard)
oc adm drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Drain with grace period
oc adm drain <node-name> --ignore-daemonsets --delete-emptydir-data --grace-period=300

# Drain with timeout
oc adm drain <node-name> --ignore-daemonsets --delete-emptydir-data --timeout=5m

# Force drain (use with extreme caution)
oc adm drain <node-name> --ignore-daemonsets --delete-emptydir-data --force

# Dry run to see what would be drained
oc adm drain <node-name> --dry-run=client

# Skip waiting for deletion
oc adm drain <node-name> --ignore-daemonsets --delete-emptydir-data --skip-wait-for-delete-timeout=0
```

**Best Practices for Draining:**
1. Cordon first, then drain
2. Monitor pod eviction progress
3. Check for PodDisruptionBudgets that might block draining
4. Consider grace periods for stateful applications
5. Verify workloads are rescheduled successfully

### Step 6: Node Maintenance

**Standard Maintenance Workflow:**

```bash
# 1. Cordon the node
oc adm cordon <node-name>

# 2. Drain the node
oc adm drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 3. Verify pods have been evicted
oc get pods -A -o wide | grep <node-name>

# 4. Perform maintenance on the node
# - SSH to node or use oc debug
# - Apply updates, reboot, etc.

# 5. Verify node is back and healthy
oc get nodes

# 6. Uncordon the node
oc adm uncordon <node-name>

# 7. Verify workloads are scheduling
oc get pods -A -o wide | grep <node-name>
```

**Accessing Node for Maintenance:**

```bash
# Debug node (creates privileged pod)
oc debug node/<node-name>

# Once in debug shell
chroot /host

# Common maintenance commands
systemctl status kubelet
systemctl restart kubelet
journalctl -u kubelet -f
rpm-ostree status

# Exit debug session
exit
```

### Step 7: Removing Nodes

**For Automated Infrastructure:**

```bash
# Scale down machine set
oc scale machineset <machineset-name> -n openshift-machine-api --replicas=<new-count>

# Delete specific machine
oc delete machine <machine-name> -n openshift-machine-api

# Monitor deletion
oc get machines -n openshift-machine-api -w
oc get nodes -w
```

**For Manual Infrastructure:**

```bash
# 1. Cordon and drain the node
oc adm cordon <node-name>
oc adm drain <node-name> --ignore-daemonsets --delete-emptydir-data --force

# 2. Delete the node from cluster
oc delete node <node-name>

# 3. Power down or repurpose the physical/virtual machine
```

### Step 8: Node Replacement

**Replacing Failed Node (Automated Infrastructure):**

```bash
# Delete failed machine
oc delete machine <machine-name> -n openshift-machine-api

# Machine set controller will create replacement automatically
oc get machines -n openshift-machine-api -w

# Approve CSRs if needed
oc get csr
oc adm certificate approve <csr-name>
```

**Replacing Failed Node (Manual Infrastructure):**

1. Delete old node: `oc delete node <node-name>`
2. Provision new node with RHCOS
3. Join new node to cluster
4. Approve CSRs
5. Apply role and environment labels (see Step 3)

## Machine and Machine Set Management

### Working with Machines

```bash
# List all machines
oc get machines -n openshift-machine-api

# Get machine details
oc describe machine <machine-name> -n openshift-machine-api

# Delete machine (will be recreated by machine set)
oc delete machine <machine-name> -n openshift-machine-api

# View machine status
oc get machines -n openshift-machine-api -o wide
```

### Working with Machine Sets

```bash
# List machine sets
oc get machinesets -n openshift-machine-api

# Describe machine set
oc describe machineset <machineset-name> -n openshift-machine-api

# Scale machine set
oc scale machineset <machineset-name> -n openshift-machine-api --replicas=<count>

# Edit machine set
oc edit machineset <machineset-name> -n openshift-machine-api

# Delete machine set
oc delete machineset <machineset-name> -n openshift-machine-api
```

### Creating Custom Machine Sets

```yaml
# Example: Create infra node machine set
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: <cluster-id>-infra-<zone>
  namespace: openshift-machine-api
spec:
  replicas: 3
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <cluster-id>
      machine.openshift.io/cluster-api-machineset: <cluster-id>-infra-<zone>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <cluster-id>
        machine.openshift.io/cluster-api-machine-role: infra
        machine.openshift.io/cluster-api-machine-type: infra
        machine.openshift.io/cluster-api-machineset: <cluster-id>-infra-<zone>
    spec:
      metadata:
        labels:
          node-role.kubernetes.io/infra: ""
      taints:
        - key: node-role.kubernetes.io/infra
          effect: NoSchedule
      # Provider-specific configuration here
```

### Auto-Scaling

```bash
# View machine autoscaler
oc get machineautoscaler -n openshift-machine-api

# Create machine autoscaler
oc create -f machine-autoscaler.yaml

# View cluster autoscaler
oc get clusterautoscaler

# Edit autoscaler settings
oc edit clusterautoscaler default
```

## Troubleshooting Node Issues

### Node Not Ready

```bash
# Check node status
oc get nodes
oc describe node <node-name>

# Check node conditions
oc get node <node-name> -o jsonpath='{.status.conditions}'

# Common causes:
# - Network issues
# - Disk pressure
# - Memory pressure
# - kubelet not running
# - Certificate issues

# Debug the node
oc debug node/<node-name>
chroot /host
systemctl status kubelet
journalctl -u kubelet -n 100
```

### Node Disk Pressure

```bash
# Check disk usage on node
oc debug node/<node-name>
chroot /host
df -h

# Clean up images
crictl rmi --prune

# Check image registry cache
du -sh /var/lib/containers/

# Clear logs
journalctl --vacuum-time=3d
```

### Node Memory Pressure

```bash
# Check memory usage
oc adm top nodes
oc describe node <node-name> | grep -A 10 "Allocated resources"

# Identify high memory pods
oc adm top pods -A | sort -k 4 -nr | head -20

# Check for memory leaks
oc debug node/<node-name>
chroot /host
free -h
top
```

### Node Network Issues

```bash
# Check SDN/CNI pods on node
oc get pods -n openshift-sdn -o wide | grep <node-name>
oc get pods -n openshift-ovn-kubernetes -o wide | grep <node-name>

# Check network operator
oc get clusteroperator network

# Debug network from node
oc debug node/<node-name>
chroot /host
ip addr
ip route
ping <api-server>
```

### CSR Issues

```bash
# View pending CSRs
oc get csr | grep Pending

# Check CSR details
oc describe csr <csr-name>

# Approve CSR
oc adm certificate approve <csr-name>

# Automated approval (for testing/dev only)
oc get csr -o name | xargs oc adm certificate approve
```

## Best Practices

1. **Always Cordon Before Drain**: Prevent new pods from scheduling
2. **Respect PodDisruptionBudgets**: Don't force drain unless necessary
3. **Monitor Workload Rescheduling**: Ensure pods move successfully
4. **Use Grace Periods**: Allow apps time to shut down cleanly
5. **Label Nodes by Role and Purpose**: Apply role (infra, storage, gpu) and environment (production, staging) labels
6. **Test in Non-Production**: Practice node operations in dev/staging
7. **Maintain Node Capacity**: Keep enough nodes for workload distribution
8. **Document Changes**: Record why nodes were added/removed/modified
9. **Use Machine Sets**: Leverage automation for infrastructure platforms
10. **Monitor Machine Health**: Watch for machine provisioning failures

## Useful Commands

```bash
# Quick node health check
oc get nodes && oc get machines -n openshift-machine-api

# Find pods on a specific node
oc get pods -A -o wide --field-selector spec.nodeName=<node-name>

# Count pods per node
oc get pods -A -o wide | awk '{print $8}' | sort | uniq -c

# View node capacity
oc get nodes -o custom-columns=NAME:.metadata.name,CPU:.status.capacity.cpu,MEMORY:.status.capacity.memory

# Check PodDisruptionBudgets
oc get pdb -A

# Emergency node reset (use with extreme caution)
oc adm drain <node-name> --force --delete-emptydir-data --ignore-daemonsets --skip-wait-for-delete-timeout=0
```

## Related Skills

- `openshift-debugging` - For troubleshooting node-related issues
- `openshift-cluster-upgrade` - Nodes are updated during cluster upgrades
- `openshift-operator-troubleshooting` - Machine API operator issues
