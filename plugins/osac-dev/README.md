# OSAC Dev Plugin

OSAC development workflows: bug fix and bug reporting with Jira integration.

## Skills

- **fix-bug** — End-to-end bug fix workflow: opens a Jira bug, writes the fix with tests, verifies build/format/tests pass, commits, posts a PR, and moves the ticket to Code Review.
- **report-bug** — Report a bug in Jira without fixing it: creates a Bug ticket with proper description, links it to an epic, and assigns it.

## Usage

```
/fix-bug
/report-bug
```

## Requirements

- [jira-cli](https://github.com/ankitpokhrel/jira-cli)
- [GitHub CLI](https://cli.github.com/)
- Claude Code >= 2.0.0
