# Intellect-3 Math Optimized TRM Router

Source: `C:\projects\trm_observability_harness\data\qwen27b_intellect3_math_hybrid_200\predictions.jsonl`
Generated: `2026-04-26T01:59:27.144000+00:00`

MeTTa contract: [`intellect3_math_optimized_router_contract.metta`](<intellect3_math_optimized_router_contract.metta>)

Use `math_trm_route_policy: always_trm` for the next live rerun. The recorded TRM-conditioned candidate is exact on more rows than the current keyword-routed final action. The optional `generic_retrieval_guard` policy has a slightly higher offline exact rate but costs a third model call.

## Candidate Scores

| Candidate | Exact | Avg Relative Distance | Delta Vs Current |
| --- | ---: | ---: | ---: |
| `current_final` | 0.0700 | 1903.1724 | +0.0000 |
| `math_skill` | 0.0600 | 1902.8515 | -0.0100 |
| `trm_skill` | 0.1050 | 77.9602 | +0.0350 |
| `retrieved` | 0.0600 | 12.1340 | -0.0100 |
| `generic_skill` | 0.0700 | 1895.2633 | +0.0000 |

## Policy Replay

| Policy | Threshold | Exact Count | Exact Rate | Avg Relative Distance | Route Sources | Delta Vs Current |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| `current_final` | - | 14 | 0.0700 | 1903.1724 | current_final:200 | +0.0000 |
| `math_skill` | - | 12 | 0.0600 | 1902.8515 | math_skill:200 | -0.0100 |
| `trm_skill` | - | 21 | 0.1050 | 77.9602 | trm_skill:200 | +0.0350 |
| `retrieved` | - | 12 | 0.0600 | 12.1340 | retrieved:200 | -0.0100 |
| `generic_retrieval_guard` | - | 22 | 0.1100 | 77.9579 | trm_skill:193, math_skill:7 | +0.0400 |
| `retrieval_threshold` | 0.0000 | 21 | 0.1050 | 77.9602 | trm_skill:200 | +0.0350 |

## Train/Test Check

Threshold selected on alternating train rows: `0.00`.

| Policy | Train Exact | Test Exact |
| --- | ---: | ---: |
| `current_final` | 0.0400 | 0.1000 |
| `math_skill` | 0.0300 | 0.0900 |
| `trm_skill` | 0.0900 | 0.1200 |
| `retrieved` | 0.0600 | 0.0600 |
| `generic_retrieval_guard` | 0.0900 | 0.1300 |
| `retrieval_threshold` | 0.0900 | 0.1200 |

## Rows Changed By Recommended Policy

