"""Offline read-only disruption review using explicit fixture data."""
import argparse
import json
import sys
from kubemedic.safety import evaluate_disruption

def main():
    parser = argparse.ArgumentParser(description="Offline disruption safety review")
    parser.add_argument("diagnosis", help="Existing diagnosis report JSON")
    parser.add_argument("inventory", help="Pod and PDB inventory JSON")
    parser.add_argument("--spare-capacity-verified", action="store_true")
    parser.add_argument("--maintenance-approved", action="store_true")
    args = parser.parse_args()
    try:
        with open(args.diagnosis, encoding="utf-8") as fh:
            diagnosis = json.load(fh)
        with open(args.inventory, encoding="utf-8") as fh:
            inventory = json.load(fh)
        result = evaluate_disruption(
            diagnosis, inventory.get("pods"), inventory.get("pdbs"),
            spare_capacity_verified=args.spare_capacity_verified,
            maintenance_approved=args.maintenance_approved)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"invalid safety evidence: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["decision"] == "REVIEW_CANDIDATE" else 3

if __name__ == "__main__":
    sys.exit(main())
