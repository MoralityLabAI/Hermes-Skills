from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_repair_curriculum.py")
SPEC = importlib.util.spec_from_file_location("build_repair_curriculum", SCRIPT)
assert SPEC and SPEC.loader
curriculum = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(curriculum)


class BuildRepairCurriculumTests(unittest.TestCase):
    def test_build_rows_contains_repair_and_control_roles(self) -> None:
        rows = curriculum.build_rows(examples_per_env=4, seed=1)
        roles = {row["role"] for row in rows}
        self.assertIn("metta_syntax_repair", roles)
        self.assertIn("semantic_contract_verifier", roles)
        self.assertIn("commit_veto", roles)

    def test_cli_writes_splits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            subprocess.run(
                [sys.executable, str(SCRIPT), "--out-dir", str(out_dir), "--examples-per-env", "3", "--seed", "7"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            manifest = json.loads((out_dir / "repair_curriculum_manifest.json").read_text(encoding="utf-8"))
            self.assertGreater(manifest["row_count"], 0)
            self.assertTrue((out_dir / "repair_curriculum_train_messages.jsonl").exists())
            self.assertTrue((out_dir / "repair_curriculum_val_messages.jsonl").exists())


if __name__ == "__main__":
    unittest.main()

