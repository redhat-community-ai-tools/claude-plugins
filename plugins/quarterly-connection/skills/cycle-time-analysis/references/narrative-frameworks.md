# Narrative Framework Examples

## Framework 1: Business Impact

**Emphasize:** WHAT problem this solves, HOW it enables business objectives, WHO benefits, WHY it matters strategically.

**Template:**
```
I [delivered/enabled/built] [WHAT] by [HOW], [enabling/solving/creating] 
[BUSINESS_VALUE]. This work [spanned/involved] [SCOPE] over [DURATION]. 
[Strategic decision or approach]. [Production status and next steps enabled].
```

**Example:**
```
Raw: "Add Windows BYOH provisioning support"

Refined:
"I delivered Phase 1 BYOH (Bring Your Own Host) provisioning support to Prow CI,
establishing foundational infrastructure that enables all future BYOH testing for
the Windows QE team. This was strategic infrastructure investment spanning 37 files
(+666 lines) over 17 days. I used a phased rollout strategy, starting with Azure
IPI and vSphere to de-risk deployment before expanding to other platforms. This
work is now running in production and directly enables Q2 Phase 2 work (WINC-1837)."
```

## Framework 2: Technical Depth

**Emphasize:** WHAT technical challenges were solved, HOW you approached the problem, technical complexity and scope, engineering rigor.

**Template:**
```
I [architected/engineered/refactored] [WHAT] by [TECHNICAL_APPROACH], 
[achieving/creating] [TECHNICAL_OUTCOME]. [Scope details]. [Design decisions 
and trade-offs]. [Quality/rigor details].
```

**Example:**
```
Raw: "Consolidate test templates"

Refined:
"I architected consolidation of 23 static YAML test files into 3 parameterized Go
templates (+1,280/-1,257 lines), building 11 resource code generators for
programmatic generation. The net +23 lines (after deleting 1,257) demonstrates
massive complexity reduction. Created single source of truth eliminating copy-paste
errors and enabling future OTE migration."
```

## Framework 3: Leadership

**Emphasize:** HOW you influenced outcomes beyond code, WHAT decisions you made and why, WHO you helped or unblocked, strategic thinking.

**Template:**
```
I [investigated/discovered/pivoted] [SITUATION], [made decision] to [ACTION], 
and [documented/communicated/enabled] [KNOWLEDGE_SHARING]. [Technical 
justification]. [Outcome and team benefit].
```

**Example:**
```
Raw: "Fix vSphere proxy job"

Refined:
"I investigated AWS proxy configuration, discovered a bootstrap limitation where
Windows nodes can't reach external resources through proxy during initial setup,
and made a strategic pivot to vSphere platform where proxy works correctly. Rather
than forcing a broken approach, I documented the decision-making process in the PR
description and leveraged proven patterns. Filled coverage gap in 6 days with
working solution, demonstrating engineering judgment and knowledge sharing."
```

## Choosing the Right Framework

**Business Impact** → Infrastructure/foundational work, customer-facing features
**Technical Depth** → Large refactors, architectural changes, complex engineering
**Leadership** → Problem-solving with pivots, cross-team collaboration, strategic decisions

You can mix frameworks for different achievements in the same report.
