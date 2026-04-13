# /quarterly-report - Generate Enhanced Quarterly Report with Cycle Time Analysis

Generate enhanced quarterly achievement report with cycle time analysis, multi-metric achievement ranking, and AI-powered narrative refinement.

## Instructions

When the user invokes `/quarterly-report`, load and execute the enhanced quarterly report workflow that includes:

1. **Information Gathering** - Collect quarter, year, usernames, and filters
2. **Data Collection & Cycle Time Analysis** - Fetch Jira/GitHub/GitLab data and calculate cycle times
3. **Multi-Metric Achievement Ranking** - Rank by cycle time, impact keywords, and complexity
4. **AI Narrative Refinement** - Transform technical descriptions into polished WHAT/HOW narratives using three frameworks
5. **Enhanced Report Generation** - Create comprehensive markdown report

This command generates a different format than `/quarterly`:
- `/quarterly` → Red Hat Quarterly Connection format (7 sections: accomplishments, priorities, development, etc.)
- `/quarterly-report` → Enhanced markdown with cycle time analysis, "By The Numbers", and "How I Work" themes

Read and execute the workflow from `skills/cycle-time-analysis/SKILL.md`.
