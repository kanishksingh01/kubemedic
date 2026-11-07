"""Kind-only network availability experiment: pausing the worker container.

This verifies NodeStatusUnknown diagnosis during an actual heartbeat outage,
not the underlying physical reason. Never run against employer/cloud workers.
"""
import json
import subprocess
import time
from datetime import datetime, timezone
from kubemedic.collector import collect_and_diagnose
from kubemedic.runtime_fault import WORKER, CONTEXT, read_node_condition, wait_ready

def command(*args, timeout=15, allow_fail=False):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if result.returncode and not allow_fail:
        raise RuntimeError(f"{args[0]} failed: {result.stderr[-250:]}")
    return result.stdout.strip()

def wait_unknown(timeout=155):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        c = read_node_condition()
        if c["ready"] == "Unknown":
            return c
        time.sleep(3)
    raise AssertionError("Node Ready never became Unknown after worker interruption")

def main():
    if command("kubectl", "config", "current-context") != CONTEXT:
        raise RuntimeError("refusing network fault outside disposable Kind context")
    if command("docker", "inspect", "--format={{.Name}}", WORKER) != "/" + WORKER:
        raise RuntimeError("Docker worker identity mismatch")
    if wait_ready(True, 60)["ready"] != "True":
        raise RuntimeError("worker must start healthy")

    start = time.monotonic()
    unavailable = None
    report = None
    restored = None
    paused = False
    try:
        command("docker", "pause", WORKER)
        paused = True
        unavailable = wait_unknown()
        report = collect_and_diagnose(WORKER, CONTEXT)
        matches = [f for f in report["findings"] if f["fault"] == "node_unreachable"]
        if not matches:
            raise AssertionError(f"Node heartbeat loss not identified: {report}")
        if report["action_executed"]:
            raise AssertionError("read-only diagnosis unexpectedly mutated Kubernetes")
    finally:
        if paused:
            command("docker", "unpause", WORKER, allow_fail=True)
        restored = wait_ready(True, 165)
    result = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "disposable Kind worker container only",
        "fault": "Docker pause caused real Kubernetes worker heartbeat loss",
        "ready_during_fault": unavailable,
        "diagnosis": report,
        "ready_after_restore": restored,
        "total_disruption_and_recovery_seconds": round(time.monotonic()-start, 3),
        "warning": "Node heartbeat loss does NOT establish CNI-specific root cause",
    }
    print(json.dumps(result, indent=2))
    with open("network-fault-report.json", "w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)

if __name__ == "__main__":
    main()
