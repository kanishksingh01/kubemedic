import unittest
from pathlib import Path
from kubemedic.evaluate import evaluate

class EvaluationTests(unittest.TestCase):
    def test_synthetic_label_set(self):
        root = Path(__file__).resolve().parents[1] / "examples" / "faults"
        result = evaluate(root)
        self.assertEqual(len(result["results"]), 5)
        self.assertEqual(result["false_negative"], 0)
        self.assertEqual(result["false_positive"], 0)
        self.assertTrue(all(not row["actions_executed"] for row in result["results"]))

if __name__ == "__main__":
    unittest.main()
