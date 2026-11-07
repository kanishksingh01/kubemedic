# Engineering case study — KubeMedic

## Problem
A Kubernetes Node can become NotReady because of runtime, networking, DNS, storage or resource pressure. Treating every NotReady condition as a drain/restart request is dangerous and can violate workload disruption policies.

## Approach
I built a deterministic evidence collector and diagnostic classifier. Its synthetic fixtures cover containerd/CRI failures, CNI, DNS, disk/memory pressure and overlapping symptoms. A read-only collector queries real Nodes, Events, Pods and PodDisruptionBudgets in disposable Kind. A conservative planner flags missing policy evidence, capacity uncertainty and critical workloads before suggesting *human investigation*, never a Node mutation.

## Reproducible evidence
- CI verifies classifications against five labeled synthetic fault cases and uploads an explicit precision/recall report. The fixtures deliberately contain the classifier's known signatures; this is not independent clinical or production accuracy.
- Live Kind integration retrieves Node conditions and Node-associated Events, injects a clearly labeled synthetic runtime event through the real Kubernetes API, and detects it without altering the worker.
- A separate live inventory check reads Pod/PDB data, verifies read-only permissions and yields a conservative HOLD.

**Proof:** [Kind Node/Event and Pod/PDB integration](https://github.com/kanishksingh01/kubemedic/actions/runs/42424188440) · [CI classifier evaluation](https://github.com/kanishksingh01/kubemedic/actions/runs/42424188439).

## Engineering decisions
- No direct drain, patch, cordon, delete or self-repair path.
- Multiple signals remain multiple hypotheses instead of a fabricated root cause.
- Missing PDB selectors, stale status or unknown Pod ownership prevent a positive disruption recommendation.
- An operator must validate capacity and maintenance approval independently.

## Important limitations
The synthetic runtime Event does not actually break containerd. The classifier has not been evaluated on independently labeled real node outages, and the planner does not cover every Kubernetes eviction invariant. The current live tests use an isolated admin kubeconfig while RBAC permissions are checked separately.

## What would make this complete
Add controlled genuine runtime/CNI fault injection, independently labeled outcomes and time-to-diagnosis metrics; prove identity-scoped collection and real eviction-policy behavior under changing PDB/capacity conditions. See [release gates](RELEASE-STATUS.md) and [full walkthrough](END-TO-END.md).
