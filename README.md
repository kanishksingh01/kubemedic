# KubeMedic

**Evidence-based Kubernetes Node diagnostics** · Independent portfolio project · Private during development

**Start here:** [Read the complete end-to-end walkthrough](docs/END-TO-END.md).

The walkthrough explains Node failures, the evidence collection and rule evaluation flow, concrete examples, live Kind tests, safety guarantees, and what remains unfinished.

**Verified:** Labeled synthetic fault tests, read-only Node/Event collection from real Kind, and reference RBAC permission checks. **Not yet:** live fault-injection accuracy evaluation or automatic repair.

[Unit/fixture CI](.github/workflows/ci.yml) · [Real Kind read-only CI](.github/workflows/kind-integration.yml) · [Architecture](docs/ARCHITECTURE.md)

No production repairs or node mutations are implemented.
