"""Read-only diagnosis tool for synthetic node snapshots."""
import argparse
import json
import sys
from kubemedic.diagnosis import diagnose

def main():
    parser = argparse.ArgumentParser(description="Classify a synthetic Kubernetes node snapshot")
    parser.add_argument("snapshot", help="Path to JSON containing node, conditions and events")
    parser.add_argument("--output", help="Optional JSON diagnosis report path")
    args = parser.parse_args()
    try:
        with open(args.snapshot, encoding="utf-8") as file:
            document = json.load(file)
        report = diagnose(document)
    except (ValueError, OSError, TypeError) as exc:
        print(f"Diagnosis input error: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(rendered + "\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
