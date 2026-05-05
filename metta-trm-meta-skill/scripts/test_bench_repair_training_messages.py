from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("bench_repair_training_messages.py")
SPEC = importlib.util.spec_from_file_location("bench_repair_training_messages", SCRIPT)
assert SPEC and SPEC.loader
bench = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bench)


class BenchRepairTrainingMessagesTests(unittest.TestCase):
    def test_extract_json_object_from_fenced_block(self) -> None:
        payload, error = bench.extract_json_object('```json\n{"decision":"commit"}\n```')
        self.assertEqual(error, "")
        self.assertEqual(payload, {"decision": "commit"})

    def test_score_prediction_primary_keys(self) -> None:
        expected = {"decision": "commit_repaired_package", "reason": "repaired_runtime_ready"}
        predicted = {"decision": "commit_repaired_package", "reason": "other"}
        score = bench.score_prediction(expected, predicted, "commit_veto")
        self.assertFalse(score["exact_action"])
        self.assertEqual(score["primary_accuracy"], 0.5)


if __name__ == "__main__":
    unittest.main()

