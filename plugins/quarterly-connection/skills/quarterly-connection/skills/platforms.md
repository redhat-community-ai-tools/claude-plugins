# Platforms Check

Quick verification of which platforms are responding. Use this for
troubleshooting or as a pre-flight check before generating a report.

## Steps

### 1. Probe Each Platform

Make lightweight calls to each platform tool with a narrow date range
(last 7 days) and the user's username. The goal is just to confirm
connectivity, not to gather meaningful data.

Run all three in parallel if possible:

```
get_jira_summary(username, <7-days-ago>, <today>)
get_github_summary(username, <7-days-ago>, <today>)
get_gitlab_summary(username, <7-days-ago>, <today>)
```

### 2. Classify Results

For each platform:
- **OK** — returned data without an `error` field
- **AUTH_FAIL** — returned an error about authentication/permissions
- **NOT_CONFIGURED** — returned an error about missing configuration
- **ERROR** — any other error

### 3. Report

```
Platform  | Status
----------|----------------
Jira      | OK
GitHub    | AUTH_FAIL
GitLab    | NOT_CONFIGURED
```

If any platform is not OK, suggest running `/configure` for detailed
troubleshooting.
