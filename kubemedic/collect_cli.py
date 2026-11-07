"""Read-only live Kubernetes collector and classifier; no remediation."""
import argparse
import json
import sys
from kubemedic.collector import collect_and_diagnose, CollectionError

def main():
    parser = argparse.ArgumentParser(description="Read-only Kubernetes Node triage")
    parser.add_argument("--node", required=True)
    parser.add_argument("--context", required=True, help="Explicit kubeconfig context")
    parser.add_argument("--events-namespace", default="default")
    args = parser.parse_args()
    try:
        report = collect_and_diagnose(args.node, args.context,
                                      events_namespace=args.events_namespace)
    except (ValueError, CollectionError) as exc:
        print(json.dumps({"error": str(exc), "action_executed": False}), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
