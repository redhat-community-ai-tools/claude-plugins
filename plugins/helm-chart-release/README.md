# Helm Chart Release Plugin

Release Helm charts to `registry.redhat.io` through the Konflux Helm release pipeline —
Pyxis onboarding, Konflux component/Tekton setup, chart versioning, and RPA/ECP configuration
in `konflux-release-data`.

## Skills

### release-helm-chart-konflux

Walks through the full Helm chart release path in Konflux, staged in the order that actually
matters:

1. **Pyxis onboarding** — add the chart to `pyxis-repo-configs`, and match `Chart.yaml`'s
   `name` to the Pyxis repo basename (enforced by the release pipeline).
2. **Konflux component + Tekton pipeline** — hand-edit the pipeline to include
   `build-helm-chart-oci-ta` (0.4+, not the outdated 0.3), and set `OVERWRITE_CHART_NAME` /
   `PUSH_CHART_TO_IMAGE_REPOSITORY` correctly for multi-stream chart repos.
3. **Chart versioning** — tag-derived versions (`helm-<tag>` prefix) vs. a static
   `CHART_VERSION`.
4. **ReleasePlanAdmission (RPA)** — a dedicated RPA using the
   `rh-push-helm-chart-to-registry-redhat-io` pipeline and `{{ oci_version }}` tagging.
5. **EnterpriseContractPolicy (ECP)** — a dedicated ECP excluding image-specific rules like
   `source_image.exists` and `test.test_data_found`.

Includes a troubleshooting checklist mapping common release failures back to the stage that
caused them.

**Best for:** teams adopting the Konflux Helm chart release pipeline for the first time, or
debugging a failing Helm release in an already-onboarded component.

## Installation

```bash
claude plugin marketplace add redhat-community-ai-tools/claude-plugins
claude plugin install helm-chart-release@ecosystem-claude-plugins
```
