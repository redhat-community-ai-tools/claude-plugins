---
name: jira-task-management
description: Manage Jira issues on Red Hat Jira (issues.redhat.com) using jira-cli. Use this skill whenever the user mentions Jira tickets, issues, bugs, tasks, epics, sprints, or wants to create/update/search work items. Also use when the user references MGMT-* issue keys, asks about task status, or wants to track work in the MGMT project.
---

# Jira Task Management

Manage issues on Red Hat Jira (`issues.redhat.com`) via `jira-cli`. The tool is pre-configured with bearer token auth for the MGMT project.

## Setup

- **Binary:** `jira` (installed via `go install github.com/ankitpokhrel/jira-cli/cmd/jira@latest`)
- **Config:** `~/.config/.jira/.config.yml` — initialized with `jira init --installation local --server https://issues.redhat.com --auth-type bearer`
- **Auth:** Bearer token in `~/.netrc` (`machine issues.redhat.com login <user> password <token>`)
- **Token generation:** https://issues.redhat.com → Profile → Personal Access Tokens
- **Default project:** MGMT
- **Jira URL pattern:** `https://issues.redhat.com/browse/<KEY>`

## Before Creating Issues

When the user asks to create a Task or Bug, two things are required before running the command:

1. **Epic link** — Every Task and Bug must be linked to an epic via `-P <EPIC-KEY>`. If the epic isn't obvious from the conversation (e.g., the user has been discussing a specific epic, or there's a CLAUDE.md reference), ask: *"Which epic should I link this to?"*

2. **Label** — Default to `-l OSAC`. Only use a different label if the user explicitly says so.

Do not set priority — it's not relevant for this project.

## Command Reference

All commands below use `--plain` for clean output and `--no-input` to skip interactive prompts. These flags are important because `jira-cli` defaults to interactive/colored output that doesn't work well in non-TTY contexts.

### View

```bash
jira issue view <KEY> --plain                    # View issue details
jira issue view <KEY> --plain --comments 100     # Include comments
```

### Search

```bash
# JQL queries — the primary way to search
jira issue list --jql '<JQL>' --plain

# Common patterns
jira issue list --jql 'assignee = currentUser() AND status not in (Closed, Done)' --plain
jira issue list --jql 'project = MGMT AND status = "In Progress"' --plain
jira issue list --jql 'project = MGMT AND labels = OSAC AND updated >= -7d' --plain

# Text search
jira issue list "search text" --plain

# Pagination
jira issue list --jql '...' --paginate 50 --plain
```

JQL tips: String values with spaces need double quotes inside single quotes — `'status = "In Progress"'`. Field names with spaces need double quotes too — `'"Epic Link" = MGMT-22619'`.

### Epics

```bash
jira epic list <EPIC-KEY> --plain                # List issues in epic
jira epic create -s "Title" -b "Description" -l OSAC    # Create epic
jira epic add <EPIC-KEY> <ISSUE-1> <ISSUE-2>     # Add issues to epic (max 50)
jira epic remove <ISSUE-KEY>                     # Remove from epic

# Filter epic contents with JQL
jira issue list --jql '"Epic Link" = <EPIC-KEY> AND status != Closed' --plain
jira issue list --jql '"Epic Link" = <EPIC-KEY> AND assignee is EMPTY' --plain
```

### Create

```bash
# Task
jira issue create -tTask -s "Summary" -b "Description" \
  -P <EPIC-KEY> -a <assignee> -l OSAC --no-input

# Bug — use the structured description template
jira issue create -tBug -s "Bug title" \
  -b $'**Description of the problem:**\n\n<describe>\n\n**How reproducible:**\n\n<rate>\n\n**Steps to reproduce:**\n\n1. <step>\n\n**Expected result:**\n\n<expected>\n\n**Actual result:**\n\n<actual>' \
  -P <EPIC-KEY> -l OSAC --no-input

# Story
jira issue create -tStory -s "Title" -b "Description" \
  -P <EPIC-KEY> -l OSAC --no-input

# Sub-task (parent is the task, not epic)
jira issue create -tSub-task -s "Title" -P <PARENT-KEY> -l OSAC --no-input

# From file or stdin
jira issue create -tTask -s "Summary" --template /path/to/desc.md -l OSAC --no-input
echo "Description" | jira issue create -tTask -s "Summary" -l OSAC --no-input

# JSON output
jira issue create -tTask -s "Summary" -b "Body" -l OSAC --no-input --raw
```

Issue types: Bug, Task, Story, Epic, Sub-task, Spike, Risk

### Edit

```bash
jira issue edit <KEY> -s "New summary" --no-input          # Summary
jira issue edit <KEY> -b "New description" --no-input      # Description
jira issue edit <KEY> -a "username" --no-input              # Assignee
jira issue edit <KEY> -P <EPIC-KEY> --no-input              # Re-parent to epic
jira issue edit <KEY> -l newlabel --no-input                # Add label
jira issue edit <KEY> --label -oldlabel --no-input          # Remove label (- prefix)
jira issue edit <KEY> -y Critical --no-input                # Priority
jira issue edit <KEY> --fix-version "v1.0" --no-input       # Fix version

# From stdin
echo "Updated desc" | jira issue edit <KEY> --no-input
```

### Transition

```bash
jira issue move <KEY> "In Progress"
jira issue move <KEY> "Code Review"
jira issue move <KEY> "Done"
jira issue move <KEY> "To Do"

# With comment or reassignment
jira issue move <KEY> "In Progress" --comment "Starting work"
jira issue move <KEY> "In Progress" -a username
```

Common statuses: To Do, New, In Progress, Code Review, QE Review, Done, Closed

### Assign

```bash
jira issue assign <KEY> username        # Assign to user
jira issue assign <KEY> $(jira me)      # Assign to self
jira issue assign <KEY> x              # Unassign
```

### Comment

```bash
jira issue comment add <KEY> "Comment text"
jira issue comment add <KEY> $'Line 1\n\nLine 2'          # Multi-line
echo "Comment" | jira issue comment add <KEY>              # From stdin
jira issue comment add <KEY> --template /path/to/file.md   # From file
```

### Link

```bash
jira issue link <KEY-1> <KEY-2> "Blocks"
jira issue link <KEY-1> <KEY-2> "Duplicate"
jira issue link <KEY-1> <KEY-2> "is blocked by"
```

### Sprints

```bash
jira sprint list --plain
jira sprint add <SPRINT_ID> <KEY-1> <KEY-2>
```

### Browser

```bash
jira open <KEY>     # Open issue in browser
jira open           # Open project page
```

## Troubleshooting

- **Auth errors / HTML in response:** Token may be expired. Regenerate at issues.redhat.com → Profile → Personal Access Tokens, update `~/.netrc`.
- **"API v3" errors:** Config must use `installation: Local` (not Cloud). Re-run `jira init --installation local`.
- **Interactive prompts hang:** Always pass `--no-input` for create/edit operations.
- **`--debug` flag:** Shows the actual REST API calls — useful for diagnosing unexpected behavior.
- **Current user:** `jira me` returns the authenticated username.
