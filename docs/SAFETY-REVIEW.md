# KubeMedic disruption safety review (offline P2)

KubeMedic can now evaluate an *offline* Pod/PDB inventory together with a diagnostic report. The program **never** invokes drain, delete, cordon or patch. It produces either `HOLD` with reasons or `REVIEW_CANDIDATE` requiring independent operator validation.

A review candidate requires: a conclusive diagnosis, explicit Pod/PDB matches with sufficient disruption allowances, supported owner kinds, separately verified replacement capacity and maintenance approval. Missing data, unmanaged/static Pods, missing or overlapping PDBs, PDBs with insufficient disruptionsAllowed, and ambiguous diagnoses force HOLD.

```bash
python -m kubemedic.cli examples/faults/runtime.json --output diagnosis.json
python -m kubemedic.plan_cli diagnosis.json examples/inventory-blocked.json --spare-capacity-verified --maintenance-approved
```

This intentionally returns a nonzero exit code for a blocked plan. The `spare-capacity-verified` and `maintenance-approved` flags represent explicit human claims, not machine-verified checks.

**Limitations:** This is a conservative demonstration rather than a complete model of Kubernetes eviction semantics. PDB counts, selectors, topology spread, critical priority classes, local storage, graceful termination, concurrent drains and cluster-autoscaler behavior need live validation. Never use a REVIEW_CANDIDATE result as authorization to drain a real node.
