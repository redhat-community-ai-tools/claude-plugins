# Operator-Specific Debug Commands

## Common Cluster Operator Issues

**Authentication Operator**
```bash
oc get oauth cluster -o yaml
oc get pods -n openshift-authentication
oc logs -n openshift-authentication -l app=oauth-openshift
```

**Console Operator**
```bash
oc get pods -n openshift-console
oc get route console -n openshift-console
oc logs -n openshift-console -l app=console
```

**DNS Operator**
```bash
oc get pods -n openshift-dns
oc logs -n openshift-dns -l dns.operator.openshift.io/daemonset-dns=default
```

**Ingress Operator**
```bash
oc get pods -n openshift-ingress
oc get ingresscontroller -n openshift-ingress-operator
oc logs -n openshift-ingress-operator -l name=ingress-operator
```

**Monitoring Operator**
```bash
oc get pods -n openshift-monitoring
oc get prometheuses -n openshift-monitoring
oc logs -n openshift-monitoring-operator -l app=cluster-monitoring-operator
```

**Network Operator**
```bash
oc get network.operator cluster -o yaml
oc get pods -n openshift-network-operator
oc get pods -n openshift-sdn  # or openshift-ovn-kubernetes
oc logs -n openshift-network-operator -l name=network-operator
```

**Storage Operator**
```bash
oc get storageclass
oc get csidriver
oc get pods -n openshift-cluster-storage-operator
oc logs -n openshift-cluster-storage-operator -l name=cluster-storage-operator
```

## Operator Health Checklist

```bash
echo "=== Cluster Operators ==="
oc get co
echo ""
echo "=== Degraded Operators ==="
oc get co | grep -v "True.*False.*False"
echo ""
echo "=== OLM Operators ==="
oc get csv -A
echo ""
echo "=== Failed CSVs ==="
oc get csv -A | grep -i failed
echo ""
echo "=== Pending Install Plans ==="
oc get installplan -A | grep -i false
echo ""
echo "=== Catalog Sources ==="
oc get catalogsource -A
```

## Quick Commands

```bash
# One-liner to check all operator health
oc get co && oc get csv -A && oc get subscription -A

# Find all operator pods
oc get pods -A | grep operator

# Check operator resource usage
oc adm top pods -A | grep operator
```
