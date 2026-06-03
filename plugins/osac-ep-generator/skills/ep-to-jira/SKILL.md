---
name: ep-to-jira
description: |
  Convert an approved OSAC enhancement proposal into a Jira epic with linked sub-tasks.
  Performs source code-aware dependency mapping to identify cross-repo impacts and breaking changes.
  Produces a complexity assessment rating the architectural impact of proposed changes.
  
  Use when user wants to create Jira tasks from an EP, convert a proposal into work items,
  or turn an enhancement into actionable Jira tickets.
  
  Also trigger when user says "create tasks for this EP", "convert this EP to Jira",
  "create a Jira epic from this enhancement", "break down this proposal into tasks",
  "what tasks are needed for this EP", or "generate Jira tickets from this enhancement".
---

# EP Decomposition and Jira Task Creation

This skill takes an approved OSAC Enhancement Proposal and decomposes it into a Jira epic with linked sub-tasks. As part of decomposition, it performs source code-aware dependency mapping to identify cross-repo impacts and breaking changes, and produces a complexity assessment rating the architectural impact of the proposed changes.

## Overview

The decomposition process follows these phases:

1. **Read the EP** - Extract title, summary, tracking link, and proposed components
2. **Dependency Mapping** - Identify cross-repo impacts using source code exploration (rg, find, tree)
3. **Complexity Assessment** - Rate architectural impact on 5 dimensions (LOW/MEDIUM/HIGH)
4. **Task Decomposition** - Break EP into ordered sub-tasks following extraction rules
5. **Create Jira Epic** - Create epic with MGMT project and OSAC label
6. **Create Sub-Tasks** - Create linked tasks under the epic with --parent flag
7. **Summary Report** - Present epic key, sub-task keys, complexity assessment, dependency map

## Prerequisites

Check these before proceeding:

- **Jira CLI authenticated:** Run `jira me` to verify authentication
  - If fails: User needs to run `jira init` to configure authentication
- **GitHub CLI authenticated:** Run `gh auth status` to verify authentication
  - If fails: User needs to run `gh auth login`
- **EP file exists:** The EP should be at `enhancement-proposals/enhancements/<slug>/README.md`
- **User confirms which EP:** Ask user to provide the EP slug or file path if not clear from context

If any prerequisite fails, STOP and provide clear instructions for what user needs to do.

## Workflow

### Step 1: Read the EP

Read the enhancement proposal file from `enhancement-proposals/enhancements/<slug>/README.md`.

**Extract from YAML frontmatter:**
- `title` - EP title (used for epic name)
- `tracking-link` - Jira ticket to link epic to (if exists)
- `authors` - EP authors (for context)

**Extract from content:**
- **Summary section** - One-paragraph overview (used for epic summary)
- **Proposal section** - Identifies proposed components and resources
- **API Extensions section** - Lists new proto messages and services
- **Implementation Details section** - Describes backend/controller changes
- **Test Plan section** - Outlines test requirements
- **Risks section** - Lists potential architectural risks

Present EP overview to user:
```
Found EP: <title>
Authors: <authors>
Tracking ticket: <tracking-link>
Summary: <one-line summary>

Proceeding with dependency mapping...
```

### Step 2: Dependency Mapping (PLAN-03)

Read `references/decomposition_guide.md` to load the dependency mapping checklist.

For each proposed new resource or API change identified in Step 1, execute these checks:

**Check 1: Proto file impact**
```bash
rg --type proto "<resource_name>" --files-with-matches
```

**Check 2: Controller/reconciler impact**
```bash
rg "reconcile.*<Resource>" --type go -l
```

**Check 3: Package import impact**
```bash
rg "import.*fulfillment.*v1" osac-operator/ --type go -l
rg "import.*fulfillment.*v1" osac-installer/ --type go -l
```

**Check 4: CRD sample impact**
```bash
find osac-operator/config/samples/ -name "*<resource>*" 2>/dev/null
```

