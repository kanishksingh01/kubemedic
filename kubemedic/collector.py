"""Read-only Kubernetes Node and Event collector backed by kubectl JSON output."""
import json
import re
import subprocess
from kubemedic.diagnosis import diagnose

NAME = re.compile(r"^[a-z0-9]([-a-z0-9.]*[a-z0-9])?$")

class CollectionError(RuntimeError):
    pass

def validate(value, label):
    if not isinstance(value, str) or len(value) > 253 or not NAME.fullmatch(value):
        raise ValueError(f"invalid {label}")
    for part in value.split("."):
        if len(part) > 63 or part.startswith("-") or part.endswith("-"):
            raise ValueError(f"invalid {label}")
    return value

def call_json(command, *, runner=subprocess.run):
    try:
        result = runner(command, capture_output=True, text=True,
                        timeout=12, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CollectionError("kubectl unavailable or timed out") from exc
    if result.returncode:
        raise CollectionError(f"read-only kubectl query failed (exit {result.returncode})")
    try:
        return json.loads(result.stdout)
    except (ValueError, TypeError) as exc:
        raise CollectionError("kubectl returned invalid JSON") from exc

def collect(node, context, *, events_namespace="default", runner=subprocess.run):
    """Uses explicit context and namespace; no shell, no mutations."""
    validate(node, "node")
    validate(context, "kubeconfig context")
    validate(events_namespace, "events namespace")
    prefix = ["kubectl", "--context", context]
    doc = call_json(prefix + ["get", "node", node, "-o", "json",
                             "--request-timeout=5s"], runner=runner)
    if not isinstance(doc, dict) or doc.get("kind") != "Node":
        raise CollectionError("response is not a Node")
    if (doc.get("metadata") or {}).get("name") != node:
        raise CollectionError("Node identity mismatch")
    status = doc.get("status") or {}
    if not isinstance(status, dict):
        raise CollectionError("invalid Node status")
    conditions = {}
    for item in status.get("conditions") or []:
        if isinstance(item, dict) and isinstance(item.get("type"), str):
            value = item.get("status")
            if value in ("True", "False", "Unknown"):
                conditions[item["type"]] = value
    events_doc = call_json(
        prefix + ["-n", events_namespace, "get", "events",
                  "--field-selector", f"involvedObject.kind=Node,involvedObject.name={node}",
                  "-o", "json", "--request-timeout=5s"], runner=runner)
    if not isinstance(events_doc, dict) or events_doc.get("kind") not in ("EventList", "List"):
        raise CollectionError("response is not an EventList")
    events = []
    for item in events_doc.get("items") or []:
        if not isinstance(item, dict):
            continue
        involved = item.get("involvedObject") or {}
        if involved.get("kind") != "Node" or involved.get("name") != node:
            continue
        reason = item.get("reason") or ""
        message = item.get("message") or ""
        events.append(f"{str(reason)[:120]}: {str(message)[:400]}")
    return {"node": node, "conditions": conditions, "events": events[-100:]}

def collect_and_diagnose(node, context, *, events_namespace="default", runner=subprocess.run):
    snapshot = collect(node, context, events_namespace=events_namespace, runner=runner)
    report = diagnose(snapshot)
    report["collection_context"] = context
    report["events_namespace"] = events_namespace
    return report
