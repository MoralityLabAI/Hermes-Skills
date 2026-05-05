from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("metta_trm_meta_skill.py")


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class MeTTaTRMMetaSkillTests(unittest.TestCase):
    def test_author_verify_export_evolve_and_bench(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package_dir = root / "package"
            verify_report = root / "verify.json"
            rows_path = root / "rows.jsonl"
            evolve_dir = root / "evolve"
            bench_path = root / "bench.json"

            run_cmd(
                "author-packet",
                "--task",
                "Improve storyworld NAV retrieval with compact MeTTa gates and TRM commit/veto rows.",
                "--base-skill",
                "storyworld-player",
                "--target-env",
                "storyworld_nav",
                "--out-dir",
                str(package_dir),
            )
            self.assertTrue((package_dir / "package.manifest.json").exists())
            self.assertTrue((package_dir / "contracts.metta").exists())

            run_cmd("verify-packet", "--package-dir", str(package_dir), "--out", str(verify_report), "--min-score", "0.85")
            report = json.loads(verify_report.read_text(encoding="utf-8"))
            self.assertGreaterEqual(report["scores"]["overall"], 0.85)
            self.assertTrue(report["ready_for_runtime_without_review"])

            run_cmd("export-trm-rows", "--package-dir", str(package_dir), "--out", str(rows_path))
            rows = [json.loads(line) for line in rows_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual({row["role"] for row in rows}, {
                "author_router",
                "metta_syntax_repair",
                "semantic_contract_verifier",
                "retrieval_policy_router",
                "skill_patch_controller",
                "commit_veto",
            })

            run_cmd("evolve-skill", "--package-dir", str(package_dir), "--verify-report", str(verify_report), "--out-dir", str(evolve_dir))
            plan = json.loads((evolve_dir / "skill_evolution_plan.json").read_text(encoding="utf-8"))
            self.assertEqual(plan["patch_category"], "runtime_packet_injection")

            run_cmd("bench-arms", "--package-dir", str(package_dir), "--out", str(bench_path))
            bench = json.loads(bench_path.read_text(encoding="utf-8"))
            self.assertEqual([arm["arm"] for arm in bench["arms"]], ["baseline", "pure_trm", "metta_runtime", "metta_runtime_repair"])

    def test_repair_packet_wraps_bare_atoms(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package_dir = root / "broken"
            repaired_dir = root / "repaired"
            package_dir.mkdir()
            (package_dir / "package.manifest.json").write_text(
                json.dumps(
                    {
                        "package_id": "broken",
                        "title": "Broken",
                        "base_skill": "storyworld-player",
                        "trm_overlay": "metta-trm-meta-skill",
                        "infusion_type": "metta_trm_meta_control_plane",
                        "target_envs": ["storyworld_nav"],
                        "bundle_outputs": [],
                        "notes": {},
                    }
                ),
                encoding="utf-8",
            )
            (package_dir / "package.metta").write_text('package-id "broken"\n(env "storyworld_nav")\n', encoding="utf-8")

            run_cmd("repair-packet", "--package-dir", str(package_dir), "--out-dir", str(repaired_dir))
            repaired = (repaired_dir / "package.metta").read_text(encoding="utf-8")
            self.assertIn('(package-id "broken")', repaired)
            self.assertTrue((repaired_dir / "repair_report.json").exists())


if __name__ == "__main__":
    unittest.main()

