# quarterly-connection

Generate Red Hat Quarterly Connection reports by aggregating accomplishments from Jira, GitHub, Google Workspace (Docs, Slides, Calendar), and GitLab into a structured performance review document.

## What It Does

Pulls data from multiple platforms and generates a report following the official Red Hat Quarterly Connection format:

1. **Accomplishments** (WHAT + HOW) — grouped into narrative themes, not ticket lists
2. **Priorities** — top priorities for the upcoming quarter
3. **Development** — template for feedback and growth areas
4. **Career Growth** — template for short/long-term aspirations
5. **Support Needed** — template for manager discussion
6. **Interests** — template for energy/enjoyment reflection
7. **Appendix** — detailed PR tables, documents, presentations

### Data Sources

| Source | Data Gathered |
|--------|--------------|
| **Jira** | Issues created/closed, by type and status |
| **GitHub** | PRs merged by repo, PRs reviewed |
| **Google Docs** | Documents authored/edited in the quarter |
| **Google Slides** | Presentations created/updated |
| **Google Calendar** | Meeting count, recurring themes, key one-offs |
| **GitLab** | MRs merged (optional) |

## Prerequisites

At least one of these tools should be available:

- [`jira`](https://github.com/ankitpokhrel/jira-cli) — Jira CLI
- [`gh`](https://cli.github.com/) — GitHub CLI
- [`gws`](https://github.com/redhat-community-ai-tools/gws) — Google Workspace CLI
- [`quarterly-mcp-server`](https://github.com/redhat-community-ai-tools/quarterly-mcp-server) — Optional MCP server for consolidated queries

The skill adapts to whatever tools are available — if a source fails, it continues with the rest.

## Install

```bash
claude plugin install quarterly-connection
```

## Commands

| Command | Description |
|---------|-------------|
| `/quarterly` | Full quarterly connection report across all platforms |
| `/report` | Single-platform summary with custom date range |
| `/configure` | Verify platform connectivity and credentials |
| `/platforms` | Quick connectivity check for all platforms |

## Usage

```text
> /quarterly
# Generates a full Quarterly Connection report — asks for quarter, year, usernames
# Outputs: ~/quarterly-report-Q{n}-{year}.md

> /report
# Single-platform summary for a custom date range

> /configure
# Tests connectivity to each configured platform

> /platforms
# Quick probe to see which platforms are responding
```

## Skills

- **quarterly-connection** — Main skill that gathers data from all sources and generates a structured QC report

## License

MIT
