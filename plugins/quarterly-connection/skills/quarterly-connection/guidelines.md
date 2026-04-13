# Quarterly Connection Guidelines

## Security

- **Never display API tokens** in output. When showing config files, mask
  token values with `****`.
- **Never write tokens** to report files or artifacts.
- Config file at `~/.quarterly-mcp-config.json` should be treated as
  sensitive — don't suggest committing it to version control.

## Privacy

- Reports may contain work output that the user considers private.
  Don't save reports to shared locations without explicit confirmation.
- When generating team reports (manager use case), each person's data
  should be presented separately — don't merge individuals into aggregates
  without being asked.

## Data Accuracy

- The MCP server queries live APIs. Results depend on correct usernames,
  date ranges, and API permissions.
- Jira uses `reporter` field for filtering — this captures issues the user
  created, not necessarily all issues they worked on. Note this limitation
  to the user if it seems relevant.
- GitHub searches merged PRs authored by the user. Draft PRs, reviews, and
  issue comments are not included.
- GitLab searches merged MRs within the date range. The date filter uses
  `updated_after`/`updated_before`, which may include MRs that were updated
  (not necessarily merged) in the range.

## Report Quality

- Raw data from the MCP tools is a starting point. The real value is in
  helping the user turn numbers into a narrative for their review.
- Group accomplishments into themes rather than presenting a flat list.
- Highlight impact — "fixed a critical auth bug affecting all users" is
  more meaningful than "closed PROJ-1234".
- When comparing quarters, focus on trends and context rather than raw
  number comparisons (a quarter with fewer PRs might have had bigger,
  more complex work).

## Error Handling

- Partial data is better than no data. If one platform fails, still
  generate the report with what's available.
- Be specific about what failed and why. "Jira returned an authentication
  error — your API token may have expired" is better than "Jira failed".
- Don't retry automatically more than once. If a platform fails twice,
  suggest the user check `/configure`.
