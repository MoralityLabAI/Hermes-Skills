# Local Qwen2.5-3B Logic Signature Camp-Gate Run

Generated: `2026-04-29T13:58:19.544520+00:00`

Evidence class: `live_model_local_3b` plus prompt-constraint projection.

Model: `D:\Research_Engine\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf`
llama.cpp completion: `D:\Research_Engine\tools\llama.cpp-b8922-cuda12.4\llama-completion.exe`
Peak child RSS: `2373.23 MB`

## Arm Summary

| Arm | Rows | Exact | Exact Rate | Contract Valid | Avg Cell Acc | Tier Counts |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `baseline` | 12 | 0 | 0.0000 | 0 | 0.0781 | none:10, weak_surface:2 |
| `metta_runtime` | 12 | 0 | 0.0000 | 0 | 0.2792 | none:3, weak_surface:9 |
| `metta_signature_projection` | 12 | 9 | 0.7500 | 9 | 0.7500 | full_candidate:9, none:3 |
| `pure_trm` | 12 | 0 | 0.0000 | 0 | 0.1562 | none:7, weak_surface:5 |

## Case Detail

| Row | Arm | Tier | Exact | Contract | Cell Acc | Output |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `camp_gate_001_5x4_4c` | `baseline` | `none` | 0 | 0 | 0.0000 | <code>T C X\nX C X\nT C X\nX C X\nT C X</code> |
| `camp_gate_001_5x4_4c` | `pure_trm` | `none` | 0 | 0 | 0.0000 | <code>T C X  \nX C T  \nT X X  \nX C T  \nT X X</code> |
| `camp_gate_001_5x4_4c` | `metta_runtime` | `weak_surface` | 0 | 0 | 0.3500 | <code>T C X X\nT C X X\nX C T T\nX X C C\nX X T T</code> |
| `camp_gate_001_5x4_4c` | `metta_signature_projection` | `full_candidate` | 1 | 1 | 1.0000 | <code>TXTX\nCXCX\nXXXX\nCTXX\nXXTC</code> |
| `camp_gate_002_4x4_3c` | `baseline` | `weak_surface` | 0 | 0 | 0.4375 | <code>T C X X\nX C T X\nX X C T\nT X C X</code> |
| `camp_gate_002_4x4_3c` | `pure_trm` | `weak_surface` | 0 | 0 | 0.3750 | <code>T C X X  \nX C T X  \nX X C T  \nX T X C</code> |
| `camp_gate_002_4x4_3c` | `metta_runtime` | `weak_surface` | 0 | 0 | 0.4375 | <code>T C X X  \nX C T X  \nX X C T  \nX X X C</code> |
| `camp_gate_002_4x4_3c` | `metta_signature_projection` | `full_candidate` | 1 | 1 | 1.0000 | <code>XXXX\nXXTC\nCXXX\nTXTC</code> |
| `camp_gate_003_4x5_4c` | `baseline` | `none` | 0 | 0 | 0.0000 | <code>T C X\nX C X\nT C X\nX C X</code> |
| `camp_gate_003_4x5_4c` | `pure_trm` | `weak_surface` | 0 | 0 | 0.2500 | <code>T C X X X  \nT C X X X  \nX C C C X  \nX X T T X</code> |
| `camp_gate_003_4x5_4c` | `metta_runtime` | `weak_surface` | 0 | 0 | 0.2500 | <code>T C X X X\nX C T T T\nX X C C T\nX X X T T</code> |
| `camp_gate_003_4x5_4c` | `metta_signature_projection` | `full_candidate` | 1 | 1 | 1.0000 | <code>XXCTT\nXXXXC\nXXXXX\nCTXTC</code> |
| `camp_gate_004_5x4_4c` | `baseline` | `none` | 0 | 0 | 0.0000 | <code>T C X\nX C X\nT C X\nX C X\nT C X</code> |
| `camp_gate_004_5x4_4c` | `pure_trm` | `none` | 0 | 0 | 0.0000 | <code>T C X  \nX C T  \nT X C  \nC T X  \nX T C</code> |
| `camp_gate_004_5x4_4c` | `metta_runtime` | `weak_surface` | 0 | 0 | 0.2000 | <code>T C X X  \nX C T T  \nT X X C  \nX C T T  \nT X X C</code> |
| `camp_gate_004_5x4_4c` | `metta_signature_projection` | `full_candidate` | 1 | 1 | 1.0000 | <code>XXTC\nTXXX\nCXCT\nXXXX\nTCXX</code> |
| `camp_gate_005_5x5_5c` | `baseline` | `none` | 0 | 0 | 0.0000 | <code>T C X\nX C X\nT C X\nX C X\nT C X</code> |
| `camp_gate_005_5x5_5c` | `pure_trm` | `none` | 0 | 0 | 0.0000 | <code>T C X\nX C X\nT C X\nX C X\nT C X</code> |
| `camp_gate_005_5x5_5c` | `metta_runtime` | `none` | 0 | 0 | 0.0000 | <code>T C X\nX C X\nT C X\nX C X\nT C X</code> |
| `camp_gate_005_5x5_5c` | `metta_signature_projection` | `none` | 0 | 0 | 0.0000 | <code></code> |
| `camp_gate_006_4x4_3c` | `baseline` | `none` | 0 | 0 | 0.0000 | <code>T C  \nX X  \nT X  \nX C</code> |
| `camp_gate_006_4x4_3c` | `pure_trm` | `weak_surface` | 0 | 0 | 0.6250 | <code>T C X T\nX C X X\nT X C T\nX X T X</code> |
| `camp_gate_006_4x4_3c` | `metta_runtime` | `weak_surface` | 0 | 0 | 0.5000 | <code>T C X X  \nX C T T  \nT X X C  \nX T C T</code> |
| `camp_gate_006_4x4_3c` | `metta_signature_projection` | `full_candidate` | 1 | 1 | 1.0000 | <code>TCXX\nXXXC\nTXXT\nCXXX</code> |
| `camp_gate_007_5x4_4c` | `baseline` | `none` | 0 | 0 | 0.0000 | <code>T C X\nX C X\nT C X\nX C X\nT C X</code> |
| `camp_gate_007_5x4_4c` | `pure_trm` | `none` | 0 | 0 | 0.0000 | <code>T C X  \nX C T  \nT X C  \nC T X  \nX T C</code> |
| `camp_gate_007_5x4_4c` | `metta_runtime` | `weak_surface` | 0 | 0 | 0.3000 | <code>T C X C  \nT X X X  \nT X X T  \nX C T T  \nX X T X</code> |
| `camp_gate_007_5x4_4c` | `metta_signature_projection` | `full_candidate` | 1 | 1 | 1.0000 | <code>XXTC\nXXTX\nXXCX\nCTXX\nXTCX</code> |
| `camp_gate_008_4x4_3c` | `baseline` | `none` | 0 | 0 | 0.0000 | <code>T C  \nX X  \nX X  \nT X</code> |
| `camp_gate_008_4x4_3c` | `pure_trm` | `weak_surface` | 0 | 0 | 0.3125 | <code>T C X T\nX C X X\nT X C T\nX X T X</code> |
| `camp_gate_008_4x4_3c` | `metta_runtime` | `weak_surface` | 0 | 0 | 0.5000 | <code>T C X X  \nX C T T  \nX X C T  \nX X X C</code> |
| `camp_gate_008_4x4_3c` | `metta_signature_projection` | `full_candidate` | 1 | 1 | 1.0000 | <code>XCXX\nXTTC\nXXXX\nCTXX</code> |
| `camp_gate_009_4x5_4c` | `baseline` | `none` | 0 | 0 | 0.0000 | <code>T C X\nX C X\nT C X\nX T X</code> |
| `camp_gate_009_4x5_4c` | `pure_trm` | `none` | 0 | 0 | 0.0000 | <code>T C X  \nX C T  \nT X C  \nC T X</code> |
| `camp_gate_009_4x5_4c` | `metta_runtime` | `weak_surface` | 0 | 0 | 0.2500 | <code>T C X C T\nX C T X C\nT X C T X\nX T C X T</code> |
| `camp_gate_009_4x5_4c` | `metta_signature_projection` | `full_candidate` | 1 | 1 | 1.0000 | <code>CXTXX\nTXCXX\nXXXTX\nCTXCX</code> |
| `camp_gate_010_5x4_4c` | `baseline` | `none` | 0 | 0 | 0.0000 | <code>T C X\nX C X\nT C X\nX C X\nT C X</code> |
| `camp_gate_010_5x4_4c` | `pure_trm` | `none` | 0 | 0 | 0.0000 | <code>T C X  \nX C T  \nT X X  \nC T X  \nX C T</code> |
| `camp_gate_010_5x4_4c` | `metta_runtime` | `none` | 0 | 0 | 0.0000 | <code>T C X T C  \nX C T C X  \nT X C X T  \nX T C X T  \nC X T C X</code> |
| `camp_gate_010_5x4_4c` | `metta_signature_projection` | `none` | 0 | 0 | 0.0000 | <code></code> |
| `camp_gate_011_5x5_5c` | `baseline` | `none` | 0 | 0 | 0.0000 | <code>T C X\nX C X\nT C X\nX C X\nT C X</code> |
| `camp_gate_011_5x5_5c` | `pure_trm` | `none` | 0 | 0 | 0.0000 | <code>T C X\nX C X\nT C X\nX C X\nT C X</code> |
| `camp_gate_011_5x5_5c` | `metta_runtime` | `none` | 0 | 0 | 0.0000 | <code>T C X\nX C X\nT C X\nX C X\nT C X</code> |
| `camp_gate_011_5x5_5c` | `metta_signature_projection` | `none` | 0 | 0 | 0.0000 | <code></code> |
| `camp_gate_012_4x4_3c` | `baseline` | `weak_surface` | 0 | 0 | 0.5000 | <code>T C X X\nX C T X\nT X X C\nX X C T</code> |
| `camp_gate_012_4x4_3c` | `pure_trm` | `weak_surface` | 0 | 0 | 0.3125 | <code>T C X T\nX C X X\nT X C T\nX X C X</code> |
| `camp_gate_012_4x4_3c` | `metta_runtime` | `weak_surface` | 0 | 0 | 0.5625 | <code>T C X X  \nX C T X  \nX X C T  \nX X X C</code> |
| `camp_gate_012_4x4_3c` | `metta_signature_projection` | `full_candidate` | 1 | 1 | 1.0000 | <code>TXCX\nCXTX\nXXXX\nXXTC</code> |

## Claim Audit

- Allowed: this measures whether local 3B emits enough verifier-visible grid state for prompt-derived symbolic closure.
- Not allowed: do not call the projection arm trained TRM lift or hidden reasoning improvement.
- Not allowed: do not treat this as an Intellect-3 leaderboard result; it is a leakage-safe micro-env.
