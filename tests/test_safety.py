import unittest
from kubemedic.safety import evaluate_disruption

DIAG = {"node": "node-1", "status": "identified_signals"}
PODS = [{"namespace": "test", "name": "web-123", "owner_kind": "ReplicaSet",
         "matching_pdbs": ["web-pdb"]}]
PDBS = [{"namespace": "test", "name": "web-pdb", "disruptions_allowed": 1}]

class SafetyTests(unittest.TestCase):
    def test_missing_inventory_refuses(self):
        p = evaluate_disruption(DIAG, None, None)
        self.assertEqual(p["decision"], "HOLD")
        self.assertFalse(p["action_executed"])

    def test_pdb_blocks(self):
        p = evaluate_disruption(DIAG, PODS,
                                [{"namespace": "test", "name": "web-pdb", "disruptions_allowed": 0}],
                                spare_capacity_verified=True, maintenance_approved=True)
        self.assertEqual(p["decision"], "HOLD")
        self.assertTrue(any("budget" in x for x in p["reasons"]))

    def test_multiple_pods_consume_shared_budget(self):
        pods = PODS + [{**PODS[0], "name": "web-456"}]
        p = evaluate_disruption(DIAG, pods, PDBS, spare_capacity_verified=True,
                                maintenance_approved=True)
        self.assertEqual(p["decision"], "HOLD")

    def test_healthy_nominal_case_is_not_permission_to_execute(self):
        p = evaluate_disruption(DIAG, PODS, PDBS,
                                spare_capacity_verified=True, maintenance_approved=True)
        self.assertEqual(p["decision"], "REVIEW_CANDIDATE")
        self.assertTrue(p["approval_required"])
        self.assertFalse(p["action_executed"])

    def test_ambiguous_diagnosis_is_hold(self):
        p = evaluate_disruption({**DIAG, "status": "ambiguous"}, PODS, PDBS,
                                spare_capacity_verified=True, maintenance_approved=True)
        self.assertEqual(p["decision"], "HOLD")

    def test_unmanaged_or_uncovered_pod_is_hold(self):
        for pod in [{**PODS[0], "owner_kind": "DaemonSet"},
                    {**PODS[0], "matching_pdbs": []},
                    {**PODS[0], "matching_pdbs": None}]:
            with self.subTest(pod=pod):
                p = evaluate_disruption(DIAG, [pod], PDBS, spare_capacity_verified=True,
                                        maintenance_approved=True)
                self.assertEqual(p["decision"], "HOLD")

    def test_critical_and_local_data_pods_are_held(self):
        for changes in (
            {"priority_class": "system-node-critical"},
            {"priority_class": "system-cluster-critical"},
            {"has_local_storage": True},
            {"has_local_storage": "unknown"},
        ):
            with self.subTest(changes=changes):
                pod = {**PODS[0], **changes}
                plan = evaluate_disruption(DIAG, [pod], PDBS,
                                           spare_capacity_verified=True,
                                           maintenance_approved=True)
                self.assertEqual(plan["decision"], "HOLD")
                self.assertFalse(plan["action_executed"])

    def test_invalid_pdb_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_disruption(DIAG, PODS, [{"namespace": "test", "name": "x", "disruptions_allowed": -1}])

if __name__ == "__main__":
    unittest.main()
