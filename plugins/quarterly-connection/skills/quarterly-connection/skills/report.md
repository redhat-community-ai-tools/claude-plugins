# Single-Platform Report

Generate a summary for a single platform (Jira, GitHub, or GitLab) with a
custom date range. Use this when the user wants data from one platform or
needs a non-standard date range.

## Steps

### 1. Determine Platform and Parameters

**Identify the platform** from the user's request:
- Mentions tickets, issues, Jira project keys -> Jira
- Mentions PRs, pull requests, GitHub repos -> GitHub
- Mentions MRs, merge requests, GitLab projects -> GitLab
- Ambiguous -> ask

**Required parameters:**
- `username` — platform-specific username
- `start_date` — YYYY-MM-DD format
- `end_date` — YYYY-MM-DD format

**Optional:**
- `project` (Jira) — project key filter
- `org` (GitHub) — organization filter
- `group` (GitLab) — group filter

If the user specifies a quarter (e.g., "Q2 2026") instead of dates, calculate:
- Q1: Jan 1 - Mar 31
- Q2: Apr 1 - Jun 30
- Q3: Jul 1 - Sep 30
- Q4: Oct 1 - Dec 31

### 2. Call the Appropriate Tool

**Jira:**
```
get_jira_summary(username, start_date, end_date, project=None)
```

**GitHub:**
```
get_github_summary(username, start_date, end_date, org=None)
```

**GitLab:**
```
get_gitlab_summary(username, start_date, end_date, group=None)
```

### 3. Present Results

The tools return JSON. Parse and present in a readable format:

**For Jira**, highlight:
- Total issues, closure rate
- Breakdown by status, type, priority
- List of closed issues (most impactful first)

**For GitHub**, highlight:
- Total merged PRs
- Breakdown by repository
- List of PRs (grouped by repo)

**For GitLab**, highlight:
- Total merged MRs
- Breakdown by project
- List of MRs (grouped by project)

### 4. Offer Next Steps

- Save the summary to a file
- Run the same query for a different date range for comparison
- Drill into specific items using the platform's dedicated skill
- Expand to a full quarterly report using `/quarterly`