**Check 5: Shared type impact**
```bash
rg "<TypeName>" fulfillment-service/proto/ --files-with-matches
```

**Check 6: Breaking changes detection**
Manually check if EP proposes:
- Proto field removal
- Field type changes
- Service or RPC renames
- Required vs optional field changes

Build dependency map table from findings:

| Repo | Impact | Files | Breaking? |
|------|--------|-------|-----------|
| fulfillment-service | High | proto/public/osac/public/v1/virtual_network_type.proto | No |
| osac-operator | Medium | controllers/virtualnetwork_controller.go | No |

Present dependency map to user:
```
Dependency Mapping Results:

<table showing repos, impact level, affected files, breaking changes>

Breaking changes detected: <YES/NO>
If YES, list: <breaking change details>

Proceeding with complexity assessment...
```

### Step 3: Complexity Assessment (PLAN-04)

Read `references/decomposition_guide.md` to load the complexity assessment framework.

Rate each of the 5 dimensions based on findings from Step 2:

**Dimension 1: Repos Touched**
- Count repos with High or Medium impact from dependency map
- LOW: 1 repo, MEDIUM: 2-3 repos, HIGH: 4+ repos

**Dimension 2: API Surface Change**
- Check if EP adds new resources (MEDIUM) or modifies existing (HIGH if breaking)
- LOW: no API change, MEDIUM: additive, HIGH: breaking

**Dimension 3: Data Migration**
- Check if EP requires database schema changes
- LOW: no schema change, MEDIUM: new tables/columns, HIGH: breaking schema change

**Dimension 4: Cross-Service Dependency**
- Check if changes require coordinated release across repos
- LOW: independent, MEDIUM: consumes existing API, HIGH: coordinated release

**Dimension 5: Testing Complexity**
- Check Test Plan section for test infrastructure needs
- LOW: unit tests only, MEDIUM: integration tests, HIGH: e2e across services

**Overall Complexity** = highest individual dimension rating

Present complexity assessment table to user:

```
Complexity Assessment:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Repos touched | MEDIUM | fulfillment-service + osac-operator |
| API surface change | MEDIUM | Additive API (new resources) |
| Data migration | MEDIUM | New tables, backward-compatible |
| Cross-service dependency | MEDIUM | Operator consumes fulfillment API |
| Testing complexity | MEDIUM | Integration tests required |
| **Overall** | **MEDIUM** | Highest individual rating |

High-risk areas: <list any HIGH-rated dimensions>

Proceeding with task decomposition...
```

### Step 4: Task Decomposition

Read `references/decomposition_guide.md` to load the task extraction strategy.

Break EP into sub-tasks following these extraction rules:

**1. API/Schema tasks**
- One task per new proto message or service
- Extract from "Proposal" and "API Extensions" sections
- Example: "Define VirtualNetwork proto schema"

**2. Controller/Backend tasks**
- One task per new reconciliation loop or handler
- Extract from "Implementation Details" section
- Example: "Implement VirtualNetwork CRUD service"

**3. Integration tasks**
- One task per cross-repo integration point identified in Step 2
- Example: "Update osac-operator to reconcile VirtualNetwork CRs"

**4. Test tasks**
- One task per test scope from "Test Plan" section
- Separate tasks for unit tests and integration tests
- Example: "Add integration tests for VirtualNetwork lifecycle"

**5. Documentation tasks**
- One task per documentation need
- Check if CLAUDE.md, README, or API docs need updates
- Example: "Update fulfillment-service CLAUDE.md with VirtualNetwork patterns"

**6. Infrastructure tasks**
- One task per infrastructure need from "Infrastructure Needed" section
- Example: "Add VirtualNetwork CRD to osac-operator"

**Order tasks per the guide:**
1. Proto/schema tasks (foundation)
2. Backend/handler tasks (implementation)
3. Controller/operator tasks (integration)
4. Test tasks (verification)
5. Documentation tasks (documentation)

Present proposed task list to user for review/modification:

