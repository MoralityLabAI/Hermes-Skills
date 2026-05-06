from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


BUILDER_SCRIPT = Path(__file__).with_name("build_commit_veto_feature_rows.py")
TRAINER_SCRIPT = Path(__file__).with_name("train_commit_veto_lora_trm.py")

BUILDER_SPEC = importlib.util.spec_from_file_location("build_commit_veto_feature_rows", BUILDER_SCRIPT)
assert BUILDER_SPEC and BUILDER_SPEC.loader
builder = importlib.util.module_from_spec(BUILDER_SPEC)
sys.modules["build_commit_veto_feature_rows"] = builder
BUILDER_SPEC.loader.exec_module(builder)

TRAINER_SPEC = importlib.util.spec_from_file_location("train_commit_veto_lora_trm", TRAINER_SCRIPT)
assert TRAINER_SPEC and TRAINER_SPEC.loader
trainer = importlib.util.module_from_spec(TRAINER_SPEC)
sys.modules["train_commit_veto_lora_trm"] = trainer
TRAINER_SPEC.loader.exec_module(trainer)


class CommitVetoFeatureSteeringTests(unittest.TestCase):
    def test_decision_policy_vetoes_verifier_disagreement(self) -> None:
        state = {
            "repaired_ready_for_runtime": True,
            "repaired_scores": {"overall": 0.97, "files": 1.0, "manifest": 1.0},
            "verifier_disagreement": True,
        }
        decision, reason = builder.decision_for(state)
        self.assertEqual(decision, "veto_or_collect_more_data")
        self.assertEqual(reason, "verifier_disagreement")

    def test_synthetic_builder_writes_splits_and_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "rows"
            subprocess.run(
                [
                    sys.executable,
                    str(BUILDER_SCRIPT),
                    "--out-dir",
                    str(out_dir),
                    "--synthetic-count",
                    "80",
                    "--seed",
                    "7",
                ],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            manifest = json.loads((out_dir / "commit_veto_feature_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["row_count"], 80)
            self.assertGreater(manifest["split_counts"]["train"], 0)
            rows = [json.loads(line) for line in (out_dir / "commit_veto_feature_rows.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertTrue(all(row["feature_contract"].startswith("(feature-target") for row in rows))
            self.assertIn("commit_repaired_package", manifest["decision_counts"])
            self.assertIn("veto_or_collect_more_data", manifest["decision_counts"])

    def test_feature_vector_is_stable_width(self) -> None:
        row = builder.make_feature_row(builder.synthetic_state(__import__("random").Random(1), 0), "unit", 0, "synthetic")
        features = trainer.state_features(row["state"])
        self.assertEqual(len(features), len(trainer.FEATURE_NAMES))
        self.assertTrue(all(isinstance(value, float) for value in features))

    def test_tiny_lora_trainer_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows_dir = root / "rows"
            subprocess.run(
                [sys.executable, str(BUILDER_SCRIPT), "--out-dir", str(rows_dir), "--synthetic-count", "96", "--seed", "11"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            out_dir = root / "train"
            subprocess.run(
                [
                    sys.executable,
                    str(TRAINER_SCRIPT),
                    "--train",
                    str(rows_dir / "commit_veto_train.jsonl"),
                    "--val",
                    str(rows_dir / "commit_veto_val.jsonl"),
                    "--heldout",
                    str(rows_dir / "commit_veto_heldout.jsonl"),
                    "--out-dir",
                    str(out_dir),
                    "--hidden-dim",
                    "16",
                    "--recursive-steps",
                    "1",
                    "--base-epochs",
                    "1",
                    "--lora-epochs",
                    "1",
                    "--batch-size",
                    "16",
                    "--ranks",
                    "1",
                    "--max-train-rows",
                    "48",
                    "--max-val-rows",
                    "16",
                    "--max-heldout-rows",
                    "16",
                    "--checkpoint-interval",
                    "999",
                    "--timeout-seconds",
                    "60",
                ],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["feature"], "commit_veto_threshold")
            self.assertTrue((out_dir / "metrics.csv").exists())
            self.assertTrue((out_dir / "lora_rank_1" / "vpd_style_audit.json").exists())


if __name__ == "__main__":
    unittest.main()
