---
name: triage-issue
description: "Intelligently triage bug reports and error messages by searching for duplicates in Jira using jira-cli and offering to create new issues or add comments to existing ones. When an agent needs to: (1) Triage a bug report or error message, (2) Check if an issue is a duplicate, (3) Find similar past issues, (4) Create a new bug ticket with proper context, or (5) Add information to an existing ticket."
---

# Triage Issue

Automatically triage bug reports and error messages by searching Jira for duplicates, identifying similar past issues, and helping create well-structured bug tickets or add context to existing issues using `jira-cli`.

**Use this skill when:** Users need to triage error messages, bug reports, or issues to determine if they're duplicates and take appropriate action.

All commands use `--plain` for clean output and `--no-input` to skip interactive prompts.

---

## Workflow

Follow this 6-step process:

### Step 1: Extract Key Information

Analyze the bug report or error message to identify search terms.

**Extract:**
- **Error signature:** Error type, error code, specific error message text
- **Context:** Component or system affected, environment, user actions
- **Symptoms:** Observable behavior, impact

**Example:**
- Input: "Users getting 'Connection timeout' error when trying to login on mobile app"
- Extracted: Error="Connection timeout", Component="login, mobile app", Symptom="can't login"

---

### Step 2: Search for Duplicates

Execute **multiple targeted searches** to catch duplicates:

#### Error-Focused Search

```bash
jira issue list --jql 'project = PROJECT_KEY AND text ~ "error signature" AND type = Bug ORDER BY created DESC' --plain
```

#### Component-Focused Search

```bash
jira issue list --jql 'project = PROJECT_KEY AND text ~ "component keywords" AND type = Bug ORDER BY updated DESC' --plain
```

#### Symptom-Focused Search

```bash
jira issue list --jql 'project = PROJECT_KEY AND summary ~ "symptom keywords" AND type = Bug ORDER BY priority DESC, updated DESC' --plain
```

#### Search Tips

- Use key terms only, not full sentences
- Order by `created DESC` or `updated DESC` for recent issues first
- Include resolved issues to find fix history
- Don't over-filter — search across all statuses

For detailed issue inspection:

```bash
jira issue view <KEY> --plain --comments 20
```

---

### Step 3: Analyze Search Results

#### Duplicate Detection

**High confidence duplicate (>90%):**
- Exact same error message in summary or description
- Same component + same error type
- Recent issue (< 30 days) with identical symptoms
- **Action:** Recommend adding comment to existing issue

**Likely duplicate (70-90%):**
- Similar error with slight variations
- Same component but different context
- **Action:** Present as possible duplicate, let user decide

**Possibly related (40-70%):**
- Similar symptoms but different error
- Same component area but different specific error
- **Action:** Mention as potentially related

**Likely new issue (<40%):**
- No similar issues found
- **Action:** Recommend creating new issue

#### Check Fix History

If similar resolved issues are found, note:
- Who fixed it (assignee)
- When was it fixed
- Has it regressed (any reopened issues)

---

### Step 4: Present Findings to User

Present findings and wait for user decision before taking any action.

#### For Likely Duplicate

```
Triage Results: Likely Duplicate

I found a very similar issue already reported:

PROJ-456 - Connection timeout during mobile login
Status: Open | Priority: High | Created: 3 days ago
https://redhat.atlassian.net/browse/PROJ-456

Similarity:
- Same error: "Connection timeout"
- Same component: Mobile app login

Recommendation: Add your details as a comment to PROJ-456

Would you like me to:
1. Add a comment to PROJ-456 with your error details
2. Create a new issue anyway
3. Show more details about PROJ-456
```

#### For No Duplicates

```
Triage Results: No Duplicates Found

I searched Jira for:
- "Connection timeout" errors
- Mobile login issues

No similar open or recent issues found.

Recommendation: Create a new bug ticket

Would you like me to create a new bug ticket?
```

#### For Possible Regression

```
Triage Results: Possible Regression

This looks like it might be a regression of a previously fixed issue:

PROJ-567 - [Same issue description]
Status: Resolved (Fixed) | Fixed: 3 months ago
https://redhat.atlassian.net/browse/PROJ-567

Recommendation: Create a new issue and reference PROJ-567

Should I create a new issue with this context?
```

---

### Step 5: Execute User Decision

#### Option A: Add Comment to Existing Issue

```bash
jira issue comment add <KEY> $'## Additional Instance Reported\n\n**Error Details:**\n[error message or stack trace]\n\n**Context:**\n- Environment: [production, staging, etc.]\n- User Impact: [scope of impact]\n- Steps to Reproduce: [if provided]\n\n**Additional Notes:**\n[any unique aspects]'
```

#### Option B: Create New Issue

Ask which project and epic to use if not already known.

```bash
jira issue create -tBug \
  -s "[Component] Error Type - Brief Symptom" \
  -b $'**Description of the problem:**\n\n[1-2 sentence summary]\n\n**Error Details:**\n```\n[Error message or stack trace]\n```\n\n**How reproducible:**\n\n[Every time / Intermittent]\n\n**Steps to reproduce:**\n\n1. [Step 1]\n2. [Step 2]\n\n**Expected result:**\n\n[What should happen]\n\n**Actual result:**\n\n[What actually happens]\n\n**User Impact:**\n- Frequency: [how often]\n- Affected Users: [scope]\n\n**Related Issues:**\n- See also: PROJ-123 (similar but resolved)' \
  -P <EPIC-KEY> -l OSAC --no-input
```

**Summary Format:** Use the pattern: `[Component] Error Type - Brief Symptom`
- "Mobile Login: Connection timeout during authentication"
- "Payment API: NullPointerException in refund processing"
- NOT "Error in production" (too vague)

If a related resolved issue was found, link it:

```bash
jira issue link <NEW-KEY> <OLD-KEY> "is caused by"
```

---

### Step 6: Provide Summary

#### If Comment Added

```
Comment added to PROJ-456
https://redhat.atlassian.net/browse/PROJ-456

What I included:
- Your error details
- Environment context
- User impact information

Next Steps:
- The assignee will be notified
- Monitor PROJ-456 for updates
```

#### If New Issue Created

```
New Issue Created

PROJ-890 - Mobile Login: Connection timeout during authentication
https://redhat.atlassian.net/browse/PROJ-890

Type: Bug | Status: Open

What's Included:
- Complete error details
- Environment and reproduction steps
- References to related issues

Next Steps:
- Assign to appropriate team member
- Set priority based on user impact
```

---

## Tips for Effective Triage

### For Search
- Use multiple search queries with different angles
- Include both open and resolved issues
- Search for error signatures and symptoms separately
- Look at recent issues first (last 30-90 days)

### For Issue Creation
- Write clear, specific summaries with component names
- Include complete error messages in code blocks
- Add environment and impact details
- Reference related issues found during search

### For Duplicate Assessment
- Exact same error + same component + recent = high confidence duplicate
- Different error signatures = likely different issues
- When unsure, lean toward creating new issue (can be closed as duplicate later)

## When NOT to Use This Skill

**Don't use for:**
- Feature requests (use spec-to-backlog)
- General task creation (use jira-task-management)
- Status reports (use generate-status-report)

**Use only when:** A bug or error needs to be triaged against existing Jira issues.

## Rules

- Always present triage findings and wait for user confirmation before creating issues or adding comments
