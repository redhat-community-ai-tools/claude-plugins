---
name: quarterly-report-assistant
description: >-
  AI-powered performance review assistant that automates quarterly achievement
  report generation by aggregating Jira, GitHub, and GitLab data, analyzing
  cycle times, identifying top achievements, and transforming technical
  descriptions into polished performance review narratives.
  Use when the user mentions quarterly reviews, performance reviews, quarterly
  reports, quarterly accomplishments, Q1/Q2/Q3/Q4 summaries, or wants to
  analyze their work output for a specific time period. Also trigger when the
  user asks "what did I accomplish", "what were my top achievements", "analyze
  my cycle times" for a quarter or multi-month period.
  Activated by command: /quarterly-report
---

# Quarterly Report Assistant - AI-Powered Performance Review Automation

Generate comprehensive quarterly achievement reports by aggregating data from
Jira, GitHub, and GitLab, analyzing cycle times, identifying top achievements,
and transforming technical descriptions into polished narratives for
performance reviews.

## Overview

This skill automates the tedious manual work of quarterly review preparation:

**Before:** 4-6 hours digging through Jira/GitHub, writing dry technical descriptions

**After:** 30 minutes of focused refinement using AI-powered analysis and narrative generation

## Prerequisites

### Required CLI Tools

This skill uses CLI tools to query platforms directly (no MCP server required):

**Required:**
- **jira CLI**: https://github.com/ankitpokhrel/jira-cli
  ```bash
  # Install via homebrew (macOS)
  brew install jira-cli
  
  # Configure
  jira init
  ```

- **GitHub CLI**: https://cli.github.com/
  ```bash
  # Install via homebrew (macOS)
  brew install gh
  
  # Authenticate
  gh auth login
  ```

**Optional:**
- **GitLab CLI**: https://gitlab.com/gitlab-org/cli
  ```bash
  brew install glab
  glab auth login
  ```

### Verify Installation

Before starting, verify CLI tools are configured:
```bash
jira me                    # Should show your Jira user info
gh api user                # Should show your GitHub user info
glab api user              # (Optional) Should show GitLab user info
```

## Data Collection Methods

This skill uses CLI tools and calculates metrics directly:

## Four-Phase Workflow

### Phase 1: Information Gathering

**Objective:** Get quarter, year, and platform-specific usernames

**Questions to ask:**
1. Which quarter and year? (e.g., Q1 2026)
2. What is your base username?
3. What is your Jira username? (often email: user@example.com)
4. What is your GitHub username? (handle)
5. What is your GitLab username? (optional, if using GitLab)
6. Jira project filter? (e.g., WINC, optional)
7. GitHub organization filter? (e.g., openshift, redhat, optional)

**Why different usernames matter:**
- Jira typically uses email format (user@company.com)
- GitHub uses handle format (username)
- GitLab may differ from both

**Store this information** for use across all tools in subsequent phases.

### Phase 2: Data Collection and Analysis

**Step 2.1: Fetch Jira Issues**

Use `jira` CLI to fetch issues created in the quarter:

```bash
# Fetch issues created in Q1 2026
jira issue list --jql "reporter = currentUser() AND created >= '2026-01-01' AND created <= '2026-03-31' AND project = {PROJECT}" --paginate 500 --plain --columns KEY,SUMMARY,TYPE,STATUS,CREATED,RESOLVED,PRIORITY
```

**Store the output** and parse it to extract:
- Issue keys, summaries, types, statuses
- Created and resolved dates
- Calculate cycle time: (resolved_date - created_date) in days
- Filter for resolved/closed issues only

**Step 2.2: Fetch GitHub PRs**

Use `gh` CLI to fetch merged PRs:

```bash
# Fetch merged PRs in Q1 2026
gh api search/issues --method GET \
  -f q="author:{github_username} is:pr is:merged merged:2026-01-01..2026-03-31 org:{org}" \
  --paginate \
  --jq '.items[] | {number: .number, title: .title, repository: .repository_url, merged_at: .closed_at, html_url: .html_url}'
```

**For each PR**, fetch detailed info to get created_at:

```bash
# Get PR details for cycle time calculation
gh pr view {pr_number} --repo {owner/repo} --json number,title,createdAt,mergedAt,changedFiles,additions,deletions
```

**Calculate cycle time:** (merged_at - created_at) in days

**Step 2.3: Analyze Cycle Times**

From the collected data, calculate:

**Jira metrics:**
- Average cycle time across all resolved issues
- Longest 10 issues by cycle time
- Distribution by type (Story, Task, Bug, Epic)

**GitHub metrics:**
- Average cycle time across all merged PRs
- Longest 10 PRs by cycle time
- Distribution by repository
- Total files changed, lines added/deleted

