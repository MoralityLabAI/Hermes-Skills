# Intellect-3 Math Answer-Manifold Micro-Env

Source: `C:\projects\trm_observability_harness\data\qwen27b_intellect3_math_hybrid_200\predictions.jsonl`
Generated: `2026-04-26T01:05:47.962150+00:00`

MeTTa contract: [`intellect3_math_answer_manifold_contract.metta`](<intellect3_math_answer_manifold_contract.metta>)

The current math TRM route is weak as a solver, but this env exposes whether future MeTTa gates should target answer parsing, small arithmetic slips, scaling errors, or route selection.

## Arm Summary

| Arm | Rows | Exact | Avg Rel Distance | Median Rel Distance | Route Sources | Top Failure Tags |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `generic_skill` | 200 | 0.0700 | 1895.2633 | 0.9600 | - | wrong_integer:71, order_of_magnitude:54, same_last_digit:33, off_by_one:17, off_by_small:14, double:12 |
| `math_skill` | 200 | 0.0600 | 1902.8515 | 0.9780 | - | wrong_integer:77, order_of_magnitude:54, same_last_digit:35, off_by_small:17, off_by_one:11, double:10 |
| `math_skill_trm` | 200 | 0.0700 | 1903.1724 | 0.9890 | math_skill:191, math_skill_trm:9 | wrong_integer:78, order_of_magnitude:54, same_last_digit:35, off_by_small:14, off_by_one:11, double:9 |
| `vanilla` | 200 | 0.0850 | 1667.4337 | 0.8750 | - | wrong_integer:77, order_of_magnitude:47, same_last_digit:33, off_by_small:16, off_by_one:14, double:10 |

## Vanilla Vs Math-TRM

| Status | Count |
| --- | ---: |
| `fixed_by_compare` | 4 |
| `partial_improvement` | 24 |
| `partial_regression` | 50 |
| `regressed_by_compare` | 7 |
| `same` | 10 |
| `unfixed` | 105 |

## Problem Rows

