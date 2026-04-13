# Workflow Controller

Route the user to the right phase based on their request.

## Routing Logic

1. **Check MCP availability first.** Before any data-gathering phase, verify
   that the quarterly MCP tools are available. If not, route to `/configure`.

2. **Parse the user's intent:**

   | Intent | Route to |
   |--------|----------|
   | Full quarterly report (Q1, Q2, etc.) | `/quarterly` |
   | Single-platform summary or custom dates | `/report` |
   | Setup, tokens, configuration | `/configure` |
   | "Is it working?", troubleshoot | `/platforms` |
   | Ambiguous — just mentions "quarterly" | Ask: full report or specific platform? |

3. **Gather required info before calling tools:**
   - Quarter and year (for `/quarterly`)
   - Date range (for `/report`)
   - Username(s) — ask if not known
   - Optional filters (project, org, group) — only ask if the user seems to
     work across many projects; otherwise skip

4. **After generating output:**
   - Present the report
   - Offer next steps: save to file, drill into details, compare quarters
   - If errors occurred on some platforms, note which ones failed and suggest
     checking `/configure`

## Remembering User Context

If this is not the first quarterly report the user has generated, check
memory for previously used usernames, projects, and organizations. Reuse
them as defaults — just confirm: "Last time you used `jdoe@redhat.com` for
Jira and `jdoe` for GitHub. Same this time?"

## Error Handling

- **MCP server not registered**: Guide to setup (see `references/setup.md`)
- **Auth failure on one platform**: Generate report for the others, note the failure
- **No results for a platform**: Could mean wrong username, wrong date range,
  or genuinely no activity — mention all three possibilities
- **Network/timeout**: Suggest retrying; MCP server may need restart
