---
name: openshift-node-operations
description: Node lifecycle management with focus on safe drain procedures, automated-vs-manual infrastructure decisions, and node failure diagnosis.
---

# OpenShift Node Operations

## Key Decision: Automated vs. Manual Infrastructure

This fork affects EVERY node operation. Determine it first.

- **Automated infrastructure** (AWS, Azure, GCP, OpenStack): Nodes are managed by MachineSets. You scale MachineSets, not nodes. The Machine controller handles provisioning, joining, and decommissioning. Never manually delete node objects — delete the Machine object instead.
- **Manual infrastructure** (bare metal, pre-provisioned VMs): You handle the full lifecycle — provisioning RHCOS, ignition config, CSR approval, labeling, and hardware decommission. The cluster only knows about nodes, not machines.

## Safe Drain Procedure

1. **Cordon first, then drain.** If you drain without cordoning, new pods can schedule on the node during drain — you get a moving target that never finishes draining.
2. **Check PDBs before draining.** A PodDisruptionBudget with `maxUnavailable: 0` or `minAvailable` equal to current replica count will block drain silently — it just hangs. Run `oc get pdb -A` and check if any PDB protects pods on your target node.
3. **Use grace periods for stateful workloads.** The default grace period may not be enough for apps that need to flush data or close connections. Set `--grace-period` explicitly for databases and message queues.
4. **`--force` loses data.** Force drain deletes pods with emptyDir volumes without waiting for graceful shutdown. Only use for node decommission, never for maintenance where you expect the node to return.
5. **`--delete-emptydir-data` is required** for most drains because system pods (metrics, logging) use emptyDir. Without this flag, drain refuses to proceed. This is safe — it's the user-data emptyDir volumes you need to worry about, and `--force` is what skips their graceful handling.

## Adding Nodes

### Automated Infrastructure
Scale the MachineSet: `oc scale machineset <name> -n openshift-machine-api --replicas=<N>`. Monitor the Machine status (not just node status) — a Machine stuck in "Provisioning" means the cloud provider call failed (quota, network, AMI issues).

### Manual Infrastructure (Bare Metal)
After provisioning and booting with ignition, watch for **TWO rounds of CSRs**:
1. First CSR: the node-bootstrapper requests a client certificate to join the cluster
2. Second CSR: the node itself requests a serving certificate

Both must be approved. Don't bulk-approve with `xargs` in production without inspecting each CSR — a rogue CSR could grant access to an unauthorized node.

## Removing and Replacing Nodes

### Automated Infrastructure
Delete the **Machine** object, NOT the node object. The MachineSet controller notices the replica count is short and creates a replacement automatically. Deleting just the node object orphans the underlying VM — it keeps running and costing money but the cluster doesn't know about it.

### Manual Infrastructure
Cordon → drain → `oc delete node <name>` → decommission the hardware/VM. The cluster does not manage the underlying infrastructure, so deleting the node object is the final cluster-side step.

### Replacement gotcha
For automated infra, simply deleting the Machine triggers replacement. For manual infra, you must provision a new machine from scratch (RHCOS + ignition + CSR approval + labeling).

## Node Failure Diagnosis Priority

When a node shows NotReady, check in this order (most common causes first):

1. **Network**: Can the node reach the API server? If the kubelet can't phone home, the node goes NotReady even though it's otherwise healthy. Check SDN/OVN pods on the node.
2. **Disk pressure**: `/var/lib/containers/` fills up from accumulated images. Clean with `crictl rmi --prune` via `oc debug node/`. Also check journal size — `journalctl --vacuum-time=3d` reclaims space.
3. **Memory pressure**: Find the top consumers with `oc adm top pods -A` — it may be system workloads (monitoring, logging) not user pods causing pressure.
4. **Kubelet not running**: `oc debug node/<name>`, then `chroot /host && systemctl status kubelet`. Check `journalctl -u kubelet` for the actual error.
5. **Certificate issues**: Expired kubelet certs cause NotReady with no obvious symptoms in pod logs. Check CSRs with `oc get csr` — pending CSRs for the node indicate cert renewal problems.

## Gotchas

- **MachineSet edits only affect NEW machines.** Changing instance type or labels in a MachineSet does not update existing machines. To apply changes, you must delete existing machines and let the MachineSet recreate them.
- **Node labels applied manually are lost on replacement.** If the Machine is deleted and recreated, the new node gets labels from the MachineSet template, not the old node. Always set persistent labels in MachineSet `spec.template.spec.metadata.labels`.
- **`oc debug node/` creates a privileged pod on the node.** If the node can't schedule pods (disk full, kubelet down), debug won't work either. In that case, SSH is the only option.
- **Deleting a node object does NOT deprovision the VM/machine.** The cloud provider keeps billing for it. Always delete the Machine object for automated infrastructure.

## When to Use Sibling Skills

- Machine API operator issues → use **openshift-operator-troubleshooting**
- Node stuck during cluster upgrade → use **openshift-cluster-upgrade** for MCP diagnosis
- Workloads not rescheduling after drain → use **openshift-debugging** for pod-level triage
