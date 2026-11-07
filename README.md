# KubeMedic

**Kubernetes node failure diagnosis and safe remediation planning.** Independent engineering study inspired by common EKS/Karpenter reliability challenges; not endorsed by AWS.

**Development visibility:** Private until ready for publication.

## P0 — Deterministic failure classifier

KubeMedic currently consumes a synthetic node snapshot and produces an evidence-linked diagnosis. This is deliberately **read-only**: it does not contact or mutate a Kubernetes cluster.

```bash
python3 -m kubemedic.cli examples/faults/runtime.json
python3 -m unittest discover -s tests -v
```

Python 3.10+ standard library; no network access or cloud credentials required.

### Initial fault classes
1. Container runtime failure (containerd/CRI not ready).
2. CNI / pod networking failure.
3. DNS resolution failure.
4. Node disk pressure and memory pressure.
5. Ambiguous or insufficient evidence (no automatic diagnosis).

### Milestones
- P0: failure catalog, synthetic examples, deterministic diagnostic rules and test reports.
- P1: read-only Kubernetes Node/Event/Pod API collector.
- P2: safe remediation advice with PodDisruptionBudget and blast-radius checks (no automatic repair by default).
- P3: comparative fault-injection benchmarks and an engineering case study.
- Later: optional AI explanations strictly grounded in collected evidence.

Read [architecture](docs/ARCHITECTURE.md) and [tracked milestones](https://github.com/kanishksingh01/kubemedic/issues/1).

**Safety:** No external system changes; use only synthetic fixtures and lab clusters. Never import proprietary operational configurations or employer data.
