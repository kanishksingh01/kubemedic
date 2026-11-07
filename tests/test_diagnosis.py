import json
import unittest
from pathlib import Path
from kubemedic.diagnosis import diagnose

ROOT = Path(__file__).resolve().parents[1] / "examples" / "faults"

class DiagnosisTests(unittest.TestCase):
    def load(self, name):
        return json.loads((ROOT / (name + ".json")).read_text(encoding="utf-8"))

    def test_labeled_faults(self):
        for fixture, expected in (
            ("runtime", "container_runtime"), ("cni", "cni"),
            ("dns", "dns"), ("disk", "disk_pressure")):
            with self.subTest(fixture=fixture):
                report = diagnose(self.load(fixture))
                self.assertIn(expected, [f["fault"] for f in report["findings"]])
                self.assertFalse(report["action_executed"])
                self.assertTrue(report["requires_operator_approval"])

    def test_ambiguous_evidence_preserves_multiple_hypotheses(self):
        result = diagnose(self.load("ambiguous"))
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual({f["fault"] for f in result["findings"]},
                         {"memory_pressure", "cni"})

    def test_unknown_not_ready_is_not_misclassified(self):
        result = diagnose({"node": "worker-1", "conditions": {"Ready": "False"}, "events": []})
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(result["findings"][0]["fault"], "unknown_not_ready")

    def test_invalid_conditions_rejected(self):
        with self.assertRaises(ValueError):
            diagnose({"node": "worker-1", "conditions": {"Ready": True}, "events": []})

    def test_empty_evidence(self):
        result = diagnose({"node": "worker-1", "conditions": {"Ready": "True"}, "events": []})
        self.assertEqual(result["findings"][0]["fault"], "insufficient_evidence")

    def test_event_evidence_is_bounded(self):
        r = diagnose({"node": "worker-1", "events": ["ContainerRuntimeNotReady" + "x" * 900],
                      "conditions": {}})
        self.assertLessEqual(len(r["findings"][0]["evidence"][0]), 240)

if __name__ == "__main__":
    unittest.main()
