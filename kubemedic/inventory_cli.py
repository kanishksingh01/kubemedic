"""Read-only Pod/PDB inventory and fail-closed disruption advice."""
import argparse
import json
import sys
from kubemedic.collector import collect_and_diagnose, CollectionError
from kubemedic.inventory import collect_and_plan

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", required=True)
    parser.add_argument("--context", required=True)
    args = parser.parse_args()
    try:
        diagnosis = collect_and_diagnose(args.node, args.context)
        result = collect_and_plan(args.node, args.context, diagnosis)
        result["diagnosis"] = diagnosis
    except (ValueError, TypeError, CollectionError) as exc:
        print(json.dumps({"error": str(exc), "action_executed": False}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    # Always nonzero for HOLD; advisory only even on REVIEW_CANDIDATE.
    return 3 if result["plan"]["decision"] == "HOLD" else 0

if __name__ == "__main__":
    sys.exit(main())
