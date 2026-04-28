---
name: generate-ep
description: |
  Generate OSAC enhancement proposals from high-level requirements, meeting notes, or Jira tickets. Use when user wants to create, draft, write, or generate an enhancement proposal, EP, or design document for OSAC. Also trigger when user provides requirements, meeting notes, or feature descriptions and asks to formalize them into an EP. Includes PR submission and review feedback iteration.
---

# OSAC Enhancement Proposal Generator

## Overview

This skill transforms rough requirements or meeting notes into a formal OSAC Enhancement Proposal following the osac-project/enhancement-proposals template. It embeds deep knowledge of the EP format, review expectations, and OSAC conventions so codebase exploration at runtime is only for the specific feature being proposed.

The skill acts as a "Senior Staff Engineer" who already knows the OSAC EP template structure and review culture, performing targeted codebase analysis to understand implementation patterns relevant to your specific proposal.

## When to Use

Trigger this skill when:
- User wants to create/draft/generate an OSAC enhancement proposal
- User provides meeting notes, requirements docs, or Jira tickets to formalize
- User says "write up a proposal", "create an EP", "draft an enhancement"
- User describes a feature and wants a formal proposal document
- User says "turn these notes into an enhancement proposal"
- User says "formalize this as an EP"

## Workflow

### Phase 1: Detect Input Mode

**Determine whether the user is providing conversational input or file-based input.**

**File-based mode indicators:**
- User provides a file path (e.g., "here's meeting-notes.md")
- User provides a Jira ticket number (MGMT-XXXXX format)
- User references a document or requirements file

**Conversational mode indicators:**
- User describes requirements directly in the conversation
- User explains what they want to build without referencing external files

**Actions:**
- If file path provided: Read the file content using the Read tool
- If Jira ticket number provided (matches `MGMT-\d+` pattern):
  ```bash
  jira issue view MGMT-XXXXX --raw | jq '.fields | {summary, description, labels}'
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

### Phase 3: Interactive Clarification (REQUIRED)

**CRITICAL:** This phase is mandatory. Do NOT skip to drafting.

After codebase exploration, **STOP and present findings to the user.**

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

**Step 4: Fill ALL sections**
Following the template from `ep_template.md`, populate each section:

**YAML Frontmatter:**
```yaml
---
title: <feature-slug>
authors:
  - <user-email-or-ask>
creation-date: <today-YYYY-MM-DD>
last-updated: <today-YYYY-MM-DD>
tracking-link:
  - <jira-url-or-TBD>
see-also:
  - <related-ep-paths-if-any>
replaces:
  - N/A
superseded-by:
  - N/A
---
```

**Content sections (ALL required):**
1. **Title**: Short, descriptive (e.g., "# OSAC Storage Network API")
2. **Summary**: 1 paragraph summarizing what is being added and why
3. **Terminology** (if applicable): Define key terms upfront
4. **Motivation**:
   - **User Stories**: At least 3-5 stories covering provider and tenant personas
   - **Goals**: 3-7 bullet points describing success criteria from user perspective
   - **Non-Goals**: 2-5 bullet points explicitly stating what is out of scope
5. **Proposal**: High-level overview of the design (1-2 paragraphs per key resource/component)
   - **Workflow Description**: Step-by-step user workflow with defined actors
   - **API Extensions**: List of new gRPC services, CRDs, webhooks, finalizers
   - **Implementation Details**: Deep technical content (proto schemas, controller logic, integration points)
   - **Risks and Mitigations**: Specific risks with concrete mitigation strategies
   - **Drawbacks**: Steel-man argument against the proposal
6. **Alternatives**: Other approaches considered and why they were rejected
7. **Open Questions** (optional): Areas requiring closure before implementation
8. **Test Plan**: Testing strategy (unit, integration, e2e) with focus on tricky areas
9. **Graduation Criteria**: Maturity levels (alpha, beta, GA) or placeholder if not targeting a release
10. **Upgrade/Downgrade Strategy**: How the feature will be upgraded/downgraded
11. **Version Skew Strategy**: How components will handle version skew
12. **Support Procedures**: How to detect and resolve issues in production
13. **Infrastructure Needed**: Additional infrastructure required (or "None")

**Substantive placeholders:** For sections where details depend on implementation (Test Plan, Graduation Criteria), write substantive placeholders that describe WHAT will go there and WHY it's deferred. Don't just write "TBD".

Example:
```markdown
## Test Plan

Test plan will be developed during implementation phase. Expected coverage includes:
- Unit tests: Proto validation, CIDR parsing, StorageClass selection logic
- Integration tests: StorageNetwork creation workflow, Subnet attachment, PV provisioning end-to-end
- E2e tests: Full workflow from StorageNetwork creation to running workload with persistent storage

