# Kubernetes Pod/PDB inventory and disruption preflight

`kubemedic.inventory_cli` uses read-only kubectl calls against an explicit context to list Pods scheduled on a named Node and policy/v1 PodDisruptionBudgets. It maps matching selectors to each Pod, reports `disruptionsAllowed`, and passes that inventory into the conservative safety adviser. No drain, eviction, patch or deletion is implemented.

An incomplete PDB status or selector, stale observedGeneration, a Pod from the wrong Node or invalid API response causes an error. Even when the offline adviser returns REVIEW_CANDIDATE, that outcome is **not** approval for a real-world Node drain. The CLI never mutates infrastructure.

The current test context uses an admin kubeconfig in disposable Kind, while reference RBAC can scope read-only API calls. Future work must apply and verify a dedicated ServiceAccount's credentials end-to-end. Cluster-wide list permissions for Pods and PDBs are required for a comprehensive node inventory.

Caveat: PDB selectors and disruptionsAllowed are only one part of Kubernetes safe eviction behavior. The current model does not handle concurrency with other drains or Pod topology constraints, local storage, or priority; it fails closed on missing/ambiguous evidence.
