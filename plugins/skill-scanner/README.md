# Skill Scanner Plugin

Scan Claude Code plugins and skills for security vulnerabilities, prompt injection, and malicious instructions.

## What It Does

Skills are prompt files that instruct Claude what to do. A malicious skill could read SSH keys, exfiltrate credentials, or modify other skills. This scanner audits installed skills and produces a risk report with severity-rated findings.

## Usage

```
/scan-skills
```

Or trigger naturally: "scan my plugins for security issues", "is this skill safe?", "audit installed skills".

## Vulnerability Categories

| Severity | Category |
|----------|----------|
| Critical | Data exfiltration, destructive commands |
| High | Persistence attacks, obfuscation, prompt injection |
| Medium | Excessive scope |
| Low | Information gathering |

## Requirements

- Claude Code >= 2.0.0