Focus areas for testing: CIDR conflict detection, CSI driver integration, multi-tenant isolation.
```

**Step 5: Write the draft**
Use the Write tool to create the EP file at the determined path.

### Phase 5: Semi-Automatic PR Submission

**Goal:** Create a PR after user confirmation.

**Step 1: Create branch and commit locally**
```bash
cd /home/eran/go/src/github/eranco74/osac-workspace/enhancement-proposals
git checkout -b enhancement/<feature-slug>
git add enhancements/<feature-slug>/README.md
git commit -m "MGMT-XXXXX: Add <feature-name> enhancement proposal"
```

**Step 2: Show PR preview to user**
Display:
- **Title**: `MGMT-XXXXX: Add <feature-name> enhancement proposal`
- **Body**: Summary + Motivation + Tracking link
- **Branch**: `enhancement/<feature-slug>`
- **Files**: `enhancements/<feature-slug>/README.md`

**Step 3: Ask for confirmation**
"Push and create PR? (yes/no)"

**Step 4: If confirmed, push and create PR**
```bash
git push -u origin enhancement/<feature-slug>
gh pr create --repo osac-project/enhancement-proposals \
  --title "MGMT-XXXXX: Add <feature-name> enhancement proposal" \
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
Report the PR URL to the user: "PR created: https://github.com/osac-project/enhancement-proposals/pull/XXX"

### Phase 6: Review Feedback Loop

**Goal:** Address reviewer feedback and iterate on the EP.

**Trigger:** User says "address the review feedback on PR #XXX" or "update the EP based on reviews"

**Step 1: Fetch reviews**
```bash
gh pr view <PR_NUMBER> --repo osac-project/enhancement-proposals --json reviews,comments
```

**Step 2: Parse feedback**
Extract both human reviewer comments and any structured feedback. Parse:
- Reviewer name
- Review state (APPROVED, CHANGES_REQUESTED, COMMENTED)
- Comment body
- Line/file context (if inline comment)

**Step 3: Load review patterns**
Read `references/review_patterns.md` for context on common feedback themes.

**Step 4: Present feedback summary**
Group feedback by theme:
- Missing sections or insufficient detail
- Unclear workflows or user stories
- Insufficient risk analysis
- Terminology inconsistencies
- Requests for additional context

**Step 5: Propose changes**
For each feedback item, propose a specific change to the EP.

**Step 6: Apply changes**
Update the EP file at `enhancement-proposals/enhancements/<feature-slug>/README.md` with the changes.

**Step 7: Commit and push**
```bash
cd /home/eran/go/src/github/eranco74/osac-workspace/enhancement-proposals
git add enhancements/<feature-slug>/README.md
git commit -m "Address review feedback: <summary-of-changes>"
git push
```

**Step 8: Notify user**
"Changes pushed to PR #XXX. Summary of updates: <list-changes>"

## Quick Reference

| Task | Command |
|------|---------|
| Explore codebase | `rg --type proto "<resource>" --files-with-matches` |
| Fetch Jira ticket | `jira issue view MGMT-XXXXX --raw \| jq '.fields \| {summary, description, labels}'` |
| Create branch | `git checkout -b enhancement/<feature-slug>` |
| Create PR | `gh pr create --repo osac-project/enhancement-proposals --title "..." --body "..."` |
| Fetch reviews | `gh pr view <N> --repo osac-project/enhancement-proposals --json reviews,comments` |
| List existing EPs | `ls /home/eran/go/src/github/eranco74/osac-workspace/enhancement-proposals/enhancements/` |
| Check proto structure | `tree -L 2 /home/eran/go/src/github/eranco74/osac-workspace/fulfillment-service/proto/` |

## Common Issues

### Token/Auth Issues
- **Symptom**: `gh pr create` fails with "Not authenticated"
- **Check**: Run `gh auth status` to verify GitHub CLI is authenticated
- **Fix**: If not authenticated, run `gh auth login` and follow prompts

- **Symptom**: `jira issue view` fails with "Not logged in"
- **Check**: Run `jira me` to verify Jira CLI is authenticated
- **Fix**: If not authenticated, configure `~/.config/.jira/.config.yml` or run `jira init`

### Context Overflow
- **Symptom**: Codebase exploration fills context, leaving no room for drafting
- **Cause**: Reading too many full files during exploration
- **Fix**: Use `rg --files-with-matches` first to find relevant files, then read only key sections (first 50 lines or specific functions) using `head -50` or targeted line ranges

### Missing Jira Ticket
- **Symptom**: User doesn't have a Jira ticket number
- **Fix**: Prompt user for ticket number. If none exists, use `TBD` in frontmatter tracking-link and note in PR body: "Tracking ticket will be created after initial review"

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
