from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("run_domain_router_bootstrap_study.py")
SPEC = importlib.util.spec_from_file_location("run_domain_router_bootstrap_study", SCRIPT)
assert SPEC and SPEC.loader
study = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(study)


class DomainRouterBootstrapStudyTests(unittest.TestCase):
    def test_domain_ids_are_unique_and_broad(self) -> None:
        self.assertEqual(len(study.DOMAIN_SPECS), 10)
        self.assertIn("formal_reasoning", study.DOMAIN_SPECS)
        self.assertIn("metacognition_learning", study.DOMAIN_SPECS)

    def test_heuristic_routes_default_cases(self) -> None:
        rows = []
        for case in study.PROMPT_CASES:
            route = study.heuristic_route(case["prompt"])
            rows.append({"expected_domain": case["expected_domain"], "route": route})
        summary = study.summarize_routes(rows)
        self.assertGreaterEqual(summary["router_accuracy"], 0.9)

    def test_build_task_uses_generic_adapter(self) -> None:
        case = study.PROMPT_CASES[0]
        route = study.heuristic_route(case["prompt"])
        task = study.build_task(case, route, 1)
        self.assertEqual(task["base_skill"], "metta-general-domain-adapter")
        self.assertTrue(task["target_env"].startswith("domain_"))
        self.assertIn("not a final task skill", task["task"])

    def test_cli_writes_offline_routes_and_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--out-dir", tmp, "--limit", "3"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            root = Path(proc.stdout.splitlines()[0].strip())
            self.assertTrue((root / "routing_summary.json").exists())
            self.assertTrue((root / "routed_tasks.json").exists())
            summary = json.loads((root / "routing_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["case_count"], 3)


if __name__ == "__main__":
    unittest.main()
