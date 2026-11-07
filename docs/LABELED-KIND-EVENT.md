# Synthetic failure signal through real Kubernetes API

The Kind integration now creates an isolated, explicitly labeled Node Event with reason `ContainerRuntimeNotReady` and an accompanying synthetic message. KubeMedic then reads this Event via actual `kubectl get events`, matches the runtime-failure signature, emits a structured diagnosis and verifies it never mutates the Node.

The test deletes the synthetic Event, and the ephemeral Kind cluster is destroyed automatically. **No actual containerd service is stopped.** This validates read-only collection, event parsing and classification integration; it does not yet measure ability to discover a true runtime outage or distinguish production root causes under confounding signals.
