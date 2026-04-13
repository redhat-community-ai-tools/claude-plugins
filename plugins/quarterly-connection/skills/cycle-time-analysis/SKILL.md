---
name: cycle-time-analysis
description: >-
  Analyzes cycle times for Jira issues and GitHub PRs to identify longest-running
  strategic work, ranks achievements by cycle time/impact/complexity, and transforms
  technical descriptions into polished performance review narratives using three
  AI-powered frameworks (business impact, technical depth, leadership). Extends
  quarterly-connection with deep achievement analysis and narrative refinement
  capabilities. Activated by command: /quarterly-report
---

# Cycle Time Analysis & Achievement Ranking

Extends quarterly-connection with AI-powered cycle time analysis, multi-metric achievement ranking, and narrative refinement frameworks.

## Overview

This skill adds advanced analytics to quarterly-connection:

**What quarterly-connection provides:**
- Data collection from Jira, GitHub, GitLab, Google Workspace
- Red Hat Quarterly Connection format generation

**What this skill adds:**
- **Cycle time analysis** - Identifies longest-running strategic work
- **Multi-metric ranking** - Scores by cycle time, impact keywords, complexity
- **Three narrative frameworks** - Business impact, technical depth, leadership
- **Enhanced markdown format** - Alternative to Red Hat QC format

## When to Use

Use `/quarterly-report` (this skill) when you want:
- Deep cycle time analysis to identify strategic work
- Achievement ranking by multiple metrics
- Polished WHAT/HOW/WHY narratives
- Enhanced markdown format

Use `/quarterly` (quarterly-connection base) when you want:
- Official Red Hat Quarterly Connection format
- Google Workspace integration
- Standard QC structure

**You can use both**: Generate `/quarterly-report` for analysis, then copy polished narratives into `/quarterly` for Red Hat submission.

## Prerequisites

Same as quarterly-connection:
- `jira` CLI or quarterly-mcp-server
- `gh` CLI
- `glab` CLI (optional)

## Four-Phase Workflow

### Phase 1: Information Gathering

Use quarterly-connection's existing data collection:
- Quarter and year (e.g., Q1 2026)
- Platform-specific usernames (Jira email, GitHub handle, GitLab handle)
- Optional filters (Jira project, GitHub org)

### Phase 2: Cycle Time Analysis

**Calculate cycle times for all work items:**

For each Jira issue:
```
cycle_time = resolved_date - created_date (in days)
```

For each GitHub PR:
```
cycle_time = merged_date - created_date (in days)
```

**Generate statistics:**
- Average cycle time (Jira vs GitHub)
- Longest 10 items by cycle time
- Distribution by repository/project

**Key insight:** Longest cycle times often indicate strategic/foundational work (not quick bug fixes).

### Phase 3: Multi-Metric Achievement Ranking

Rank achievements using THREE complementary metrics:

#### Metric 1: Cycle Time (Longest Strategic Work)
- Sort all items by cycle_days descending
- Top 10 = longest-running = likely strategic/foundational

#### Metric 2: Impact (Infrastructure Keywords)
- Base score = cycle_days
- Apply multipliers for keywords in title:
  - `infrastructure, foundational, framework, template, automation` → 1.5x
  - `release, backport, multi-, across, all` → 1.3x
  - `CI, test, workflow, pipeline` → 1.2x
- Sort by adjusted score descending

#### Metric 3: Complexity (Scope)
- For GitHub PRs: `(files_changed * 0.5) + (lines_added / 100)`
- For Jira: Use cycle_days as proxy
- Sort by complexity score descending

**Cross-reference rankings:**
Items appearing in top 10 of multiple rankings = TRUE TOP ACHIEVEMENTS

### Phase 4: AI-Powered Narrative Refinement

For each top achievement, apply one of THREE frameworks:

#### Framework 1: Business Impact
**Emphasize:**
- WHAT problem this solves for customers/users
- HOW this enables business objectives
- WHO benefits (team, customers, enterprise)
- WHY this matters strategically

**Template:**
```
I [delivered/enabled/built] [WHAT] by [HOW], [enabling/solving/creating] 
[BUSINESS_VALUE]. This work [spanned/involved] [SCOPE] over [DURATION]. 
[Strategic decision or approach]. [Production status and next steps enabled].
```

**Example:**
```
Raw: "Add Windows BYOH provisioning support"

Refined:
"I delivered Phase 1 BYOH (Bring Your Own Host) provisioning support to Prow CI,
establishing foundational infrastructure that enables all future BYOH testing for
the Windows QE team. This was strategic infrastructure investment spanning 37 files
(+666 lines) over 17 days. I used a phased rollout strategy, starting with Azure
IPI and vSphere to de-risk deployment before expanding to other platforms. This
work is now running in production and directly enables Q2 Phase 2 work (WINC-1837)."
```

#### Framework 2: Technical Depth
**Emphasize:**
- WHAT technical challenges were solved
- HOW you approached the problem (architecture, design)
- Technical complexity and scope
- Engineering rigor (testing, validation, deployment)

**Template:**
```
I [architected/engineered/refactored] [WHAT] by [TECHNICAL_APPROACH], 
[achieving/creating] [TECHNICAL_OUTCOME]. [Scope details]. [Design decisions 
and trade-offs]. [Quality/rigor details].
```

**Example:**
```
Raw: "Consolidate test templates"

Refined:
"I architected consolidation of 23 static YAML test files into 3 parameterized Go
templates (+1,280/-1,257 lines), building 11 resource code generators for
programmatic generation. The net +23 lines (after deleting 1,257) demonstrates
massive complexity reduction. Created single source of truth eliminating copy-paste
errors and enabling future OTE migration."
```

