# Full Quarterly Connection Report

Generate a comprehensive Red Hat Quarterly Connection report by gathering
data from all available platforms and structuring it into the official format.

## Steps

### 1. Gather Parameters

Collect the following from the user. If any are already known from the
conversation or memory, confirm rather than re-asking.

**Required:**
- `quarter` (1-4) — e.g., "Q2" means quarter=2
- `year` — e.g., 2026
- `username` — base username (can be discovered via `gh api graphql -f query='{ viewer { login } }'` for GitHub, or from git config)

**Optional (ask only if relevant):**
- `jira_username` — if different from base username (often an email)
- `github_username` — if different from base username
- `gitlab_username` — if different from base username
- `jira_project` — filter to a specific Jira project key
- `github_org` — filter to a specific GitHub organization
- `gitlab_group` — filter to a specific GitLab group

### 2. Gather Data from All Sources (in parallel)

Calculate the date range for the quarter:
- Q1: Jan 1 – Mar 31
- Q2: Apr 1 – Jun 30
- Q3: Jul 1 – Sep 30
- Q4: Oct 1 – Dec 31

**Jira** — query issues created and closed in the quarter:
```bash
jira issue list -q 'reporter = currentUser() AND created >= "YYYY-MM-DD" AND created <= "YYYY-MM-DD"'
```

**GitHub** — query PRs merged and PRs reviewed:
```bash
gh api search/issues -f q='is:pr author:USERNAME merged:YYYY-MM-DD..YYYY-MM-DD'
gh api search/issues -f q='is:pr reviewed-by:USERNAME -author:USERNAME merged:YYYY-MM-DD..YYYY-MM-DD' --jq '.total_count'
```

**Google Docs & Slides** — list documents modified in the quarter:
```bash
gws drive files list --params '{"q":"modifiedTime > \"YYYY-MM-DDT00:00:00\" and modifiedTime < \"YYYY-MM-DDT00:00:00\" and (mimeType = \"application/vnd.google-apps.document\" or mimeType = \"application/vnd.google-apps.presentation\")", "orderBy":"modifiedTime desc", "pageSize":50, "fields":"files(id,name,mimeType,modifiedTime,createdTime,webViewLink)"}' --format json
```

**Google Calendar** — summarize meetings attended:
```bash
gws calendar events list --params '{"calendarId":"primary","timeMin":"YYYY-MM-DDT00:00:00Z","timeMax":"YYYY-MM-DDT00:00:00Z","singleEvents":true,"orderBy":"startTime","maxResults":250}' --format json
```
Then parse to count total meetings, identify recurring themes, and notable one-offs.

**GitLab** (if available) — via quarterly-mcp-server or direct API.

### 3. Filter and Classify Google Workspace Data

Google Drive returns everything modified in the period, including noise.
Filter and classify before using:

**Google Docs — keep:**
- Design docs, proposals, architecture documents
- Enhancement proposals, implementation plans, gap analyses
- Developer guides, user guides, runbooks
- Incident investigations, postmortems

**Google Docs — exclude from main narrative (move to appendix or skip):**
- Auto-generated meeting notes (e.g., "- Notes by Gemini", "Meeting started")
- Shared recurring meeting note docs modified by many people
- Documents created before the quarter that were only lightly edited

**Google Slides — keep:**
- Presentations the user authored or significantly contributed to
- Demo decks, training decks, roadmap presentations

**Google Calendar — extract:**
- Total meeting count (filter out working location and focus time events)
- Recurring meeting themes with counts (shows where time was invested)
- Notable one-off meetings (interviews, kickoffs, demos, all-hands)
- Interview events (look for "Interview" in the summary)

### 4. Analyze and Theme the Data

This is the critical step. Don't just dump raw data — analyze it:

1. **Identify 2-3 themes** from the Jira tickets and PRs. Look for related
   tickets across repos, epics, or shared prefixes (e.g., MGMT-234xx all
   being networking). Two to three strong themes with depth is better than
   four or five thin ones.

2. **For each theme**, gather:
   - What was delivered (concrete outcomes, not just ticket titles)
   - How it was done (collaboration, approach, skills used)
   - Supporting PRs and documents from Google Docs/Slides

3. **Identify cross-team contributions**: interviews (from calendar),
   PR reviews (from GitHub), training delivered, documents shared,
   and community participation (from recurring meeting patterns).

4. **Match Google Docs/Slides to themes** — design docs and presentations
   are evidence of architectural thinking and leadership, not just code output.

### 5. Write the Report

Structure the report following the Red Hat Quarterly Connection format.
See the SKILL.md for the full format specification.

Write in the user's voice — first person, reflective, conversational.
See SKILL.md "Writing Style" and "Writing the Accomplishments Section"
for detailed guidance and examples.

**Key sections to populate from data:**
- Question 1: Accomplishments — 2-3 narrative paragraphs with WHAT+HOW
  woven together, plus a "By the Numbers" table at the end
- Question 2: Priorities — 2-3 paragraphs explaining what's next and why
- Appendix: PR table by repo, key docs (filtered), key presentations

**Sections to leave as templates (only include based on quarter):**
- Question 3: Development — Q3 only
- Question 4: Career Growth — Q3 only
- Question 5: Support Needed — Q3 only
- Interests — Q1 only

### 6. Save and Offer Enhancements

Save the report to `~/quarterly-report-Q{quarter}-{year}.md`.

After presenting, offer to:

1. **Enrich the narrative** — help the user strengthen the HOW sections
   with more specific examples of collaboration, leadership, or technical
   approach

2. **Save to Google Docs** — create a Google Doc version for easier editing
   and sharing with their manager

3. **Compare with previous quarter** — run the report for the previous
   quarter and highlight trends

4. **Drill into specifics** — use Jira/GitHub/Google skills to investigate
   specific items mentioned in the report

### 7. Handle Partial Failures

If one or more platforms return errors:

- Still present data from the platforms that succeeded
- Clearly note which platform(s) failed and why
- Suggest checking `/configure` to verify credentials
- Offer to retry the failed platform(s)
