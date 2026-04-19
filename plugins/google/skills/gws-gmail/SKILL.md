---
name: gws-gmail
description: "Gmail: Send, read, and manage email. Use when the user wants to check email, read messages, summarize threads, search inbox, send replies, forward messages, or do anything involving Gmail — even if they don't say 'Gmail' explicitly (e.g., 'what did Alice email me about', 'summarize that NVIDIA thread', 'check my inbox')."
metadata:
  version: 0.22.0
  openclaw:
    category: "productivity"
    requires:
      bins:
        - gws
    cliHelp: "gws gmail --help"
---

# gmail (v1)

> **PREREQUISITE:** Read `../gws-shared/SKILL.md` for auth, global flags, and security rules — especially the **API-Specific Defaults** section. Gmail requires `"userId": "me"` on every raw API call.

```bash
gws gmail <resource> <method> [flags]
```

## Choosing the Right Command

Prefer helper commands (`+triage`, `+read`, `+send`, etc.) over raw API calls — they handle parameter defaults, MIME encoding, and output formatting automatically. Drop to raw API calls only when no helper covers the use case.

## Helper Commands

| Command | Description |
|---------|-------------|
| [`+triage`](../gws-gmail-triage/SKILL.md) | Show unread inbox summary (sender, subject, date) |
| [`+read`](../gws-gmail-read/SKILL.md) | Read a message body and headers by ID |
| [`+send`](../gws-gmail-send/SKILL.md) | Send an email |
| [`+reply`](../gws-gmail-reply/SKILL.md) | Reply to a message (handles threading automatically) |
| [`+reply-all`](../gws-gmail-reply-all/SKILL.md) | Reply-all to a message (handles threading automatically) |
| [`+forward`](../gws-gmail-forward/SKILL.md) | Forward a message to new recipients |
| [`+watch`](../gws-gmail-watch/SKILL.md) | Watch for new emails and stream them as NDJSON |

## Common Workflows

### Find and read a specific email

Search by subject, sender, or keywords, then read the body with `+read`:

```bash
# Step 1: Search for the thread (userId is required)
gws gmail users threads list --params '{"userId": "me", "q": "subject:NVIDIA escalation precompiled driver", "maxResults": 5}'

# Step 2: Read each message in the thread using its message ID
gws gmail +read --id <MESSAGE_ID> --headers
```

The thread list response includes `threads[].id` and `threads[].snippet`. Each thread's messages are in the `messages` array when you fetch the thread. Use `+read` with individual message IDs to get full bodies.

### Summarize an email thread

```bash
# Step 1: Find the thread
gws gmail users threads list --params '{"userId": "me", "q": "subject:weekly sync", "maxResults": 1}'

# Step 2: Get thread details (returns all messages with snippets)
gws gmail users threads get --params '{"userId": "me", "id": "<THREAD_ID>", "format": "metadata", "metadataHeaders": ["From", "To", "Subject", "Date"]}'

# Step 3: Read full body of specific messages that need more detail
gws gmail +read --id <MESSAGE_ID>
```

For threads with many messages, start with `format: "metadata"` to get headers and snippets, then use `+read` only on the messages that need full body extraction.

### Check inbox and act on messages

```bash
# Step 1: Triage unread messages
gws gmail +triage

# Step 2: Read a specific message from the triage output
gws gmail +read --id <ID_FROM_TRIAGE> --headers

# Step 3: Reply, forward, or take action
gws gmail +reply --message-id <ID> --body 'Thanks, I will review this.'
```

### Search with Gmail query syntax

The `q` parameter in raw API calls supports Gmail search operators:

| Query | Finds |
|-------|-------|
| `from:alice@example.com` | Messages from Alice |
| `subject:quarterly report` | Messages with subject containing "quarterly report" |
| `has:attachment filename:pdf` | Messages with PDF attachments |
| `after:2025/01/01 before:2025/06/01` | Messages in date range |
| `is:unread label:inbox` | Unread inbox messages |
| `"exact phrase"` | Messages containing exact phrase |

## Raw API Resources

When no helper command fits, use the raw API. Every `users.*` method requires `"userId": "me"` in `--params`.

### users

  - `getProfile` — Gets the current user's Gmail profile.
  - `stop` — Stop receiving push notifications for the given user mailbox.
  - `watch` — Set up or update a push notification watch on the given user mailbox.
  - `drafts` — Operations on the 'drafts' resource
  - `history` — Operations on the 'history' resource
  - `labels` — Operations on the 'labels' resource
  - `messages` — Operations on the 'messages' resource
  - `settings` — Operations on the 'settings' resource
  - `threads` — Operations on the 'threads' resource

## Discovering Commands

```bash
# Browse resources and methods
gws gmail --help

# Inspect a method's required params, types, and defaults
gws schema gmail.<resource>.<method>
```
