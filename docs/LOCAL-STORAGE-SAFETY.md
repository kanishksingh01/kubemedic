# Conservative disruption safety: critical and local-data pods

KubeMedic's read-only Pod inventory now records `priorityClassName` and whether a Pod has an `emptyDir` or `hostPath` volume. Its planner returns `HOLD` even if PDB and capacity checks otherwise pass for critical system Pods or potential local-data loss. It never performs a drain. Unknown storage/priority inputs are held for review.

This check is intentionally conservative and incomplete: `emptyDir` may be disposable, but users must deliberately decide that; hostPath may be persistent only on that node. Further storage-driver checks, local PVCs, topology policy, DaemonSets and maintenance authorization require evaluation before a real operation.

Unit tests exercise both collector extraction and fail-closed planner results. The Kubernetes Kind integration continues to verify the collector cannot patch or delete nodes.
