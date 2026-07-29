---
name: quarterly-connection
description: >-
  Generate Red Hat quarterly connection reports by aggregating accomplishments
  from Jira, GitHub, GitLab, Google Workspace (Docs, Slides, Calendar), and
  other sources into a structured performance review document following the
  Red Hat Quarterly Connection format (accomplishments, priorities, development,
  career growth, support needs, and interests).
  Use when the user mentions quarterly reviews, quarterly connections,
  performance reviews, quarterly reports, quarterly accomplishments,
  Q1/Q2/Q3/Q4 summaries, or wants to gather their work output across
  platforms for a specific time period. Also trigger when the user asks
  "what did I accomplish", "what did I ship", "what did I work on" for
  a quarter or multi-month period.
  Activated by commands: /quarterly, /report, /configure, /platforms.
---

# Quarterly Connection Report Generator

Generate Red Hat Quarterly Connection reports by pulling data from multiple
sources — Jira, GitHub, GitLab, Google Docs, Google Slides, Google Calendar —
and structuring it into the official Quarterly Connection format.

## Red Hat Quarterly Connection Format

The Quarterly Connection is a structured performance review conversation between
an associate and their manager. The report must follow this format:

### Which questions appear each quarter

| Question | Q1 | Q2 | Q3 | Q4 |
|----------|----|----|----|----|
| 1. Accomplishments | Yes | Yes | Yes | Yes |
| 2. Priorities | Yes | Yes | Yes | Yes |
| 3. Development (feedback) | — | — | Yes | — |
| 4. Career Growth | — | — | Yes | — |
| 5. Support Needed | — | — | Yes | — |
| Interests | Yes | — | — | — |

Always include Q1 and Q2 (accomplishments + priorities). Include the others
based on which quarter the report covers.

### Question 1: Accomplishments (every quarter)
**"What accomplishments are you most proud of last quarter? Reflect not only
on WHAT you've accomplished but also on HOW you've accomplished it."**

- Write 2-3 narrative paragraphs, each telling the story of one accomplishment
- Weave WHAT and HOW together naturally in first person
- Include a "By the Numbers" table at the end for supporting data
- Manager will assess: "Do accomplishments align to priorities?"

### Question 2: Priorities (every quarter)
**"What are your top priorities for this quarter?"**

- Write 2-3 paragraphs covering your top priorities
- Explain why each priority matters and how it connects to last quarter's work
- Reference Jira tickets or initiatives where relevant
- Manager will assess: "Are these the correct priorities for business goals?"

### Question 3: Development (Q3 only)
**"What feedback have you received? Key takeaways including top strengths
and opportunities for development?"**

- Leave as template for the user to fill in (this is personal/subjective)
- Provide placeholder sections for Strengths and Areas of Opportunity

### Question 4: Career Growth (Q3 only)
**"How do you see yourself continuing to make an impact at Red Hat?
What are your career aspirations, short (1-2 years) and long term (3-5 years)?"**

- Leave as template for the user to fill in

### Question 5: Support Needed (Q3 only)
**"What support do you need to be successful? How can your manager help you?"**

- Leave as template for the user to fill in

### Interests (Q1 only)
**"What is the most enjoyable / least enjoyable part of your job, or what
gives you energy / takes your energy away?"**

- Leave as template for the user to fill in

### Appendix
- Detailed GitHub PR table by repo
- Key documents authored (from Google Docs)
- Key presentations (from Google Slides)
- Jira ticket details (optional, for reference)

## Data Sources

Gather data from ALL available sources. Don't limit to just Jira/GitHub/GitLab.

### Primary Sources (aggregate automatically)

| Source | What to gather | How |
|--------|---------------|-----|
| **Jira** | Issues created/closed, by type and status | `jira issue list` CLI or quarterly-mcp-server |
| **GitHub** | PRs merged, by repo; PRs reviewed | `gh api search/issues` or quarterly-mcp-server |
| **GitLab** | MRs merged, by project | quarterly-mcp-server if available |
| **Google Docs** | Documents authored/edited in quarter | `gws drive files list` with date + mimeType filter |
| **Google Slides** | Presentations created/updated | `gws drive files list` with presentation mimeType |
| **Google Calendar** | Meeting count, recurring themes, key one-offs | `gws calendar events list` with date range |

### Fallback Strategy

If the quarterly-mcp-server is not registered, use CLI tools directly:
- **Jira**: `jira issue list -q '<JQL>'`
- **GitHub**: `gh api search/issues` with search query syntax
- **Google Workspace**: `gws` CLI commands

If a source fails, continue with the others. Partial data is better than
no report.

## Quick Start

1. If the user invoked a specific command (e.g. `/quarterly`, `/configure`),
   read the matching file in `commands/{command}.md` and follow it.
