# KubeMedic architecture

## P0 (implemented)
Synthetic NodeSnapshot JSON → schema validation → evidence-matching deterministic rules → multiple hypotheses / uncertainty → JSON report.

**Evidence is not root-cause proof.** A NodeNotReady condition alone yields `unknown_not_ready`. If CNI and memory-pressure signals coexist, both are reported rather than inventing one cause.

## P1 (next)
A read-only, namespace/cluster-scoped Kubernetes collector will normalize Node conditions, Kubernetes Events and select Pod symptoms into the same JSON schema. Controller-runtime integration and watched objects will be introduced only when the read-only event contract is validated.

## P2
Risk assessment must account for PodDisruptionBudgets, capacity, workload criticality, failure domain and node maintenance windows. No node drain or replacement occurs without an explicit safe-action policy.

## P3
Evaluate against labeled reproducible fault scenarios, track diagnosis precision/recall, ambiguity rate, time to diagnosis, and disruptive recommendations. Compare against operator-only event inspection.

## Security
No Kubernetes access or external credentials in P0. All fixtures are synthetic and independent of proprietary infrastructure. Do not treat classifications as instructions to repair a real node.
