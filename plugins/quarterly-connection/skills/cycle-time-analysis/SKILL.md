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

For each top achievement, apply one of three frameworks (Business Impact, Technical Depth, or Leadership). Each framework has templates and examples — see `references/narrative-frameworks.md`.

### Phase 5: Enhanced Report Generation

Generate the enhanced markdown report using the template in `references/report-template.md`.

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
