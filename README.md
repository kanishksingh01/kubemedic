# KubeMedic

**Evidence-linked Kubernetes Node diagnostics and conservative disruption planning.** Independent cloud infrastructure portfolio project; not affiliated with AWS. Private during development.

**Engineering case study:** [Problem, design, measured evidence and tradeoffs](docs/CASE-STUDY.md).

**Start:** [Full end-to-end guide](docs/END-TO-END.md) · [Release criteria](docs/RELEASE-STATUS.md).

KubeMedic classifies runtime, CNI, DNS, and resource-pressure signatures, retrieves Node/Event information from real Kind, and examines Pod/PDB coverage before proposing further investigation. Its recommendation system is read-only; no node drains or replacements exist in the current product.

**Runtime fault proof:** [Actual containerd interruption → Ready=False → runtime diagnosis → Ready=True after restart](https://github.com/kanishksingh01/kubemedic/actions/runs/42425849378), approximately 49-second test window.


**Additional proof:** [Worker-heartbeat-loss classification and restoration](https://github.com/kanishksingh01/kubemedic/actions/runs/42426445271), and [restricted-ServiceAccount Node/Pod/PDB collection](https://github.com/kanishksingh01/kubemedic/actions/runs/42426765487). Critical-priority Pods and local data-risk now force HOLD.

**Current status:** Working read-only prototype with fixture evaluation and Kind validation; a genuine containerd interruption was diagnosed and recovered in disposable Kind; broader CNI/EKS accuracy remains unproven. AI deferred.

[CI](.github/workflows/ci.yml) · [Kind tests](.github/workflows/kind-integration.yml) · [Architecture](docs/ARCHITECTURE.md)
