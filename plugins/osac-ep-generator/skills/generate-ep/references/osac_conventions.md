# OSAC Enhancement Proposal Conventions

This document captures OSAC-specific conventions for EP authoring, PR submission, and Jira integration.

## Repository and Directory Structure

### Target Repository
- **GitHub organization**: `osac-project`
- **Repository**: `enhancement-proposals`
- **Full URL**: `https://github.com/osac-project/enhancement-proposals`

### Directory Layout
Enhancement proposals follow this structure:
```
enhancement-proposals/
├── guidelines/
│   └── enhancement_template.md         # The template all proposals follow
├── enhancements/
│   ├── <feature-slug>/
│   │   └── README.md                   # The actual proposal
│   ├── networking/
│   │   └── README.md
│   ├── bare-metal-fulfillment/
│   │   └── README.md
│   └── vmaas/
│       └── README.md
```

**Feature slug**: Lowercase with hyphens (e.g., `storage-network`, `gpu-scheduling`, `multi-region-support`)

## PR Title and Body Format

### Title Format
```
MGMT-XXXXX: Add <feature-name> enhancement proposal
```

Examples:
- `MGMT-22637: Add Networking API enhancement proposal`
- `MGMT-23384: Add Carbide integration enhancement proposal`
- `MGMT-22638: ComputeInstance Phase and Condition Updates`

If no Jira ticket exists (rare), use:
```
NO-ISSUE: Add <feature-name> enhancement proposal
```

### PR Body
The PR body should include:
1. **Summary**: 1-2 sentence overview (copy from EP Summary section)
2. **Motivation**: Why this enhancement is needed (copy from EP Motivation section)
3. **Tracking Link**: Jira ticket URL
4. **Related EPs**: Links to related proposals (if any)

Example:
```markdown
## Summary
This enhancement introduces a Networking API for OSAC fulfillment services, providing familiar cloud networking primitives (VirtualNetwork, Subnet, SecurityGroup) as first-class resources.

## Motivation
OSAC needs a unified networking layer aligned with major cloud providers. A standalone API with first-class resources lets tenants define topology before workloads, reference existing networks, and manage SecurityGroups centrally.

## Tracking
https://issues.redhat.com/browse/MGMT-22637

## Related
- Region and Availability Zone API: https://github.com/osac-project/enhancement-proposals/pull/20
```

## Jira Integration

### Jira Project
- **Project key**: `MGMT`
- **Jira instance**: `issues.redhat.com`
- **Full URL format**: `https://issues.redhat.com/browse/MGMT-XXXXX`

### Tracking Link in YAML Frontmatter
```yaml
tracking-link:
  - https://issues.redhat.com/browse/MGMT-22637
```

**Important**: Use the full URL, not just the ticket key. The frontmatter expects a list (array), so use the `-` prefix even for a single link.

### Ticket Lifecycle
1. Create Jira ticket (type: Story or Epic) for the enhancement proposal
2. Write the EP with the tracking-link in frontmatter
3. Open PR with ticket number in title
4. Move ticket to "Code Review" when PR is opened
5. Move ticket to "Done" when PR is merged

## Branch Naming

### Recommended Patterns
- `enhancement/<feature-slug>` (preferred)
- `feature/add-<feature-slug>`
- `proposal/<feature-slug>`

Examples:
- `enhancement/storage-network`
- `feature/add-gpu-scheduling`
- `proposal/multi-region-support`

**Convention**: Use `enhancement/` prefix for consistency with existing OSAC patterns.

## Existing Enhancement Proposals (Reference Library)

Use these as quality benchmarks and pattern references:

| Slug | Description | Lines | Notable Patterns |
|------|-------------|-------|------------------|
| `networking` | OSAC Networking API with VirtualNetwork, Subnet, SecurityGroup, PublicIP resources | 818 | Terminology section, dual-stack IPv4/IPv6, NetworkClass pluggable architecture |
| `bare-metal-fulfillment` | Bare metal host provisioning with HostPool, Host, HostClass resources | ~400 | ESI integration, serial console support, network attachment at interface level |
| `vmaas` | Virtual Machine as a Service with ComputeInstance and ComputeInstanceTemplate | ~300 | Template-based provisioning, GPU support, live migration |
| `carbide-integration` | Carbide registry integration for OSAC | ~250 | Third-party integration pattern |
| `computeinstance-phase-condition-expansion` | Updates to ComputeInstance status and lifecycle | ~200 | API evolution pattern for existing resources |
| `organizations` | Multi-tenancy organization model | ~300 | Tenant isolation, RBAC patterns |
| `tenant-specific-storageclasses` | Tenant-scoped storage class management | ~200 | Provider/tenant resource split pattern |
| `vm-api-fields` | Additional fields for VM creation API | ~150 | Incremental API enhancement |

