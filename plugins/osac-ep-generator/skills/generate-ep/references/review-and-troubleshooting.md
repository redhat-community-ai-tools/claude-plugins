# Review Feedback Loop & Troubleshooting

## Phase 6: Review Feedback Loop

**Goal:** Address reviewer feedback and iterate on the EP.

**Trigger:** User says "address the review feedback on PR #N" or "update the EP based on reviews"

**Step 1: Fetch reviews**
```bash
gh pr view <PR_NUMBER> --repo osac-project/enhancement-proposals --json reviews,comments
```

**Step 2: Parse feedback**
Extract both human reviewer comments and any structured feedback. Parse:
- Reviewer name
- Review state (APPROVED, CHANGES_REQUESTED, COMMENTED)
- Comment body
- Line/file context (if inline comment)

**Step 3: Load review patterns**
Read `references/review_patterns.md` for context on common feedback themes.

**Step 4: Present feedback summary**
Group feedback by theme:
- Missing sections or insufficient detail
- Unclear workflows or user stories
- Insufficient risk analysis
- Terminology inconsistencies
- Requests for additional context

**Step 5: Propose changes**
For each feedback item, propose a specific change to the EP.

**Step 6: Apply changes**
Update the EP file at `enhancement-proposals/enhancements/<feature-slug>/README.md` with the changes.

**Step 7: Commit and push**
```bash
cd /home/eran/go/src/github/eranco74/osac-workspace/enhancement-proposals
git add enhancements/<feature-slug>/README.md
git commit -m "Address review feedback: <summary-of-changes>"
git push
```

**Step 8: Notify user**
"Changes pushed to PR. Summary of updates: <list-changes>"

## Quick Reference

| Task | Command |
|------|---------|
| Explore codebase | `rg --type proto "<resource>" --files-with-matches` |
| Fetch Jira ticket | `jira issue view MGMT-<number> --raw \| jq '.fields \| {summary, description, labels}'` |
| Create branch | `git checkout -b enhancement/<feature-slug>` |
| Create PR | `gh pr create --repo osac-project/enhancement-proposals --title "..." --body "..."` |
| Fetch reviews | `gh pr view <N> --repo osac-project/enhancement-proposals --json reviews,comments` |
| List existing EPs | `ls /home/eran/go/src/github/eranco74/osac-workspace/enhancement-proposals/enhancements/` |
| Check proto structure | `tree -L 2 /home/eran/go/src/github/eranco74/osac-workspace/fulfillment-service/proto/` |

## Common Issues

### Token/Auth Issues
- **Symptom**: `gh pr create` fails with "Not authenticated"
- **Check**: Run `gh auth status` to verify GitHub CLI is authenticated
- **Fix**: If not authenticated, run `gh auth login` and follow prompts

- **Symptom**: `jira issue view` fails with "Not logged in"
- **Check**: Run `jira me` to verify Jira CLI is authenticated
- **Fix**: If not authenticated, configure `~/.config/.jira/.config.yml` or run `jira init`

### Context Overflow
- **Symptom**: Codebase exploration fills context, leaving no room for drafting
- **Cause**: Reading too many full files during exploration
- **Fix**: Use `rg --files-with-matches` first to find relevant files, then read only key sections

### Missing Jira Ticket
- **Symptom**: User doesn't have a Jira ticket number
- **Fix**: Prompt user for ticket number. If none exists, use `TBD` in frontmatter tracking-link