| Row | Status | Expected | Vanilla | Math-TRM | Vanilla Rel Dist | TRM Rel Dist | TRM Tags | Route |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `intellect_3_math_0` | `partial_improvement` | 34 | 12 | 14 | 0.6471 | 0.5882 | same_last_digit | `math_skill` |
| `intellect_3_math_1` | `fixed_by_compare` | 1007 | 2014 | 1007 | 1.0000 | 0.0000 | exact | `math_skill` |
| `intellect_3_math_10` | `unfixed` | 4 | 2 | 2 | 0.5000 | 0.5000 | half, off_by_small | `math_skill` |
| `intellect_3_math_100` | `unfixed` | 18 | 11 | 11 | 0.3889 | 0.3889 | wrong_integer | `math_skill` |
| `intellect_3_math_101` | `unfixed` | 6 | 2 | 2 | 0.6667 | 0.6667 | off_by_small | `math_skill` |
| `intellect_3_math_102` | `unfixed` | 16 | 160 | 160 | 9.0000 | 9.0000 | wrong_integer | `math_skill` |
| `intellect_3_math_103` | `regressed_by_compare` | 16 | 16 | 120 | 0.0000 | 6.5000 | wrong_integer | `math_skill` |
| `intellect_3_math_104` | `partial_improvement` | 67 | 11 | 115 | 0.8358 | 0.7164 | wrong_integer | `math_skill` |
| `intellect_3_math_105` | `unfixed` | 126 | 18 | 18 | 0.8571 | 0.8571 | wrong_integer | `math_skill` |
| `intellect_3_math_106` | `unfixed` | 24 | 11 | 11 | 0.5417 | 0.5417 | wrong_integer | `math_skill` |
| `intellect_3_math_107` | `partial_regression` | 20 | 21 | 16 | 0.0500 | 0.2000 | off_by_small | `math_skill` |
| `intellect_3_math_108` | `unfixed` | 1234 | 1 | 1 | 0.9992 | 0.9992 | order_of_magnitude | `math_skill` |
| `intellect_3_math_109` | `unfixed` | 8 | 1999 | 1999 | 248.8750 | 248.8750 | order_of_magnitude | `math_skill` |
| `intellect_3_math_11` | `partial_improvement` | 64 | 120 | 11 | 0.8750 | 0.8281 | wrong_integer | `math_skill` |
| `intellect_3_math_110` | `partial_regression` | 89 | 148 | 28 | 0.6629 | 0.6854 | wrong_integer | `math_skill` |
| `intellect_3_math_111` | `partial_improvement` | 5300 | 1009 | 2025 | 0.8096 | 0.6179 | wrong_integer | `math_skill` |
| `intellect_3_math_112` | `unfixed` | 8 | 10 | 10 | 0.2500 | 0.2500 | off_by_small | `math_skill` |
| `intellect_3_math_113` | `unfixed` | 1 | 2 | 2 | 1.0000 | 1.0000 | double, off_by_one | `math_skill` |
| `intellect_3_math_114` | `unfixed` | 232 | 1200 | 1200 | 4.1724 | 4.1724 | wrong_integer | `math_skill` |
| `intellect_3_math_115` | `unfixed` | 28 | 14 | 14 | 0.5000 | 0.5000 | half | `math_skill` |
| `intellect_3_math_116` | `unfixed` | 0 | 1 | -1 | 1.0000 | 1.0000 | off_by_one | `math_skill` |
| `intellect_3_math_117` | `unfixed` | 1100 | 2013 | 2013 | 0.8300 | 0.8300 | wrong_integer | `math_skill` |
| `intellect_3_math_118` | `unfixed` | 1225 | 120000 | 120000 | 96.9592 | 96.9592 | order_of_magnitude | `math_skill` |
| `intellect_3_math_119` | `unfixed` | 4 | 3 | 3 | 0.2500 | 0.2500 | off_by_one | `math_skill` |
| `intellect_3_math_12` | `unfixed` | 12 | 172 | 172 | 13.3333 | 13.3333 | order_of_magnitude, same_last_digit | `math_skill` |
| `intellect_3_math_120` | `partial_improvement` | 288 | 194400 | 108000 | 674.0000 | 374.0000 | order_of_magnitude | `math_skill` |
| `intellect_3_math_121` | `partial_regression` | 8 | 12 | 2 | 0.5000 | 0.7500 | wrong_integer | `math_skill` |
| `intellect_3_math_122` | `unfixed` | 1360 | 100000 | 100000 | 72.5294 | 72.5294 | order_of_magnitude, same_last_digit | `math_skill` |
| `intellect_3_math_123` | `partial_regression` | 503 | 1008 | 2010 | 1.0040 | 2.9960 | wrong_integer | `math_skill` |
| `intellect_3_math_124` | `unfixed` | 114 | 18 | 18 | 0.8421 | 0.8421 | wrong_integer | `math_skill` |
| `intellect_3_math_125` | `unfixed` | 90 | 10 | 10 | 0.8889 | 0.8889 | same_last_digit | `math_skill` |
| `intellect_3_math_126` | `same` | 2 | 2 | 2 | 0.0000 | 0.0000 | exact | `math_skill` |
| `intellect_3_math_127` | `partial_regression` | 67 | 100 | 1999 | 0.4925 | 28.8358 | order_of_magnitude | `math_skill` |
| `intellect_3_math_128` | `unfixed` | 4 | 3 | 3 | 0.2500 | 0.2500 | off_by_one | `math_skill` |
| `intellect_3_math_129` | `regressed_by_compare` | 2018 | 2018 | 2028 | 0.0000 | 0.0050 | same_last_digit | `math_skill` |
| `intellect_3_math_13` | `unfixed` | 1 | 1009 | 1009 | 1008.0000 | 1008.0000 | order_of_magnitude | `math_skill` |
| `intellect_3_math_130` | `unfixed` | 5 | 20 | 20 | 3.0000 | 3.0000 | wrong_integer | `math_skill` |
| `intellect_3_math_131` | `partial_regression` | 60 | 100 | 160 | 0.6667 | 1.6667 | same_last_digit | `math_skill` |
| `intellect_3_math_132` | `unfixed` | 7993 | 2022 | 2022 | 0.7470 | 0.7470 | wrong_integer | `math_skill` |
| `intellect_3_math_133` | `partial_regression` | 4 | 100 | 169 | 24.0000 | 41.2500 | order_of_magnitude | `math_skill` |
| `intellect_3_math_134` | `partial_regression` | 27 | 17 | 130 | 0.3704 | 3.8148 | wrong_integer | `math_skill` |
| `intellect_3_math_135` | `unfixed` | 3 | 11 | 11 | 2.6667 | 2.6667 | wrong_integer | `math_skill` |
| `intellect_3_math_136` | `unfixed` | 44 | 2014 | 2014 | 44.7727 | 44.7727 | order_of_magnitude, same_last_digit | `math_skill` |
| `intellect_3_math_137` | `partial_improvement` | 71622400 | 11 | 130 | 1.0000 | 1.0000 | order_of_magnitude, same_last_digit | `math_skill` |
| `intellect_3_math_138` | `unfixed` | 75 | 108 | 108 | 0.4400 | 0.4400 | wrong_integer | `math_skill` |
| `intellect_3_math_139` | `unfixed` | 60 | 120 | 120 | 1.0000 | 1.0000 | double, same_last_digit | `math_skill` |
| `intellect_3_math_14` | `unfixed` | 3 | 10 | 10 | 2.3333 | 2.3333 | wrong_integer | `math_skill` |
| `intellect_3_math_140` | `partial_regression` | 1278 | 180 | 14 | 0.8592 | 0.9890 | order_of_magnitude | `math_skill_trm` |
| `intellect_3_math_141` | `partial_regression` | 457 | 195 | 12096 | 0.5733 | 25.4683 | order_of_magnitude | `math_skill` |
| `intellect_3_math_142` | `partial_regression` | 9 | 3 | 2 | 0.6667 | 0.7778 | wrong_integer | `math_skill` |
| `intellect_3_math_143` | `unfixed` | 23 | 13 | 13 | 0.4348 | 0.4348 | same_last_digit | `math_skill` |
| `intellect_3_math_144` | `unfixed` | 105263157894736848 | 105263 | 105263 | 1.0000 | 1.0000 | order_of_magnitude | `math_skill` |
| `intellect_3_math_145` | `partial_regression` | 167 | 100 | 1592 | 0.4012 | 8.5329 | wrong_integer | `math_skill` |
| `intellect_3_math_146` | `unfixed` | 2 | 1008 | 1008 | 503.0000 | 503.0000 | order_of_magnitude | `math_skill` |
| `intellect_3_math_147` | `unfixed` | 171 | 198 | 198 | 0.1579 | 0.1579 | wrong_integer | `math_skill` |
| `intellect_3_math_148` | `unfixed` | 15 | 10 | 10 | 0.3333 | 0.3333 | off_by_small | `math_skill` |
| `intellect_3_math_149` | `unfixed` | 4 | 3 | 3 | 0.2500 | 0.2500 | off_by_one | `math_skill` |
| `intellect_3_math_15` | `unfixed` | 50 | 10000 | 10000 | 199.0000 | 199.0000 | order_of_magnitude, same_last_digit | `math_skill` |
| `intellect_3_math_150` | `unfixed` | 9 | 17 | 17 | 0.8889 | 0.8889 | wrong_integer | `math_skill` |
| `intellect_3_math_151` | `partial_regression` | 6 | 12 | 18 | 1.0000 | 2.0000 | wrong_integer | `math_skill_trm` |
| `intellect_3_math_152` | `partial_improvement` | 1820 | 100 | 1919 | 0.9451 | 0.0544 | wrong_integer | `math_skill` |
| `intellect_3_math_153` | `partial_improvement` | 45 | 150 | 10 | 2.3333 | 0.7778 | wrong_integer | `math_skill` |
| `intellect_3_math_154` | `unfixed` | 10091 | 1009 | 1009 | 0.9000 | 0.9000 | order_of_magnitude | `math_skill` |
| `intellect_3_math_155` | `fixed_by_compare` | 256 | 299376 | 256 | 1168.4375 | 0.0000 | exact | `math_skill` |
| `intellect_3_math_156` | `partial_regression` | 9 | 19 | 149 | 1.1111 | 15.5556 | order_of_magnitude, same_last_digit | `math_skill` |
| `intellect_3_math_157` | `unfixed` | 5 | 10 | 10 | 1.0000 | 1.0000 | double, off_by_small | `math_skill` |
| `intellect_3_math_158` | `unfixed` | 62 | 118 | 118 | 0.9032 | 0.9032 | wrong_integer | `math_skill` |
| `intellect_3_math_159` | `unfixed` | 960 | 1296 | 1296 | 0.3500 | 0.3500 | wrong_integer | `math_skill` |
| `intellect_3_math_16` | `unfixed` | 45 | 128 | 128 | 1.8444 | 1.8444 | wrong_integer | `math_skill` |
| `intellect_3_math_160` | `unfixed` | 18 | 184467 | 184467 | 10247.1667 | 10247.1667 | order_of_magnitude | `math_skill` |
| `intellect_3_math_161` | `unfixed` | 0 | 196830 | 196830 | 196830.0000 | 196830.0000 | same_last_digit | `math_skill` |
| `intellect_3_math_162` | `unfixed` | 28 | 100 | 100 | 2.5714 | 2.5714 | wrong_integer | `math_skill` |
| `intellect_3_math_163` | `partial_regression` | 3 | 191 | 2023 | 62.6667 | 673.3333 | order_of_magnitude, same_last_digit | `math_skill` |
| `intellect_3_math_164` | `unfixed` | 2400 | 120000 | 120000 | 49.0000 | 49.0000 | order_of_magnitude, same_last_digit | `math_skill` |
| `intellect_3_math_165` | `unfixed` | 31 | 1994 | 1994 | 63.3226 | 63.3226 | order_of_magnitude | `math_skill` |
| `intellect_3_math_166` | `unfixed` | 70 | 120 | 120 | 0.7143 | 0.7143 | same_last_digit | `math_skill` |
| `intellect_3_math_167` | `partial_regression` | 2016 | 120 | 12 | 0.9405 | 0.9940 | order_of_magnitude | `math_skill` |
| `intellect_3_math_168` | `unfixed` | 40 | 120 | 120 | 2.0000 | 2.0000 | same_last_digit | `math_skill` |
| `intellect_3_math_169` | `partial_regression` | 256 | 128 | 19683 | 0.5000 | 75.8867 | order_of_magnitude | `math_skill` |
| `intellect_3_math_17` | `same` | 2 | 2 | 2 | 0.0000 | 0.0000 | exact | `math_skill` |
| `intellect_3_math_170` | `partial_regression` | 32 | 120 | 1364 | 2.7500 | 41.6250 | order_of_magnitude | `math_skill` |
| `intellect_3_math_171` | `unfixed` | 503 | 1009 | 1009 | 1.0060 | 1.0060 | wrong_integer | `math_skill` |
| `intellect_3_math_172` | `same` | 169 | 169 | 169 | 0.0000 | 0.0000 | exact | `math_skill` |
| `intellect_3_math_173` | `partial_improvement` | 2500 | 1156 | 2025 | 0.5376 | 0.1900 | wrong_integer | `math_skill` |
| `intellect_3_math_174` | `partial_regression` | 1996 | 1001 | 251 | 0.4985 | 0.8742 | wrong_integer | `math_skill` |
| `intellect_3_math_175` | `partial_regression` | 60 | 120 | 132 | 1.0000 | 1.2000 | wrong_integer | `math_skill` |
| `intellect_3_math_176` | `unfixed` | 180 | 198 | 198 | 0.1000 | 0.1000 | wrong_integer | `math_skill` |
| `intellect_3_math_177` | `partial_regression` | 10613 | 10007 | 104060 | 0.0571 | 8.8050 | wrong_integer | `math_skill` |
| `intellect_3_math_178` | `partial_regression` | 92 | 120 | 288 | 0.3043 | 2.1304 | wrong_integer | `math_skill` |
| `intellect_3_math_179` | `partial_regression` | 4 | 3 | 2 | 0.2500 | 0.5000 | half, off_by_small | `math_skill` |
| `intellect_3_math_18` | `unfixed` | 1 | 180 | 180 | 179.0000 | 179.0000 | order_of_magnitude | `math_skill_trm` |
| `intellect_3_math_180` | `unfixed` | 2 | 4 | 4 | 1.0000 | 1.0000 | double, off_by_small | `math_skill` |
| `intellect_3_math_181` | `unfixed` | 10 | 20 | 20 | 1.0000 | 1.0000 | double, same_last_digit | `math_skill` |
| `intellect_3_math_182` | `partial_regression` | 50 | 32 | 16 | 0.3600 | 0.6800 | wrong_integer | `math_skill` |
| `intellect_3_math_183` | `partial_regression` | 100 | 74 | 149 | 0.2600 | 0.4900 | wrong_integer | `math_skill` |
| `intellect_3_math_184` | `partial_regression` | 92 | 1985 | 1988 | 20.5761 | 20.6087 | order_of_magnitude | `math_skill` |
| `intellect_3_math_185` | `unfixed` | 2 | 1024 | 1024 | 511.0000 | 511.0000 | order_of_magnitude | `math_skill` |
| `intellect_3_math_186` | `partial_regression` | 3 | 1 | 120000 | 0.6667 | 39999.0000 | order_of_magnitude | `math_skill` |
| `intellect_3_math_187` | `unfixed` | 4 | 143 | 143 | 34.7500 | 34.7500 | order_of_magnitude | `math_skill` |
| `intellect_3_math_188` | `unfixed` | 504 | 2014 | 2014 | 2.9960 | 2.9960 | same_last_digit | `math_skill` |
| `intellect_3_math_189` | `same` | 12 | 12 | 12 | 0.0000 | 0.0000 | exact | `math_skill` |
| `intellect_3_math_19` | `partial_improvement` | 8 | 3 | 10 | 0.6250 | 0.2500 | off_by_small | `math_skill` |
| `intellect_3_math_190` | `partial_regression` | 600 | 1000 | 250000 | 0.6667 | 415.6667 | order_of_magnitude, same_last_digit | `math_skill` |
| `intellect_3_math_191` | `partial_regression` | 62 | 120 | 128 | 0.9355 | 1.0645 | wrong_integer | `math_skill` |
| `intellect_3_math_192` | `unfixed` | 12 | 13 | 13 | 0.0833 | 0.0833 | off_by_one | `math_skill` |
| `intellect_3_math_193` | `unfixed` | 9 | 10 | 10 | 0.1111 | 0.1111 | off_by_one | `math_skill` |
| `intellect_3_math_194` | `unfixed` | 652400 | 193740 | 193740 | 0.7030 | 0.7030 | same_last_digit | `math_skill` |
| `intellect_3_math_195` | `partial_regression` | 1006 | 1007 | 2014 | 0.0010 | 1.0020 | wrong_integer | `math_skill` |
| `intellect_3_math_196` | `unfixed` | 85 | 12 | 12 | 0.8588 | 0.8588 | wrong_integer | `math_skill` |
| `intellect_3_math_197` | `partial_regression` | 39 | 27 | 12 | 0.3077 | 0.6923 | wrong_integer | `math_skill` |
| `intellect_3_math_198` | `partial_regression` | 8 | 10 | 12 | 0.2500 | 0.5000 | off_by_small | `math_skill` |
| `intellect_3_math_199` | `partial_improvement` | 89 | 11 | 101 | 0.8764 | 0.1348 | wrong_integer | `math_skill` |
| `intellect_3_math_2` | `partial_regression` | 5 | 100000 | 120000 | 19999.0000 | 23999.0000 | order_of_magnitude | `math_skill` |
| `intellect_3_math_20` | `fixed_by_compare` | 18 | 180 | 18 | 9.0000 | 0.0000 | exact | `math_skill_trm` |
| `intellect_3_math_21` | `same` | 100 | 100 | 100 | 0.0000 | 0.0000 | exact | `math_skill_trm` |
| `intellect_3_math_22` | `unfixed` | 102 | 132 | 132 | 0.2941 | 0.2941 | same_last_digit | `math_skill` |
| `intellect_3_math_23` | `unfixed` | 1 | 30 | 30 | 29.0000 | 29.0000 | order_of_magnitude | `math_skill` |
| `intellect_3_math_24` | `unfixed` | 6 | 16 | 16 | 1.6667 | 1.6667 | same_last_digit | `math_skill` |
| `intellect_3_math_25` | `unfixed` | 828 | 1008 | 1008 | 0.2174 | 0.2174 | same_last_digit | `math_skill` |
| `intellect_3_math_26` | `unfixed` | 8 | 13 | 13 | 0.6250 | 0.6250 | off_by_small | `math_skill` |
| `intellect_3_math_27` | `partial_improvement` | 8 | 2024 | 1200 | 252.0000 | 149.0000 | order_of_magnitude | `math_skill` |
| `intellect_3_math_28` | `unfixed` | 8 | 16 | 16 | 1.0000 | 1.0000 | double | `math_skill` |
| `intellect_3_math_29` | `unfixed` | 6 | 7 | 5 | 0.1667 | 0.1667 | off_by_one | `math_skill` |
| `intellect_3_math_3` | `partial_regression` | 10 | 12 | 1 | 0.2000 | 0.9000 | order_of_magnitude | `math_skill_trm` |
| `intellect_3_math_30` | `unfixed` | 2500 | 10000 | 10000 | 3.0000 | 3.0000 | same_last_digit | `math_skill` |
| `intellect_3_math_31` | `partial_improvement` | 50 | 2500 | 49 | 49.0000 | 0.0200 | off_by_one | `math_skill` |
| `intellect_3_math_32` | `regressed_by_compare` | 2000 | 2000 | 1500 | 0.0000 | 0.2500 | same_last_digit | `math_skill` |
| `intellect_3_math_33` | `partial_regression` | 50 | 49 | 19 | 0.0200 | 0.6200 | wrong_integer | `math_skill` |
| `intellect_3_math_34` | `same` | 23 | 23 | 23 | 0.0000 | 0.0000 | exact | `math_skill` |
| `intellect_3_math_35` | `regressed_by_compare` | 20 | 20 | 10 | 0.0000 | 0.5000 | half, same_last_digit | `math_skill` |
| `intellect_3_math_36` | `unfixed` | 2179 | 2023 | 2023 | 0.0716 | 0.0716 | wrong_integer | `math_skill` |
| `intellect_3_math_37` | `unfixed` | 25 | 17 | 17 | 0.3200 | 0.3200 | wrong_integer | `math_skill` |
| `intellect_3_math_38` | `unfixed` | 0 | 1 | 1 | 1.0000 | 1.0000 | off_by_one | `math_skill` |
| `intellect_3_math_39` | `partial_improvement` | 21 | 129 | 120 | 5.1429 | 4.7143 | wrong_integer | `math_skill` |
| `intellect_3_math_4` | `unfixed` | 7 | 1009 | 1009 | 143.1429 | 143.1429 | order_of_magnitude | `math_skill` |
| `intellect_3_math_40` | `partial_improvement` | 32 | 1997 | 1996 | 61.4062 | 61.3750 | order_of_magnitude | `math_skill` |
| `intellect_3_math_41` | `unfixed` | 100902018 | 201802 | 201802 | 0.9980 | 0.9980 | order_of_magnitude | `math_skill` |
| `intellect_3_math_42` | `unfixed` | 3780 | 10800 | 10800 | 1.8571 | 1.8571 | same_last_digit | `math_skill` |
| `intellect_3_math_43` | `partial_regression` | 50 | 1250 | 100000 | 24.0000 | 1999.0000 | order_of_magnitude, same_last_digit | `math_skill` |
| `intellect_3_math_44` | `partial_regression` | 4016 | 3015 | 2011 | 0.2493 | 0.4993 | wrong_integer | `math_skill` |
| `intellect_3_math_45` | `partial_regression` | 243 | 288 | 48 | 0.1852 | 0.8025 | wrong_integer | `math_skill` |
| `intellect_3_math_46` | `unfixed` | 35 | 120 | 120 | 2.4286 | 2.4286 | wrong_integer | `math_skill` |
| `intellect_3_math_47` | `partial_improvement` | 1374 | 176400 | 1050 | 127.3843 | 0.2358 | wrong_integer | `math_skill` |
| `intellect_3_math_48` | `partial_regression` | 1 | 100100 | -100100 | 100099.0000 | 100101.0000 | order_of_magnitude | `math_skill` |
| `intellect_3_math_49` | `unfixed` | 261 | 17 | 17 | 0.9349 | 0.9349 | order_of_magnitude | `math_skill` |
| `intellect_3_math_5` | `same` | 1 | 1 | 1 | 0.0000 | 0.0000 | exact | `math_skill` |
| `intellect_3_math_50` | `partial_improvement` | 2025 | 8092 | 8088 | 2.9960 | 2.9941 | wrong_integer | `math_skill_trm` |
| `intellect_3_math_51` | `partial_improvement` | 7 | 1310 | 13 | 186.1429 | 0.8571 | wrong_integer | `math_skill` |
| `intellect_3_math_52` | `unfixed` | 1018 | 2007 | 2007 | 0.9715 | 0.9715 | wrong_integer | `math_skill` |
| `intellect_3_math_53` | `unfixed` | 15 | 24 | 24 | 0.6000 | 0.6000 | wrong_integer | `math_skill` |
| `intellect_3_math_54` | `unfixed` | 6 | 12 | 12 | 1.0000 | 1.0000 | double | `math_skill` |
| `intellect_3_math_55` | `regressed_by_compare` | 13 | 13 | 25 | 0.0000 | 0.9231 | wrong_integer | `math_skill` |
| `intellect_3_math_56` | `unfixed` | 6 | 24 | 24 | 3.0000 | 3.0000 | wrong_integer | `math_skill` |
| `intellect_3_math_57` | `same` | 15 | 15 | 15 | 0.0000 | 0.0000 | exact | `math_skill` |
| `intellect_3_math_58` | `partial_regression` | 1 | 10 | 11 | 9.0000 | 10.0000 | order_of_magnitude, same_last_digit | `math_skill` |
| `intellect_3_math_59` | `partial_regression` | 1382 | 1009 | -1 | 0.2699 | 1.0007 | order_of_magnitude | `math_skill` |
| `intellect_3_math_6` | `unfixed` | 8556 | 2020 | 2020 | 0.7639 | 0.7639 | wrong_integer | `math_skill` |
| `intellect_3_math_60` | `same` | 111 | 111 | 111 | 0.0000 | 0.0000 | exact | `math_skill` |
| `intellect_3_math_61` | `unfixed` | 2 | 1 | 1 | 0.5000 | 0.5000 | half, off_by_one | `math_skill` |
| `intellect_3_math_62` | `unfixed` | 154 | 1003 | 1003 | 5.5130 | 5.5130 | wrong_integer | `math_skill` |
| `intellect_3_math_63` | `partial_regression` | 1289 | 1000 | 199 | 0.2242 | 0.8456 | same_last_digit | `math_skill_trm` |
| `intellect_3_math_64` | `unfixed` | 48 | 144 | 144 | 2.0000 | 2.0000 | wrong_integer | `math_skill` |
| `intellect_3_math_65` | `partial_regression` | 625 | 1000 | 100000 | 0.6000 | 159.0000 | order_of_magnitude | `math_skill` |
| `intellect_3_math_66` | `unfixed` | 578 | 4042 | 4042 | 5.9931 | 5.9931 | wrong_integer | `math_skill` |
| `intellect_3_math_67` | `partial_improvement` | 9 | 13 | 12 | 0.4444 | 0.3333 | off_by_small | `math_skill` |
| `intellect_3_math_68` | `unfixed` | 5940 | 5994 | 5994 | 0.0091 | 0.0091 | wrong_integer | `math_skill` |
| `intellect_3_math_69` | `unfixed` | 49 | 13 | 13 | 0.7347 | 0.7347 | wrong_integer | `math_skill` |
| `intellect_3_math_7` | `fixed_by_compare` | 14 | 12 | 14 | 0.1429 | 0.0000 | exact | `math_skill_trm` |
| `intellect_3_math_70` | `partial_improvement` | 2016 | 12768 | 12752 | 5.3333 | 5.3254 | wrong_integer | `math_skill` |
| `intellect_3_math_71` | `unfixed` | 1033 | 1012 | 1012 | 0.0203 | 0.0203 | wrong_integer | `math_skill` |
| `intellect_3_math_72` | `unfixed` | -12 | -18 | -18 | 0.5000 | 0.5000 | wrong_integer | `math_skill` |
| `intellect_3_math_73` | `unfixed` | 25 | 10 | 10 | 0.6000 | 0.6000 | wrong_integer | `math_skill` |
| `intellect_3_math_74` | `partial_regression` | 9089 | 100000 | 179017 | 10.0023 | 18.6960 | order_of_magnitude | `math_skill` |
| `intellect_3_math_75` | `unfixed` | 4033 | 2017 | 2017 | 0.4999 | 0.4999 | wrong_integer | `math_skill` |
| `intellect_3_math_76` | `partial_improvement` | 622 | 1999 | 242 | 2.2138 | 0.6109 | same_last_digit | `math_skill` |
| `intellect_3_math_77` | `regressed_by_compare` | 1005 | 1005 | 2010 | 0.0000 | 1.0000 | double | `math_skill` |
| `intellect_3_math_78` | `partial_regression` | 96 | 112 | 200 | 0.1667 | 1.0833 | wrong_integer | `math_skill` |
| `intellect_3_math_79` | `unfixed` | 7 | 4 | 4 | 0.4286 | 0.4286 | off_by_small | `math_skill` |
| `intellect_3_math_8` | `unfixed` | 1010 | 1347 | 1347 | 0.3337 | 0.3337 | wrong_integer | `math_skill` |
| `intellect_3_math_80` | `same` | 1010 | 1010 | 1010 | 0.0000 | 0.0000 | exact | `math_skill` |
| `intellect_3_math_81` | `partial_regression` | 61 | 1301 | 100000 | 20.3279 | 1638.3443 | order_of_magnitude | `math_skill` |
| `intellect_3_math_82` | `unfixed` | 3 | 1 | 1 | 0.6667 | 0.6667 | off_by_small | `math_skill` |
| `intellect_3_math_83` | `unfixed` | 1008 | 2018 | 2018 | 1.0020 | 1.0020 | same_last_digit | `math_skill` |
| `intellect_3_math_84` | `unfixed` | 1023 | 1 | 1 | 0.9990 | 0.9990 | order_of_magnitude | `math_skill` |
| `intellect_3_math_85` | `partial_improvement` | 102 | 2500 | 1 | 23.5098 | 0.9902 | order_of_magnitude | `math_skill` |
| `intellect_3_math_86` | `unfixed` | 17 | 1 | 1 | 0.9412 | 0.9412 | order_of_magnitude | `math_skill` |
| `intellect_3_math_87` | `regressed_by_compare` | 1024 | 1024 | 2048 | 0.0000 | 1.0000 | double | `math_skill` |
| `intellect_3_math_88` | `unfixed` | 1991 | 1999 | 1999 | 0.0040 | 0.0040 | wrong_integer | `math_skill` |
| `intellect_3_math_89` | `partial_regression` | 8128 | 12500 | 400000 | 0.5379 | 48.2126 | order_of_magnitude | `math_skill` |
| `intellect_3_math_9` | `partial_regression` | 40 | 120 | 192 | 2.0000 | 3.8000 | wrong_integer | `math_skill` |
| `intellect_3_math_90` | `partial_regression` | 5 | 1000 | 1200 | 199.0000 | 239.0000 | order_of_magnitude | `math_skill` |
| `intellect_3_math_91` | `partial_improvement` | 12 | 120 | 108 | 9.0000 | 8.0000 | wrong_integer | `math_skill` |
| `intellect_3_math_92` | `partial_improvement` | 62208 | 130000 | 1369 | 1.0898 | 0.9780 | order_of_magnitude | `math_skill` |
| `intellect_3_math_93` | `unfixed` | 10053 | 202305 | 202305 | 19.1238 | 19.1238 | order_of_magnitude | `math_skill` |
| `intellect_3_math_94` | `unfixed` | 14 | 55 | 55 | 2.9286 | 2.9286 | wrong_integer | `math_skill` |
| `intellect_3_math_95` | `unfixed` | 80 | 20 | 20 | 0.7500 | 0.7500 | same_last_digit | `math_skill` |
| `intellect_3_math_96` | `partial_regression` | 91 | 133 | 175 | 0.4615 | 0.9231 | wrong_integer | `math_skill` |
| `intellect_3_math_97` | `unfixed` | 6423 | 100000 | 100000 | 14.5690 | 14.5690 | order_of_magnitude | `math_skill` |
| `intellect_3_math_98` | `unfixed` | 999 | 1999 | 1999 | 1.0010 | 1.0010 | same_last_digit | `math_skill` |
| `intellect_3_math_99` | `unfixed` | 60 | 132 | 132 | 1.2000 | 1.2000 | wrong_integer | `math_skill` |
