"""Read-only Pod/PDB inventory for conservative disruption planning.

The output feeds kubemedic.safety.evaluate_disruption; it never drains a Node.
Only standard policy/v1 PDB label selectors are supported. Invalid/stale inputs
fail closed with CollectionError.
"""
from kubemedic.collector import call_json, validate, CollectionError
from kubemedic.diagnosis import diagnose
from kubemedic.safety import evaluate_disruption
import subprocess

def matches_selector(labels, selector):
    if not isinstance(selector, dict):
        raise CollectionError("PDB selector is not an object")
    if not isinstance(labels, dict):
        labels = {}
    for key, value in (selector.get("matchLabels") or {}).items():
        if labels.get(key) != value:
            return False
    for expr in selector.get("matchExpressions") or []:
        if not isinstance(expr, dict):
            raise CollectionError("invalid PDB matchExpression")
        key, op, values = expr.get("key"), expr.get("operator"), expr.get("values", [])
        if not isinstance(key, str) or not isinstance(values, list):
            raise CollectionError("invalid PDB selector expression")
        present = key in labels
        if op == "In":
            ok = present and labels[key] in values
        elif op == "NotIn":
            ok = not present or labels[key] not in values
        elif op == "Exists":
            ok = present
        elif op == "DoesNotExist":
            ok = not present
        else:
            raise CollectionError("unsupported PDB selector operator")
        if not ok:
            return False
    return True

def _items(doc, expected):
    if not isinstance(doc, dict) or doc.get("kind") not in (expected, "List"):
        raise CollectionError(f"expected {expected} response")
    items = doc.get("items")
    if not isinstance(items, list):
        raise CollectionError("invalid Kubernetes resource list")
    return items

def collect_inventory(node, context, *, runner=subprocess.run):
    validate(node, "node")
    validate(context, "context")
    prefix = ["kubectl", "--context", context, "get"]
    pod_doc = call_json(
        prefix + ["pods", "--all-namespaces", "--field-selector",
                  f"spec.nodeName={node}", "-o", "json", "--request-timeout=5s"],
        runner=runner)
    pdb_doc = call_json(
        prefix + ["poddisruptionbudgets.policy", "--all-namespaces",
                  "-o", "json", "--request-timeout=5s"], runner=runner)
    raw_pods = _items(pod_doc, "PodList")
    raw_pdbs = _items(pdb_doc, "PodDisruptionBudgetList")
    pdbs = []
    for item in raw_pdbs:
        meta = item.get("metadata") or {}
        status = item.get("status") or {}
        ns, name = meta.get("namespace"), meta.get("name")
        allowed = status.get("disruptionsAllowed")
        if not isinstance(ns, str) or not isinstance(name, str) or type(allowed) is not int or allowed < 0:
            raise CollectionError("PDB status unavailable")
        if status.get("observedGeneration", -1) < meta.get("generation", 0):
            raise CollectionError("stale PDB status")
        selector = (item.get("spec") or {}).get("selector")
        if selector is None:
            raise CollectionError("PDB selector unavailable")
        pdbs.append({"namespace": ns, "name": name, "disruptions_allowed": allowed,
                     "selector": selector})
    pods = []
    for item in raw_pods:
        meta = item.get("metadata") or {}
        spec = item.get("spec") or {}
        status = item.get("status") or {}
        ns, name = meta.get("namespace"), meta.get("name")
        if not isinstance(ns, str) or not isinstance(name, str):
            raise CollectionError("Pod identity unavailable")
        if spec.get("nodeName") != node:
            raise CollectionError("Pod list contains a different node")
        if meta.get("deletionTimestamp"):
            raise CollectionError("Pod termination in progress")
        labels = meta.get("labels") or {}
        matching = [p["name"] for p in pdbs if p["namespace"] == ns
                    and matches_selector(labels, p["selector"])]
        owners = meta.get("ownerReferences") or []
        owner = owners[0].get("kind") if len(owners) == 1 else None
        if status.get("phase") not in ("Running", "Pending"):
            owner = None
        volumes = spec.get("volumes") or []
        if not isinstance(volumes, list):
            raise CollectionError("Pod volume inventory malformed")
        has_local_storage = any(isinstance(v, dict) and
                                any(key in v for key in ("hostPath", "emptyDir"))
                                for v in volumes)
        priority_class = spec.get("priorityClassName") or ""
        if not isinstance(priority_class, str):
            raise CollectionError("invalid Pod priority class")
        pods.append({"namespace": ns, "name": name, "owner_kind": owner,
                     "matching_pdbs": matching,
                     "has_local_storage": has_local_storage,
                     "priority_class": priority_class})
    return {"node": node, "pods": pods,
            "pdbs": [{k: p[k] for k in ("namespace", "name", "disruptions_allowed")} for p in pdbs],
            "source": "read-only Kubernetes Pod/PDB API",
            "action_executed": False}

def collect_and_plan(node, context, diagnosis, *, runner=subprocess.run):
    inventory = collect_inventory(node, context, runner=runner)
    plan = evaluate_disruption(diagnosis, inventory["pods"], inventory["pdbs"])
    return {"inventory": inventory, "plan": plan}
