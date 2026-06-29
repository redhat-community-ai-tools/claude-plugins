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

**Root cause:**

<why it is broken — the underlying technical reason, if known. Otherwise describe the observed symptom in detail.>

**How reproducible:**

<Always / Sometimes / Rare>

**Steps to reproduce:**

<Concrete, copy-pasteable commands and YAML that someone can follow from scratch to hit the bug.>

1. <create prerequisite resources — show the exact osac/oc command or YAML manifest>
2. <trigger the bug — show the exact command>
3. <observe the failure — show the verification command, e.g. oc get/describe/logs>

**Expected result:**

<what should happen — include expected command output if helpful>

**Actual result:**

<what actually happens — include actual command output showing the error>

**Environment:**

- Cluster: <hostname or type>
- OCP version: <version if known>
- Relevant component versions: <e.g. CNV, OVN-K>" \
  --label OSAC \
  --affects-version "OSAC" \
  --no-input --raw 2>/dev/null | jq -r '.key')
```

**Key extraction notes:**
- Use `--raw` to get JSON output on stdout, then `jq -r '.key'` to extract the issue key reliably.
- Redirect stderr to `/dev/null` — the success message (`✓ Issue created`) goes to stderr and is not needed.
- Do **not** use `grep -oP` on the text output — it can match multiple keys in the URL or fail silently.

### Adding diagnostic output as a comment

After creating the ticket, add a comment with raw diagnostic output. Every output block must be preceded by the exact command that produced it — never dump output without identifying the command.

```bash
jira issue comment add $KEY --body "$(cat <<'DIAG'
## Diagnostic Output

### <command 1, e.g.: oc describe pod -n namespace pod-name>
```
<output>
```

### <command 2, e.g.: oc get events -n namespace --sort-by='.lastTimestamp'>
```
<output>
```
DIAG
)" --no-input
```

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
