# Real worker heartbeat outage test

The lab creates a disposable Kind cluster, pauses its own worker's Docker container, and checks whether Kubernetes reports Node Ready=Unknown with NodeStatusUnknown. KubeMedic reads that status through the Kubernetes API, assigns the **node_unreachable** diagnostic category, and verifies that resuming the worker restores Ready=True.

This verifies a *Node reachability symptom*, **not** a Cilium/CNI root cause. The classifier deliberately does not claim a CNI failure from heartbeat loss alone.

The test never accesses external clusters and always tries to unpause its worker in a finally block. It still requires a dedicated CI cluster and should not be copied onto shared nodes. No node drain or repair is performed by KubeMedic.
