---
name: capture-tasks-from-meeting-notes
description: "Analyze meeting notes to find action items and create Jira tasks for assigned work using jira-cli. When an agent needs to: (1) Create Jira tasks or tickets from meeting notes, (2) Extract or find action items from notes, (3) Parse meeting notes for assigned tasks, or (4) Analyze notes and generate tasks for team members."
---

# Capture Tasks from Meeting Notes

## Overview

Automatically extract action items from meeting notes and create Jira tasks with proper assignees using `jira-cli`. This skill parses unstructured meeting notes (pasted text), identifies action items with assignees, and creates tasks — eliminating the tedious post-meeting ticket creation process.

**Use this skill when:** Users have meeting notes with action items that need to become Jira tasks.

All commands use `--plain` for clean output and `--no-input` to skip interactive prompts.

---

## Workflow

Follow this 6-step process to turn meeting notes into actionable Jira tasks:

### Step 1: Get Meeting Notes

Obtain the meeting notes from the user. Ask them to paste the notes directly.

If unclear, ask: "Could you paste the meeting notes here?"

---

### Step 2: Parse Action Items

Scan the notes for action items with assignees.

#### Common Patterns

**Pattern 1: @mention format** (highest priority)
```
@Sarah to create user stories for chat feature
@Mike will update architecture doc
```

**Pattern 2: Name + action verb**
```
Sarah to create user stories
Mike will update architecture doc
Lisa should review the mockups
```

**Pattern 3: Action: Name - Task**
```
Action: Sarah - create user stories
Action Item: Mike - update architecture
```

**Pattern 4: TODO with assignee**
```
TODO: Create user stories (Sarah)
TODO: Update docs - Mike
```

**Pattern 5: Bullet with name**
```
- Sarah: create user stories
- Mike - update architecture
```

#### Extraction Logic

**For each action item, extract:**

1. **Assignee Name** — Text after @ symbol, name before "to"/"will"/"should", name after "Action:" or in parentheses
2. **Task Description** — Text after "to", "will", "should", "-", ":"
3. **Context** (optional) — Meeting title/date, surrounding discussion context

---

### Step 3: Confirm Project and Epic

Before creating tasks, identify the target Jira project and epic.

**Ask:** "Which Jira project and epic should I create these tasks in? (e.g., project MGMT, epic MGMT-12345)"

If the user is unsure about the project, list available projects:

```bash
jira project list --plain
```

---

### Step 4: Present Action Items

Show the parsed action items to the user before creating any tasks.

#### Presentation Format

```
I found [N] action items from the meeting notes. Should I create these Jira tasks in [PROJECT] under epic [EPIC-KEY]?

1. [Task description]
   Assigned to: [Name]

2. [Task description]
   Assigned to: [Name]

Would you like me to:
1. Create all tasks
2. Skip some tasks (which ones?)
3. Modify any descriptions or assignees
```

#### Wait for Confirmation

Do NOT create tasks until user confirms.

---

### Step 5: Create Tasks

Once confirmed, create each Jira task.

#### For Each Action Item

```bash
jira issue create -tTask \
  -s "Task description" \
  -b $'**Action Item from Meeting Notes**\n\n**Task:** Original action item text\n\n**Context:**\nMeeting title/date\nRelevant discussion points' \
  -P <EPIC-KEY> -a <assignee> -l OSAC --no-input
```

#### Task Summary Format

Use action verbs and be specific:
- "Create user stories for chat feature"
- "Update architecture documentation"
- "Review and approve design mockups"

#### Handling Assignee Lookup

The `-a` flag expects a Jira username or email. If you only have a first name from the notes:
- Ask the user for the full username/email
- Or create the task unassigned and note: "Please assign manually"

---

### Step 6: Provide Summary

After all tasks are created, present a comprehensive summary.

```
Created [N] tasks in [PROJECT]:

1. [PROJ-123] - [Task summary]
   Assigned to: [Name]
   https://redhat.atlassian.net/browse/PROJ-123

2. [PROJ-124] - [Task summary]
   Assigned to: [Name]
   https://redhat.atlassian.net/browse/PROJ-124

Next Steps:
- Review tasks in Jira for accuracy
- Add any additional details or attachments
- Adjust priorities if needed
```

---

## Handling Edge Cases

### No Action Items Found

If no action items with assignees are detected:

```
I analyzed the meeting notes but couldn't find any action items with clear assignees.

Action items typically follow patterns like:
- @Name to do X
- Name will do X
- Action: Name - do X

Options:
1. I can search for TODO items without assignees
2. You can point out specific action items to create
```

### Mixed Formats (Some With Assignees, Some Without)

```
I found [N] action items:
- [X] with clear assignees
- [Y] without assignees

Should I:
1. Create all [N] tasks ([X] assigned, [Y] unassigned)
2. Only create the [X] tasks with assignees
3. Ask you to assign the [Y] unassigned tasks
```

### Duplicate Action Items

If the same task appears multiple times, flag it and ask whether to create one or two tasks.

---

## When NOT to Use This Skill

**Don't use for:**
- Summarizing meetings (no task creation)
- General Jira task creation (use jira-task-management)
- Creating epics or stories from specs (use spec-to-backlog)

**Use only when:** Meeting notes exist and action items need to become Jira tasks.

## Rules

- Always present parsed action items and wait for user confirmation before creating any Jira tasks
- Use action verbs in task summaries: "Create", "Update", "Review", not "Chat feature work"
