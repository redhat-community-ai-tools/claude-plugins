---
name: dci-mcp-management
description: Manage DCI jobs, components, Jira tickets, GitHub/GitLab issues, Red Hat support cases, and Google Drive docs via the dci-mcp-server MCP integration
---

# DCI MCP Management

AI-assisted DCI (Distributed CI) and multi-platform integration through the dci-mcp-server MCP server. See the [plugin README](../../README.md) for setup, prerequisites, and tool reference.

## When to Use This Plugin

Use **dci-mcp-server** for DCI-centric workflows that span multiple platforms — CI job analysis, cross-referencing DCI results with Jira tickets, GitHub/GitLab PRs, Red Hat support cases, and Google Drive reports. For standalone Jira or GitHub work unrelated to DCI, prefer the `jira`, `jira-mcp`, or built-in GitHub plugins instead.

## DCI Job Query Syntax

The `search_dci_jobs` tool uses a parenthesized query language. Every condition must be wrapped in parentheses, and combined conditions need extra grouping.

### Operators

| Operator | Example |
|----------|---------|
| Equality | `(status='failure')` |
| Comparison | `(created_at>='2025-06-01')`, `(duration>=1000)` |
| List membership | `(tags in ['daily'])`, `(status in ['failure', 'error'])` |
| AND / OR | `((cond1) and (cond2))` |
| Nested fields | `(components.type='ocp')`, `(components.version='4.19.0')` |

### Parenthesization Rules

- 1 condition: `(field='value')`
- 2 conditions: `((cond1) and (cond2))`
- 3 conditions: `(((cond1) and (cond2)) and (cond3))`

### Common Query Patterns

Find failed daily jobs for a specific OCP version in a date range:
```
(((tags in ['daily']) and (status='failure')) and (components.type='ocp'))
```

Find jobs by component type and version:
```
((components.type='ocp') and (components.version='4.19.0'))
```

Find jobs with multiple component filters (e.g., OCP + storage):
```
(((components.type='ocp') and (components.version='4.19.0')) and ((components.type='storage') and (components.name='my-storage')))
```

Filter by date range:
```
((created_at>='2025-06-01') and (created_at<='2025-06-07'))
```

Never use `=` for dates — always use `>=` / `<=` range comparisons.

## DCI Component Query Syntax

The `query_dci_components` tool uses a different DSL:

- `eq(type,ocp)` — filter by type (not by name)
- `and(eq(type,ocp),contains(tags,build:ga))` — GA OCP components
- `ilike(name,%)` — list all components
- `like(name,ocp-%)` — name pattern matching

## Usage Patterns

### CI Monitoring

```
"Find all failed daily jobs for OCP 4.19 in the last week"
"Show me the error rate trend for the BOS2 lab this month"
"List GA OpenShift components released after 2025-01-01"
```

### Cross-Platform Correlation

```
"Find the failing DCI job, get the related Jira ticket, and check if there's a GitHub PR fixing it"
"Search for OCP 4.19 Jira tickets and cross-reference with DCI job results"
"Find open GitLab merge requests related to a DCI test failure"
```

### Support Case Investigation

```
"Get the details of support case 03619625 and check if there's a related errata"
"List attachments for a support case and find linked Bugzilla bugs"
```

### Reporting

```
"Generate a DCI report and convert it to a Google Doc in the weekly-reports folder"
"Create a Google Doc summarizing this week's CI failures"
```

## MCP Prompts

The server provides structured analysis prompts that guide multi-step investigations.

### Root Cause Analysis (rca)

```
"Use the rca prompt for DCI job abc12345-..."
```

Performs structured root cause analysis: gathers evidence from ansible.log, logjuicer, and must_gather files, applies the 5 Whys method, adversarially challenges findings, and produces a confidence-rated report at `/tmp/dci/rca-<job id>.md`.

### Weekly / Biweekly Analysis

```
"Use the weekly prompt for the BOS2 remoteci"
"Use the biweekly prompt for team MyTeam"
```

Analyzes DCI jobs over 1 or 2 weeks: job counts, failure rates, top failure reasons, anomaly detection, and recommendations. Reports saved to `/tmp/dci/`.

### Quarterly Analysis

```
"Use the quarterly prompt for the BOS2 remoteci"
```

Comprehensive 3-month analysis with paginated data collection, caching, and statistics across pipelines, topics, components, and failure patterns. Includes trend detection and anomaly detection. Reports saved to `/tmp/dci/<remoteci>/quarterly/`.

## Reference

- [dci-mcp-server](https://github.com/redhat-community-ai-tools/dci-mcp-server)
- [DCI Documentation](https://doc.distributed-ci.io/)
- [MCP Protocol](https://modelcontextprotocol.io)
