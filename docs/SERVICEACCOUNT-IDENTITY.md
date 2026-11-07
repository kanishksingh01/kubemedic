# Least-privilege credential-bound Kubernetes reads

The disposable Kind integration now generates a short-lived ServiceAccount TokenRequest credential and creates a separate `kubemedic-scoped` kubeconfig context. It runs the actual Node/Event collector and Pod/PDB inventory using this identity, **not the Kind cluster-admin context**.

This complements the explicit `kubectl auth can-i` checks, which verify that the ServiceAccount cannot patch or delete Nodes. The test's synthetic Node Event is still created using the disposable CI cluster-admin context and then read with the restricted identity.

The token is generated inside GitHub's isolated CI runner and is not committed to the repository or printed in the report. This is a disposable test, not a recommended credential-management scheme for real clusters. Future deployments must use supported in-cluster credentials and audit controls.
