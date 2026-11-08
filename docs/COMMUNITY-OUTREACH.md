# KubeMedic — Community outreach kit (draft, not posted)

**Target communities:** [Kubernetes SIG Node](https://github.com/kubernetes/community/blob/main/sig-node/README.md) via its #sig-node Slack channel; [Karpenter contributors](https://github.com/kubernetes-sigs/karpenter) via #karpenter-dev for explicitly Karpenter-specific questions; [Cilium community](https://docs.cilium.io/en/stable/community/community/) #kubernetes only for confirmed CNI diagnostics.

## Draft title
Node NotReady triage: what evidence makes a diagnosis reliable enough for a disruption plan?

## Draft
I've been building KubeMedic, a read-only Kubernetes node-diagnostics lab. It combines Node conditions and Events with Pod/PDB inventory and outputs an evidence-linked diagnosis plus a conservative HOLD/REVIEW_CANDIDATE recommendation. It never patches, drains, or replaces nodes.

In disposable Kind tests I interrupted containerd and separately paused a worker's heartbeat, then verified diagnostic classification and restoration. I deliberately classify heartbeat loss as *node unreachable* rather than inventing a CNI root cause. Scoped ServiceAccount reads and PDB/critical-Pod/local-data refusal tests are also working.

I would appreciate guidance on two gaps: how do SIG Node contributors recommend distinguishing kubelet/runtime/CNI failures with minimally privileged read-only evidence, and what additional hard blockers should a drain-planning tool consider (CSI/local PV, topology, concurrent disruptions, etc.)?

I'd be interested in participating in a focused discussion or sharing a reproducible synthetic fault demo if that helps the community. This is an independent experiment, not an AWS/Karpenter bug report.

## Etiquette
For SIG Node, ask a specific technical question in an appropriate channel or meeting agenda; don't cross-post the whole project. Don't present a CNI failure as confirmed without matching evidence, and don't claim EKS validation when the lab is Kind.

## Useful external background (not original source of this issue backlog)
[Karpenter Node NotReady troubleshooting](https://karpenter.sh/docs/troubleshooting/) discusses possible permissions, security-group and network causes. [SIG Node](https://github.com/kubernetes/community/blob/main/sig-node/README.md) focuses on pod/host resource interactions.

See [our end-to-end documentation](END-TO-END.md).
