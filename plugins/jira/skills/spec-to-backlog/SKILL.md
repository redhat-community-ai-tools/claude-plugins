---
name: spec-to-backlog
description: "Transform specification documents into structured Jira backlogs using jira-cli. When an agent needs to: (1) Create Jira tickets from a spec or requirements document, (2) Break down a feature spec into implementation tasks, (3) Create an epic with child tickets from a design doc, or (4) Convert requirements into a Jira backlog."
---

# Spec to Backlog

Transform specification documents into structured Jira backlogs using `jira-cli`. This skill reads requirement documents, intelligently breaks them down into logical implementation tasks, creates an Epic first, then generates individual Jira tickets linked to that Epic.

**Use this skill when:** Users have a spec, requirements doc, or design document that needs to become a Jira backlog.

All commands use `--plain` for clean output and `--no-input` to skip interactive prompts.

---

## Workflow

**CRITICAL: Always follow this exact sequence:**

1. **Get Specification** → Obtain the spec content
2. **Confirm Project and Epic Details** → Identify target Jira project
3. **Analyze Specification** → Break down into logical tasks
4. **Present Breakdown** → Show user the planned Epic and tickets
5. **Create Epic FIRST** → Establish parent Epic and capture its key
6. **Create Child Tickets** → Generate tickets linked to the Epic
7. **Provide Summary** → Present all created items with links

---

## Step 1: Get Specification

Ask the user to provide the spec. This can be:
- Pasted text directly in the conversation
- A file path to read
- A URL to fetch

---

## Step 2: Confirm Project and Epic Details

**Ask:** "Which Jira project should I create these tickets in? (e.g., MGMT, ENG)"

If the user is unsure:

```bash
jira project list --plain
```

---

## Step 3: Analyze Specification

Read the spec and decompose it into:

### Epic-Level Goal
What is the overall objective? This becomes your Epic.

### Implementation Tasks
Break the work into logical, independently implementable tasks.

**Breakdown principles:**
- **Size:** 3-10 tasks per spec typically
- **Clarity:** Each task should be specific and actionable
- **Independence:** Tasks can be worked on separately when possible
- **Completeness:** Include backend, frontend, testing, documentation, and infrastructure tasks when the spec touches those areas

**Choose appropriate issue types based on content:**
- **Bug** — Fixing existing problems ("fix", "resolve", "broken")
- **Story** — New user-facing features ("feature", "user can", "add ability to")
- **Task** — Technical work without direct user impact ("implement", "setup", "configure", "refactor")

**Use action verbs:** Implement, Create, Build, Add, Design, Integrate, Update, Fix, Optimize, Configure, Deploy, Test, Document

---

## Step 4: Present Breakdown to User

**Before creating anything**, show the user your planned breakdown:

```
I've analyzed the spec and here's the backlog I'll create:

**Epic:** [Epic Summary]
[Brief description of epic scope]

**Implementation Tickets (7):**
1. [Story] Create user registration flow
2. [Task] Design authentication database schema
3. [Story] Build login form UI components
4. [Bug] Fix existing session timeout handling
5. [Task] Configure CI/CD pipeline for auth service
6. [Story] Implement password reset API
7. [Task] Write integration tests for auth flow

Shall I create these tickets in [PROJECT]?
```

**Wait for user confirmation** before proceeding.

---

## Step 5: Create Epic FIRST

**The Epic must be created before any child tickets.**

```bash
jira epic create \
  -s "Epic Summary" \
  -b $'## Overview\nBrief summary of what this epic delivers\n\n## Objectives\n- Key objective 1\n- Key objective 2\n\n## Scope\nWhat is included and what is not\n\n## Success Criteria\n- Measurable criterion 1\n- Measurable criterion 2' \
  -l OSAC --no-input
```

Capture the Epic key from the output (e.g., "MGMT-123"). You'll need it for every child ticket.

Confirm to user: "Created Epic: MGMT-123 - Epic Summary"

---

## Step 6: Create Child Tickets

Create each implementation task as a child ticket linked to the Epic.

### For Each Task

```bash
jira issue create -t<IssueType> \
  -s "Task summary with action verb" \
  -b $'## Context\nBrief context from the spec\n\n## Requirements\n- Requirement 1\n- Requirement 2\n\n## Technical Details\n- Technologies involved\n- Dependencies\n\n## Acceptance Criteria\n- [ ] Testable criterion 1\n- [ ] Testable criterion 2' \
  -P <EPIC-KEY> -l OSAC --no-input
```

Where `<IssueType>` is one of: Task, Story, Bug

### Task Summary Format

- "Implement user registration API endpoint"
- "Design authentication database schema"
- "Build login form UI components"
- NOT "Do backend work" (too vague)
- NOT "Frontend" (not actionable)

### Acceptance Criteria Best Practices

Make them **testable** and **specific**:
- "API returns 201 status on successful user creation"
- "Password must be at least 8 characters and hashed with bcrypt"
- NOT "User can log in" (too vague)
- NOT "It works" (not testable)

---

## Step 7: Provide Summary

After all tickets are created:

```
Backlog created successfully!

**Epic:** MGMT-123 - User Authentication System
https://redhat.atlassian.net/browse/MGMT-123

**Implementation Tickets (7):**

1. MGMT-124 - Design authentication database schema
   https://redhat.atlassian.net/browse/MGMT-124

2. MGMT-125 - Implement user registration API endpoint
   https://redhat.atlassian.net/browse/MGMT-125

3. MGMT-126 - Build login form UI components
   https://redhat.atlassian.net/browse/MGMT-126

Next Steps:
- Review tickets in Jira for accuracy and completeness
- Assign tickets to team members
- Estimate story points if your team uses them
- Schedule work for the upcoming sprint
```

---

## Edge Cases

### Existing Epic

If user wants to add tickets to an existing Epic:
- Skip Epic creation (Step 5)
- Ask for the existing Epic key
- Proceed with Step 6 using the provided Epic key

### Large Specifications (15+ tickets)

- Present the full breakdown
- Ask: "This spec would create 18 tickets. Should I create all of them, or would you like to adjust the scope?"
- Offer to create a subset first

### Ambiguous Specifications

If the spec lacks detail:
- Create fewer, broader tickets
- Note in descriptions: "Detailed requirements need to be defined during refinement"
- Ask: "The spec is light on implementation details. Should I create high-level tickets that can be refined later?"

---

## Tips for High-Quality Breakdowns

- **Be Specific** — "Create login form UI with email/password inputs and validation" not "Do frontend work"
- **Include Technical Context** — Mention technologies, components, integration points
- **Logical Grouping** — Related work stays in the same ticket
- **Avoid Duplication** — Don't create redundant tickets
- **Note Dependencies** — Use "Depends on" or "Blocks" in descriptions
- **Include Testing** — Either as part of feature tasks or as separate testing tasks

## When NOT to Use This Skill

**Don't use for:**
- Individual task creation (use jira-task-management)
- Meeting action items (use capture-tasks-from-meeting-notes)
- Bug triaging (use triage-issue)

**Use only when:** A spec or requirements document needs to become a structured Jira backlog.
