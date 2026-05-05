from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("run_repair_generalization_study.py")
SPEC = importlib.util.spec_from_file_location("run_repair_generalization_study", SCRIPT)
assert SPEC and SPEC.loader
study = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(study)


class RunRepairGeneralizationStudyTests(unittest.TestCase):
    def test_heldout_tasks_do_not_use_curriculum_envs(self) -> None:
        envs = {task["target_env"] for task in study.HELDOUT_TASKS}
        curriculum_envs = {
            "storyworld_nav",
            "tool_contract_router",
            "intellect3_logic",
            "primehub_schema_router",
            "trm_mcp_lookup",
            "metta_eval_optimizer",
        }
        self.assertFalse(envs & curriculum_envs)

    def test_summary_comparison_shape(self) -> None:
        summary = study.summarize_controller(
            {"exact_action_rate": 1.0, "mean_key_accuracy": 1.0},
            {"averages": {"raw_overall": 0.8, "repaired_overall": 0.9, "ready_for_runtime_rate": 0.5}},
        )
        self.assertEqual(summary["controller_exact_action_rate"], 1.0)
        self.assertEqual(summary["raw_bootstrap_overall"], 0.8)


if __name__ == "__main__":
    unittest.main()

