# KubeMedic — Delivery and release gates

## Implemented and integration-tested
- Rule-based, evidence-citing diagnosis for runtime, CNI, DNS, disk/memory pressure and ambiguity.
- Real Kind read-only Node and Events collection; isolated synthetic Event and separate **actual containerd service stop** successfully diagnosed with Ready=False and verified recovery.
- Conservative offline PDB-aware disruption planner that never mutates a Node.
- Read-only Pod/PDB inventory with namespace, selector and status checks.
- Reproducible hand-labeled synthetic precision/recall report.

## Still required before claiming completion
- Extend the verified actual containerd fault experiment to real CNI/network failures and independently labeled validation cases.
- Independently label unseen failure cases and calculate confusion matrix, false positives and diagnostic time.
- Verify service-account-credential-bound reads, not only admin-context reads plus RBAC checks.
- Handle topology spread, local storage, concurrent evictions, critical Pod classes, and live PDB drift.
- Validate risk recommendations against safely staged recovery operations; no production auto-repair.

## Verified genuine runtime experiment
[CI proof](https://github.com/kanishksingh01/kubemedic/actions/runs/42425849378): disposable Kind worker containerd stopped; Node Ready became False; KubeMedic correctly matched the real condition message; containerd restarted; Node Ready returned True (~49.04 s for entire test window). No Node drain or production repair operation was performed.

## Current release classification
**Experimental read-only diagnostic prototype.** See [end-to-end walkthrough](END-TO-END.md).