# Quarterly Report Assistant Plugin

AI-powered performance review assistant for automating quarterly achievement report generation.

## Overview

Transform quarterly review preparation from **4-6 hours of manual work** into **30 minutes of focused refinement**.

This Claude Code plugin:
1. Aggregates data from Jira, GitHub, and GitLab using CLI tools
2. Analyzes cycle times to identify your longest-running strategic work
3. Ranks achievements by cycle time, impact, and complexity
4. Transforms technical PR/issue descriptions into polished business-impact narratives
5. Generates comprehensive enhanced markdown reports ready for Workday

## Features

- **Cycle Time Analysis**: Identify longest-running PRs and Jira issues (strategic work)
- **Smart Achievement Ranking**: Score by cycle time, infrastructure keywords, and complexity
- **Three Narrative Styles**: Business impact, technical depth, or leadership framing
- **CLI-Based**: Uses jira, gh, and glab CLI tools (no MCP server required)
- **On-Demand Loading**: Loaded only when you need it (token efficient)

## Installation

### 1. Install CLI Tools

**Required:**
```bash
# Jira CLI
brew install jira-cli
jira init

# GitHub CLI
brew install gh
gh auth login
```

**Optional:**
```bash
# GitLab CLI (if you use GitLab)
brew install glab
glab auth login
```

### 2. Verify CLI Tools

```bash
jira me          # Should show your Jira user info
gh api user      # Should show your GitHub user info
glab api user    # (Optional) Should show GitLab user info
```

### 3. Install the Plugin

**Option A: From GitHub (recommended)**
```bash
# Clone to your plugins directory
mkdir -p ~/.claude/plugins
cd ~/.claude/plugins
git clone https://github.com/redhat-community-ai-tools/quarterly-mcp-server.git quarterly-report-assistant
```

**Option B: From claude-plugins marketplace (coming soon)**
```bash
claude plugin marketplace add https://github.com/redhat-community-ai-tools/claude-plugins
claude plugin install quarterly-report-assistant
```

## Usage

### Basic Workflow

Start a Claude Code session and use the `/quarterly-report` command:

```
/quarterly-report
```

Claude will guide you through:
1. Specifying quarter and year (e.g., Q1 2026)
2. Providing usernames (Jira email, GitHub handle, GitLab handle)
3. Setting optional filters (Jira project, GitHub org)
4. Analyzing cycle times and identifying top achievements
5. Refining each achievement into polished narratives
6. Generating comprehensive enhanced markdown report

### Example Session

```
You: /quarterly-report

Claude: I'll help you generate your quarterly achievement report. Let me start by gathering some information:

1. Which quarter and year? (e.g., Q1 2026)
2. What is your Jira username (email)?
3. What is your GitHub username?
4. (Optional) Jira project filter?
5. (Optional) GitHub organization filter?

You: Q1 2026, jdoe@company.com, jdoe-gh, MYPROJECT, myorg

Claude: [Runs CLI queries to fetch data]
[Analyzes cycle times]
[Identifies top achievements]
[Refines narratives]
[Generates enhanced report]

Your Q1 2026 report has been saved to ~/Q1-2026-Accomplishments-Enhanced.md

Top 5 Achievements:
1. repo#123: Infrastructure PR (17 days, 37 files, strategic impact)
2. PROJ-456: Major refactor (63 days, complex architectural work)
...
```

## What You Get

### Enhanced Markdown Report

The generated report includes:

1. **Executive Summary**: High-level stats across all platforms
2. **Top Accomplishments with WHAT/HOW Narratives**: 2-4 paragraphs per achievement
   - What you accomplished (scope, duration, impact)
   - How you accomplished it (approach, decisions, strategy)
   - Why it matters (business value, team impact, strategic alignment)
3. **By The Numbers**: Supporting data table
4. **How I Work**: Themes and patterns across achievements
5. **Cycle Time Analysis**: Longest-running work identification
6. **Appendix**: Full PR/issue lists for reference

### Example Achievement Narrative

Instead of:
> "Added AWS UPI jobs across 5 releases"

You get:
> "I enabled comprehensive Windows testing for enterprise customers using user-provisioned infrastructure, delivering a single PR covering 5 active OpenShift releases (4.18-4.22) instead of separate efforts. This demonstrates efficient delivery and multi-release thinking - 1,156 lines across 25 files in just 8 days from creation to production deployment. Many enterprise customers use UPI instead of IPI, and this PR closes a major platform coverage gap."

