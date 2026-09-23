---
name: release-helm-chart-konflux
description: Release a Helm chart to registry.redhat.io through Konflux — Pyxis onboarding, Konflux component setup, build-helm-chart-oci-ta pipeline configuration, chart versioning, and RPA/ECP setup in konflux-release-data. Use when the user wants to onboard, configure, debug, or release a Helm chart via Konflux.
---

# Releasing Helm Charts to registry.redhat.io via Konflux

Konflux has a dedicated pipeline for releasing Helm charts to `registry.redhat.io`. It is a
separate path from container-image releases — different task, different pipeline, different
RPA/ECP — and several steps have non-obvious ordering and gotchas. Work through the stages in
order; skipping ahead (e.g. configuring the component before Pyxis is onboarded) produces
release failures that are hard to trace back to the missing step.

## Stage 1: Onboard the chart in Pyxis (must happen first)

Pyxis is the backend for the Red Hat Catalog and must know about the chart before Konflux can
release it. The Helm release pipeline will fail if this step is skipped or misconfigured.

1. Add a config entry to the [`pyxis-repo-configs`](https://gitlab.cee.redhat.com/releng/pyxis-repo-configs) GitLab repo.
   See the [Pyxis config example](https://gitlab.cee.redhat.com/releng/pyxis-repo-configs/-/blob/main/products/dpu-kit-for-nvidia/dpu-kit-for-nvidia.yaml?ref_type=heads#L110-138).
2. Open a merge request. Once merged, the GitOps service (`cicada`) automatically creates the
   corresponding repository entry inside Pyxis — there is no manual Pyxis-side step.
3. Do not attempt to configure or trigger the Konflux release until the Pyxis entry exists;
   the release pipeline resolves the chart against Pyxis and will not find it otherwise.

**Critical constraint:** the `name` field in `Chart.yaml` must exactly equal the basename of the
Pyxis repository URL. This is enforced by the Helm release pipeline itself, not just a
convention — a mismatch fails the release, not just the catalog listing. See a real
[`Chart.yaml` name example](https://github.com/rh-ecosystem-edge/dpf-hcp-provisioner-operator/blob/release-4.22/helm/dpf-hcp-provisioner-operator/Chart.yaml#L2)
next to its matching [Pyxis config](https://gitlab.cee.redhat.com/releng/pyxis-repo-configs/-/blob/main/products/dpu-kit-for-nvidia/dpu-kit-for-nvidia.yaml?ref_type=heads#L110-138).

## Stage 2: Create the Konflux component

Each Helm chart is its own Konflux component (same mechanism as a container-image component,
under an existing application/tenant). Do not reuse the standard container build pipeline
templates the UI offers — they are built for images, not charts, and produce a broken pipeline
if applied as-is. You must hand-edit the Tekton pipeline definitions.

### Required task: `build-helm-chart-oci-ta`

The pipeline must include the [`build-helm-chart-oci-ta`](https://github.com/konflux-ci/build-definitions/blob/main/task/build-helm-chart-oci-ta/0.3/build-helm-chart-oci-ta.yaml)
task. **Use version 0.4 or later** — the only version indexed at that link (0.3) is outdated and
is missing required parameters described below. Check the task-bundle resolver in your pipeline
for the pinned version and bump it if it still points at `0.3`.

Reference pipelines that already pin `0.4+` and set the required parameters below:
- [Pull-request pipeline example](https://github.com/rh-ecosystem-edge/dpf-hcp-provisioner-operator/blob/release-4.22/.tekton/dpf-hcp-provisioner-chart-4-22-pull-request.yaml)
- [Push pipeline example](https://github.com/rh-ecosystem-edge/dpf-hcp-provisioner-operator/blob/release-4.22/.tekton/dpf-hcp-provisioner-chart-4-22-push.yaml)

### Required task parameters

Set both of these explicitly — the task's defaults are wrong for any repo with multiple
chart streams (i.e. a separate component per version):

- `OVERWRITE_CHART_NAME: "false"` — without this, the task overwrites the component name
  (which includes your version-stream suffix, e.g. `-4-22`) with the bare chart name from
  `Chart.yaml`. If you have multiple streams, this collapses them into one identity.
- `PUSH_CHART_TO_IMAGE_REPOSITORY: "true"` — without this, the task pushes the chart to a
  Quay repository named after the chart itself, which is not owned by this component if you
  have multiple streams. Only skip this if you truly have a single stream and want that
  behavior.

If you only have one chart stream ever, both defaults may work — but set them explicitly anyway
so a future second stream doesn't silently break the existing one.

## Stage 3: Chart versioning

**Default approach — let the task generate the version.** `build-helm-chart-oci-ta` derives a
unique version per commit from Git tags, in the form:

```
<git-tag>.<number-of-commits-since-tag>+<commit-sha>
```

Example: `4.22.7+g43d31c1` (`7` = commits since the last tag). When Helm pushes the chart as an
OCI artifact, `+` is not a valid OCI tag character and becomes `_`: `4.22.7_g43d31c1`.

Git tags used for this **must** carry a `helm-` prefix, or the task will not find them:

```bash
git tag helm-4.22
git push upstream helm-4.22
```

**Alternative — pin a static version.** Set the `CHART_VERSION` parameter explicitly on the
task instead of relying on tag-derived versioning. Use this only if the team has a reason to
avoid tag-driven versions (e.g. an external version source of truth); otherwise prefer the
generated version since it requires no manual bump per release.

This generated/pinned version ends up as the `org.opencontainers.image.version` OCI annotation
on the pushed chart artifact, which feeds `{{ oci_version }}` in the release pipeline (see
Stage 4) — versioning here and the RPA in Stage 4 are coupled, not independent choices.

## Stage 4: Configure the ReleasePlanAdmission (RPA) in `konflux-release-data`

Helm charts need their **own** RPA — do not reuse a container-image RPA. They use a different
release pipeline (`rh-push-helm-chart-to-registry-redhat-io`) and different tag templating.

- Set the release pipeline to `rh-push-helm-chart-to-registry-redhat-io`.
- Tags configured on the RPA should reference `{{ oci_version }}`. This variable resolves from
  the `org.opencontainers.image.version` annotation Helm sets when pushing the chart as an OCI
  artifact (see Stage 3) — if the annotation is missing or the version wasn't generated by
  `build-helm-chart-oci-ta`, `{{ oci_version }}` will resolve empty and the release tag will be wrong.
- See the [example RPA](https://gitlab.cee.redhat.com/releng/konflux-release-data/-/blob/main/config/kflux-prd-rh02.0fk9.p1/product/ReleasePlanAdmission/dpu-kit-for-nvidia-operator/dpu-kit-for-nvidia-operator-charts-prod-4-22.yaml?ref_type=heads).

## Stage 5: Configure the EnterpriseContractPolicy (ECP) in `konflux-release-data`

Create a **dedicated** ECP for Helm chart components rather than pointing at a container-image
ECP. Several stock EC rules assume a container-image artifact and will always fail against a
Helm chart, so they must be excluded, notably:

- `source_image.exists`
- `test.test_data_found`

See the [example ECP](https://gitlab.cee.redhat.com/releng/konflux-release-data/-/blob/main/config/kflux-prd-rh02.0fk9.p1/product/EnterpriseContractPolicy/registry-dpu-kit-for-nvidia-operator-kflux-charts-prod.yaml?ref_type=heads)
for the exclusion list to start from.

## Triggering the release

Once Stages 1–5 are done, trigger the release through the standard Konflux release process
(same mechanism as any other component) — nothing Helm-specific is needed at trigger time.

## Troubleshooting checklist

If a Helm release fails or behaves unexpectedly, check in this order:

1. **Release pipeline can't find the chart in the catalog / Pyxis lookup fails** → Pyxis
   onboarding (Stage 1) is missing or the MR hasn't merged yet.
2. **Release fails on chart name validation** → `Chart.yaml` `name` does not match the basename
   of the Pyxis repo URL (Stage 1).
3. **`build-helm-chart-oci-ta` errors about unknown parameters, or version isn't generated as
   expected** → pipeline is pinned to task version `0.3`; bump to `0.4+` (Stage 2).
4. **Wrong component's chart name/version appears, or streams collide** → `OVERWRITE_CHART_NAME`
   is not set to `"false"` (Stage 2).
5. **Chart pushed to the wrong Quay repo (named after the chart, not the component)** →
   `PUSH_CHART_TO_IMAGE_REPOSITORY` is not set to `"true"` (Stage 2).
6. **Generated version doesn't match expectations, or `{{ oci_version }}` is empty in the RPA**
   → check the `helm-` prefixed Git tag exists and was pushed (Stage 3), and that the RPA's
   tag template references `{{ oci_version }}` exactly (Stage 4).
7. **EC gate fails on `source_image.exists` or `test.test_data_found`** → the component is
   using a container-image ECP instead of a dedicated Helm-chart ECP with these rules excluded
   (Stage 5).
