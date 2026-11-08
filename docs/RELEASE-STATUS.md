# KubeMedic — Release status and evidence

## Lab-V1 acceptance
- [x] Deterministic, evidence-linked node-failure diagnosis with explicit uncertainty
- [x] Labeled synthetic runtime, DNS, CNI, resource-pressure, and mixed-signal tests
- [x] Real Kind **containerd service interruption** detected from Node condition evidence and restored
- [x] Real Kind **worker heartbeat loss** classified as node-unreachable, not fabricated CNI root cause, and restored
- [x] Read-only Kubernetes Node/Event/Pod/PDB collection under a short-lived **scoped ServiceAccount** credential
- [x] PDB-aware advisory planner with fail-closed missing status, maintenance, and capacity checks
- [x] Critical-system Pod priority class and potential hostPath/emptyDir local data-loss holds
- [x] All mutations disabled; diagnostics never drain/cordon/patch/delete Nodes

## CI evidence
[Scoped Kubernetes read integration](https://github.com/kanishksingh01/kubemedic/actions/runs/42427713412), [worker heartbeat failure](https://github.com/kanishksingh01/kubemedic/actions/runs/42426445271), and [real containerd fault](https://github.com/kanishksingh01/kubemedic/actions/runs/42426445265) passed.

## Remaining before production consideration
Independent blind fault-classification precision/recall across many real fault classes, genuine CNI and DNS fault labs, CSI/local-PVC safety, topology/disruption concurrency, multi-node blast radius, safe staged repair procedures, and deployment operationalization. No automatic repair is included or implied.

**Classification: read-only experimental node diagnostics and conservative recovery planning; not an EKS repair controller.** [Walkthrough](END-TO-END.md).
