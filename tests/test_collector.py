import json
import unittest
from unittest.mock import Mock
from kubemedic.collector import collect, collect_and_diagnose, CollectionError

NODE = {"kind": "Node", "metadata": {"name": "worker-1"},
        "status": {"conditions": [
            {"type": "Ready", "status": "False"},
            {"type": "DiskPressure", "status": "True"}]}}
EVENTS = {"kind": "EventList", "items": [
    {"involvedObject": {"kind": "Node", "name": "worker-1"},
     "reason": "ImageGCFailed", "message": "node disk is full"},
    {"involvedObject": {"kind": "Node", "name": "other-node"},
     "reason": "ContainerRuntimeNotReady", "message": "ignore"}]}

class CollectorTests(unittest.TestCase):
    def runner(self, command, **kwargs):
        if "node" in command:
            return Mock(returncode=0, stdout=json.dumps(NODE))
        return Mock(returncode=0, stdout=json.dumps(EVENTS))

    def test_collect_read_only_and_identity(self):
        commands = []
        def recording(command, **kwargs):
            commands.append(command)
            return self.runner(command, **kwargs)
        snapshot = collect("worker-1", "kind-lab", runner=recording)
        self.assertEqual(snapshot["conditions"]["DiskPressure"], "True")
        self.assertEqual(len(snapshot["events"]), 1)
        self.assertEqual(len(commands), 2)
        for command in commands:
            self.assertIn("--context", command)
            self.assertIn("kind-lab", command)
            self.assertIn("get", command)
            self.assertNotIn("patch", command)
            self.assertNotIn("delete", command)

    def test_collector_to_diagnosis(self):
        report = collect_and_diagnose("worker-1", "kind-lab", runner=self.runner)
        self.assertIn("disk_pressure", [f["fault"] for f in report["findings"]])
        self.assertFalse(report["action_executed"])

    def test_invalid_name_rejected_without_command(self):
        def fail(*args, **kwargs):
            self.fail("kubectl should not be called")
        with self.assertRaises(ValueError):
            collect("worker-1;rm", "kind-lab", runner=fail)

    def test_node_mismatch_fails_closed(self):
        def fake(cmd, **kwargs):
            result = dict(NODE)
            result["metadata"] = {"name": "wrong-node"}
            return Mock(returncode=0, stdout=json.dumps(result))
        with self.assertRaises(CollectionError):
            collect("worker-1", "kind-lab", runner=fake)

    def test_api_errors_return_collection_error(self):
        def bad(*args, **kwargs):
            return Mock(returncode=1, stderr="forbidden")
        with self.assertRaises(CollectionError):
            collect("worker-1", "kind-lab", runner=bad)

if __name__ == "__main__":
    unittest.main()