## Three Narrative Styles

The skill can refine achievements using three frameworks:

1. **Business Impact**: Customer value, business objectives, strategic importance
2. **Technical Depth**: Architecture, complexity, engineering rigor
3. **Leadership**: Decision-making, influence, strategic thinking

Choose the style that best fits each achievement.

## How It Works

### Phase 1: Information Gathering
- Collects quarter, year, usernames, and filters
- Handles platform-specific username differences (Jira email vs GitHub handle)

### Phase 2: Data Collection & Analysis
- Uses `jira` CLI to fetch issues created/resolved in quarter
- Uses `gh` CLI to fetch merged PRs with detailed metrics
- Calculates cycle times for all items
- Identifies top 10 longest-running work
- Ranks achievements by cycle time, impact keywords, and complexity

### Phase 3: Narrative Refinement
- Fetches detailed context for each top achievement
- Applies three refinement frameworks
- Generates polished WHAT/HOW/WHY narratives
- Quantifies impact (files changed, cycle time, team benefit)

### Phase 4: Report Generation
- Compiles statistics from all platforms
- Combines refined narratives with supporting data
- Generates enhanced markdown report
- Saves to `~/Q{quarter}-{year}-Accomplishments-Enhanced.md`

## Comparison: MCP Server vs Skill

This plugin can also be used as an **MCP server** (always-loaded tools).

| Aspect | MCP Server | Skill (Plugin) |
|--------|------------|----------------|
| Token Usage | High (always loaded) | Low (on-demand) |
| Use Case | Frequent queries | Quarterly reports |
| Installation | Register with Claude Code | Install as plugin |
| Loading | Always in context | Loaded when triggered |
| Best For | Daily CI/testing queries | Once-per-quarter reviews |

**Recommendation:** Use the **skill** for quarterly reports (this plugin). Use the **MCP server** only if you need daily access to Jira/GitHub queries.

## CLI Commands Reference

### Jira Queries

```bash
# List issues created in Q1 2026
jira issue list --jql "reporter = currentUser() AND created >= '2026-01-01' AND created <= '2026-03-31'" --paginate 500

# Get issue details
jira issue view PROJ-123 --plain
```

### GitHub Queries

```bash
# Search merged PRs
gh api search/issues -f q="author:username is:pr is:merged merged:2026-01-01..2026-03-31 org:myorg"

# Get PR details
gh pr view 123 --repo owner/repo --json number,title,createdAt,mergedAt,changedFiles,additions,deletions
```

### GitLab Queries

```bash
# List merged MRs
glab api /merge_requests --paginate -f state=merged -f author_username=username -f updated_after=2026-01-01 -f updated_before=2026-03-31
```

## Troubleshooting

### CLI Not Authenticated

```bash
# Re-authenticate Jira
jira init

# Re-authenticate GitHub
gh auth refresh

# Re-authenticate GitLab
glab auth login
```

### No Data Returned

1. Verify CLI tools are authenticated: `jira me`, `gh api user`
2. Check date range format (YYYY-MM-DD)
3. Try without project/org filters first
4. Verify JQL syntax for Jira queries

### Rate Limits

GitHub API has rate limits (5000/hour authenticated):
```bash
gh api rate_limit
```

If hit, wait or continue later.

## Contributing

Contributions welcome! This plugin is part of the Red Hat Community AI Tools.

**Ideas for enhancements:**
- Recognition mining (extract peer kudos from PR comments)
- Interactive dialog mode (guided achievement narrative building)
- Goal setting based on historical velocity
- Export to Google Docs or Confluence
- Team aggregation (manager view of team accomplishments)

## License

Apache License 2.0 - See [LICENSE](../LICENSE) for details.

## Related Projects

- [quarterly-mcp-server](https://github.com/redhat-community-ai-tools/quarterly-mcp-server) - MCP server version with always-available tools
- [ci-failure-tracker](https://github.com/redhat-community-ai-tools/ci-failure-tracker) - Automated CI failure tracking
- [claude-plugins](https://github.com/redhat-community-ai-tools/claude-plugins) - Plugin marketplace

## Support

- **Issues**: https://github.com/redhat-community-ai-tools/quarterly-mcp-server/issues
- **Discussions**: https://github.com/redhat-community-ai-tools/quarterly-mcp-server/discussions

---

**Built for Claude Code** | **Part of Red Hat Community AI Tools**