```
Proposed Task Breakdown (<N> tasks):

Proto/Schema Tasks:
1. Define VirtualNetwork proto schema
2. Define Subnet proto schema
...

Backend/Handler Tasks:
3. Implement VirtualNetworks CRUD service
4. Implement Subnets CRUD service
...

Integration Tasks:
5. Add VirtualNetwork CRD and controller to osac-operator
...

Test Tasks:
6. Add unit tests for networking service handlers
7. Add integration tests for VirtualNetwork lifecycle
...

Documentation Tasks:
8. Update fulfillment-service CLAUDE.md with networking patterns
...

Review this task list. Would you like to:
- Proceed with creating Jira epic and tasks? (y)
- Modify the task list? (provide changes)
- Add more tasks? (describe what's missing)
```

Wait for user confirmation before proceeding to Step 5.

### Step 5: Create Jira Epic

Once user confirms task list, create the Jira epic using jira CLI.

**Create epic:**
```bash
epic_key=$(jira epic create \
  --project MGMT \
  --name "<EP Title from frontmatter>" \
  --summary "Implement <EP Title> enhancement proposal" \
  --body "Tracking epic for EP: enhancement-proposals/enhancements/<slug>/README.md

<EP Summary section content>

See full proposal: <github-link-to-ep-file>" \
  --label OSAC \
  --no-input \
  --raw | jq -r '.key')
```

**Link to tracking ticket (if tracking-link exists in EP frontmatter):**
```bash
# Extract tracking ticket key from URL (e.g., MGMT-22637 from https://issues.redhat.com/browse/MGMT-22637)
tracking_ticket=$(echo "<tracking-link>" | grep -oP 'MGMT-\d+')

if [[ -n "$tracking_ticket" ]]; then
  jira issue link "$epic_key" "$tracking_ticket" --type "implements"
fi
```

Report epic creation:
```
Created epic: $epic_key
Epic URL: https://issues.redhat.com/browse/$epic_key
Linked to tracking ticket: $tracking_ticket (if applicable)

Creating sub-tasks...
```

### Step 6: Create Sub-Tasks

For each task identified in Step 4, create a Jira task linked to the epic.

**Task creation pattern:**
```bash
jira issue create \
  --project MGMT \
  --type Task \
  --parent "$epic_key" \
  --summary "<task summary>" \
  --body "<task description>

Repo: <affected-repo>
Files: <affected-files>

Acceptance criteria:
- <criterion 1>
- <criterion 2>
" \
  --label OSAC \
  --no-input
```

**Build task description from decomposition:**
- **Summary:** Short task name from Step 4
- **Body:** Include:
  - Affected repo(s) from dependency map
  - Key files to create/modify
  - Acceptance criteria based on task type

**Track created tasks:**
Store each created task key for final report.

Report progress:
```
Creating sub-tasks... (<N> total)

[1/N] Created: MGMT-XXXXX - Define VirtualNetwork proto schema
[2/N] Created: MGMT-XXXXY - Define Subnet proto schema
...
[N/N] Created: MGMT-XXXXZ - Update CLAUDE.md with networking patterns

All sub-tasks created.
```

### Step 7: Summary Report

Present final summary with all key information:

```
=== EP Decomposition Complete ===

Epic: $epic_key
Epic URL: https://issues.redhat.com/browse/$epic_key
Sub-tasks created: <count>

Sub-Task List:
- MGMT-XXXXX: Define VirtualNetwork proto schema
- MGMT-XXXXY: Define Subnet proto schema
- MGMT-XXXXZ: Implement VirtualNetworks CRUD service
...

Complexity Assessment:
- Overall: <RATING>
- High-risk areas: <list any HIGH-rated dimensions>
- Breaking changes: <YES/NO with details>

Dependency Map:
<table from Step 2>

Next steps:
1. Assign tasks to team members in Jira
2. Prioritize tasks following the ordering (proto → backend → controller → tests → docs)
3. Track progress in epic: <epic-url>
```

For common issues (auth errors, type not found, EP not found, search overload), see `references/troubleshooting.md`.