| Row | Expected | Current | TRM Skill | Retrieved | Generic | TRM Exact | Similarity |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `intellect_3_math_2` | 5 | 120000 | 1007 | 1007 | 100000 | False | 0.1867 |
| `intellect_3_math_6` | 8556 | 2020 | 14 | 14 | 202000 | False | 0.2412 |
| `intellect_3_math_8` | 1010 | 1347 | 14 | 14 | 1347 | False | 0.2309 |
| `intellect_3_math_9` | 40 | 192 | 128 | 1 | 192 | False | 0.2175 |
| `intellect_3_math_10` | 4 | 2 | 14 | 14 | 3 | False | 0.1828 |
| `intellect_3_math_11` | 64 | 11 | 1 | 1 | 11 | False | 0.2429 |
| `intellect_3_math_13` | 1 | 1009 | 1007 | 1007 | 1009 | False | 0.2121 |
| `intellect_3_math_14` | 3 | 10 | 18 | 18 | 3 | False | 0.2122 |
| `intellect_3_math_15` | 50 | 10000 | 0 | 100 | 10000 | False | 0.2184 |
| `intellect_3_math_16` | 45 | 128 | 1 | 1 | 1 | False | 0.2164 |
| `intellect_3_math_19` | 8 | 10 | 100000 | 1 | 100000 | False | 0.1942 |
| `intellect_3_math_22` | 102 | 132 | 100 | 14 | 132 | False | 0.2047 |
| `intellect_3_math_23` | 1 | 30 | 15 | 1 | 10 | False | 0.1870 |
| `intellect_3_math_25` | 828 | 1008 | 1001 | 14 | 1008 | False | 0.1966 |
| `intellect_3_math_27` | 8 | 1200 | 1 | 1 | 1200 | False | 0.2526 |
| `intellect_3_math_30` | 2500 | 10000 | 14 | 14 | 2500 | False | 0.1968 |
| `intellect_3_math_32` | 2000 | 1500 | 1007 | 1007 | 1500 | False | 0.1840 |
| `intellect_3_math_33` | 50 | 19 | 99 | 1007 | 98 | False | 0.2155 |
| `intellect_3_math_36` | 2179 | 2023 | 14 | 14 | 2023 | False | 0.2143 |
| `intellect_3_math_38` | 0 | 1 | 0 | 1 | 10 | True | 0.2536 |
| `intellect_3_math_39` | 21 | 120 | 129 | 100 | 120 | False | 0.1833 |
| `intellect_3_math_40` | 32 | 1996 | 14 | 14 | 1996 | False | 0.2103 |
| `intellect_3_math_42` | 3780 | 10800 | 1007 | 1007 | 10800 | False | 0.2317 |
| `intellect_3_math_43` | 50 | 100000 | 14 | 14 | 1250 | False | 0.2076 |
| `intellect_3_math_45` | 243 | 48 | 243 | 1 | 243 | True | 0.2476 |
| `intellect_3_math_47` | 1374 | 1050 | 0 | 18 | 1050 | False | 0.2148 |
| `intellect_3_math_48` | 1 | -100100 | 1 | 1 | -100100 | True | 0.2563 |
| `intellect_3_math_51` | 7 | 13 | 1012 | 1 | 13 | False | 0.2294 |
| `intellect_3_math_52` | 1018 | 2007 | 448 | 1 | 2007 | False | 0.2802 |
| `intellect_3_math_53` | 15 | 24 | 12 | 1 | 24 | False | 0.2231 |
| `intellect_3_math_54` | 6 | 12 | 1 | 1 | 12 | False | 0.2509 |
| `intellect_3_math_55` | 13 | 25 | 10 | 1 | 25 | False | 0.1956 |
| `intellect_3_math_56` | 6 | 24 | 12 | 100 | 12 | False | 0.1978 |
| `intellect_3_math_58` | 1 | 11 | 4 | 1 | 11 | False | 0.2386 |
| `intellect_3_math_59` | 1382 | -1 | 14 | 14 | -1 | False | 0.1838 |
| `intellect_3_math_64` | 48 | 144 | 1 | 1 | 1728 | False | 0.1872 |
| `intellect_3_math_65` | 625 | 100000 | 14 | 14 | 1000 | False | 0.2022 |
| `intellect_3_math_66` | 578 | 4042 | 14 | 14 | 404 | False | 0.2138 |
| `intellect_3_math_67` | 9 | 12 | 13 | 1 | 13 | False | 0.1987 |
| `intellect_3_math_68` | 5940 | 5994 | 5559 | 100 | 5994 | False | 0.1895 |
| `intellect_3_math_70` | 2016 | 12752 | 127008 | 1 | 12752 | False | 0.1837 |
| `intellect_3_math_72` | -12 | -18 | 14 | 14 | -18 | False | 0.2488 |
| `intellect_3_math_74` | 9089 | 179017 | 100178 | 14 | 179001 | False | 0.1854 |
| `intellect_3_math_76` | 622 | 242 | 123456 | 1 | 100000 | False | 0.2333 |
| `intellect_3_math_77` | 1005 | 2010 | 1007 | 1007 | 1005 | False | 0.2581 |
| `intellect_3_math_78` | 96 | 200 | 100 | 100 | 200 | False | 0.1978 |
| `intellect_3_math_79` | 7 | 4 | 6 | 18 | 6 | False | 0.2023 |
| `intellect_3_math_81` | 61 | 100000 | 1 | 1 | 100000 | False | 0.1997 |
| `intellect_3_math_82` | 3 | 1 | 3 | 1 | 2 | True | 0.1856 |
| `intellect_3_math_83` | 1008 | 2018 | 3 | 1 | 2018 | False | 0.2235 |
| `intellect_3_math_84` | 1023 | 1 | 14 | 14 | 2048 | False | 0.1899 |
| `intellect_3_math_87` | 1024 | 2048 | 1024 | 14 | 2048 | True | 0.1894 |
| `intellect_3_math_88` | 1991 | 1999 | 1937 | 1 | 1937 | False | 0.2001 |
| `intellect_3_math_89` | 8128 | 400000 | 20 | 1 | 100000 | False | 0.2191 |
| `intellect_3_math_90` | 5 | 1200 | 204 | 1 | 1000 | False | 0.2043 |
| `intellect_3_math_91` | 12 | 108 | 1 | 1 | 120 | False | 0.2143 |
| `intellect_3_math_92` | 62208 | 1369 | 128 | 1 | 130000 | False | 0.2845 |
| `intellect_3_math_93` | 10053 | 202305 | 2011 | 1 | 202305 | False | 0.1948 |
| `intellect_3_math_96` | 91 | 175 | 13 | 1 | 239 | False | 0.2574 |
| `intellect_3_math_97` | 6423 | 100000 | 14 | 14 | 100000 | False | 0.2107 |
| `intellect_3_math_98` | 999 | 1999 | 1000 | 1 | 1999 | False | 0.2535 |
| `intellect_3_math_99` | 60 | 132 | 84 | 18 | 200 | False | 0.2157 |
| `intellect_3_math_100` | 18 | 11 | 14 | 14 | 12 | False | 0.1777 |
| `intellect_3_math_102` | 16 | 160 | 14 | 14 | 160 | False | 0.1876 |
| `intellect_3_math_103` | 16 | 120 | 14 | 14 | 120 | False | 0.2046 |
| `intellect_3_math_104` | 67 | 115 | 1 | 1 | 11 | False | 0.2127 |
| `intellect_3_math_105` | 126 | 18 | 27 | 18 | 18 | False | 0.2054 |
| `intellect_3_math_106` | 24 | 11 | 19 | 1 | 14 | False | 0.2109 |
| `intellect_3_math_109` | 8 | 1999 | 14 | 14 | 1999 | False | 0.1859 |
| `intellect_3_math_111` | 5300 | 2025 | 1025 | 1 | 1009 | False | 0.2054 |
| `intellect_3_math_113` | 1 | 2 | 14 | 14 | 2 | False | 0.2000 |
| `intellect_3_math_115` | 28 | 14 | 25 | 1007 | 14 | False | 0.2049 |
| `intellect_3_math_116` | 0 | -1 | 1 | 1 | -1 | False | 0.1849 |
| `intellect_3_math_117` | 1100 | 2013 | 14 | 14 | 1798 | False | 0.1698 |
| `intellect_3_math_120` | 288 | 108000 | 1 | 1 | 194400 | False | 0.2505 |
| `intellect_3_math_122` | 1360 | 100000 | 100 | 1 | 100000 | False | 0.2096 |
| `intellect_3_math_123` | 503 | 2010 | 1005 | 2 | 2010 | False | 0.2243 |
| `intellect_3_math_124` | 114 | 18 | 6 | 1 | 6 | False | 0.2250 |
| `intellect_3_math_125` | 90 | 10 | 39 | 1 | 39 | False | 0.2196 |
| `intellect_3_math_126` | 2 | 2 | 1 | 1 | 1 | False | 0.2594 |
| `intellect_3_math_127` | 67 | 1999 | 14 | 14 | 100 | False | 0.2113 |
| `intellect_3_math_129` | 2018 | 2028 | 2018 | 1 | 2018 | True | 0.1676 |
| `intellect_3_math_130` | 5 | 20 | 100 | 100 | 10 | False | 0.2316 |
| `intellect_3_math_131` | 60 | 160 | 52 | 1 | 160 | False | 0.1817 |
| `intellect_3_math_133` | 4 | 169 | 16 | 1 | 16 | False | 0.2173 |
| `intellect_3_math_134` | 27 | 130 | 128 | 14 | 170 | False | 0.1982 |
| `intellect_3_math_135` | 3 | 11 | 27 | 1 | 100000 | False | 0.1798 |
| `intellect_3_math_136` | 44 | 2014 | 1 | 1 | 2014 | False | 0.2316 |
| `intellect_3_math_137` | 71622400 | 130 | 13 | 1 | 11 | False | 0.2044 |
| `intellect_3_math_138` | 75 | 108 | 27 | 2 | 108 | False | 0.2152 |
| `intellect_3_math_139` | 60 | 120 | 100 | 100 | 120 | False | 0.1889 |
| `intellect_3_math_141` | 457 | 12096 | 18 | 18 | 1950 | False | 0.2003 |
| `intellect_3_math_142` | 9 | 2 | 1 | 1 | 2 | False | 0.2403 |
| `intellect_3_math_143` | 23 | 13 | 19 | 1 | 19 | False | 0.2359 |
| `intellect_3_math_145` | 167 | 1592 | 100 | 1 | 157 | False | 0.2113 |
| `intellect_3_math_146` | 2 | 1008 | 0 | 1 | 0 | False | 0.2217 |
| `intellect_3_math_147` | 171 | 198 | 14 | 14 | 1980 | False | 0.2090 |
| `intellect_3_math_148` | 15 | 10 | 1007 | 1007 | 10 | False | 0.1974 |
| `intellect_3_math_150` | 9 | 17 | 15 | 2 | 17 | False | 0.1873 |
| `intellect_3_math_152` | 1820 | 1919 | 100 | 100 | 100 | False | 0.2017 |
| `intellect_3_math_153` | 45 | 10 | 40 | 1 | 100 | False | 0.2052 |
| `intellect_3_math_154` | 10091 | 1009 | 2018 | 1 | 2019 | False | 0.2074 |
| `intellect_3_math_157` | 5 | 10 | 14 | 14 | 10 | False | 0.1952 |
| `intellect_3_math_160` | 18 | 184467 | 14 | 14 | 100000 | False | 0.1876 |
| `intellect_3_math_161` | 0 | 196830 | 0 | 1 | 196830 | True | 0.2300 |
| `intellect_3_math_162` | 28 | 100 | 20 | 14 | 20 | False | 0.2099 |
| `intellect_3_math_163` | 3 | 2023 | 1 | 1 | 100 | False | 0.2619 |
| `intellect_3_math_164` | 2400 | 120000 | 100000 | 1 | 112500 | False | 0.2382 |
| `intellect_3_math_166` | 70 | 120 | 14 | 14 | 0 | False | 0.2054 |
| `intellect_3_math_168` | 40 | 120 | 24 | 1 | 24 | False | 0.2040 |
| `intellect_3_math_170` | 32 | 1364 | 14 | 14 | 104857 | False | 0.1889 |
| `intellect_3_math_172` | 169 | 169 | 16 | 1 | 169 | False | 0.2090 |
| `intellect_3_math_173` | 2500 | 2025 | 1156 | 1 | 2025 | False | 0.2511 |
| `intellect_3_math_175` | 60 | 132 | 120 | 1 | 120 | False | 0.1985 |
| `intellect_3_math_177` | 10613 | 104060 | 10007 | 2 | 10403 | False | 0.2766 |
| `intellect_3_math_178` | 92 | 288 | 138 | 1 | 198 | False | 0.2092 |
| `intellect_3_math_180` | 2 | 4 | 3 | 1007 | 3 | False | 0.2319 |
| `intellect_3_math_181` | 10 | 20 | 15 | 1007 | 15 | False | 0.1941 |
| `intellect_3_math_182` | 50 | 16 | 20 | 100 | 32 | False | 0.2236 |
| `intellect_3_math_183` | 100 | 149 | 75 | 100 | 75 | False | 0.2307 |
| `intellect_3_math_184` | 92 | 1988 | 14 | 14 | 1988 | False | 0.2002 |
| `intellect_3_math_186` | 3 | 120000 | 1 | 1 | 12 | False | 0.2353 |
| `intellect_3_math_187` | 4 | 143 | 0 | 1 | 143 | False | 0.2287 |
| `intellect_3_math_188` | 504 | 2014 | 18099 | 18 | 2014 | False | 0.1907 |
| `intellect_3_math_190` | 600 | 250000 | 600 | 14 | 1000 | True | 0.1784 |
| `intellect_3_math_191` | 62 | 128 | 64 | 1 | 56 | False | 0.2267 |
| `intellect_3_math_193` | 9 | 10 | 5 | 1 | 10 | False | 0.1789 |
| `intellect_3_math_194` | 652400 | 193740 | 487201 | 1 | 193720 | False | 0.2586 |
| `intellect_3_math_197` | 39 | 12 | 39 | 1 | 39 | True | 0.2039 |
| `intellect_3_math_199` | 89 | 101 | 11 | 1 | 101 | False | 0.2366 |
