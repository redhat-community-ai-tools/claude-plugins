---
name: openshift-operator-troubleshooting
description: Deep troubleshooting guide for OpenShift cluster operators and Operator Lifecycle Manager (OLM) including diagnosing degraded operators, failed installations, subscription issues, and operator conflicts. Use when operators are degraded, failing to install/upgrade, or causing cluster issues.
---

# OpenShift Operator Troubleshooting

This skill provides comprehensive guidance for troubleshooting OpenShift cluster operators and OLM-managed operators, covering installation, upgrade, and operational issues.

## When to Use This Skill

- Cluster operators showing DEGRADED or PROGRESSING status
- Operator installations or upgrades failing
- OLM subscription or install plan issues
- Operator conflicts or dependency problems
- CSV (ClusterServiceVersion) errors
- CRD (Custom Resource Definition) issues
- Operator resource constraints or crashes

## Understanding OpenShift Operators

**Cluster Operators**: Core platform operators managed by Cluster Version Operator (CVO)
**OLM Operators**: Add-on operators managed by Operator Lifecycle Manager

```bash
# View cluster operators
oc get clusteroperators

# View OLM-managed operators
oc get csv -A
oc get operators -A
```

## Troubleshooting Cluster Operators

### Step 1: Identify Degraded Operators

```bash
# List all cluster operators with status
oc get clusteroperators

# Look for:
# AVAILABLE=False: Operator not functioning
# PROGRESSING=True: Operator still reconciling
# DEGRADED=True: Operator has issues

# Filter for degraded operators
oc get co -o json | jq -r '.items[] | select(.status.conditions[] | select(.type=="Degraded" and .status=="True")) | .metadata.name'

# Get operator details
oc describe clusteroperator <operator-name>
```

### Step 2: Analyze Operator Status

```bash
# Get detailed status
oc get clusteroperator <operator-name> -o yaml

# Check status conditions
oc get co <operator-name> -o jsonpath='{.status.conditions}' | jq

# View operator versions
oc get co <operator-name> -o jsonpath='{.status.versions}'

# Check related objects
oc get co <operator-name> -o jsonpath='{.status.relatedObjects}' | jq
```

### Step 3: Check Operator Pods and Resources

```bash
# Find operator namespace
oc get co <operator-name> -o jsonpath='{.status.relatedObjects[].resource}' | grep namespace

# Common operator namespaces:
# openshift-*: Platform operators
# openshift-kube-*: Kubernetes control plane
# openshift-cluster-*: Cluster-wide services

# List pods in operator namespace
oc get pods -n <operator-namespace>

# Check pod status
oc describe pod <pod-name> -n <operator-namespace>

# View operator logs
oc logs -n <operator-namespace> <pod-name>
oc logs -n <operator-namespace> <pod-name> --previous

# For multiple replicas
oc logs -n <operator-namespace> -l app=<operator-app> --tail=100

# Follow logs in real-time
oc logs -n <operator-namespace> -l app=<operator-app> -f
```

For operator-specific debug commands (authentication, console, DNS, ingress, monitoring, network, storage), see `references/operator-specific-commands.md`.

## Troubleshooting OLM Operators

### Step 1: Check Operator Subscriptions

```bash
# List all subscriptions
oc get subscription -A

# Get subscription details
oc describe subscription <subscription-name> -n <namespace>

# Check subscription status
oc get subscription <subscription-name> -n <namespace> -o yaml

# View available channels
oc get packagemanifest <operator-package-name> -o yaml
```

### Step 2: Check Install Plans

```bash
# List install plans
oc get installplan -A

# Get install plan details
oc describe installplan <installplan-name> -n <namespace>

# Check if approval is required
oc get installplan -n <namespace> -o json | jq '.items[] | select(.spec.approved==false)'

# Approve install plan
oc patch installplan <installplan-name> -n <namespace> --type merge -p '{"spec":{"approved":true}}'
```

