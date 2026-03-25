# OSAC CRD Reference

## Finalizers

| CRD | Operator Finalizer | Feedback Finalizer |
|-----|-------------------|-------------------|
| VirtualNetwork | `osac.openshift.io/virtualnetwork-finalizer` | `fulfillment-controller` |
| Subnet | `osac.openshift.io/subnet-finalizer` | `fulfillment-controller` |
| SecurityGroup | `osac.openshift.io/securitygroup-finalizer` | `fulfillment-controller` |
| ComputeInstance | `osac.openshift.io/computeinstance` | `osac.openshift.io/computeinstance-feedback` |
| ClusterOrder | `osac.openshift.io/finalizer` | N/A |

## Key Annotations

| Annotation | Purpose |
|------------|---------|
| `osac.openshift.io/management-state` | Set to `unmanaged` to skip reconciliation |
| `osac.openshift.io/implementation-strategy` | Networking strategy (e.g., `cudn_net`) |
| `osac.openshift.io/reconciled-config-version` | Config version applied by AAP |
| `osac.openshift.io/tenant-id` | Tenant isolation |
| `osac.openshift.io/owner-reference` | Parent resource reference |

## Operator Environment Variables

### Controller Enable Flags

| Variable | Default | Purpose |
|----------|---------|---------|
| OSAC_ENABLE_TENANT_CONTROLLER | false* | Enable Tenant reconciler |
| OSAC_ENABLE_HOST_POOL_CONTROLLER | false* | Enable HostPool reconciler |
| OSAC_ENABLE_COMPUTE_INSTANCE_CONTROLLER | false* | Enable ComputeInstance reconciler |
| OSAC_ENABLE_CLUSTER_CONTROLLER | false* | Enable ClusterOrder reconciler |
| OSAC_ENABLE_NETWORKING_CONTROLLER | false* | Enable networking reconcilers |

*If none are set, all controllers are enabled by default.

### AAP Configuration

| Variable | Purpose |
|----------|---------|
| OSAC_PROVISIONING_PROVIDER | `aap` or `eda` (default: `eda`) |
| OSAC_AAP_URL | AAP base URL |
| OSAC_AAP_TOKEN | AAP API token |
| OSAC_AAP_STATUS_POLL_INTERVAL | Job poll interval (default: 30s) |
| OSAC_AAP_TEMPLATE_PREFIX | Prefix for networking templates (default: `osac`) |
| OSAC_AAP_PROVISION_TEMPLATE | Explicit provision template name |
| OSAC_AAP_DEPROVISION_TEMPLATE | Explicit deprovision template name |
| OSAC_FULFILLMENT_SERVER_ADDRESS | gRPC address for feedback (empty = disabled) |
| OSAC_FULFILLMENT_TOKEN_FILE | OAuth2 token for fulfillment gRPC |
| OSAC_REMOTE_CLUSTER_KUBECONFIG | Path to remote cluster kubeconfig |
| OSAC_MAX_JOB_HISTORY | Jobs kept in status (default: 10) |

## TLS and Certificates

All TLS certificates are managed by cert-manager with a self-signed `default-ca` ClusterIssuer.

**Certificate secrets:**
- `fulfillment-grpc-server-tls` — gRPC server
- `fulfillment-rest-gateway-tls` — REST gateway
- `fulfillment-api-tls` — Ingress proxy (external)
- `fulfillment-controller-tls` — Controller
- `fulfillment-database-server-cert` — PostgreSQL server
- `fulfillment-database-client-cert` — PostgreSQL client

**Debugging TLS issues:**
```bash
kubectl get certificate -n $NAMESPACE
kubectl describe certificate -n $NAMESPACE <name>
kubectl logs -n cert-manager deploy/cert-manager
```
