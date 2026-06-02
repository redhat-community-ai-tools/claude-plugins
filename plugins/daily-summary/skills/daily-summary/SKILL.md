---
name: daily-summary
description: Generate a daily status update formatted for Slack. Use whenever the user asks for a daily summary, standup update, status report, EOD update, or wants to share what they worked on today. Also trigger when the user says "what did I do today", "daily update", "standup", "share progress", "status update for slack", or "end of day". Even if the user just says "daily" or "summary" in a work context, this skill likely applies.
---

# Daily Summary for Slack

Generate a Slack-formatted daily status update by gathering data from multiple sources, cross-referencing them, and producing a concise update ready to paste into Slack.

## Strategy

The goal is to produce an accurate picture of the user's day. Different data sources overlap — a Jira ticket may have a corresponding PR, a git commit may relate to a planning phase. Cross-reference everything to avoid duplicates and to enrich each item with full context (ticket + PR + description).

## Step 1: Gather Data

Collect from ALL sources in parallel. Cast a wide net — it's better to gather too much and filter than to miss work.

### Jira (primary work tracker)

```bash
# Recently updated issues assigned to user
jira issue list --jql 'project = MGMT AND labels = OSAC AND assignee = currentUser() AND updated >= -2d' --plain

# Then view each non-Epic issue for status details
jira issue view <KEY> --plain
```

### GitHub PRs (across all OSAC repos)

```bash
# Check each repo for recent PRs
for repo in fulfillment-service osac-aap osac-templates osac-operator osac-installer; do
  gh pr list --author @me --state all \
    --search "updated:>=$(date -d '2 days ago' +%Y-%m-%d)" \
    --repo osac-project/$repo 2>/dev/null
done
```

### Git history (local commits, including submodules)

```bash
# Root repo commits
git log --oneline --since="2 days ago" --author="$(git config user.name)"

# Submodule commits
git submodule foreach --quiet \
  'echo "=== $name ===" && git log --oneline --since="2 days ago" --author="$(git config user.name)" 2>/dev/null'
```

### Planning context

Read these files if they exist — they provide context about what phase/milestone is active:
- `.planning/STATE.md`
- `.planning/ROADMAP.md`
- `.planning/config.json` (contains Jira ticket mappings for phases)

### Session context

Include any work discussed or completed in the current conversation session.

### Memory files

Check auto-memory for recent project context:
- `~/.claude/projects/-home-eran-go-src-github-eranco74-osac-project/memory/MEMORY.md`

## Step 2: Cross-Reference and Deduplicate

- Match PRs to Jira tickets by looking for ticket keys (e.g., `MGMT-12345`) in PR titles, branch names, and commit messages
- Group related items together under their parent Epic
- If a git commit relates to a PR that relates to a Jira ticket, present it as one unified item, not three

## Step 3: Categorize

Classify each work item:

| Category | Criteria |
|----------|----------|
| **Accomplished** | Jira status is Done/Closed, PRs are merged, tasks fully completed |
| **Key Effort** | Actively in progress, partial completion, open PRs |
| **Risks/Challenges** | Blockers, failing tests, dependency issues, anything stalled |

## Step 4: Format for Slack

### Jira IDs as links

Every Jira ticket key must be a clickable Slack link using `<https://issues.redhat.com/browse/MGMT-1234|MGMT-1234>`. This applies everywhere a Jira ID appears — epic headers, ticket references, and mentions in descriptions or risks. Do NOT use markdown link syntax `[text](url)` — Slack won't render it.

### Emoji codes

- `:rocket:` — section header for accomplishments
- `:checked:` — completed item
- `:merged2:` — merged PR (prefix before PR URL)
- `:review:` — PR awaiting review
- `:in-progress:` — work in progress
- `:person_climbing:` — section header for key effort
- `:rotating_light:` — section header for risks

### Output Template

```
:rocket: Accomplishments

<https://issues.redhat.com/browse/EPIC-KEY|EPIC-KEY> (Epic Name)
:checked: <https://issues.redhat.com/browse/TICKET-KEY|TICKET-KEY>: Summary of what was done, with brief inline description of the work completed.
:merged2: https://github.com/osac-project/<repo>/pull/<number>

:person_climbing: Key Effort

<https://issues.redhat.com/browse/EPIC-KEY|EPIC-KEY> (Epic Name)
:in-progress: <https://issues.redhat.com/browse/TICKET-KEY|TICKET-KEY>: Summary
Brief inline description of progress — what's done, what remains.
:review: PR ready for review:
https://github.com/osac-project/<repo>/pull/<number>

:rotating_light: Risks & Challenges

None
```

### Formatting details

- **Epic header**: `<URL|EPIC-KEY> (Epic Name)` — key as Slack link, epic name in parentheses
- **Ticket line**: starts with emoji (`:checked:`, `:in-progress:`), then `<URL|TICKET-KEY>: Summary`. Description follows inline or on the next line, kept to 1-2 lines.
- **One ticket per line**: each ticket gets its own line — do not combine multiple tickets on a single line
- **Merged PRs**: prefix the URL line with `:merged2:`
- **Open PRs**: prefix with `:review:` followed by "PR ready for review:" or "PRs ready for review:", then URL(s) on following lines
- **PR URLs**: always full URLs on their own lines: `https://github.com/osac-project/<repo>/pull/<number>`

## Rules

- Group items under their parent Epic
- Make every Jira ID a clickable Slack link: `<https://issues.redhat.com/browse/KEY|KEY>`
- Include full GitHub PR URLs, prefixed with `:merged2:` for merged or `:review:` for open
- Keep descriptions concise: 1-2 lines per item
- If work isn't tracked in Jira, include it under the most relevant epic
- If no work is found from automated sources, ask the user what they worked on before producing output
- Present the draft to the user for review before they paste it — they may want to add or remove items
