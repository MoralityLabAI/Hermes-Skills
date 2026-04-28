from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPO_ROOT = Path(__file__).resolve().parents[2]
STUDY_DIR = REPO_ROOT / "research" / "studies" / "2026-04-22-metta-trm-hermes-pipeline"
ARTIFACTS_DIR = STUDY_DIR / "artifacts"

DEFAULT_PROFILES = {
    "allenai_ifeval": {
        "profile": "exact_contract_instruction_wrapper",
        "cluster": "choice_contract",
        "primary_metric": "gated_contract_success_rate",
        "abstraction_bundle": ARTIFACTS_DIR / "primehub_external_ifeval_bundle" / "primehub_external_ifeval_bundle.jsonl",
        "critic_support_bundle": ARTIFACTS_DIR
        / "primehub_external_ifeval_critic_support_bundle"
        / "primehub_external_ifeval_critic_support_bundle.jsonl",
        "promotion_guardrail": "preserve unrelated-family critic and gated-router metrics while improving wrapper contract success",
    },
    "aime2026": {
        "profile": "hard_numeric_verification",
        "cluster": "hard_reasoning_numeric",
        "primary_metric": "gated_boxed_exact_rate",
        "abstraction_bundle": ARTIFACTS_DIR / "primehub_external_aime2026_bundle" / "primehub_external_aime2026_bundle.jsonl",
        "critic_support_bundle": ARTIFACTS_DIR
        / "primehub_external_aime2026_critic_support_bundle"
        / "primehub_external_aime2026_critic_support_bundle.jsonl",
        "promotion_guardrail": "preserve unrelated-family critic calibration while improving boxed exactness and visible output",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile a MeTTa-derived Primehub family router profile bundle.")
    parser.add_argument("--out-dir", required=True, help="Output directory for router profile artifacts.")
    return parser.parse_args()


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def profile_row(env_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    abstraction_path = Path(config["abstraction_bundle"])
    critic_path = Path(config["critic_support_bundle"])
    abstraction_rows = load_jsonl(abstraction_path)
    critic_rows = load_jsonl(critic_path)
    return {
        "source_env_name": env_name,
        "router_profile": str(config["profile"]),
        "cluster": str(config["cluster"]),
        "primary_metric": str(config["primary_metric"]),
        "abstraction_bundle": str(abstraction_path),
        "critic_support_bundle": str(critic_path),
        "abstraction_rows": len(abstraction_rows),
        "critic_support_rows": len(critic_rows),
        "promotion_guardrail": str(config["promotion_guardrail"]),
        "route_mode": "family_specialist",
    }


def build_markdown(bundle: Dict[str, Any]) -> str:
    lines = [
        "# Primehub Family Router Bundle",
        "",
        "This bundle keeps MeTTa family rows modular instead of merging every family into one shared critic.",
        "",
        "| Env | Profile | Primary metric | Abstraction rows | Critic rows |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for row in bundle["profiles"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['source_env_name']}`",
                    f"`{row['router_profile']}`",
                    f"`{row['primary_metric']}`",
                    str(row["abstraction_rows"]),
                    str(row["critic_support_rows"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Promotion rule: target-family lift must be reported with unrelated-family critic drift and gated-router regression.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    profiles = [profile_row(env_name, config) for env_name, config in DEFAULT_PROFILES.items()]
    bundle = {
        "bundle_type": "primehub_family_router",
        "version": "router_profiles_v1",
        "profiles": profiles,
        "interference_metrics": [
            "target_family_lift",
            "unrelated_critic_drift",
            "unrelated_gated_router_regression",
            "whole_holdout_critic_drift",
            "net_interference_score",
        ],
    }
    write_json(out_dir / "primehub_family_router_bundle.json", bundle)
    write_jsonl(out_dir / "primehub_family_router_profiles.jsonl", profiles)
    write_markdown(out_dir / "primehub_family_router_bundle.md", build_markdown(bundle))
    print(str(out_dir / "primehub_family_router_bundle.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