### Step 3: Check ClusterServiceVersion (CSV)

```bash
# List all CSVs
oc get csv -A

# Get CSV details
oc describe csv <csv-name> -n <namespace>

# Check CSV status
oc get csv <csv-name> -n <namespace> -o jsonpath='{.status.phase}'
# Phases: Pending, InstallReady, Installing, Succeeded, Failed

# Check CSV conditions
oc get csv <csv-name> -n <namespace> -o yaml | grep -A 10 conditions

# View CSV requirements
oc get csv <csv-name> -n <namespace> -o jsonpath='{.spec.install.spec.deployments}'
```

### Step 4: Check Operator Pods

```bash
# Find operator pods from CSV
oc get csv <csv-name> -n <namespace> -o jsonpath='{.spec.install.spec.deployments[*].name}'

# Check deployment
oc get deployment -n <namespace>
oc describe deployment <operator-deployment> -n <namespace>

# Check pods
oc get pods -n <namespace>
oc logs -n <namespace> <operator-pod>

# Check events
oc get events -n <namespace> --sort-by='.lastTimestamp'
```

### Step 5: Check CRDs and Custom Resources

```bash
# List CRDs installed by operator
oc get crd | grep <operator-domain>

# Get CRD details
oc describe crd <crd-name>

# Check CRD version
oc get crd <crd-name> -o jsonpath='{.spec.versions}'

# List custom resources
oc get <crd-plural> -A

# Validate custom resource
oc get <crd-plural> <resource-name> -n <namespace> -o yaml
oc describe <crd-plural> <resource-name> -n <namespace>
```

## Common OLM Issues and Solutions

### Issue: Operator Stuck in "Installing"

```bash
# Check install plan
oc get installplan -n <namespace>
oc describe installplan <installplan-name> -n <namespace>

# Check if approval needed
oc patch installplan <installplan-name> -n <namespace> --type merge -p '{"spec":{"approved":true}}'

# Check for resource conflicts
oc get events -n <namespace>

# Check operator deployment
oc get deployment -n <namespace>
oc describe deployment <operator-deployment> -n <namespace>
```

### Issue: CSV in "Failed" State

```bash
# Check CSV conditions
oc get csv <csv-name> -n <namespace> -o yaml

# Common causes:
# - Missing CRDs
# - Insufficient permissions
# - Resource conflicts
# - Image pull errors

# Check for missing requirements
oc get csv <csv-name> -n <namespace> -o jsonpath='{.status.requirementStatus}'

# Delete and recreate if necessary
oc delete csv <csv-name> -n <namespace>
# OLM will recreate from subscription
```

### Issue: Operator Image Pull Errors

```bash
# Check pod events
oc describe pod <operator-pod> -n <namespace>

# Verify image pull secrets
oc get secrets -n <namespace>
oc describe secret <pull-secret> -n <namespace>

# Link secret to operator service account
oc secrets link <service-account> <pull-secret> --for=pull -n <namespace>

# Check catalog source
oc get catalogsource -n openshift-marketplace
oc describe catalogsource <catalog-name> -n openshift-marketplace
```

### Issue: Multiple Operators Conflicting

```bash
# Check for CRD conflicts
oc get crd -o custom-columns=NAME:.metadata.name,CREATED:.metadata.creationTimestamp

# Check which CSV owns CRD
oc get crd <crd-name> -o jsonpath='{.metadata.ownerReferences}'

# List all CSVs that reference the CRD
oc get csv -A -o json | jq -r '.items[] | select(.spec.customresourcedefinitions.owned[]?.name=="<crd-name>") | .metadata.name'

# Remove conflicting operator
oc delete subscription <subscription-name> -n <namespace>
oc delete csv <csv-name> -n <namespace>
```

### Issue: Operator Upgrade Failed

