from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("train_repair_controller.py")
SPEC = importlib.util.spec_from_file_location("train_repair_controller", SCRIPT)
assert SPEC and SPEC.loader
trainer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(trainer)


def make_message(raw_atom: str, repaired_atom: str, repair_type: str = "env_arg_inserted") -> dict:
    action = {"accept_repair": True, "repair": repair_type, "repaired_atom": repaired_atom}
    payload = {
        "role": "metta_syntax_repair",
        "state": {
            "raw_atom": raw_atom,
            "repair_type": repair_type,
            "target_envs": ["storyworld_nav"],
        },
        "tools": ["repair-packet", "verify-packet"],
        "output_contract": {"required_keys": sorted(action)},
    }
    return {
        "messages": [
            {"role": "system", "content": "test"},
            {"role": "user", "content": json.dumps(payload)},
            {"role": "assistant", "content": json.dumps(action)},
        ],
        "meta": {"role": "metta_syntax_repair"},
    }


class TrainRepairControllerTests(unittest.TestCase):
    def test_predict_env_inserted(self) -> None:
        row = make_message(
            '(summary "short value")',
            '(summary "storyworld_nav" "short value")',
        )
        controller = trainer.train_controller([row])
        self.assertEqual(trainer.predict_action(row, controller), trainer.expected_action(row))

    def test_verifier_allows_nonblocking_retrieval_gap(self) -> None:
        state = {
            "raw_scores": {"overall": 0.8, "files": 1.0, "manifest": 1.0, "retrieval": 0.0},
            "repaired_scores": {"overall": 0.9, "files": 1.0, "manifest": 1.0, "retrieval": 0.0},
        }
        action = trainer.predict_verifier_action(state)
        self.assertEqual(action["verdict"], "runtime_ready")
        self.assertEqual(action["failing_components_after_repair"], ["retrieval"])

    def test_cli_evaluates_exact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            row = make_message('(summary "short value")', '(summary "storyworld_nav" "short value")')
            train = root / "train.jsonl"
            val = root / "val.jsonl"
            train.write_text(json.dumps(row) + "\n", encoding="utf-8")
            val.write_text(json.dumps(row) + "\n", encoding="utf-8")
            out = root / "out"
            subprocess.run(
                [sys.executable, str(SCRIPT), "--train-messages", str(train), "--val-messages", str(val), "--out-dir", str(out)],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["exact_action_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
