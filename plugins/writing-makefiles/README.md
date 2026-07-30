# Writing Makefiles Plugin

Write developer-shortcut Makefiles with self-documenting help, standard targets, and common-mistake avoidance.

## Skills

### writing-makefiles
Guidance for creating and reviewing Makefiles as developer command shortcuts. Covers self-documenting `make help` targets, standard target naming (`build`, `test`, `lint`, `run`, `clean`), the "wrap scripts, don't inline logic" pattern, common mistakes (missing separator, forgotten `.PHONY`, variable expansion), and testing strategies.

**Prerequisites:**
- `make` (GNU Make)

## Installation

```bash
claude plugin marketplace add redhat-community-ai-tools/claude-plugins
claude plugin install writing-makefiles@ecosystem-claude-plugins
```