2. Otherwise, read `skills/controller.md` to determine the right workflow:
   - If the user asked for a full quarterly report, execute `/quarterly`
   - If the user wants a single-platform summary, execute `/report`
   - If the user needs to set up or verify configuration, execute `/configure`
   - If unsure, execute `/platforms` to check what's configured

## Writing Style — Conversational, Not Structured

Every section must read as a **direct, first-person answer** to the question
being asked. Write in the user's voice — reflective and conversational — not
as a structured report with headers and bullet points.

**Key principle:** The output should feel like something you'd say to your
manager in a 1:1, not a project status report for stakeholders.

## Writing the Accomplishments Section

This is the most important section. Follow these principles:

1. **Answer the question directly** — Start with what you're most proud of
   and why. Don't start with a header or a category name. Write in first
   person, reflective tone.

2. **Weave WHAT and HOW together** — Don't separate them into labeled
   sections. The HOW should flow naturally from the WHAT: "I delivered X
   by doing Y, which required Z." This reads more naturally than
   "**What:** X. **How:** Y."

3. **Theme, not ticket** — Group related work into 2-3 narrative paragraphs.
   Each paragraph tells the story of one major accomplishment.

4. **Impact over activity** — "By the end of March, tenants can create
   VirtualNetworks through both APIs" is better than "Merged 29 PRs."

5. **Cross-team contributions** — Weave in interviews, PR reviews, training,
   and community participation naturally rather than listing them separately.

6. **Supporting data at the end** — Include a "By the Numbers" table at the
   bottom for reference, but the narrative comes first.

## Example Accomplishment (good)

```
The accomplishment I'm most proud of this quarter is delivering the
OSAC VMaaS networking layer from zero to a working end-to-end demo.
At the start of Q1 there was no networking model in OSAC. By the end
of March, tenants can create VirtualNetworks, Subnets, and
SecurityGroups through both APIs, and we demonstrated cross-cluster
VM connectivity live. I owned this across the entire stack — API
schema, database migrations, gRPC servers, K8s CRDs and controllers,
and Ansible playbooks — merging 29 PRs across 4 repos.

What made this work was taking an architect-first approach rather than
jumping into code. I started by writing the networking design doc and
getting alignment through 18 GORI landing zone sessions. When
integration testing revealed bugs, I fixed them immediately in context
rather than filing them for later.
```

## Writing the Priorities Section

The priorities should also read as a direct answer: "My top priority
for Q2 is..." Explain not just what you plan to do, but why it matters
and how it connects to the work just completed. Use 2-3 narrative
paragraphs that tell a coherent story about where you're headed,
rather than a numbered list.

## Phases

### 1. Configure (`/configure`)
Verify platform connectivity and credentials. See `skills/configure.md`.

### 2. Platforms (`/platforms`)
Quick check of which platforms respond. See `skills/platforms.md`.

### 3. Report (`/report`)
Single-platform summary for a custom date range. See `skills/report.md`.

### 4. Quarterly (`/quarterly`)
Full quarterly report. This is the main workflow. See `skills/quarterly.md`.

## Working with Existing Skills

When deeper investigation into specific items is needed:

- **Jira details**: Use the Jira skill for ticket deep-dives
- **GitHub details**: Use the GitHub MCP tools for PR reviews, commit history
- **Google Workspace**: Use the Google plugin skills for Docs/Slides/Calendar
- **GitLab details**: Use the GitLab skill for MR details

## Usernames

Users often have different usernames across platforms:

- `username` — base username, used as fallback
- `jira_username` — Jira-specific (often an email like `user@redhat.com`)
- `github_username` — GitHub handle
- `gitlab_username` — GitLab handle

If the user provides only one username, use it as the base and ask whether
their handles differ on other platforms.

## Output

Save the report as `~/quarterly-report-Q{quarter}-{year}.md`.

The report follows the Red Hat Quarterly Connection structure:
- Questions 1-2 (accomplishments + priorities): populated from data
- Questions 3-5 + Interests: left as templates for the user to fill in
- Appendix: detailed activity data for reference

After generating, offer to:
1. Enrich specific sections with more narrative context
2. Save the report to a Google Doc
3. Compare with a previous quarter
4. Drill into specific items using platform-specific skills

## Guidelines

See [guidelines.md](guidelines.md) for security, privacy, data accuracy, and error handling rules.

- Always confirm the quarter and year before gathering data
- Ask for usernames upfront rather than guessing
- If a platform returns an error, continue with what works
- Group accomplishments into themes — never present a flat ticket list
- Always include both WHAT and HOW for accomplishments
- Leave personal/subjective sections as templates, don't fabricate answers
- The report should be a starting point the user edits, not the final word
