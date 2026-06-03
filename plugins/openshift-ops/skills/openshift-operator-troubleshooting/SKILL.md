---
name: openshift-operator-troubleshooting
description: Diagnose degraded cluster operators and failing OLM operators using status-triple analysis, CSV lifecycle debugging, and OLM component triage.
---

# OpenShift Operator Troubleshooting

## First: Which Kind of Operator?

OpenShift has two distinct operator systems with completely different troubleshooting paths:

- **Cluster Operators** (CVO-managed): Core platform components — networking, ingress, authentication, monitoring, etc. Listed by `oc get co`. You cannot install, uninstall, or reinstall these — they are managed by the Cluster Version Operator. Troubleshooting focuses on WHY they're degraded.
- **OLM Operators** (Operator Lifecycle Manager): Add-on operators installed via OperatorHub — things like AMQ, Elasticsearch, custom operators. Listed by `oc get csv -A`. These have a full lifecycle (install, upgrade, uninstall) and troubleshooting focuses on the OLM resource chain.

## Cluster Operator Diagnosis

### The Status Triple

Every ClusterOperator has three status conditions. The combination tells you the severity:

| AVAILABLE | PROGRESSING | DEGRADED | Meaning |
|-----------|-------------|----------|---------|
| True | False | False | Healthy. Normal state. |
| True | True | False | Reconciling. Normal during upgrades. Wait. |
| True | False | True | Partial failure — operator is serving but something is wrong. Investigate but not urgent. |
| True | True | True | Actively broken and trying to fix itself. Monitor closely. |
| False | True | False | Not serving but working on it. May recover. Give it 10-15 minutes before escalating. |
| False | any | True | Full failure. Immediate action required. |

**PROGRESSING=True for >30 minutes** (outside of a cluster upgrade) is abnormal. Something is stuck.

### Diagnosis Priority

1. **Read the status conditions** — they almost always contain the actual error message. `oc get co <name> -o jsonpath='{.status.conditions}'` is more useful than any other command.
2. **Find the operator's namespace** from `relatedObjects` in the CO status. Each operator runs in its own namespace (usually `openshift-<name>`).
3. **Check operator pod logs** in that namespace. The operator log, not the operand log, is where the root cause lives.
4. **Check dependency chains** — some operators depend on others. For example, the console operator depends on authentication; if auth is degraded, console may also degrade as a secondary effect. Fix the root operator first.

## OLM Operator Diagnosis

### CSV Phase Lifecycle

Subscriptions create InstallPlans, which create ClusterServiceVersions (CSVs). The CSV phase tells you where it's stuck:

- **Pending**: Waiting for dependencies (other operators or CRDs). Check `status.requirementStatus` for what's missing.
- **InstallReady**: Dependencies satisfied, about to install. If stuck here, check the install plan.
- **Installing**: Deployment is being created. If stuck >5 minutes, check the deployment and pod status — usually an image pull failure or resource constraint.
- **Succeeded**: Healthy. Normal state.
- **Failed**: Check `status.conditions` for the reason. Common causes: missing CRDs, insufficient RBAC permissions, resource conflicts with another operator.

**Key insight**: Deleting a failed CSV triggers OLM to recreate it from the subscription. This is a valid recovery action when the transient cause (e.g., resource pressure) has been resolved.

### Install Plan Gotchas

- **Manual approval mode**: Install plans pile up silently. Each pending upgrade creates a new install plan that requires explicit approval (`spec.approved: true`). An unapproved install plan blocks ALL future upgrades for that operator.
- **Automatic approval**: Upgrades apply as soon as OLM detects them. If an upgrade breaks your operator, you may not notice until the operand fails. Check CSV phase after auto-upgrades.

### CRD Ownership Conflicts

Two operators claiming the same CRD is a real problem that produces confusing errors. Diagnose by checking `metadata.ownerReferences` on the CRD — it shows which CSV owns it. If the wrong operator owns it, delete the conflicting operator's subscription and CSV, then let the correct operator recreate the CRD.

## OLM Infrastructure Diagnosis

OLM itself has three components in a dependency chain. Failures cascade downward:

1. **OLM Operator** (`openshift-operator-lifecycle-manager`): Manages CSV lifecycle. If it's down, no operator installs or upgrades happen.
2. **Catalog Operator** (same namespace): Resolves dependencies and creates install plans from catalog sources. If it's down, subscriptions stop resolving.
3. **Package Server**: Serves the `packagemanifest` API. If it's down, `oc get packagemanifest` returns empty results and new operator installs appear to have no available operators.

**Catalog source stale?** Delete the catalog pod in `openshift-marketplace` to force a refresh: `oc delete pod -n openshift-marketplace -l olm.catalogSource=<name>`. This is non-destructive — the pod is recreated and re-pulls the catalog index.

## Gotchas

- **Restarting an operator pod rarely fixes the root cause.** Check logs before restarting. If the operator crashes due to a misconfigured CR, it will crash again immediately after restart.
- **OperatorGroup must exist before the subscription.** If you create a subscription in a namespace without an OperatorGroup, nothing happens — no error, no install plan, just silence.
- **Cluster operators cannot be reinstalled.** They are managed by CVO. If a cluster operator is broken, you must fix it in place — deleting and recreating its resources usually makes things worse because CVO fights you.
- **OLM operator logs are in `openshift-operator-lifecycle-manager`**, not the operator's own namespace. When debugging OLM-level issues (install plan stuck, CSV not created), look at OLM's logs, not the failing operator's logs.

## When to Use Sibling Skills

- Operator degraded during upgrade → use **openshift-cluster-upgrade** for upgrade-specific diagnosis
- Operator can't schedule pods (resource pressure) → use **openshift-node-operations** for node capacity analysis
- General cluster health investigation → use **openshift-debugging** for layered triage
