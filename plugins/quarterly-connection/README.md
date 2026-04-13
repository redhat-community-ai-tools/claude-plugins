# quarterly-connection

Generate Red Hat Quarterly Connection reports by aggregating accomplishments from Jira, GitHub, Google Workspace (Docs, Slides, Calendar), and GitLab. Includes cycle time analysis, achievement ranking, and AI-powered narrative refinement for polished performance review documents.

**Two output formats:**
- `/quarterly` → Official Red Hat QC format (7 sections)
- `/quarterly-report` → Enhanced markdown with cycle time analysis and polished narratives

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

| Command | Description | Output Format |
|---------|-------------|---------------|
| `/quarterly` | Full quarterly connection report | Red Hat QC format (7 sections) |
| `/quarterly-report` | Enhanced report with cycle time analysis & narrative polish | Enhanced markdown with rankings |
| `/report` | Single-platform summary with custom date range | Basic summary |
| `/configure` | Verify platform connectivity and credentials | — |
| `/platforms` | Quick connectivity check for all platforms | — |

## Usage

### Basic Quarterly Report (Red Hat QC Format)

```text
> /quarterly
# Generates official Red Hat Quarterly Connection report
# Outputs: ~/quarterly-report-Q{n}-{year}.md
# Format: 7 sections (accomplishments, priorities, development, career growth, support, interests, appendix)
```

### Enhanced Report with Cycle Time Analysis

```text
> /quarterly-report
# Generates enhanced report with:
# - Cycle time analysis (identifies longest-running strategic work)
# - Multi-metric achievement ranking (cycle time + impact keywords + complexity)
# - AI-powered narrative refinement (business impact, technical depth, leadership frameworks)
# Outputs: ~/Q{n}-{year}-Accomplishments-Enhanced.md
# Format: Enhanced markdown with "By The Numbers", "How I Work" themes, polished WHAT/HOW narratives
```

**When to use which:**
- Use `/quarterly` for official Red Hat QC submission
- Use `/quarterly-report` for deep analysis and narrative polish
- Use both: Analyze with `/quarterly-report`, then copy polished narratives into `/quarterly` for submission

### Other Commands

```text
> /report
# Single-platform summary for a custom date range

> /configure
# Tests connectivity to each configured platform

> /platforms
# Quick probe to see which platforms are responding
```

## Skills

- **quarterly-connection** — Main skill that gathers data from all sources and generates structured Red Hat QC report
- **cycle-time-analysis** — Analyzes cycle times, ranks achievements by multiple metrics, and transforms technical descriptions into polished narratives using AI frameworks

## Features

### Cycle Time Analysis (NEW in v1.1.0)

Identifies your longest-running work as a signal of strategic/foundational contributions:

- **Average cycle times** - Jira issues vs GitHub PRs
- **Longest work items** - Top 10 by days from creation to completion
- **Insight**: Longer cycle times often = infrastructure/foundational work (not quick bug fixes)

### Multi-Metric Achievement Ranking (NEW in v1.1.0)

Ranks accomplishments using three complementary metrics:

1. **Cycle Time** - Longest-running work (strategic projects)
2. **Impact** - Keyword scoring (infrastructure, multi-release, automation)
3. **Complexity** - Scope analysis (files changed, lines added/deleted)

Items appearing in top 10 of multiple rankings = YOUR TRUE TOP ACHIEVEMENTS

### AI-Powered Narrative Frameworks (NEW in v1.1.0)

Three frameworks for transforming technical descriptions into polished narratives:

**Business Impact Framework**
- Emphasizes: Customer value, business objectives, strategic importance
- Example: "Added AWS UPI jobs" → "Enabled comprehensive Windows testing for enterprise customers using user-provisioned infrastructure..."

**Technical Depth Framework**
- Emphasizes: Architecture, complexity, engineering rigor
- Example: "Consolidated templates" → "Architected consolidation of 23 static YAMLs into 3 parameterized Go templates (+1,280/-1,257 lines)..."

**Leadership Framework**
- Emphasizes: Decision-making, strategic pivots, knowledge sharing
- Example: "Fixed proxy job" → "Investigated AWS limitation, discovered blocker, made strategic pivot to vSphere, documented decision-making..."

## License

MIT
