"""Read-only disruption safety adviser. Never performs node operations.

A conservative plan needs explicit inputs; missing data fails closed.
PodDisruptionBudget results are supplied as evidence, not fabricated.
"""
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class DisruptionPlan:
    node: str
    decision: str
    reasons: tuple[str, ...]
    action: str
    approval_required: bool = True
    action_executed: bool = False

    def as_dict(self):
        result = asdict(self)
        result["reasons"] = list(self.reasons)
        return result

def evaluate_disruption(
    diagnosis: dict[str, Any],
    pods: list[dict[str, Any]] | None,
    pdbs: list[dict[str, Any]] | None,
    *,
    spare_capacity_verified: bool = False,
    maintenance_approved: bool = False,
) -> dict[str, Any]:
    """Only recommend considering a drain; never say a drain is unconditionally safe.

    pods must contain namespace, name, owner_kind and matching_pdbs (PDB names).
    pdbs must contain namespace, name, disruptions_allowed (integer).
    Unsupported pod ownership and unknown PDB coverage force a HOLD.
    """
    if not isinstance(diagnosis, dict) or not isinstance(diagnosis.get("node"), str):
        raise ValueError("diagnosis must identify a node")
    reasons = []
    if pods is None or pdbs is None:
        reasons.append("pod inventory or PodDisruptionBudget coverage not supplied")
        return DisruptionPlan(diagnosis["node"], "HOLD", tuple(reasons),
                              "collect pod and PDB evidence").as_dict()
    if not isinstance(pods, list) or not isinstance(pdbs, list):
        raise ValueError("pods and pdbs must be lists")
    budget_map = {}
    for budget in pdbs:
        if not isinstance(budget, dict):
            raise ValueError("PDB entries must be objects")
        key = (budget.get("namespace"), budget.get("name"))
        value = budget.get("disruptions_allowed")
        if not all(isinstance(x, str) and x for x in key) or type(value) is not int or value < 0:
            raise ValueError("malformed PDB coverage")
        if key in budget_map:
            raise ValueError("duplicate PDB entry")
        budget_map[key] = value
    required = {}
    for pod in pods:
        if not isinstance(pod, dict):
            raise ValueError("pod entries must be objects")
        ns, name, owner, names = (pod.get("namespace"), pod.get("name"),
                                  pod.get("owner_kind"), pod.get("matching_pdbs"))
        if not isinstance(ns, str) or not ns or not isinstance(name, str) or not name:
            raise ValueError("invalid Pod identity")
        if not isinstance(names, list) or not all(isinstance(x, str) and x for x in names):
            reasons.append(f"{ns}/{name}: PDB selection coverage unknown")
            continue
        if pod.get("has_local_storage") is True:
            reasons.append(f"{ns}/{name}: local ephemeral or hostPath storage requires data-loss review")
        elif pod.get("has_local_storage") not in (False, None):
            reasons.append(f"{ns}/{name}: local storage inventory uncertain")
        priority = pod.get("priority_class", "")
        if not isinstance(priority, str):
            reasons.append(f"{ns}/{name}: priority class inventory uncertain")
        elif priority in ("system-node-critical", "system-cluster-critical"):
            reasons.append(f"{ns}/{name}: critical system priority class")
        if owner not in ("ReplicaSet", "StatefulSet", "ReplicationController"):
            reasons.append(f"{ns}/{name}: unmanaged/static/unknown ownership")
        if len(names) > 1:
            reasons.append(f"{ns}/{name}: overlapping PDBs")
        if len(names) == 0:
            reasons.append(f"{ns}/{name}: no matching PDB")
        for budget_name in names:
            key = (ns, budget_name)
            required[key] = required.get(key, 0) + 1
    for key, count in required.items():
        available = budget_map.get(key)
        if available is None:
            reasons.append(f"{key[0]}/{key[1]}: PDB status unavailable")
        elif available < count:
            reasons.append(f"{key[0]}/{key[1]}: disruption budget {available} < node pods {count}")
    if not spare_capacity_verified:
        reasons.append("replacement capacity has not been verified")
    if not maintenance_approved:
        reasons.append("maintenance approval is missing")
    if diagnosis.get("status") in ("unknown", "ambiguous"):
        reasons.append("diagnosis is ambiguous or inconclusive")
    if reasons:
        return DisruptionPlan(diagnosis["node"], "HOLD", tuple(reasons),
                              "do not drain; collect evidence / plan remediation").as_dict()
    return DisruptionPlan(
        diagnosis["node"], "REVIEW_CANDIDATE", tuple(),
        "operator may evaluate manual drain after independent policy validation"
    ).as_dict()