```bash
# Check subscription channel
oc get subscription <subscription-name> -n <namespace> -o yaml

# Check install plan for upgrade
oc get installplan -n <namespace>

# Rollback to previous version (if needed)
oc delete installplan <failed-installplan> -n <namespace>

# Update subscription to stable channel
oc patch subscription <subscription-name> -n <namespace> --type='merge' -p '{"spec":{"channel":"stable"}}'
```

## Operator Lifecycle Manager (OLM) Troubleshooting

### Check OLM Components

```bash
# Check OLM operators
oc get pods -n openshift-operator-lifecycle-manager

# OLM operator logs
oc logs -n openshift-operator-lifecycle-manager -l app=olm-operator

# Catalog operator logs
oc logs -n openshift-operator-lifecycle-manager -l app=catalog-operator

# Package server logs
oc logs -n openshift-operator-lifecycle-manager -l app=packageserver
```

### Check Catalog Sources

```bash
# List catalog sources
oc get catalogsource -A

# Check catalog source health
oc get catalogsource -n openshift-marketplace
oc describe catalogsource <catalog-name> -n openshift-marketplace

# Check catalog pod
oc get pods -n openshift-marketplace | grep <catalog-name>
oc logs -n openshift-marketplace <catalog-pod>

# Refresh catalog
oc delete pod -n openshift-marketplace -l olm.catalogSource=<catalog-name>
```

### Check OperatorGroup

```bash
# List operator groups
oc get operatorgroup -A

# Check operator group configuration
oc describe operatorgroup <operatorgroup-name> -n <namespace>

# Verify target namespaces
oc get operatorgroup <operatorgroup-name> -n <namespace> -o jsonpath='{.spec.targetNamespaces}'
```

## Advanced Troubleshooting

### Enable Operator Debug Logging

```bash
# For cluster operators (example: ingress)
oc patch ingresscontroller default -n openshift-ingress-operator --type='merge' -p '{"spec":{"logging":{"access":{"destination":{"type":"Container"}}}}}'

# For OLM operators, check operator-specific documentation
# Many operators support log level configuration via env vars or CR
```

### Collect Must-Gather for Operators

```bash
# General must-gather
oc adm must-gather

# Operator-specific must-gather (if available)
oc adm must-gather --image=<operator-must-gather-image>

# For cluster operators
oc adm inspect clusteroperator/<operator-name>
oc adm inspect namespace/<operator-namespace>
```

### Check Operator Metrics

```bash
# Port-forward to Prometheus
oc port-forward -n openshift-monitoring prometheus-k8s-0 9090:9090

# Query operator metrics
# Access http://localhost:9090

# Check operator-specific metrics
# Example: up{job="<operator-name>"}
```

### Verify RBAC Permissions

```bash
# Check service account
oc get sa -n <namespace>
oc describe sa <operator-sa> -n <namespace>

# Check roles and role bindings
oc get role,rolebinding -n <namespace>
oc get clusterrole,clusterrolebinding | grep <operator-name>

# Check if operator can perform actions
oc auth can-i create pods --as=system:serviceaccount:<namespace>:<operator-sa>
```

## Best Practices

1. **Check Logs First**: Operator logs usually contain the root cause
2. **Verify Resource Requirements**: Ensure sufficient CPU/memory
3. **Check Dependencies**: Operators may depend on other operators or services
4. **Review Operator Documentation**: Each operator has specific requirements
5. **Validate CRs**: Ensure custom resources meet the CRD schema
6. **Monitor During Changes**: Watch operator status during upgrades or config changes
7. **Use Must-Gather**: Collect comprehensive diagnostics for complex issues
8. **Check Red Hat Knowledgebase**: Many issues have documented solutions
9. **Keep Operators Updated**: Use stable channels and approved versions
10. **Test in Non-Production**: Validate operator changes before production

For the operator health checklist script and quick commands, see `references/operator-specific-commands.md`.

## Related Skills

- `openshift-debugging` - General cluster troubleshooting
- `openshift-cluster-upgrade` - Operators are updated during upgrades
- `openshift-node-operations` - Some operators manage node resources
