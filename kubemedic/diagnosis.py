"""Small explainable, deterministic classifier for synthetic Kubernetes node snapshots."""
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class Finding:
    fault: str
    severity: str
    evidence: tuple[str, ...]
    recommendation: str
    action_executed: bool = False

    def as_dict(self):
        result = asdict(self)
        result["evidence"] = list(self.evidence)
        return result

PATTERNS = {
    "container_runtime": (
        ("ContainerRuntimeNotReady", "PLEG is not healthy", "container runtime is down",
         "containerd unavailable", "CRI not ready"),
        "Investigate container runtime service and kubelet logs; avoid a blind restart"),
    "cni": (
        ("NetworkPluginNotReady", "FailedCreatePodSandBox", "CNI plugin not initialized",
         "cilium agent not ready"),
        "Inspect CNI DaemonSet health, routes and pod sandbox errors"),
    "node_unreachable": (
        ("NodeStatusUnknown", "Kubelet stopped posting node status",
         "Kubelet never posted node status"),
        "Check node reachability and kubelet heartbeat; cause remains unconfirmed"),
    "dns": (
        ("DNSResolutionFailed", "NodeLocalDNSNotReady", "no such host",
         "SERVFAIL", "DNS query timeout"),
        "Check CoreDNS, NodeLocal DNS and upstream resolver reachability"),
}
PRESSURES = {
    "DiskPressure": ("disk_pressure", "Inspect ephemeral-storage, image usage and eviction signals"),
    "MemoryPressure": ("memory_pressure", "Inspect memory working sets, evictions and OOM events"),
}

def _normalize_snapshot(snapshot: dict[str, Any]):
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be a JSON object")
    name = snapshot.get("node")
    if not isinstance(name, str) or not name or len(name) > 253:
        raise ValueError("node must be a non-empty Kubernetes node identifier")
    conditions = snapshot.get("conditions", {})
    events = snapshot.get("events", [])
    if not isinstance(conditions, dict) or not isinstance(events, list):
        raise ValueError("conditions must be an object and events must be a list")
    if any(not isinstance(item, str) for item in events):
        raise ValueError("each event must be a string")
    if any(not isinstance(k, str) or v not in ("True", "False", "Unknown")
           for k, v in conditions.items()):
        raise ValueError("condition values must be True, False or Unknown strings")
    return name, conditions, events

def diagnose(snapshot: dict[str, Any]) -> dict[str, Any]:
    name, conditions, events = _normalize_snapshot(snapshot)
    findings: list[Finding] = []
    # Event snippets are reported as evidence for deterministic rules, not as authoritative root causes.
    for fault, (markers, recommendation) in PATTERNS.items():
        found = []
        for event in events:
            if any(marker.lower() in event.lower() for marker in markers):
                found.append(event[:240])
        if found:
            findings.append(Finding(fault, "warning", tuple(found[:5]), recommendation))
    for condition, (fault, recommendation) in PRESSURES.items():
        if conditions.get(condition) == "True":
            findings.append(Finding(fault, "warning", (f"{condition}=True",), recommendation))
    if conditions.get("NetworkUnavailable") == "True" and not any(f.fault == "cni" for f in findings):
        findings.append(Finding(
            "network_unavailable", "warning", ("NetworkUnavailable=True",),
            "Inspect node networking before blaming the CNI"))
    if conditions.get("Ready") == "False" and not findings:
        findings.append(Finding(
            "unknown_not_ready", "unknown", ("Ready=False",),
            "Collect kubelet, CRI, CNI and Node events before selecting a repair"))
    if not findings:
        findings.append(Finding(
            "insufficient_evidence", "unknown", tuple(),
            "No specific failure detected; continue read-only investigation"))
    # Multiple matching causes are not collapsed into a single unjustified root cause.
    status = "ambiguous" if len(findings) > 1 else (
        "unknown" if findings[0].severity == "unknown" else "identified_signals")
    return {
        "node": name,
        "status": status,
        "findings": [finding.as_dict() for finding in findings],
        "suggested_next_step": "human review of supporting evidence",
        "requires_operator_approval": True,
        "action_executed": False,
    }
