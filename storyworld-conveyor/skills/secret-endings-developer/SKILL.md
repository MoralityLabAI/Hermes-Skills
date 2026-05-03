     1|---
     2|name: secret-endings-developer
     3|description: Focus on enhancing secret ending development in the storyworld factory.
     4|---
     5|
     6|# Secret Endings Developer Skill
     7|
     8|Use this skill when Hermes needs to focus specifically on developing and refining secret endings in the storyworld factory.
     9|
    10|## Workflow
    11|
    12|1. Start from the secret-focused factory configuration.
    13|2. Run the enhanced Monte Carlo and multiple-paths analysis.
    14|3. Ensure at least 3 secret options per story arc with explicit ending routes.
    15|4. Verify that secret ending routes have proper prerequisites and complex effects.
    16|5. Use the enhanced quality gate checks for secret ending metrics.
    17|
    18|## Key Configurations to Use
    19|
    20|- `/mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/sample_data/factory_macbeth_secret_endings.json`
    21|- Enhanced secret requirement in brief: `min_secret_options_per_arc: 3`
    22|- Enhanced quality gate: `min-secret-options: 3`, `min-secret-endings: 2`
    23|
    24|## Command Examples
    25|
    26|```bash
    27|python3 /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/run_storyworld_factory.py --config /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/sample_data/factory_macbeth_secret_endings.json --run-id macbeth_secret_dev --force
    28|```
    29|
    30|## Focus Areas
    31|
    32|- **Spool Structure:** Ensure spool sequencing supports secret branching
    33|- **Character Thread Continuity:** Maintain character tension through secret routes
    34|- **Secret Options:** 3+ per arc with explicit ending routes
    35|- **Desirability Formulas:** Use exponential threat curves, loyalty erosion functions
    36|- **After-Effects:** Include location-bound, prophetic resonance, haunting attachments
    37|- **Metric Warping:** Emphasize fear, loyalty, honor dimensions
    38|- **Monte Carlo Quality:** Focus on secret route viability
    39|- **Path Diversity:** Ensure ending diversity through multiple-paths analysis
    40|
    41|## Validation Checklist
    42|
    43|Before marking a secret ending development loop complete, verify:
    44|
    45|- [ ] Factory run completes without errors in secret-related stages
    46|- [ ] Quality report shows at least 3 secret options per arc
    47|- [ ] Quality report shows at least 2 viable secret endings
    48|- [ ] Multiple-paths analysis shows diverse secret route completion
    49|- [ ] Monte Carlo rehearsal indicates secret ending viability >85%
    50|- [ ] Secret options have complex prerequisites and effects
    51|- [ ] Artistry pass has enriched desirability formulas beyond simple nudges
    52|
    53|## Failure Mode Handling
    54|
    55|- If secret ending gates fail, run focused multiple-path analysis on failing branches
    56|- If Monte Carlo viability is <70%, increase bias and run targeted rebalancing
    57|- If artistry pass fails to generate complex secret options, review spool structure
    58|- If quality gate shows <3 secret options, revisit the secret_ends_gates.py audit
    59|
    60|## Artifact Focus
    61|
    62|After runs, analyze these key outputs:
    63|
    64|- `{report_dir}/multiple_paths_secrets.txt` - Secret route completion diversity
    65|- `{report_dir}/monte_carlo_secrets.txt` - Secret ending viability percentages
    66|- `{quality_report}` - Secret options and endings counts
    67|- `{artistry_world}` - Inspect desirability formulas and effect complexity
    68|