**Key takeaways**:
- Networking EP (818 lines) sets the bar for technical depth
- Most EPs are 200-400 lines, with deep Implementation Details sections
- All EPs follow the template structure exactly (no skipped sections)
- Successful EPs define terminology upfront and use it consistently

## File Naming

### EP File
Always `README.md` inside the feature directory:
```
enhancement-proposals/enhancements/storage-network/README.md
```

**Do not** use:
- `storage-network.md` (file should be README.md)
- `PROPOSAL.md` or `ENHANCEMENT.md` (non-standard names)
- Multiple files in the feature directory (single README.md only)

### Assets (optional)
If your EP includes diagrams or additional files:
```
enhancement-proposals/enhancements/storage-network/
├── README.md
├── diagrams/
│   ├── architecture.png
│   └── workflow.mermaid
└── examples/
    └── subnet-example.yaml
```

Reference assets from README.md using relative paths:
```markdown
![Architecture Diagram](diagrams/architecture.png)
```

## Linting and Validation

### YAML Frontmatter Validation
The enhancement-proposals repo has CI that validates frontmatter. Required fields:
- `title` (lowercase-with-hyphens format)
- `authors` (list of email addresses)
- `creation-date` (YYYY-MM-DD format)
- `last-updated` (YYYY-MM-DD format)
- `tracking-link` (list with at least one URL or "TBD")

Optional fields:
- `see-also` (list of related EP paths)
- `replaces` (list of superseded EP paths)
- `superseded-by` (list of newer EP paths)

### Section Headers
The linter enforces that all required template sections are present. Do not remove sections — if a section doesn't apply, explain why:
```markdown
## Infrastructure Needed

No additional infrastructure is required for this enhancement. All work will be done in existing OSAC repositories.
```

### Common Linting Errors
- **Missing frontmatter field**: Add the field even if "TBD"
- **Wrong date format**: Use `YYYY-MM-DD` not `MM/DD/YYYY`
- **Missing section**: Add all sections from template
- **Invalid YAML**: Check indentation and list syntax (`-` prefix for list items)

## Review and Approval

### Minimum Reviewers
- At least 2 approvals required
- Reviewers should have domain expertise (networking, bare metal, compute, etc.)
- Cross-team reviews encouraged (e.g., fulfillment-service and osac-operator teams)

### Merge Criteria
- All required sections present and substantive
- All reviewer feedback addressed
- CI passes (frontmatter validation)
- At least 2 approvals
- No unresolved "changes requested" reviews

### After Merge
- Update tracking Jira ticket to "Done"
- Announce in team Slack channel (if applicable)
- Create implementation epic/sub-tasks in Jira (see PLAN-02 for automation)

## Commit Message Format

When committing the EP file:
```
MGMT-XXXXX: Add <feature-name> enhancement proposal

- <key change 1>
- <key change 2>
```

When addressing review feedback:
```
Address review feedback: <summary>

- <change 1>
- <change 2>
```

**Do not** use generic commit messages like "Update README.md" — be specific about what changed and why.

## Command Reference

### Creating EP PR
```bash
cd enhancement-proposals
git checkout -b enhancement/<feature-slug>
mkdir -p enhancements/<feature-slug>
# Write enhancements/<feature-slug>/README.md
git add enhancements/<feature-slug>/README.md
git commit -m "MGMT-XXXXX: Add <feature-name> enhancement proposal"
git push -u origin enhancement/<feature-slug>
gh pr create --repo osac-project/enhancement-proposals \
  --title "MGMT-XXXXX: Add <feature-name> enhancement proposal" \
  --body "<summary + motivation + tracking link>"
```

### Fetching PR Reviews
```bash
gh pr view <PR_NUMBER> --repo osac-project/enhancement-proposals --json reviews,comments
```

### Listing Existing EPs
```bash
ls enhancement-proposals/enhancements/
```

### Checking Frontmatter Validity (local)
```bash
head -20 enhancements/<feature-slug>/README.md | grep -A20 "^---"
```
