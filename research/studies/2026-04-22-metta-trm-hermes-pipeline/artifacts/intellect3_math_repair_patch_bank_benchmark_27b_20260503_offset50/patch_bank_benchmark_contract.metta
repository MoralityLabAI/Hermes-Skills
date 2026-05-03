;; Live Intellect-3-Math patch-bank benchmark.
(= env_id intellect3_math_patch_bank_benchmark)
(= incumbent_patch incumbent_current_skill)
(= (patch_gate raw_baseline_no_skill) comparison_only)
(= (patch_gate codex_near_miss_repair_v3) reject_patch)
(= (patch_exact raw_baseline_no_skill) 0/10)
(= (patch_exact incumbent_current_skill) 2/10)
(= (patch_exact codex_near_miss_repair_v3) 0/10)