#### Framework 3: Leadership
**Emphasize:**
- HOW you influenced outcomes beyond code
- WHAT decisions you made and why
- WHO you helped or unblocked
- Strategic thinking and judgment calls

**Template:**
```
I [investigated/discovered/pivoted] [SITUATION], [made decision] to [ACTION], 
and [documented/communicated/enabled] [KNOWLEDGE_SHARING]. [Technical 
justification]. [Outcome and team benefit].
```

**Example:**
```
Raw: "Fix vSphere proxy job"

Refined:
"I investigated AWS proxy configuration, discovered a bootstrap limitation where
Windows nodes can't reach external resources through proxy during initial setup,
and made a strategic pivot to vSphere platform where proxy works correctly. Rather
than forcing a broken approach, I documented the decision-making process in the PR
description and leveraged proven patterns. Filled coverage gap in 6 days with
working solution, demonstrating engineering judgment and knowledge sharing."
```

### Phase 5: Enhanced Report Generation

Generate enhanced markdown report saved to `~/Q{quarter}-{year}-Accomplishments-Enhanced.md`

**Report structure:**

```markdown
# Q{quarter} {year} Quarterly Accomplishments
**[Name]** | [Team/Role]
**Period:** {start_date} - {end_date}

---

## Executive Summary

**What I accomplished this quarter - ordered by strategic impact:**

1. [Top achievement 1 - one-line summary]
2. [Top achievement 2 - one-line summary]
...

---

## Top Accomplishments - WHAT and HOW

### 1. [Achievement Title] (PR #XXXXX or JIRA-KEY)

**WHAT I Accomplished:**
- [Deliverables]
- Scope: X files, +Y lines
- Duration: Z days
- Related Jira: KEY

**HOW I Accomplished It:**
- [Approach, architecture, decisions]
- [Key technical choices]
- [Rollout strategy]
- [Production status]

**Impact:**
- [Who benefits]
- [What it enables]
- [Strategic value]

**Why This Matters:**
[Strategic importance paragraph]

---

[Repeat for top 5 achievements]

---

## By The Numbers - Q{quarter} {year}

| Metric | Achievement |
|--------|-------------|
| GitHub PRs Merged | X |
| Jira Issues Filed | Y |
| Jira Issues Closed | Z (W% closure rate) |
| Average Cycle Time (Jira) | A days |
| Average Cycle Time (GitHub) | B days |

---

## How I Work - Key Themes

[Analyze patterns across achievements:]

### 1. [Theme 1 - e.g., Strategic Decision-Making]
- [Examples from achievements]

### 2. [Theme 2 - e.g., Fast Iteration]
- [Examples from achievements]

---

## Cycle Time Analysis

### Jira Issues - Average: X days

**Longest issues (strategic work):**
1. [KEY]: [Summary] ([N days])
...

### GitHub PRs - Average: Y days

**Longest PRs (foundational work):**
1. [repo#number]: [Title] ([N days, F files])
...

---

**Generated:** {current_date}
**Tool:** quarterly-connection with cycle-time-analysis
```

## CLI Commands Reference

### Fetch Jira Issues

```bash
jira issue list \
  --jql "reporter = currentUser() AND created >= 'YYYY-MM-DD' AND created <= 'YYYY-MM-DD'" \
  --plain \
  --columns KEY,SUMMARY,TYPE,STATUS,CREATED,RESOLVED
```

### Fetch GitHub PRs

```bash
gh search prs \
  --author=USERNAME \
  --merged \
  --merged-at=YYYY-MM-DD..YYYY-MM-DD \
  --owner=ORG \
  --json number,title,createdAt,closedAt,url,repository
```

### Get PR Details

```bash
gh pr view PR_NUMBER \
  --repo OWNER/REPO \
  --json number,title,createdAt,mergedAt,changedFiles,additions,deletions,url
```

## Choosing the Right Narrative Framework

**Business Impact** → Infrastructure/foundational work, customer-facing features
**Technical Depth** → Large refactors, architectural changes, complex engineering
**Leadership** → Problem-solving with pivots, cross-team collaboration, strategic decisions

You can mix frameworks for different achievements in the same report.

## Success Criteria

The workflow is successful when:
1. ✅ User has enhanced markdown report at `~/Q{quarter}-{year}-Accomplishments-Enhanced.md`
2. ✅ Top 5 achievements have polished WHAT/HOW/WHY narratives
3. ✅ Report includes cycle time analysis and "By The Numbers"
4. ✅ Ready for performance review with minimal editing
5. ✅ Process took ~30 minutes instead of 4-6 hours

## Graceful Degradation

- If Jira API fails: Continue with GitHub data only
- If GitHub API rate limited: Use available data, note limitation
- Partial data is better than no report

## What This Skill Does NOT Do

- ❌ Auto-submit reports to Workday or any system
- ❌ Make assumptions about importance (user reviews rankings)
- ❌ Fabricate achievements (uses only real data)
- ❌ Replace `/quarterly` command (complementary, not replacement)

## Integration with quarterly-connection

This skill **extends** quarterly-connection's capabilities:

**Data collection:** Reuses quarterly-connection's `/configure` and platform setup
**Output formats:** Adds `/quarterly-report` as alternative to `/quarterly`
**Use together:** Analyze with `/quarterly-report`, format with `/quarterly`

---

**License:** Apache-2.0  
**Contributors:** Ronnie Rasouli (cycle-time-analysis), Eran Cohen (quarterly-connection)
