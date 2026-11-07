"""Genuine containerd service interruption within *disposable Kind only*.

Never takes a supplied Docker node/context. CI uses its own temporary cluster.
Restarts containerd in a finally block, even if diagnosis assertions fail.
"""
import json
import subprocess
import time
from datetime import datetime, timezone
from kubemedic.collector import collect_and_diagnose

WORKER = "kubemedic-worker"
CONTEXT = "kind-kubemedic"

def exec_command(args, timeout=20, check=True):
    result = subprocess.run(args, text=True, capture_output=True,
                            timeout=timeout, check=False)
    if check and result.returncode:
        raise RuntimeError(f"{args[0]} {args[1]} failed: {result.stderr[-400:]}")
    return result

def runtime_command(*args, check=True):
    return exec_command(["docker", "exec", WORKER, "systemctl", *args], check=check)

def read_node_condition():
    doc = json.loads(exec_command(
        ["kubectl", "--context", CONTEXT, "get", "node", WORKER,
         "-o", "json", "--request-timeout=5s"]).stdout)
    for condition in ((doc.get("status") or {}).get("conditions") or []):
        if condition.get("type") == "Ready":
            return {"ready": condition.get("status"),
                    "reason": condition.get("reason"),
                    "message": condition.get("message")}
    return {"ready": "Unknown", "reason": "MissingCondition"}

def wait_ready(expected, timeout=160):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        last = read_node_condition()
        if (last["ready"] == "True") == expected:
            return last
        time.sleep(3)
    raise AssertionError(f"worker ready state did not become {expected}: {last}")

def main():
    if exec_command(["kubectl", "config", "current-context"]).stdout.strip() != CONTEXT:
        raise RuntimeError("refusing runtime fault: active context is not disposable Kind")
    healthy = wait_ready(True, 60)
    stop_at = time.monotonic()
    fault = None
    diagnosis = None
    recovered = None
    try:
        runtime_command("stop", "containerd")
        active = runtime_command("is-active", "containerd", check=False)
        if active.returncode == 0:
            raise AssertionError("containerd did not stop")
        fault = wait_ready(False, timeout=150)
        diagnosis = collect_and_diagnose(WORKER, CONTEXT)
        if diagnosis["action_executed"]:
            raise AssertionError("diagnosis unexpectedly performed a mutation")
        if not any(f["fault"] == "container_runtime" for f in diagnosis["findings"]):
            raise AssertionError(f"runtime interruption not recognized: {diagnosis}")
    finally:
        runtime_command("start", "containerd")
        recovered = wait_ready(True, timeout=180)
    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "fault_class": "real containerd systemd stop on ephemeral Kind worker",
        "scope": "disposable kind-kubemedic only; no production node",
        "initial_ready": healthy, "runtime_outage_ready": fault,
        "diagnosis": diagnosis, "after_runtime_restart_ready": recovered,
        "duration_through_restoration_seconds": round(time.monotonic()-stop_at, 3),
        "recovery_verified": recovered["ready"] == "True",
    }
    print(json.dumps(report, indent=2))
    with open("runtime-fault-report.json", "w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)

if __name__ == "__main__":
    main()
