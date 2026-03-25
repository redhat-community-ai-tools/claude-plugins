# OSAC Architecture

## Component Flow

```
Client (curl/grpcurl)
  → OpenShift Route (TLS passthrough)
    → Envoy Ingress Proxy (fulfillment-ingress-proxy:8000)
      ├─ /api/* → REST Gateway (fulfillment-rest-gateway:8000)
      └─ gRPC   → gRPC Server (fulfillment-grpc-server:8000)
                    → PostgreSQL (fulfillment-database:5432)

fulfillment-controller watches fulfillment DB → creates/updates K8s CRs

osac-operator watches K8s CRs → triggers AAP jobs → updates CR status

osac-operator feedback controllers → signal fulfillment-service via gRPC
```

## Resource Hierarchy

```
NetworkClass (platform-defined, read-only in public API)
  └── VirtualNetwork (tenant L2 network with CIDR)
        ├── Subnet (CIDR range, creates Namespace + CUDN)
        └── SecurityGroup (firewall rules)
ComputeInstance (KubeVirt VM, attached to Subnet + SecurityGroups)
```

## Key Pods

| Pod | Process | Purpose |
|-----|---------|---------|
| `fulfillment-grpc-server` | `fulfillment-service start grpc-server` | Core gRPC API, DB migrations |
| `fulfillment-rest-gateway` | `fulfillment-service start rest-gateway` | HTTP/JSON to gRPC proxy |
| `fulfillment-controller` | `fulfillment-service start controller` | Watches DB events, reconciles K8s CRs |
| `fulfillment-ingress-proxy` | Envoy | TLS termination, routing |
| `fulfillment-database` | PostgreSQL 15 | Persistent storage |
| `osac-operator-controller-manager` | `/manager` | Watches CRs, triggers AAP, feedback to fulfillment |
| `osac-aap-*` | AAP components | Controller, EDA, Gateway |
