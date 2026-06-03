---
name: generate-ep
description: |
  Generate OSAC enhancement proposals from high-level requirements, meeting notes, or Jira tickets. Use when user wants to create, draft, write, or generate an enhancement proposal, EP, or design document for OSAC. Also trigger when user provides requirements, meeting notes, or feature descriptions and asks to formalize them into an EP. Includes PR submission and review feedback iteration.
---

# OSAC Enhancement Proposal Generator

## Overview

This skill transforms rough requirements or meeting notes into a formal OSAC Enhancement Proposal following the osac-project/enhancement-proposals template. It embeds deep knowledge of the EP format, review expectations, and OSAC conventions so source code exploration at runtime is only for the specific feature being proposed.

The skill acts as a "Senior Staff Engineer" who already knows the OSAC EP template structure and review culture, performing targeted source code analysis to understand implementation patterns relevant to your specific proposal.

## Workflow

### Phase 1: Detect Input Mode

**Determine whether the user is providing conversational input or file-based input.**

**File-based mode indicators:**
- User provides a file path (e.g., "here's meeting-notes.md")
- User provides a Jira ticket number (MGMT-<number> format)
- User references a document or requirements file

**Conversational mode indicators:**
- User describes requirements directly in the conversation
- User explains what they want to build without referencing external files

**Actions:**
- If file path provided: Read the file content using the Read tool
- If Jira ticket number provided (matches `MGMT-\d+` pattern):
  ```bash
  jira issue view MGMT-<number> --raw | jq '.fields | {summary, description, labels}'
  ```
- If conversational: Capture the user's description as the input

**Store the input** for use in clarification and drafting phases.

### Phase 2: Codebase Exploration

**Goal:** Understand existing patterns relevant to the proposed feature.

**Step 1: Load OSAC conventions**
- Read `references/osac_conventions.md` for repo layout and existing EPs

**Step 2: Identify relevant repos**
Based on the feature description, identify which OSAC repos are affected:
- `fulfillment-service`: New APIs, gRPC services, proto schemas
- `osac-operator`: Kubernetes operators, CRDs, controllers
- `osac-aap`: Ansible playbooks for provisioning
- `enhancement-proposals`: Related EPs

**Step 3: Explore existing patterns**
Use targeted searches to understand implementation patterns:

```bash
# Find similar proto resources
cd /home/eran/go/src/github/eranco74/osac-workspace/fulfillment-service
rg --type proto "message <RelatedResource>" --files-with-matches

# Find controllers for similar resources
cd /home/eran/go/src/github/eranco74/osac-workspace/osac-operator
rg "reconcile.*<RelatedResource>" --type go -A5

# Check directory structure
tree -L 2 fulfillment-service/proto/

# Find related EPs
cd /home/eran/go/src/github/eranco74/osac-workspace/enhancement-proposals
ls enhancements/
rg "<relevant-term>" enhancements/*/README.md --files-with-matches
```

**Discovery goals:**
- Which repos will be affected?
- Are there existing similar patterns (e.g., NetworkClass pattern for pluggable backends)?
- What are potential breaking changes?
- Which related EPs should be referenced?

**Constraint:** Limit exploration to relevant files only. Use `--files-with-matches` first, then selectively read key sections. Don't overwhelm context with full file reads.

### Phase 3: Interactive Clarification

This phase is mandatory — do not skip to drafting.

After source code exploration, **STOP and present findings to the user.**

**Structure your clarification:**

1. **What I found:**
   - List discovered patterns, existing implementations, architectural touchpoints
   - Example: "I found that VirtualNetwork uses the NetworkClass pattern for pluggable backends. This is defined in `fulfillment-service/proto/public/osac/public/v1/network_class_type.proto`."

2. **What I need to know:**
   - Enumerate specific unknowns that prevent drafting a complete EP
   - Be explicit about each gap: scope boundaries, user stories, technical constraints, dependencies
   - Example questions:
     - "Should this new StorageNetwork resource follow the same NetworkClass pattern, or is storage provisioning always CSI-based?"
     - "Which personas are the primary users: tenants, providers, or both?"
     - "Is this proposal dependent on any in-progress work or other EPs?"
     - "Do you have a Jira tracking ticket for this? If so, what's the number?"
     - "Who are the stakeholders and subject matter experts I should list as reviewers?"

3. **Wait for answers:**
   - Do NOT proceed to drafting until the user clarifies each item
   - If the user says "just draft it", push back: "I need answers to avoid making wrong assumptions. Let's clarify [specific item] first."

**Store the answers** to inform the EP draft.

### Phase 4: Draft EP

**Prerequisites:** User has provided clarifications from Phase 3.