**Present the findings:**
```
Your Q1 2026 Cycle Time Analysis:

Jira Issues:
- Total filed: X
- Total closed: Y (Z% closure rate)
- Average cycle time: A days

Longest Jira Issues:
1. PROJ-123: Summary (42 days) - Story
2. PROJ-456: Summary (38 days) - Task
...

GitHub PRs:
- Total merged: X
- Average cycle time: B days

Longest GitHub PRs:
1. owner/repo#123: Title (17 days, 37 files, +666 lines)
2. owner/repo#456: Title (8 days, 25 files, +1156 lines)
...
```

**Step 2.4: Identify Top Achievements**

Apply THREE ranking strategies to the combined Jira + GitHub data:

**Ranking 1: By cycle time (longest strategic work)**
- Sort all items by cycle_days descending
- Top 10 = longest-running work = likely strategic/foundational

**Ranking 2: By impact (infrastructure keywords)**
- Score each item: base_score = cycle_days
- Boost if title contains keywords:
  - infrastructure, foundational, framework, template, automation (+50%)
  - release, backport, multi-, across (+30%)
  - CI, test, workflow (+20%)
- Sort by adjusted score descending

**Ranking 3: By complexity (scope)**
- For GitHub PRs: Score by (files_changed * 0.5) + (lines_added / 100)
- For Jira: Score by cycle_days (proxy for complexity)
- Sort by score descending

**Cross-reference the rankings:**
- Items appearing in top 10 of multiple rankings = YOUR TOP ACHIEVEMENTS
- Present a combined list with justification:

```
Top 5 Achievements (Based on Cycle Time + Impact + Complexity):

1. repo#123: "Add BYOH provisioning support" (17 days, 37 files, +666 lines)
   - Longest 5% of PRs (cycle time ranking)
   - Infrastructure keyword match (impact ranking)
   - High scope (complexity ranking)

2. PROJ-456: "Update Core WINC Tests" (63 days)
   - Longest Jira issue (cycle time ranking)
   - Epic-level effort (complexity ranking)

...
```

### Phase 3: Achievement Narrative Refinement

For EACH of the top 5 achievements identified in Phase 2:

**Step 3.1: Gather Detailed Context**

For GitHub PRs, fetch additional details:

```bash
# Get PR details
gh pr view {pr_number} --repo {owner/repo} --json number,title,body,createdAt,mergedAt,changedFiles,additions,deletions,labels,commits

# Check for backports (multi-release indicator)
gh api "repos/{owner/repo}/pulls/{pr_number}/commits" --jq '.[].commit.message' | grep -i backport
```

**Extract:**
- Files changed, lines added/deleted
- Whether it's multi-release (backport commits, multiple version labels)
- Related Jira tickets (from PR body)
- Time to merge (created → merged)
- Number of commits

For Jira issues, fetch detailed info:

```bash
# Get issue details
jira issue view {ISSUE_KEY} --plain

# Check for linked PRs and sub-tasks
jira issue view {ISSUE_KEY} --plain | grep -E "(Pull Request|Sub-task)"
```

**Extract:**
- Issue type (Story, Task, Bug, Epic)
- Description text (for context on WHAT/WHY)
- Linked PRs (GitHub links)
- Sub-tasks (indicates large effort)
- Time to resolve (created → resolved)

**Step 3.2: Apply Narrative Refinement Frameworks**

For each achievement, write THREE narrative versions using different frameworks:

**Framework 1: Business Impact Style**

Transform technical description to emphasize:
- WHAT problem this solves for customers/users
- HOW this enables business objectives
- WHO benefits (team, customers, enterprise)
- WHY this matters strategically

Example:
```
Raw: "Add Windows BYOH provisioning support to step-registry"
Context: "37 files, +666 lines, 17 days, Phase 1 BYOH support"

Refined:
"I delivered Phase 1 BYOH (Bring Your Own Host) provisioning support to Prow CI,
establishing foundational infrastructure that enables all future BYOH testing for
the Windows QE team. This was strategic infrastructure investment spanning 37 files
(+666 lines) over 17 days. I used a phased rollout strategy, starting with Azure
IPI and vSphere to de-risk deployment before expanding to other platforms. This
work is now running in production and directly enables Q2 Phase 2 work (WINC-1837)."
```

**Framework 2: Technical Depth Style**

Transform to emphasize:
- WHAT technical challenges were solved
- HOW you approached the problem (architecture, design decisions)
- Technical complexity and scope (lines changed, files affected)
- Engineering rigor (testing, validation, production deployment)

