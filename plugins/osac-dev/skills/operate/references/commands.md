# OSAC Operational Commands

## 1. Building and Deploying

### Build Local Images

```bash
# From project root
./scripts/build-local-images.sh              # Build all three images
./scripts/build-local-images.sh --push       # Build and push to quay.io
./scripts/build-local-images.sh --tag v1.0   # Custom tag (default: local)
```

**Components built:**
- `fulfillment-service` → `quay.io/eranco74/fulfillment-service:local`
- `osac-operator` → `quay.io/eranco74/osac-operator:local`
- `osac-aap` (EE image) → `quay.io/eranco74/osac-aap:local`

### Deploy via Kustomize

```bash
# Apply overlay (e.g., eran)
kubectl apply -k osac-installer/overlays/eran

# Or build and review first
kustomize build osac-installer/overlays/eran | less
```

### Update Image References

Edit `osac-installer/overlays/<name>/kustomization.yaml`:
```yaml
images:
- name: ghcr.io/osac-project/fulfillment-service
  newName: quay.io/eranco74/fulfillment-service
  newTag: local
- name: ghcr.io/osac-project/osac-operator
  newName: quay.io/eranco74/osac-operator
  newTag: local
```

Then re-apply: `kubectl apply -k osac-installer/overlays/<name>`

### Create a New Overlay

```bash
cp -r osac-installer/overlays/development osac-installer/overlays/<name>
# Edit kustomization.yaml: change namespace, prefix, image refs
# Edit prefixTransformer.yaml: change prefix
# Add files/license.zip and files/quay-pull-secret.json
kubectl apply -k osac-installer/overlays/<name>
```

---

## 2. Checking Service Health

### Fulfillment Service

```bash
ROUTE=$(kubectl get route -n $NAMESPACE fulfillment-api -o jsonpath='{.spec.host}')
TOKEN=$(kubectl create token -n $NAMESPACE admin)

# REST health check
curl -sk https://$ROUTE/healthz

# gRPC health check
grpcurl -insecure -H "Authorization: Bearer $TOKEN" $ROUTE:443 grpc.health.v1.Health/Check

# List services
grpcurl -insecure -H "Authorization: Bearer $TOKEN" $ROUTE:443 list

# Metrics
kubectl port-forward -n $NAMESPACE deploy/fulfillment-grpc-server 8002:8002
curl http://localhost:8002/metrics
```

### Operator

```bash
kubectl port-forward -n $NAMESPACE deploy/osac-operator-controller-manager 8081:8081
curl http://localhost:8081/healthz
curl http://localhost:8081/readyz
```

### Database

```bash
kubectl exec -it -n $NAMESPACE statefulset/fulfillment-database -- \
  psql -U client -d service -c "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 5;"
```

---

## 3. Checking Logs

```bash
# Fulfillment service logs
kubectl logs -f -n $NAMESPACE deploy/fulfillment-grpc-server
kubectl logs -f -n $NAMESPACE deploy/fulfillment-rest-gateway
kubectl logs -f -n $NAMESPACE deploy/fulfillment-controller

# Operator logs
kubectl logs -f -n $NAMESPACE deploy/osac-operator-controller-manager

# AAP logs
kubectl logs -f -n $NAMESPACE deploy/osac-aap-controller
kubectl logs -f -n $NAMESPACE deploy/osac-aap-eda-api

# Enable debug logging (edit deployment)
# fulfillment: --log-level=debug
# operator: --zap-log-level=debug --zap-devel=true
```

---

## 4. API Operations

### REST API (Public)

```bash
# List resources
curl -sk -H "Authorization: Bearer $TOKEN" "https://$ROUTE/api/fulfillment/v1/virtual_networks" | jq
curl -sk -H "Authorization: Bearer $TOKEN" "https://$ROUTE/api/fulfillment/v1/subnets" | jq
curl -sk -H "Authorization: Bearer $TOKEN" "https://$ROUTE/api/fulfillment/v1/compute_instances" | jq
curl -sk -H "Authorization: Bearer $TOKEN" "https://$ROUTE/api/fulfillment/v1/network_classes" | jq
curl -sk -H "Authorization: Bearer $TOKEN" "https://$ROUTE/api/fulfillment/v1/security_groups" | jq
```

### gRPC API — Signal (Private)

Signal triggers re-reconciliation for a stuck resource:

```bash
grpcurl -insecure -H "Authorization: Bearer $TOKEN" \
  -d '{"id": "<resource-id>"}' $ROUTE:443 osac.private.v1.Subnets/Signal

grpcurl -insecure -H "Authorization: Bearer $TOKEN" \
  -d '{"id": "<resource-id>"}' $ROUTE:443 osac.private.v1.VirtualNetworks/Signal
```

### Helper Script

```bash
# scripts/networking.sh — quick gRPC operations
export TOKEN=$(kubectl create token -n $NAMESPACE admin)
export OSAC_HOST=fulfillment-api-$NAMESPACE.apps.<cluster>:443

./scripts/networking.sh list-nc          # List NetworkClasses
./scripts/networking.sh list-vn          # List VirtualNetworks
./scripts/networking.sh list-subnets     # List Subnets
./scripts/networking.sh create-nc <name> <strategy>
./scripts/networking.sh create-vn <name> <nc-id> <cidr> [region]
./scripts/networking.sh create-subnet <name> <vn-id> <cidr>
./scripts/networking.sh delete <Service> <id>
```

---

## 5. Cleanup Workflows

### Delete All Resources (ordered)

**Important:** Always confirm with the user before running. Delete in this order:

```bash
# 1. Delete compute instances
for id in $(curl -sk -H "Authorization: Bearer $TOKEN" "https://$ROUTE/api/fulfillment/v1/compute_instances" | jq -r '.items[].id'); do
  curl -sk -X DELETE -H "Authorization: Bearer $TOKEN" "https://$ROUTE/api/fulfillment/v1/compute_instances/$id"
done

# 2. Wait for CIs to be deleted, then delete subnets
for id in $(curl -sk -H "Authorization: Bearer $TOKEN" "https://$ROUTE/api/fulfillment/v1/subnets" | jq -r '.items[].id'); do
  curl -sk -X DELETE -H "Authorization: Bearer $TOKEN" "https://$ROUTE/api/fulfillment/v1/subnets/$id"
done

# 3. Wait for subnets, then delete virtual networks
for id in $(curl -sk -H "Authorization: Bearer $TOKEN" "https://$ROUTE/api/fulfillment/v1/virtual_networks" | jq -r '.items[].id'); do
  curl -sk -X DELETE -H "Authorization: Bearer $TOKEN" "https://$ROUTE/api/fulfillment/v1/virtual_networks/$id"
done
```

### Force Cleanup K8s Resources

**Last resort — confirm with user first:**

```bash
# Remove finalizers from stuck CRs
kubectl patch <crd> -n $NAMESPACE <name> --type=json \
  -p '[{"op":"remove","path":"/metadata/finalizers"}]'

# Delete orphaned CUDNs (remove OVN finalizer first)
kubectl patch clusteruserdefinednetwork <name> --type=json \
  -p '[{"op":"remove","path":"/metadata/finalizers"}]' && \
kubectl delete clusteruserdefinednetwork <name>

# Restart controller after cleanup
kubectl rollout restart -n $NAMESPACE deploy/fulfillment-controller
```
