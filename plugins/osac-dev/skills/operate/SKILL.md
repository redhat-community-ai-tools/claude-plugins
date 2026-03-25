---
name: operate
description: Deploy, debug, and operate the OSAC platform — covers building images, deploying via kustomize, debugging stuck resources, checking logs, fixing finalizer issues, signaling resources, AAP job troubleshooting, and end-to-end cleanup. Use when the user says 'deploy', 'debug', 'why is X stuck', 'check logs', 'clean up', 'restart controller', 'signal resource', 'check AAP job', 'build images', or asks about OSAC operational issues.
---

# OSAC Operations

Deploy, debug, and operate all OSAC platform components.

**Reference files** (read only the ones you need):
- `references/architecture.md` — Component overview, pod table, resource hierarchy
- `references/commands.md` — Build, deploy, health checks, logs, API operations
- `references/debugging.md` — Stuck resource diagnosis, common scenarios, AAP job failures
- `references/crd-reference.md` — Finalizers, annotations, env vars, TLS certs

## Before You Start

1. **Determine the namespace.** If the user didn't specify one, discover it:
   ```bash
   kubectl get ns | grep -E 'osac|fulfillment'
   ```
   If multiple namespaces exist, ask the user which one. Set `NAMESPACE=<result>` for all subsequent commands.

2. **Set up route and token** (needed for most operations):
   ```bash
   ROUTE=$(kubectl get route -n $NAMESPACE fulfillment-api -o jsonpath='{.spec.host}')
   TOKEN=$(kubectl create token -n $NAMESPACE admin)
   ```

3. **Check kubectl access.** If `kubectl cluster-info` fails, ask the user to configure their kubeconfig before proceeding.

## Confirmation Rules

Operations in OSAC can leave orphaned cloud resources if done wrong. These rules prevent that:

- **Before deleting any resource:** List what will be deleted, show it to the user, and ask "Should I proceed with deleting these?" Wait for confirmation.
- **Before removing any finalizer:** First check if a deprovision AAP job is still running for that resource. If it is, tell the user and wait. A running deprovision job that loses its finalizer will leave orphaned infrastructure.
- **Before bulk operations:** Always inventory first, show the user the count, and confirm.

These aren't optional guardrails — removing a finalizer on a resource with an active job, or deleting a VirtualNetwork before its Subnets are gone, causes real operational problems that are painful to clean up.

## Workflows

### Debugging Stuck Resources

This is the most common operational task. A resource is "stuck" when it stays in CREATING, DELETING, or another transitional state for more than a few minutes.

**Always follow this order:**

**Step 1: Try signaling first (safest).** Signaling triggers re-reconciliation without any manual state changes. This fixes most issues — especially when the controller missed an event or the watch stream broke.

```bash
grpcurl -insecure -H "Authorization: Bearer $TOKEN" \
  -d '{"id": "<resource-id>"}' $ROUTE:443 osac.private.v1.<Resources>/Signal
```

Replace `<Resources>` with `Subnets`, `VirtualNetworks`, `ComputeInstances`, or `SecurityGroups`.

Wait 1-2 minutes after signaling. If the resource progresses, you're done.

**Step 2: If signaling didn't help, diagnose.** Read `references/debugging.md` and follow the Diagnosis Checklist:
1. Check fulfillment API state (is deletion_timestamp set?)
2. Check K8s CR state and finalizers
3. Check AAP job status — is a deprovision job running, failed, or missing?
4. Check for CUDN finalizer issues (subnets only)
5. Check operator and controller logs for errors

**Step 3: Apply the targeted fix based on diagnosis.** Common scenarios:

- **CUDN stuck with OVN finalizer** (subnets) → Patch and delete CUDN in quick succession. See `references/debugging.md`.
- **AAP job failed** → Confirm no job is running, then ask user: "The deprovision job failed. I need to remove the finalizer from the CR to unblock deletion. This means the AAP cleanup won't run — should I proceed?"
- **K8s CR gone but API record stuck** → Signal the resource (step 1 should have caught this).
- **Controller not processing events** → Restart: `kubectl rollout restart -n $NAMESPACE deploy/fulfillment-controller`

**Step 4: Verify the fix.** After any fix, confirm the resource is actually gone from both the API and K8s. Check logs for new errors.

### Cleanup (Delete All Resources)

**Step 1: Inventory.** List everything and show the user:

```bash
echo "=== Compute Instances ==="
curl -sk -H "Authorization: Bearer $TOKEN" "https://$ROUTE/api/fulfillment/v1/compute_instances" | jq '[.items[] | {id, name: .metadata.name, state: .status.state}]'
echo "=== Subnets ==="
curl -sk -H "Authorization: Bearer $TOKEN" "https://$ROUTE/api/fulfillment/v1/subnets" | jq '[.items[] | {id, name: .metadata.name, state: .status.state}]'
echo "=== Virtual Networks ==="
curl -sk -H "Authorization: Bearer $TOKEN" "https://$ROUTE/api/fulfillment/v1/virtual_networks" | jq '[.items[] | {id, name: .metadata.name, state: .status.state}]'
```

Tell the user: "I found X compute instances, Y subnets, and Z virtual networks. I'll delete them in that order (CIs first, then subnets, then VNs) since they have dependencies. Should I proceed?"

**Step 2: Delete in dependency order.** ComputeInstances → Subnets → VirtualNetworks. Wait for each level to fully delete before starting the next. See `references/commands.md` Section 5 for the deletion loops.

**Step 3: Handle stuck resources.** If anything is still in DELETING after 2-3 minutes:
- Try signaling first
- Check if deprovision jobs are running (do NOT remove finalizers if they are)
- If jobs are done/failed, ask user before removing finalizers
- For CUDNs with OVN finalizers, patch and delete in quick succession

**Step 4: Restart controller and verify.** After cleanup:
```bash
kubectl rollout restart -n $NAMESPACE deploy/fulfillment-controller
```
Then verify both API and K8s sides show zero resources.

### Deploy / Update Images

Read `references/commands.md` Section 1 for the full details. The short version:

1. Edit `osac-installer/overlays/<name>/kustomization.yaml` — update `newTag` for the relevant images
2. Preview: `kustomize build osac-installer/overlays/<name> | grep image:`
3. Apply: `kubectl apply -k osac-installer/overlays/<name>`
4. Watch rollouts: `kubectl rollout status -n $NAMESPACE deploy/<deployment-name>`
5. Health check after rollout completes

### Check Health / Status

Read `references/commands.md` Section 2. Quick checks:
- REST: `curl -sk https://$ROUTE/healthz`
- gRPC: `grpcurl -insecure -H "Authorization: Bearer $TOKEN" $ROUTE:443 grpc.health.v1.Health/Check`
- Operator: port-forward to 8081, check `/healthz` and `/readyz`

If unhealthy, pivot to the debugging workflow above.

### Check Logs

Read `references/commands.md` Section 3. Start with the component the user asked about:
- `fulfillment-grpc-server` — API issues
- `fulfillment-controller` — reconciliation issues
- `osac-operator-controller-manager` — CR/AAP issues

Filter for errors first: `kubectl logs -n $NAMESPACE deploy/<name> | grep -i error | tail -20`

### AAP Job Issues

Read `references/debugging.md` — AAP Job Debugging section. Get the AAP route and admin password, then check job status and logs via the AAP API.
