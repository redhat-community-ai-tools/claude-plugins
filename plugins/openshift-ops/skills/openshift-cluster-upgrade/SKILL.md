---
name: openshift-cluster-upgrade
description: Plan and troubleshoot OpenShift cluster upgrades with focus on irreversibility, upgrade-path validation, and stuck-upgrade diagnosis.
---

# OpenShift Cluster Upgrade

## Critical: Upgrades Are Irreversible

OpenShift cluster upgrades cannot be rolled back. There is no "undo." The only recovery from a catastrophically failed upgrade is restoring from an etcd backup, which requires full cluster downtime and loses all changes made after the backup. Prevention is everything — every section below exists to prevent you from starting an upgrade that will fail.

## Pre-Upgrade Gate Checks

Do NOT proceed unless ALL of these pass:
1. **All ClusterOperators healthy**: AVAILABLE=True, PROGRESSING=False, DEGRADED=False for every CO. A single degraded operator can block the upgrade partway through.
2. **All nodes Ready**: A NotReady node will block MCP rollout and stall the upgrade.
3. **No critical alerts firing**: Check Prometheus/AlertManager — active alerts often indicate problems that will worsen during upgrade.
4. **Sufficient resource headroom**: Nodes need spare capacity because pods are evicted and rescheduled one node at a time during worker updates. If the cluster is already at capacity, pods will have nowhere to go.
5. **Certificates not expiring soon**: Expired certs during upgrade cause cascading failures. Check CSRs and certificate secrets.
6. **etcd backup taken**: Since upgrades are irreversible, an etcd snapshot is your only safety net.

If any gate fails, fix it first. Starting an upgrade on a degraded cluster compounds problems.

## Upgrade Path Decision

- **Standard**: Set the channel (stable-4.x), run `oc adm upgrade`, pick the target version. This is the happy path.
- **EUS-to-EUS**: Extended Update Support lets you skip intermediate minor versions, but it's a TWO-HOP process. Example: 4.14 EUS → 4.15 (intermediate) → 4.16 EUS. You must fully complete the first hop before starting the second.
- **Large clusters**: Pause the worker MachineConfigPool before upgrading (`oc patch mcp worker --type merge -p '{"spec":{"paused":true}}'`). This lets the control plane update first. Then unpause workers in batches by unpausing one MCP at a time or by using node selectors. This prevents all workers from draining simultaneously.
- **Air-gapped**: Mirror the release images to your internal registry first, create an ImageContentSourcePolicy, then upgrade with `--to-image` pointing to the mirrored image.

## What Happens During an Upgrade (Three Phases)

1. **CVO updates cluster operators**: Downloads new release image, rolls out updated operators. Watch with `oc get co`.
2. **Control plane nodes update**: API servers, controller managers, schedulers update one control plane node at a time. Brief API unavailability is normal.
3. **Worker nodes update**: MachineConfigOperator renders new configs, nodes drain and reboot one at a time. This is the slowest phase. Watch with `oc get mcp` — UPDATED=True, UPDATING=False, DEGRADED=False means complete.

## Stuck Upgrade Diagnosis

Follow this priority chain — each step is the most likely cause at that point:

1. **Check clusterversion conditions**: `oc describe clusterversion` — the status conditions usually contain the actual error message explaining what's blocked
2. **Find the degraded ClusterOperator**: `oc get co` — look for DEGRADED=True or AVAILABLE=False. This is the blocker ~60% of the time
3. **Check MCP state**: `oc get mcp` — if worker or master pool shows DEGRADED=True, a node failed to apply the new machine config
4. **Check for nodes that won't drain**: A node stuck in SchedulingDisabled with pods still running means drain is blocked. Check for PodDisruptionBudgets (`oc get pdb -A`) that prevent eviction — a PDB with `maxUnavailable: 0` will block drain forever
5. **Check machine-config-daemon on the stuck node**: If MCP is degraded, the machine-config-daemon log on the specific node usually has the error. Use `oc logs -n openshift-machine-config-operator` with the node-specific daemon pod
6. **Force drain as last resort**: Only for decommission scenarios. Force drain loses data in emptyDir volumes and ignores PDBs

## Gotchas

- `--force` on `oc adm upgrade` bypasses version-graph safety checks. It does NOT force a stuck upgrade to continue. Almost never correct.
- `--allow-explicit-upgrade` is only for upgrading to versions not in the recommended graph. Don't use it for normal upgrades.
- Worker node updates are intentionally slow (one node at a time). A 20-node cluster can take 2+ hours for the worker phase alone. Don't panic at slow progress.
- `oc adm upgrade --clear` cancels a pending upgrade but does NOT revert changes already applied. Use only if the upgrade hasn't started yet.
- If the upgrade started but stalled, you must fix the blocker and let it continue — you cannot cancel mid-upgrade.

## When to Use Sibling Skills

- ClusterOperator degraded during upgrade → use **openshift-operator-troubleshooting** to diagnose the specific operator
- Node won't drain or is NotReady → use **openshift-node-operations** for drain/node diagnosis
- General cluster health investigation pre-upgrade → use **openshift-debugging** for triage
