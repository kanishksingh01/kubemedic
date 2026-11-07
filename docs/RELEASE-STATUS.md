# KubeMedic — Delivery and release gates

## Implemented and integration-tested
- Rule-based, evidence-citing diagnosis for runtime, CNI, DNS, disk/memory pressure and ambiguity.
- Real Kind read-only Node and Events collection; isolated synthetic Node Event injection.
- Conservative offline PDB-aware disruption planner that never mutates a Node.
- Read-only Pod/PDB inventory with namespace, selector and status checks.
- Reproducible hand-labeled synthetic precision/recall report.

## Still required before claiming completion
- Inject real isolated runtime/CNI/network failures rather than only labeling synthetic Events.
- Independently label unseen failure cases and calculate confusion matrix, false positives and diagnostic time.
- Verify service-account-credential-bound reads, not only admin-context reads plus RBAC checks.
- Handle topology spread, local storage, concurrent evictions, critical Pod classes, and live PDB drift.
- Validate risk recommendations against safely staged recovery operations; no production auto-repair.

## Current release classification
**Experimental read-only diagnostic prototype.** See [end-to-end walkthrough](END-TO-END.md).