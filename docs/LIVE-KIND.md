# KubeMedic read-only Kubernetes integration

The Kind workflow stands up an isolated two-node cluster, applies a reference least-privilege ServiceAccount, verifies allowed and denied verbs using Kubernetes RBAC authorization checks, and runs the collector against a real worker Node.

The Node is expected to be healthy; success proves that live Node and Event API results are parsed correctly without altering workloads. It does not prove classification of injected production-like failures. Those remain fixtures until bounded fault injection is added.

The workflow uploads a machine-readable diagnosis report. No cloud credentials, proprietary cluster data or destructive operations are used.

Important: the current Python CLI runs as the GitHub runner kubeconfig identity (cluster-admin for disposable Kind), while RBAC checks separately verify the proposed ServiceAccount's permissions. Full impersonation/token-backed execution is a subsequent hardening step.
