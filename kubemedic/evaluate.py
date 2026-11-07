"""Evaluate deterministic diagnostic rules against labeled SYNTHETIC fixtures.

These scores are only fixture coverage, never estimates of production accuracy.
"""
import argparse
import json
from pathlib import Path
from kubemedic.diagnosis import diagnose

LABELS = {
    "runtime": {"container_runtime"},
    "cni": {"cni"},
    "dns": {"dns"},
    "disk": {"disk_pressure"},
    "ambiguous": {"cni", "memory_pressure"},
}
TARGETS = sorted(set().union(*LABELS.values()))

def evaluate(root: Path) -> dict:
    true_positive = false_positive = false_negative = 0
    cases = []
    for name, expected in LABELS.items():
        with (root / (name + ".json")).open(encoding="utf-8") as f:
            data = json.load(f)
        result = diagnose(data)
        predicted = {f["fault"] for f in result["findings"] if f["fault"] in TARGETS}
        tp = len(expected & predicted)
        fp = len(predicted - expected)
        fn = len(expected - predicted)
        true_positive += tp
        false_positive += fp
        false_negative += fn
        cases.append({"fixture": name, "expected": sorted(expected),
                      "predicted": sorted(predicted), "true_positive": tp,
                      "false_positive": fp, "false_negative": fn,
                      "actions_executed": result["action_executed"]})
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    return {
        "scope": "five hand-labeled synthetic fixtures, not real incidents",
        "true_positive": true_positive, "false_positive": false_positive,
        "false_negative": false_negative, "fixture_precision": round(precision, 4),
        "fixture_recall": round(recall, 4),
        "results": cases,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fixtures", default="examples/faults")
    p.add_argument("--output", default="synthetic-evaluation.json")
    args = p.parse_args()
    report = evaluate(Path(args.fixtures))
    print(json.dumps(report, indent=2))
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    if report["false_positive"] or report["false_negative"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
