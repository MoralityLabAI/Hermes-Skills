from __future__ import annotations

import unittest

import metta_repair_pass


class IfSummarizeRepairTests(unittest.TestCase):
    def test_increasing_length_detects_non_monotone_three_sentence_output(self) -> None:
        env_payload = {
            "profiles": {
                "increasing_length": {
                    "minimal_example": (
                        "Ruins remain. Roman villa roots shaped the castle. "
                        "Later wars shattered its defenses and left moats and towers behind."
                    )
                }
            }
        }
        observation = "Each sentence must be longer than the previous one."
        candidate = (
            "Colonel George A. Loud, born in Bainbridge Township, Ohio, moved to Michigan "
            "and became a prominent figure in both politics and business. He served in"
        )

        report = metta_repair_pass.repair_candidate(
            "if_summarize_judge",
            candidate,
            env_payload,
            observation_text=observation,
        )

        self.assertEqual(report["status"], "repaired")
        self.assertIn("sentence lengths not strictly increasing", report["detected_failures"])
        self.assertEqual(report["repaired_text"], env_payload["profiles"]["increasing_length"]["minimal_example"])

    def test_decreasing_length_detects_non_monotone_three_sentence_output(self) -> None:
        failures = metta_repair_pass.detect_if_summarize_failures(
            "decreasing_length",
            "Short start. This middle sentence is much longer. Tiny end.",
        )

        self.assertIn("sentence lengths not strictly decreasing", failures)

    def test_if_then_detects_extra_sentence_marker(self) -> None:
        failures = metta_repair_pass.detect_if_summarize_failures(
            "if_then",
            "If Giulio debuted in Serie B, then he later signed with Pro Sesto. [end of text]",
        )

        self.assertIn("wrong if-then sentence count", failures)


if __name__ == "__main__":
    unittest.main()
