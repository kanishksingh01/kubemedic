# KubeMedic — End-to-end walkthrough

> **Status:** Working rule-based classifier + read-only Node/Event collector verified in a disposable Kind cluster. Independent AWS/EKS-aligned reliability project; not affiliated with AWS.

## 1. The problem

A Kubernetes Node becoming NotReady does not explain *why*. The cause might be containerd/CRI, a CNI problem, DNS, memory pressure, disk pressure, or several problems at once. Blind restarts or drains may make things worse.

**What we built:** An evidence-linked, deterministic diagnostic report, not a repair bot. P0 uses labeled synthetic fixtures; P1 reads real Kubernetes Node conditions and Events. No node mutations are implemented.

## 2. End-to-end flow

```text
   Synthetic fixture JSON         Real Kubernetes API (read-only)
           |                        |
           |                   kubectl get node
           |                   kubectl get events
           |                        |
           +----------> NodeSnapshot normalizer
                                  |
                         Rule-based classifier
                                  |
             matching signals / multiple hypotheses
                                  |
                     JSON diagnosis report
                                  |
                 human reviews next diagnostic step
                 (no cordon, drain, delete, or patch)
```

## 3. Follow a typical failure

1. A Node reports `Ready=False`.
2. KubeMedic collects its condition values and Node-associated Event reasons/messages.
3. If events contain a CRI/runtime failure signature, the report includes a `container_runtime` finding and quotes bounded evidence snippets.
4. If the Node simultaneously reports `MemoryPressure=True`, the classifier reports a *second* finding, rather than pretending one signal proves the root cause.
5. If it only sees `Ready=False`, it returns `unknown_not_ready` and asks for more signals.
6. The report says `action_executed=false` and `requires_operator_approval=true`. The program does not touch the Node.

Initial labeled scenarios: runtime failure, CNI issue, DNS failure, disk pressure, and ambiguous CNI + memory-pressure signals. These fixtures are **synthetic**, not recordings from employer clusters.

## 4. Test the system (CI runs automatically)

- [Unit and fixture CI](../.github/workflows/ci.yml)
- [Read-only Kind integration](../.github/workflows/kind-integration.yml)
- [Successful live Kind run](https://github.com/kanishksingh01/kubemedic/actions/runs/42398881397)

The Kind workflow creates a disposable two-node cluster, applies reference RBAC, checks that a ServiceAccount can read Nodes and Events but **cannot** delete Nodes or patch Pods, and runs the collector against a live, healthy Kind worker. Its node report is uploaded as a workflow artifact.

Optional local read-only fixture check, from repository root with Python 3.10+:

```bash
python3 -m kubemedic.cli examples/faults/runtime.json
python3 -m unittest discover -s tests -v
```

Optional *own disposable lab* Node read (requires an existing kubeconfig context):

```bash
python3 -m kubemedic.collect_cli --node kubemedic-worker --context kind-kubemedic --events-namespace default
```

No command should target a shared or employer cluster. The current CLI uses the provided kubeconfig identity, while CI separately checks the proposed ServiceAccount permissions.

## 5. Reading a report

A diagnosis includes `node`, `status`, `findings`, evidence strings, a recommended next diagnostic step, `requires_operator_approval`, and `action_executed`. Finding severity is a classifier label, not a validated incident priority or certainty score.

**What counts as success:** Identifying the expected fault category in labeled fixtures, preserving ambiguity when multiple clues coexist, handling a healthy live Node without mutation, and refusing invalid API responses.

**What it does not prove:** Precise root-cause attribution or time-to-repair performance for real failures. Live fault injection and diagnostic precision/recall evaluation remain outstanding.

## 6. Code map

| Component | Location |
| --- | --- |
| Rules and evidence | [kubemedic/diagnosis.py](../kubemedic/diagnosis.py) |
| Node and Event collector | [kubemedic/collector.py](../kubemedic/collector.py) |
| Fixture CLI | [kubemedic/cli.py](../kubemedic/cli.py) |
| Live read-only CLI | [kubemedic/collect_cli.py](../kubemedic/collect_cli.py) |
| Labeled scenarios | [examples/faults/](../examples/faults/) |
| Reference permissions | [deploy/read-only-rbac.yaml](../deploy/read-only-rbac.yaml) |
| Unit tests | [tests/](../tests/) |

## 7. Next milestones

- Introduce controlled Kind failure scenarios with verifiable labels, and compute diagnostic accuracy and false-positive rate.
- Add read-only signals from pods, CNI health, runtime/Node Problem Detector as appropriate.
- Design disruption-safety checks for PodDisruptionBudgets, node capacity, workload priority and failure domains.
- Only consider opt-in recovery after extensive tests; AI explanation remains deferred.

See [P0 issue](https://github.com/kanishksingh01/kubemedic/issues/1) and [blueprint](https://github.com/kanishksingh01/kubemedic/issues/6).
