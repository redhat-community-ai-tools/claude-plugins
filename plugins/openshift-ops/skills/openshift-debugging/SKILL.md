---
name: openshift-debugging
description: Diagnose OpenShift cluster issues using layered triage, failure-mode classification, and prioritized diagnostic workflows.
---

# OpenShift Debugging

## Triage: Identify the Layer

Every cluster issue lives in one of three layers. Identify the layer first — it determines your diagnostic path.

- **Application layer** (pods, deployments, statefulsets): Symptoms are pod-level — CrashLoopBackOff, ImagePullBackOff, Pending, OOMKilled. Start with `oc describe pod` and `oc logs`.
- **Platform layer** (operators, controllers, API server): Symptoms are cluster-wide — degraded ClusterOperators, API timeouts, webhook failures. Start with `oc get co` and check the operator namespace.
- **Infrastructure layer** (nodes, networking, storage): Symptoms are node-level — NotReady nodes, PVC stuck in Pending, cross-node connectivity failures. Start with `oc get nodes` and `oc describe node`.

If unsure which layer: run `oc get co && oc get nodes && oc get pods -A --field-selector status.phase!=Running,status.phase!=Succeeded` — whichever returns problems first tells you the layer.

## Failure Modes and Diagnosis Priority

### CrashLoopBackOff

1. Check `oc logs <pod> --previous` FIRST — current container logs may be from a restart that hasn't crashed yet
2. If logs are empty, the container dies before the app starts — check image entrypoint and command, not application code
3. If logs show OOMKilled, check container memory limits vs actual usage — the limit may be too low for the workload
4. Check liveness probe — an aggressive probe kills healthy-but-slow-starting containers. Look for `failureThreshold` and `initialDelaySeconds`
5. Check ConfigMap/Secret mounts — a missing mount causes immediate crash with no useful log

### Pending Pods

1. Run `oc describe pod` and read the Events section. If there are NO events at all, the scheduler never attempted placement — this is almost always insufficient resources or a nodeSelector/affinity that matches zero nodes
2. If events mention "FailedScheduling" with "Insufficient cpu/memory" — check `oc adm top nodes` for actual vs allocatable
3. If events mention taints — check tolerations on the pod spec, not just node taints
4. If the pod has a PVC — check if the PVC itself is Pending (`oc get pvc`). A Pending PVC blocks the pod indefinitely with no obvious error on the pod

### ImagePullBackOff

Differentiate three distinct causes:
- **Authentication failure** (403/401): Image exists but pull secret is wrong or missing. Check if the secret is linked to the pod's service account with `--for=pull`.
- **Image not found** (404/manifest unknown): Wrong tag, wrong registry, or image was deleted. Verify the exact image:tag exists.
- **Network/registry unreachable** (timeout/connection refused): The node can't reach the registry. This is infrastructure-layer — check node DNS and proxy settings.

### Networking Failures

1. **Service has no endpoints**: Service selector doesn't match pod labels — this is the #1 cause of "connection refused" between services
2. **NetworkPolicy blocking traffic**: The default-deny pattern catches people — if ANY NetworkPolicy selects a pod, only explicitly allowed traffic gets through
3. **DNS resolution fails**: Check if CoreDNS pods are running in `openshift-dns`. If they're crashlooping, nothing in the cluster can resolve service names
4. **Route returns 503**: The backend pods exist but aren't Ready — check readiness probes, not the Route or Ingress config

## Gotchas

- `oc get events -A --sort-by='.lastTimestamp'` is your best first move when you don't know what's wrong — events expire after 1 hour by default, so check early
- A pod in "Completed" status is NOT a failure — Jobs and init containers produce Completed pods normally. Only flag it if the pod should be long-running
- `oc adm top` requires metrics-server. If it returns "metrics not available," the monitoring stack has a problem — that's a platform-layer issue, not whatever you were originally debugging

## When to Use Sibling Skills

- Degraded ClusterOperator → use **openshift-operator-troubleshooting**
- Node NotReady or disk/memory pressure → use **openshift-node-operations**
- Issue appeared during or after a cluster upgrade → use **openshift-cluster-upgrade**