**Step 1: Load template knowledge**
- Read `references/ep_template.md` for full template structure and section completion guidance
- Read `references/review_patterns.md` to anticipate reviewer expectations

**Step 2: Determine feature slug**
Create a lowercase, hyphen-separated slug based on the feature name:
- Example: "Storage Network API" → `storage-network`
- Example: "GPU Scheduling" → `gpu-scheduling`

**Step 3: Create EP file**
File path: `enhancement-proposals/enhancements/<feature-slug>/README.md`

#### Step 4: Fill ALL sections

Following `references/ep_template.md`, populate the YAML frontmatter (title, authors, dates, tracking-link, see-also) and all content sections:

**Content sections (ALL required):** Title, Summary, Terminology (if applicable), Motivation (User Stories, Goals, Non-Goals), Proposal (Workflow, API Extensions, Implementation Details, Risks, Drawbacks), Alternatives, Open Questions, Test Plan, Graduation Criteria, Upgrade/Downgrade Strategy, Version Skew Strategy, Support Procedures, Infrastructure Needed. See `references/ep_template.md` for section guidance and examples.

For sections where details depend on implementation (Test Plan, Graduation Criteria), write substantive placeholders describing WHAT will go there — not just "TBD". Example: "Test plan will include unit tests for proto validation, integration tests for creation workflows, and e2e tests for the full stack."

**Step 5: Write the draft**
Use the Write tool to create the EP file at the determined path.

### Phase 5: Semi-Automatic PR Submission

**Goal:** Create a PR after user confirmation.

**Step 1: Create branch and commit locally**
```bash
cd /home/eran/go/src/github/eranco74/osac-workspace/enhancement-proposals
git checkout -b enhancement/<feature-slug>
git add enhancements/<feature-slug>/README.md
git commit -m "MGMT-<number>: Add <feature-name> enhancement proposal"
```

**Step 2: Show PR preview to user**
Display:
- **Title**: `MGMT-<number>: Add <feature-name> enhancement proposal`
- **Body**: Summary + Motivation + Tracking link
- **Branch**: `enhancement/<feature-slug>`
- **Files**: `enhancements/<feature-slug>/README.md`

**Step 3: Ask for confirmation**
"Push and create PR? (yes/no)"

**Step 4: If confirmed, push and create PR**
```bash
git push -u origin enhancement/<feature-slug>
gh pr create --repo osac-project/enhancement-proposals \
  --title "MGMT-<number>: Add <feature-name> enhancement proposal" \
  --body "$(cat <<'EOF'
## Summary
<copy-from-EP-summary-section>

## Motivation
<copy-from-EP-motivation-section>

## Tracking
<jira-url>
EOF
)"
```

**Step 5: Report PR URL**
Report the PR URL to the user: "PR created: https://github.com/osac-project/enhancement-proposals/pull/<number>"

For Phase 6 (review feedback loop), quick reference commands, and troubleshooting, see `references/review-and-troubleshooting.md`.

## Rules

- Phase 3 (Interactive Clarification) is mandatory — always present source code findings and ask clarifying questions before drafting the EP
- Use `rg --files-with-matches` first, then read only key sections — do not read entire files during exploration

### Enhancement-Proposals Repo Not Cloned
- **Symptom**: `ls enhancement-proposals/` fails with "No such file or directory"
- **Check**: Run `ls /home/eran/go/src/github/eranco74/osac-workspace/` to see available repos
- **Fix**: Advise user to run `./bootstrap.sh` from workspace root to clone all OSAC repos

### Skill Doesn't Trigger
- **Symptom**: User says "draft an enhancement proposal" but skill doesn't activate
- **Cause**: Phrase not recognized as trigger
- **Fix**: User should explicitly mention "EP", "enhancement proposal", or reference this skill by name

### Review Feedback Not Found
- **Symptom**: `gh pr view` returns empty reviews array
- **Cause**: PR has no reviews yet, or PR number is incorrect
- **Fix**: Verify PR number with `gh pr list --repo osac-project/enhancement-proposals`. If no reviews, tell user: "No reviews found yet — PR may be awaiting reviewers"

## Notes

- **File paths**: Always use absolute paths from `/home/eran/go/src/github/eranco74/osac-workspace/`
- **Reference files**: The skill loads `ep_template.md`, `review_patterns.md`, and `osac_conventions.md` at runtime — these embed the domain knowledge
- **Codebase exploration**: Target exploration to the specific feature being proposed; don't re-discover the EP template structure (that's in reference files)
- **Clarification phase**: Never skip — it's the most critical step for producing a quality EP
- **All sections required**: Even if "TBD", include all template sections with substantive placeholders