Example:
```
Raw: "Create Go templates and resource generators"
Context: "22 files changed, +1280/-1257 lines, 7 days, consolidates 23 YAMLs → 3 templates"

Refined:
"I architected consolidation of 23 static YAML test files into 3 parameterized Go
templates (+1,280/-1,257 lines), building 11 resource code generators for
programmatic generation. The net +23 lines (after deleting 1,257) demonstrates
massive complexity reduction. Created single source of truth eliminating copy-paste
errors and enabling future OTE migration. This is technical debt reduction done right -
investing in architectural improvements that pay long-term dividends."
```

**Framework 3: Leadership Style**

Transform to emphasize:
- HOW you influenced outcomes beyond individual contribution
- WHAT decisions you made and why
- WHO you helped or unblocked
- Strategic thinking and judgment calls

Example:
```
Raw: "Add vSphere proxy test"
Context: "9 files, +187 lines, 6 days, strategic pivot from AWS to vSphere"

Refined:
"I investigated AWS proxy configuration, discovered a bootstrap limitation where
Windows nodes can't reach external resources through proxy during initial setup
(before WMCO configures them), and made a strategic pivot to vSphere platform where
proxy works correctly. Rather than forcing a broken approach, I documented the
decision-making process in the PR description and leveraged proven patterns from
existing vsphere-proxy-e2e-operator job. Filled coverage gap in 6 days with working
solution, demonstrating engineering judgment and knowledge sharing."
```

**Step 3.3: Choose Best Style for Each Achievement**

Not all achievements fit the same narrative style:
- Infrastructure/foundational work → business_impact or technical_depth
- Problem-solving with pivots → leadership
- Large refactors → technical_depth
- Customer-facing features → business_impact

**Key principles:**
1. Answer WHAT, HOW, and WHY
2. Weave technical details into impact narrative
3. Use first person ("I delivered", "I architected")
4. Focus on decision-making and strategic thinking
5. Quantify where possible (X files, Y days, Z releases)

**Example transformation:**

Raw: "Add Windows BYOH provisioning support to step-registry"

Context: "37 files, +666 lines, 17 days, Phase 1 BYOH support"

Refined (business_impact style):
"I delivered Phase 1 BYOH (Bring Your Own Host) provisioning support to Prow CI,
establishing foundational infrastructure that enables all future BYOH testing
for the Windows QE team. This was strategic infrastructure investment spanning
37 files (+666 lines) over 17 days. I used a phased rollout strategy, starting
with Azure IPI and vSphere to de-risk deployment before expanding to other
platforms. This work is now running in production and directly enables Q2
Phase 2 work (WINC-1837)."

### Phase 4: Report Generation

**Step 4.1: Compile Data Summary**

From the CLI queries in Phase 2, compile statistics:

**Jira Summary:**
- Total issues filed
- Total issues closed
- Closure rate (closed / total * 100)
- Breakdown by status (Closed, In Progress, To Do, etc.)
- Breakdown by type (Story, Task, Bug, Epic, etc.)
- Average cycle time for closed issues

**GitHub Summary:**
- Total PRs merged
- Breakdown by repository
- Average cycle time for merged PRs
- Total files changed, lines added/deleted (aggregated)

**GitLab Summary (if applicable):**
- Total MRs merged
- Breakdown by project

**Step 4.2: Create Enhanced Markdown Report**

Combine the data summary with refined narratives from Phase 3.

Create an ENHANCED version with:

**Section 1: Top Accomplishments - WHAT and HOW**

For each of the top 5 achievements from Phase 2/3:
- Write 2-4 paragraphs per achievement
- Lead with the refined narrative from Phase 3
- Include technical details (files changed, cycle time)
- Explain HOW you accomplished it (phased rollout, architecture decisions)
- Show WHY it matters (enables Q2 work, fills coverage gap, team impact)

**Example structure for one achievement:**

```markdown
### 1. Built Foundational BYOH Infrastructure (PR #73920)

**WHAT I Accomplished:**
- Delivered Phase 1 BYOH provisioning support to Prow CI
- Scope: 37 files changed, +666 lines
- Duration: 17 days (2026-01-24 → 2026-02-10)
- Related Jira: WINC-1473

**HOW I Accomplished It:**
- Phased rollout strategy - Started with Azure IPI and vSphere to de-risk
- Step-registry integration - Integrated terraform-windows-provisioner
- Reusable components - Built provision/deprovision chains
- Production deployment - Successfully deployed and running

**Impact:**
- Foundation for Q2 work - Enables WINC-1837 (Phase 2)
- Team capability expansion - Windows QE can now test BYOH scenarios
- Risk-managed rollout - Phased approach prevented disruptions

**Why This Matters:**
This is strategic infrastructure investment - not fixing a bug, but building
foundational capability that multiplies team testing capacity.
```

**Section 2: By The Numbers**

Include a table from the generated report:

