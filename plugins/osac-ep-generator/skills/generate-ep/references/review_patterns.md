# OSAC Enhancement Proposal Review Patterns

This document captures common review feedback patterns from past OSAC EP PRs to help anticipate reviewer expectations and avoid common issues.

## Common Reviewer Expectations

### Completeness
- All template sections must be present, even if marked "TBD" or "N/A"
- User stories should cover provider AND tenant perspectives
- Implementation details should be thorough — successful EPs are 400-800 lines with deep technical content
- Test plans should describe strategy, not just "tests will be added"

### Clarity
- Technical terms should be defined upfront (see Networking EP's Terminology section)
- Relationships between resources should be explicit (parent-child, ownership, scope)
- Workflows should enumerate steps with actor roles clearly defined
- YAML frontmatter must be valid and all required fields present

### Consistency with OSAC Patterns
- New APIs should follow existing fulfillment-service patterns (gRPC + REST, proto schemas)
- Resources should include tenant isolation metadata (annotations for tenant-id, owner-reference)
- Controller patterns should align with osac-operator conventions
- Integration with osac-aap should be described for provisioning workflows

### Architectural Alignment
- Proposals should reference related EPs in see-also field
- Breaking changes to existing APIs must be called out explicitly
- Cross-repo impacts should be enumerated (which components need changes?)
- Pluggable architectures (like NetworkClass) are preferred over hardcoded implementations

## Frequent Feedback Themes

### Missing Context
**Pattern**: Reviewers ask "why this approach?" when alternatives aren't discussed
**Example**: "Why not use existing Kubernetes Network Policies instead of SecurityGroups?"
**Fix**: Add Alternatives section explaining other approaches and why they were rejected

### Vague Non-Goals
**Pattern**: Non-Goals that are too broad or don't clarify scope
**Example**: "Advanced features are out of scope" (too vague)
**Fix**: Be specific: "Auto-scaling and multi-region placement are out of scope and will be addressed in a separate VDCaaS proposal"

### Insufficient User Stories
**Pattern**: User stories that describe implementation, not user goals
**Bad**: "As a tenant, I want the VirtualNetwork CRD to have a CIDR field"
**Good**: "As a tenant, I want to define an isolated network with my own IP address space so that I can control my network topology"
**Fix**: Rewrite stories from user perspective using the "As a [role], I want to [action] so that I can [goal]" formula

### Test Plan Placeholders
**Pattern**: Test plan says "tests will be added" without describing what or how
**Bad**: "Unit and integration tests will be added during implementation"
**Good**: "Test plan will include: (1) Unit tests for proto validation and CIDR parsing, (2) Integration tests for VirtualNetwork creation and Subnet attachment workflows, (3) E2e tests validating full networking stack from ComputeInstance to external connectivity"
**Fix**: Describe the testing strategy even if details are TBD

### Missing Risk Analysis
**Pattern**: Risks section is empty or only lists obvious risks without mitigations
**Example**: "Risk: Implementation might have bugs" (too generic)
**Fix**: Identify specific risks (version skew between components, performance bottlenecks with large SecurityGroup rule counts, IPv6 adoption complexity) and provide concrete mitigations

### Inconsistent Terminology
**Pattern**: Same concept called by different names throughout the proposal
**Example**: "Floating IP" in user stories, "PublicIP" in API section, "External IP" in workflow
**Fix**: Define key terms in a Terminology section (see Networking EP) and use consistently

### Workflow Gaps
**Pattern**: Workflow description jumps from creation to deletion without describing intermediate operations
**Fix**: Include all lifecycle operations (create, read, update, delete, lifecycle management like start/stop for VMs)

## Review Interaction Patterns

### How Reviewers Engage
- **Inline comments**: Most feedback is file/line-specific, asking for clarification or flagging inconsistencies
- **Summary comments**: High-level architectural questions or requests for additional sections
- **Approval with comments**: Common pattern is APPROVED + minor suggestions for improvement before merge
- **Iteration**: Multiple rounds of feedback are normal — EPs evolve through discussion

### Key Reviewers by Domain
- **Networking**: adriengentil, eranco74, larsks, AlonaKaplan
- **Bare Metal**: tzumainn, eranco74
- **VMaaS**: adriengentil, akshaynadkarni, hpdempsey

### Response Expectations
- Address each comment explicitly (either update the proposal or explain why not)
- Update the `last-updated` field when making changes
- Push commits that address feedback with descriptive messages
- Don't resolve comments yourself — let the reviewer resolve after confirming fix

## Common CodeRabbit Patterns

**Note**: CodeRabbit feedback was not observed in the OSAC enhancement-proposals repo review history. The repo uses human reviewers exclusively. If CodeRabbit is added in the future, expect:
- Structured feedback in "Inline comments:" blocks
- Linting enforcement (YAML frontmatter validation)
- Spelling and grammar suggestions
- Consistency checks (term usage, section headers)

Current review process is human-driven with emphasis on technical depth and architectural alignment.

## Addressing Feedback

### Best Practices
1. **Read the full review first** before making changes — understand the big picture
2. **Group related feedback** — if multiple reviewers flag the same issue, address it comprehensively
3. **Ask clarifying questions** — if feedback is unclear, reply with a question rather than guessing
4. **Document decisions** — if you disagree with feedback, explain your reasoning (reviewers may approve your approach)
5. **Update incrementally** — commit small, focused changes that address specific feedback rather than one large "address all feedback" commit

### Iteration Workflow
1. Fetch reviews: `gh pr view <PR_NUMBER> --repo osac-project/enhancement-proposals --json reviews,comments`
2. Parse feedback and identify themes (missing sections, unclear workflows, insufficient detail)
3. Update the EP file with changes
4. Commit with descriptive message: `git commit -m "Address review feedback: clarify NetworkClass pattern and add Terminology section"`
5. Push: `git push`
6. Comment on PR with summary: "Updated to address feedback — added Terminology section, expanded Risks analysis, and clarified Workflow steps"

### When to Stop Iterating
- All reviewers have approved
- Remaining comments are "nits" (minor suggestions) that reviewers say can be addressed later
- Consensus is reached on core architectural decisions
- All required sections are substantive (not just "TBD")

### Red Flags (Stalled PR indicators)
- Reviewers ask the same question multiple times (feedback not addressed)
- Long gaps between reviews (author not responsive)
- Major architectural disagreement (needs synchronous discussion, not async PR comments)
- Missing required sections despite multiple reviews

If any red flags appear, escalate to synchronous discussion (Slack, video call) rather than continuing async iteration.
