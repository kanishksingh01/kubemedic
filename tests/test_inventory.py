import json
import unittest
from unittest.mock import Mock
from kubemedic.inventory import collect_inventory, matches_selector
from kubemedic.collector import CollectionError

NODE = "lab-worker"
POD = {"metadata": {"namespace": "demo", "name": "web-abc", "labels": {"app": "web"},
                    "ownerReferences": [{"kind": "ReplicaSet"}]},
       "spec": {"nodeName": NODE}, "status": {"phase": "Running"}}
PDB = {"metadata": {"namespace": "demo", "name": "web-pdb", "generation": 2},
       "spec": {"selector": {"matchLabels": {"app": "web"}}},
       "status": {"disruptionsAllowed": 1, "observedGeneration": 2}}

def runner(cmd, **kwargs):
    doc = {"kind": "PodList", "items": [POD]} if "pods" in cmd else {
        "kind": "PodDisruptionBudgetList", "items": [PDB]}
    return Mock(returncode=0, stdout=json.dumps(doc))

class InventoryTests(unittest.TestCase):
    def test_real_api_shapes_and_pdb_mapping(self):
        commands = []
        def tracking(cmd, **kwargs):
            commands.append(cmd)
            return runner(cmd, **kwargs)
        report = collect_inventory(NODE, "kind-kubemedic", runner=tracking)
        self.assertEqual(report["pods"][0]["matching_pdbs"], ["web-pdb"])
        self.assertEqual(report["pdbs"][0]["disruptions_allowed"], 1)
        self.assertTrue(all("get" in c and "patch" not in c for c in commands))
        self.assertFalse(report["action_executed"])

    def test_match_expressions(self):
        self.assertTrue(matches_selector({"app": "x", "env": "dev"}, {
            "matchExpressions": [
                {"key": "app", "operator": "In", "values": ["x"]},
                {"key": "foo", "operator": "DoesNotExist"}]}))
        self.assertFalse(matches_selector({"app": "x"}, {
            "matchExpressions": [{"key": "app", "operator": "NotIn", "values": ["x"]}]}))
        with self.assertRaises(CollectionError):
            matches_selector({}, {"matchExpressions": [{"key": "x", "operator": "Invalid"}]})

    def test_stale_pdb_status_fails_closed(self):
        stale = dict(PDB)
        stale["status"] = {"disruptionsAllowed": 1, "observedGeneration": 1}
        def f(cmd, **kwargs):
            if "pods" in cmd:
                return Mock(returncode=0, stdout=json.dumps({"kind": "PodList", "items": [POD]}))
            return Mock(returncode=0, stdout=json.dumps({
                "kind": "PodDisruptionBudgetList", "items": [stale]}))
        with self.assertRaisesRegex(CollectionError, "stale"):
            collect_inventory(NODE, "kind-kubemedic", runner=f)

    def test_missing_selection_is_error(self):
        malformed = dict(PDB)
        malformed["spec"] = {}
        def f(cmd, **kwargs):
            d = {"kind": "PodList", "items": [POD]} if "pods" in cmd else {
                "kind": "PodDisruptionBudgetList", "items": [malformed]}
            return Mock(returncode=0, stdout=json.dumps(d))
        with self.assertRaisesRegex(CollectionError, "selector unavailable"):
            collect_inventory(NODE, "kind-kubemedic", runner=f)

if __name__ == "__main__":
    unittest.main()
