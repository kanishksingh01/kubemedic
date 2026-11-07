# KubeMedic reproducible classifier evaluation

Run `python -m kubemedic.evaluate --output synthetic-evaluation.json` against the five hand-labeled JSON fixtures. The report contains per-fixture expected and predicted fault categories and aggregated true-positive, false-positive and false-negative counts. GitHub CI fails if any labeled category is missed or any unexpected classifier category appears in the controlled fixture suite.

**Strong limitation:** These are small, intentionally constructed synthetic cases that overlap the classifier's known signatures. A high fixture precision/recall is **not** evidence of diagnostic accuracy on real-world Node failure events. Production evaluation needs independently labeled fault injections, broader negative samples, counterfactual noise, confidence calibration, and live operator comparison.

The report is uploaded as a GitHub Actions artifact so reviewers can inspect exact input/output cases.