```markdown
| Metric | Q1 2026 Achievement |
|--------|---------------------|
| GitHub PRs Merged | 93 |
| Jira Issues Filed | 58 |
| Jira Issues Closed | 41 (70.7% closure rate) |
| Release Branches Supported | 5 (4.18-4.22) |
| Platforms Tested | 6 (AWS, Azure, GCP, vSphere, Nutanix, BYOH) |
| Average Cycle Time (Jira) | 24 days |
| Average Cycle Time (GitHub) | 15 days |
```

**Section 3: How I Work - Key Themes**

Analyze patterns across the top achievements:
- Strategic decision-making (pivots, phased rollouts)
- Fast iteration (cycle times, delivery speed)
- Multi-release thinking (backports, broad impact)
- Production mindset (deployed and running)
- Infrastructure over features (foundational capability building)

**Step 4.3: Save Enhanced Report**

Save as `~/Q{quarter}-{year}-Accomplishments-Enhanced.md`

Offer to:
1. Refine specific sections further
2. Add more achievements (beyond top 5)
3. Compare with previous quarter
4. Generate a shorter executive summary (for Workday text box)

## Writing Style

**Conversational, not structured:**
- Write in first person ("I delivered", "I architected")
- Answer WHAT, HOW, WHY naturally in narrative flow
- Don't separate into labeled sections unless helpful for clarity
- Focus on decision-making and strategic thinking, not just activity

**Impact over activity:**
- "Enabled comprehensive Windows testing for enterprise customers" > "Merged 25 PRs"
- "Filled vSphere proxy coverage gap with strategic pivot" > "Added test job"
- "60% reduction in manual triage time" > "Built dashboard"

**Quantify where possible:**
- Cycle times (17 days, 8 days)
- Scope (37 files, +666 lines)
- Impact (5 releases, 60% time savings, 93 PRs)
- Team benefit ("Windows QE can now test BYOH scenarios")

## Edge Cases

**CLI tools not installed:**
- Check which tools are missing:
  ```bash
  command -v jira || echo "jira CLI not installed"
  command -v gh || echo "GitHub CLI not installed"
  command -v glab || echo "GitLab CLI not installed (optional)"
  ```
- Guide user through installation (see Prerequisites)
- Verify authentication after installation

**User doesn't know their usernames:**
- Jira: Run `jira me` to get user email
- GitHub: Run `gh api user --jq .login` to get username
- GitLab: Run `glab api user --jq .username` to get username

**CLI authentication expired:**
- Jira: Run `jira init` to re-authenticate
- GitHub: Run `gh auth refresh`
- GitLab: Run `glab auth login`

**No data returned:**
- Verify CLI tools are authenticated (run `jira me`, `gh api user`)
- Check date range format (YYYY-MM-DD)
- Try without project/org filters first
- Check JQL syntax for Jira queries
- Verify GitHub search query syntax

**Too many achievements (100+ PRs):**
- Focus on top 10 by cycle time
- Group related PRs into themes (e.g., "AWS UPI test suite across 5 releases")
- Prioritize infrastructure over bug fixes
- Ask user which achievements they're most proud of

**User wants different narrative style:**
- Show all three frameworks (business_impact, technical_depth, leadership)
- Let them pick which resonates for each achievement
- Mix styles - infrastructure work might need technical_depth, while problem-solving needs leadership

**Rate limits (GitHub API):**
- GitHub API has rate limits (5000/hour authenticated)
- If hit, wait or ask user to continue later
- Use `gh api rate_limit` to check remaining quota

## Success Criteria

The skill is successful when:

1. User gets a comprehensive enhanced markdown report
2. Top 5 achievements have polished WHAT/HOW narratives
3. Report includes cycle time analysis and "By the Numbers" summary
4. Report is ready to copy into Workday with minimal editing
5. Process takes ~30 minutes instead of 4-6 hours

## After Report Generation

**Offer next steps:**
1. Generate shorter executive summary (for Workday 4000-char limit)
2. Compare with previous quarter to track growth
3. Drill into specific PRs/issues for more detail
4. Suggest goals for next quarter based on velocity analysis

**Don't auto-submit anywhere** - The report is a DRAFT for user refinement.

## Related Skills and Tools

**When to delegate:**
- Detailed Jira ticket investigation → Use Jira CLI or Jira skills
- GitHub PR code review → Use GitHub CLI or GitHub skills
- Google Workspace data → Use gws CLI or Google skills
- Specific platform deep-dives → Use platform-specific skills

**This skill's scope:**
- Aggregate multi-platform data using CLI tools
- Analyze cycle times and identify top work
- Transform technical descriptions into polished narratives
- Generate comprehensive enhanced reports

**This skill does NOT:**
- Auto-submit reports to Workday or any system
- Make assumptions about what's "important" - user decides
- Fabricate context or achievements - uses only real data
- Edit code or modify repositories
