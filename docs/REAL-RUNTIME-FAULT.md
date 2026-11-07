# Actual containerd failure on a disposable Kind worker

The new `Real Runtime Fault (Disposable Kind)` CI workflow creates a temporary Kind cluster with a worker named `kubemedic-worker`. The harness validates the current Kubernetes context and then **stops containerd inside that isolated Kind node**, not the GitHub host's Docker daemon. It waits for the Kubernetes Node Ready condition to turn non-True, invokes the regular read-only collector/classifier, restarts containerd in a finally block and verifies Ready=True returns.

Node Ready condition reason/message and real Node Events are used as diagnostic evidence. The JSON report will capture the exact observed condition, root-cause hints and recovery window. If the runtime service does not stop, Ready does not change, diagnostic signature is not recognized, or recovery fails, the test fails.

**Do not execute this harness outside disposable CI Kind.** It uses fixed context and worker container names and does not accept arbitrary targets. No customer, employer or cloud cluster is affected. This tests a genuine local container-runtime outage, but not all real-world EKS/EC2 failure classes or safe automatic repair.
