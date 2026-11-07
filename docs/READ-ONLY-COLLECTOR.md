# Read-only Kubernetes collector (P1)

The collector uses `kubectl` with an explicit kubeconfig context to get a single Node and to list Node events from an explicitly selected namespace. All calls are read-only and execute without a shell.

Example for your own disposable lab only:

```bash
python3 -m kubemedic.collect_cli --node kind-worker --context kind-lab --events-namespace default
```

The name of the node and context must match actual resources in that lab. The collector does not download or infer credentials; it uses the existing, explicitly selected kubeconfig context.

Safety: no delete, patch, cordon, drain or other mutation. Reference read-only RBAC is in `deploy/read-only-rbac.yaml`. The actual invoking identity must be scoped accordingly.

Limitations: Events may be aggregated, expire quickly, or be located outside the chosen namespace. Missing signals are not proof of absence. The current collector does not access kubelet journald, CRI socket, Cilium status, or Node Problem Detector. A later version can add safely scoped diagnostic integrations after test coverage.
