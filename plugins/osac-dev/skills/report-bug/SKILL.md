---
name: report-bug
description: Report a bug in Jira without fixing it — creates a Bug ticket with proper description, links it to an epic, and assigns it. Use when the user says 'report a bug', 'file a bug', 'log a bug', 'open a bug ticket', or wants to track a bug without immediately writing a fix.
---

# Report Bug

Create a Jira Bug ticket with a structured description, link it to an epic, and assign it.

## When to Use

- User wants to track a bug without fixing it right now
- User says "report a bug", "file a bug", "log this bug", "open a ticket for this"
- A bug is discovered but the fix is deferred or assigned to someone else

## Gather Inputs

Collect from conversation context. Ask only if truly ambiguous:

| Input | Required | Default |
|-------|----------|---------|
| Bug summary | Yes | From conversation context |
| Description / root cause | Yes | From conversation context or investigation |
| Steps to reproduce | If known | From conversation context |
| Epic key | If ambiguous | Ask user — e.g. "Which epic should I link this to?" |
| Label | No | `OSAC` |
| Assignee | No | Unassigned — only assign if user specifies |

## Create the Bug

```bash
KEY=$(jira issue create -t Bug --project MGMT \
  --summary "<concise bug title>" \
  --body "**Description of the problem:**

<what is broken>

**How reproducible:**

<Always / Sometimes / Rare>

**Steps to reproduce:**

1. <step>

**Expected result:**

<what should happen>

**Actual result:**

<what actually happens>" \
  --label OSAC \
  --affects-version "OSAC" \
  --no-input --raw 2>/dev/null | jq -r '.key')
```

**Key extraction notes:**
- Use `--raw` to get JSON output on stdout, then `jq -r '.key'` to extract the issue key reliably.
- Redirect stderr to `/dev/null` — the success message (`✓ Issue created`) goes to stderr and is not needed.
- Do **not** use `grep -oP` on the text output — it can match multiple keys in the URL or fail silently.

### Link to epic

```bash
jira issue edit $KEY -P <EPIC-KEY> --no-input
```

If user specified an assignee:
```bash
jira issue assign $KEY <assignee>
```

## Report

Output to user:

```
Bug reported:

Jira:   https://issues.redhat.com/browse/<KEY>
Epic:   <EPIC-KEY>
Status: New
```
