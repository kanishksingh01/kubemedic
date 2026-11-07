# KubeMedic

**Evidence-linked Kubernetes Node diagnostics and conservative disruption planning.** Independent cloud infrastructure portfolio project; not affiliated with AWS. Private during development.

**Start:** [Full end-to-end guide](docs/END-TO-END.md) · [Release criteria](docs/RELEASE-STATUS.md).

KubeMedic classifies runtime, CNI, DNS, and resource-pressure signatures, retrieves Node/Event information from real Kind, and examines Pod/PDB coverage before proposing further investigation. Its recommendation system is read-only; no node drains or replacements exist in the current product.

**Current status:** Working read-only prototype with fixture evaluation and Kind validation; real runtime/CNI fault-injection accuracy remains unproven. AI deferred.

[CI](.github/workflows/ci.yml) · [Kind tests](.github/workflows/kind-integration.yml) · [Architecture](docs/ARCHITECTURE.md)
