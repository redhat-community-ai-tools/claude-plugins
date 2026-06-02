# Upgrade Strategies

## EUS to EUS Upgrade

Extended Update Support allows skipping intermediate versions:

```bash
# Example: 4.10 (EUS) → 4.12 (EUS)
# First upgrade to 4.11
oc adm upgrade --to=4.11.z

# Wait for completion, then upgrade to 4.12
oc adm upgrade channel eus-4.12
oc adm upgrade --to=4.12.z
```

## Managing Large Clusters

For clusters with many nodes:

```bash
# Pause machine config pools to control rollout
oc patch mcp worker --type merge -p '{"spec":{"paused":true}}'

# Update control plane first
# Then unpause workers in batches

# Unpause when ready
oc patch mcp worker --type merge -p '{"spec":{"paused":false}}'
```

## Air-Gapped Upgrades

```bash
# Mirror release images
oc adm release mirror

# Create ImageContentSourcePolicy
oc apply -f image-content-source-policy.yaml

# Upgrade using mirrored images
oc adm upgrade --to-image=<mirrored-registry>:<version>
```

## Useful Commands

```bash
# Quick status check
oc get clusterversion && oc get co && oc get mcp && oc get nodes

# Detailed upgrade status
oc describe clusterversion | grep -A 20 "Status:"

# Cancel upgrade (not recommended, only if not started)
oc adm upgrade --clear

# Get upgrade history
oc get clusterversion -o jsonpath='{.items[0].status.history}'

# Check if version is recommended
oc adm upgrade --include-not-recommended

# View release info
oc adm release info <version>
```
