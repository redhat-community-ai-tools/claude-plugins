# OSAC Debugging Guide

## Diagnosis Checklist

When a resource is stuck or not progressing, work through these steps in order:

### Step 1: Check fulfillment API state
```bash
curl -sk -H "Authorization: Bearer $TOKEN" \
  "https://$ROUTE/api/fulfillment/v1/<resource>/<id>" | jq '{state: .status.state, deletion: .metadata.deletion_timestamp}'
```

### Step 2: Check K8s CR state
```bash
kubectl get <crd> -n $NAMESPACE -o wide
kubectl get <crd> -n $NAMESPACE <name> -o jsonpath='{.status}' | jq
```

### Step 3: Check finalizers
```bash
kubectl get <crd> -n $NAMESPACE <name> -o jsonpath='{.metadata.finalizers}'
```

### Step 4: Check AAP job status (from CR)
```bash
kubectl get <crd> -n $NAMESPACE <name> -o jsonpath='{.status.jobs}' | jq
```

### Step 5: Check operator logs for errors
```bash
kubectl logs -n $NAMESPACE deploy/osac-operator-controller-manager | grep -i error | tail -20
```

### Step 6: Check controller logs
```bash
kubectl logs -n $NAMESPACE deploy/fulfillment-controller | grep -i error | tail -20
```

---

## Common Stuck Scenarios

### Resource stuck in DELETING (fulfillment API)

**Cause:** Fulfillment controller finalizer not removed. Usually because K8s CR is gone but fulfillment DB record still has finalizer.

**Safe fix — signal the resource to trigger re-reconciliation:**
```bash
grpcurl -insecure -H "Authorization: Bearer $TOKEN" \
  -d '{"id": "<id>"}' $ROUTE:443 osac.private.v1.<Resources>/Signal
```

### K8s CR stuck with finalizers

**Cause:** AAP deprovision job failed or is still running.

**Diagnosis:**
```bash
kubectl get <crd> -n $NAMESPACE <name> -o jsonpath='{.status.jobs}' | jq '.[] | select(.type=="deprovision")'
```

**If job failed (old code / stale template) — confirm with user before proceeding:**
```bash
kubectl patch <crd> -n $NAMESPACE <name> --type=json \
  -p '[{"op":"remove","path":"/metadata/finalizers"}]'
```

**If job is running:** Wait or check AAP UI for the job. Do not remove finalizers while a job is active.

### Subnet stuck — CUDN has OVN finalizer

**Cause:** OVN controller re-adds `k8s.ovn.org/user-defined-network-protection` finalizer.

**Fix — remove finalizer and delete in quick succession:**
```bash
kubectl patch clusteruserdefinednetwork <name> --type=json \
  -p '[{"op":"remove","path":"/metadata/finalizers"}]' && \
kubectl delete clusteruserdefinednetwork <name>
```

### Controller not processing events

**Cause:** Controller started before gRPC server was ready, watch stream failed.

**Fix:**
```bash
kubectl rollout restart -n $NAMESPACE deploy/fulfillment-controller
```

### ComputeInstance stuck in STARTING

**Possible causes:**
- VM created in wrong namespace (MGMT-23626)
- AAP provision job still running
- Tenant CR not found
- Image pull failure

**Diagnosis:**
```bash
kubectl get vm -A -o wide
kubectl get vmi -A -o wide
kubectl get dv -A
kubectl get events -n <vm-namespace> --sort-by='.lastTimestamp' | tail -20
```

---

## AAP Job Debugging

### Check Job via API

```bash
AAP_ROUTE=$(kubectl get route -n $NAMESPACE osac-aap -o jsonpath='{.spec.host}')
AAP_PASS=$(kubectl get secret -n $NAMESPACE osac-aap-admin-password -o jsonpath='{.data.password}' | base64 -d)

# Get job details
curl -sk -u admin:$AAP_PASS "https://$AAP_ROUTE/api/v2/jobs/<job-id>/" | jq '{status, started, finished, elapsed}'

# Get job stdout/logs
curl -sk -u admin:$AAP_PASS "https://$AAP_ROUTE/api/v2/jobs/<job-id>/stdout/?format=txt"

# List recent jobs
curl -sk -u admin:$AAP_PASS "https://$AAP_ROUTE/api/v2/jobs/?order_by=-id&page_size=10" | jq '.results[] | {id, name: .name, status, started}'
```

### AAP Job Templates (prefix-based for networking)

| Template | Resource | Action |
|----------|----------|--------|
| `{prefix}-create-virtual-network` | VirtualNetwork | Provision |
| `{prefix}-delete-virtual-network` | VirtualNetwork | Deprovision |
| `{prefix}-create-subnet` | Subnet | Provision (creates Namespace + CUDN) |
| `{prefix}-delete-subnet` | Subnet | Deprovision |
| `{prefix}-create-security-group` | SecurityGroup | Provision |
| `{prefix}-delete-security-group` | SecurityGroup | Deprovision |
| `{prefix}-create-compute-instance` | ComputeInstance | Provision (creates VM) |
| `{prefix}-delete-compute-instance` | ComputeInstance | Deprovision |

### Common AAP Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Job fails with "role not found" | Template role renamed or missing from EE | Rebuild EE image, re-vendor collections |
| Bootstrap job stuck | AAP not ready, license missing | Check `kubectl logs job/aap-bootstrap`, verify license.zip |
| Webhook not triggering | EDA activation down | Check EDA pod, restart activation |
| Job stays Pending | Instance group pod can't start | Check pod spec, SA, secrets in controller.yml |
