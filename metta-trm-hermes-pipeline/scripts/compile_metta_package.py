from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


ATOM_RE = re.compile(r"^\((?P<body>.*)\)$")
TOKEN_RE = re.compile(r'"(?:[^"\\]|\\.)*"|[^\s()]+')
ENV_GROUP_HEADS = {
    "answer-shape",
    "constraint",
    "example-status",
    "forbid",
    "summary",
    "minimal-example",
    "query-cue",
    "retrieval-priority",
    "validation-path",
    "validator-note",
    "verifier-caveat",
    "failure-mode",
    "repair-hint",
    "trace-label",
}
PROFILE_GROUP_HEADS = {
    "profile-summary",
    "profile-query-cue",
    "profile-constraint",
    "profile-forbid",
    "profile-minimal-example",
    "profile-repair-hint",
    "profile-trace-label",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile a MeTTa skill package into TRM bundle artifacts.")
    parser.add_argument("package_dir", help="Package directory containing package.manifest.json and .metta files.")
    parser.add_argument("--out-dir", required=True, help="Output directory for the compiled bundle.")
    return parser.parse_args()


def load_manifest(package_dir: Path) -> Dict[str, Any]:
    manifest_path = package_dir / "package.manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"missing manifest: {manifest_path}")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("package.manifest.json must decode to an object")
    return payload


def iter_metta_files(package_dir: Path) -> Iterable[Path]:
    for path in sorted(package_dir.glob("*.metta")):
        if path.is_file():
            yield path


def strip_quotes(token: str) -> str:
    token = token.strip()
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        return json.loads(token)
    return token


def parse_atoms(path: Path) -> List[Dict[str, Any]]:
    atoms: List[Dict[str, Any]] = []
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith(";"):
            continue
        match = ATOM_RE.match(line)
        if not match:
            continue
        tokens = [strip_quotes(token) for token in TOKEN_RE.findall(match.group("body"))]
        if not tokens:
            continue
        atoms.append(
            {
                "head": str(tokens[0]),
                "args": [str(token) for token in tokens[1:]],
                "source_file": path.name,
                "line_no": line_no,
            }
        )
    return atoms


def env_index(manifest: Dict[str, Any], atoms: List[Dict[str, Any]]) -> List[str]:
    envs = [str(item) for item in manifest.get("target_envs") or [] if str(item).strip()]
    if envs:
        return envs
    discovered = []
    for atom in atoms:
        if atom["head"] == "env" and atom["args"]:
            env_name = atom["args"][0]
            if env_name not in discovered:
                discovered.append(env_name)
    return discovered


def group_by_env(atoms: List[Dict[str, Any]], envs: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {env: [] for env in envs}
    for atom in atoms:
        if atom["head"] not in ENV_GROUP_HEADS:
            continue
        if not atom["args"]:
            continue
        env_name = atom["args"][0]
        if env_name in grouped:
            grouped[env_name].append(atom)
    return grouped


def group_profiles_by_env(atoms: List[Dict[str, Any]], envs: List[str]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    grouped: Dict[str, Dict[str, List[Dict[str, Any]]]] = {env: {} for env in envs}
    for atom in atoms:
        if atom["head"] not in PROFILE_GROUP_HEADS:
            continue
        if len(atom["args"]) < 3:
            continue
        env_name = atom["args"][0]
        profile_id = atom["args"][1]
        if env_name not in grouped:
            continue
        grouped[env_name].setdefault(profile_id, []).append(atom)
    return grouped


def values_for(head: str, env_atoms: List[Dict[str, Any]]) -> List[str]:
    values = []
    for atom in env_atoms:
        if atom["head"] != head or len(atom["args"]) < 2:
            continue
        values.append(atom["args"][1])
    return values


def profile_values_for(head: str, profile_atoms: List[Dict[str, Any]]) -> List[str]:
    values = []
    for atom in profile_atoms:
        if atom["head"] != head or len(atom["args"]) < 3:
            continue
        values.append(atom["args"][2])
    return values


def build_profile_packets(profile_atoms_by_env: Dict[str, Dict[str, List[Dict[str, Any]]]]) -> Dict[str, Dict[str, Any]]:
    profile_packets: Dict[str, Dict[str, Any]] = {}
    for env_name, env_profiles in profile_atoms_by_env.items():
        profile_packets[env_name] = {}
        for profile_id, atoms in env_profiles.items():
            minimal_examples = profile_values_for("profile-minimal-example", atoms)
            profile_packets[env_name][profile_id] = {
                "query_cues": profile_values_for("profile-query-cue", atoms),
                "summary": profile_values_for("profile-summary", atoms)[0] if profile_values_for("profile-summary", atoms) else "",
                "constraints": profile_values_for("profile-constraint", atoms),
                "forbids": profile_values_for("profile-forbid", atoms),
                "minimal_example": minimal_examples[0] if minimal_examples else "",
                "minimal_examples": minimal_examples,
                "repair_hints": profile_values_for("profile-repair-hint", atoms),
                "trace_labels": profile_values_for("profile-trace-label", atoms),
            }
    return profile_packets


def build_retrieval_packet(
    env_atoms: Dict[str, List[Dict[str, Any]]],
    profile_atoms_by_env: Dict[str, Dict[str, List[Dict[str, Any]]]],
) -> Dict[str, Any]:
    packet: Dict[str, Any] = {"envs": {}}
    profile_packets = build_profile_packets(profile_atoms_by_env)
    for env_name, atoms in env_atoms.items():
        answer_shapes = values_for("answer-shape", atoms)
        minimal_examples = values_for("minimal-example", atoms)
        packet["envs"][env_name] = {
            "query_cues": values_for("query-cue", atoms),
            "answer_shape": answer_shapes[0] if answer_shapes else "",
            "answer_shapes": answer_shapes,
            "summary": values_for("summary", atoms)[0] if values_for("summary", atoms) else "",
            "constraints": values_for("constraint", atoms),
            "forbids": values_for("forbid", atoms),
            "minimal_example": minimal_examples[0] if minimal_examples else "",
            "minimal_examples": minimal_examples,
            "example_status": values_for("example-status", atoms)[0] if values_for("example-status", atoms) else "",
            "validator_notes": values_for("validator-note", atoms),
            "validation_path": values_for("validation-path", atoms)[0] if values_for("validation-path", atoms) else "",
            "known_verifier_gaps": values_for("verifier-caveat", atoms),
            "failure_modes": values_for("failure-mode", atoms),
            "repair_hints": values_for("repair-hint", atoms),
            "trace_labels": values_for("trace-label", atoms),
            "retrieval_priorities": values_for("retrieval-priority", atoms),
            "profiles": profile_packets.get(env_name) or {},
        }
    return packet


def build_critic_hints(
    env_atoms: Dict[str, List[Dict[str, Any]]],
    profile_atoms_by_env: Dict[str, Dict[str, List[Dict[str, Any]]]],
) -> Dict[str, Any]:
    hints: Dict[str, Any] = {"envs": {}}
    profile_packets = build_profile_packets(profile_atoms_by_env)
    for env_name, atoms in env_atoms.items():
        answer_shapes = values_for("answer-shape", atoms)
        env_hint = {
            "required_shape": answer_shapes[0] if answer_shapes else "",
            "checks": values_for("constraint", atoms) + values_for("forbid", atoms) + values_for("validator-note", atoms),
            "repair_hints": values_for("repair-hint", atoms),
        }
        env_profiles = profile_packets.get(env_name) or {}
        if env_profiles:
            env_hint["profiles"] = {
                profile_id: {
                    "checks": list(profile_payload.get("constraints") or []) + list(profile_payload.get("forbids") or []),
                    "repair_hints": list(profile_payload.get("repair_hints") or []),
                    "summary": str(profile_payload.get("summary") or "").strip(),
                }
                for profile_id, profile_payload in env_profiles.items()
            }
        hints["envs"][env_name] = env_hint
    return hints


def build_trace_labels(
    env_atoms: Dict[str, List[Dict[str, Any]]],
    profile_atoms_by_env: Dict[str, Dict[str, List[Dict[str, Any]]]],
) -> Dict[str, Any]:
    labels: Dict[str, Any] = {"envs": {}}
    profile_packets = build_profile_packets(profile_atoms_by_env)
    for env_name, atoms in env_atoms.items():
        env_label = {
            "failure_modes": values_for("failure-mode", atoms),
            "trace_labels": values_for("trace-label", atoms),
            "repair_hints": values_for("repair-hint", atoms),
        }
        env_profiles = profile_packets.get(env_name) or {}
        if env_profiles:
            env_label["profiles"] = {
                profile_id: {
                    "trace_labels": list(profile_payload.get("trace_labels") or []),
                    "repair_hints": list(profile_payload.get("repair_hints") or []),
                }
                for profile_id, profile_payload in env_profiles.items()
            }
        labels["envs"][env_name] = env_label
    return labels


def build_artifact_contract(manifest: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
    outputs = [
        "bundle.manifest.json",
        "atoms.json",
        "retrieval_packet.json",
        "critic_hints.json",
        "trace_labels.json",
        "artifact_contract.json",
        "compiler_summary.md",
    ]
    return {
        "package_id": manifest.get("package_id", ""),
        "bundle_outputs": outputs,
        "out_dir": str(out_dir),
        "runtime_consumers": [
            "retrieval overlay",
            "critic prompt builder",
            "trace labeler",
            "future row builder",
        ],
    }


def build_bundle_manifest(manifest: Dict[str, Any], atoms: List[Dict[str, Any]], envs: List[str], metta_files: List[Path]) -> Dict[str, Any]:
    counts = defaultdict(int)
    for atom in atoms:
        counts[atom["head"]] += 1
    return {
        "package_id": manifest.get("package_id", ""),
        "title": manifest.get("title", ""),
        "base_skill": manifest.get("base_skill", ""),
        "trm_overlay": manifest.get("trm_overlay", ""),
        "infusion_type": manifest.get("infusion_type", ""),
        "target_envs": envs,
        "source_files": [path.name for path in metta_files],
        "atom_counts": dict(sorted(counts.items())),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notes": manifest.get("notes", ""),
    }


def render_summary(manifest: Dict[str, Any], envs: List[str], atoms: List[Dict[str, Any]], out_dir: Path) -> str:
    lines = [
        "# Compiler Summary",
        "",
        f"- package: `{manifest.get('package_id', '')}`",
        f"- base skill: `{manifest.get('base_skill', '')}`",
        f"- overlay: `{manifest.get('trm_overlay', '')}`",
        f"- infusion type: `{manifest.get('infusion_type', '')}`",
        f"- env count: `{len(envs)}`",
        f"- atom count: `{len(atoms)}`",
        "",
        "## Envs",
        "",
    ]
    for env_name in envs:
        lines.append(f"- `{env_name}`")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{out_dir / 'bundle.manifest.json'}`",
            f"- `{out_dir / 'retrieval_packet.json'}`",
            f"- `{out_dir / 'critic_hints.json'}`",
            f"- `{out_dir / 'trace_labels.json'}`",
        ]
    )
    return "\n".join(lines) + "\n"


def write_json(path: Path, payload: Dict[str, Any] | List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    package_dir = Path(args.package_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    manifest = load_manifest(package_dir)
    metta_files = list(iter_metta_files(package_dir))
    if not metta_files:
        raise SystemExit(f"no .metta files found in {package_dir}")

    atoms: List[Dict[str, Any]] = []
    for path in metta_files:
        atoms.extend(parse_atoms(path))

    envs = env_index(manifest, atoms)
    env_atoms = group_by_env(atoms, envs)
    profile_atoms_by_env = group_profiles_by_env(atoms, envs)
    bundle_manifest = build_bundle_manifest(manifest, atoms, envs, metta_files)
    retrieval_packet = build_retrieval_packet(env_atoms, profile_atoms_by_env)
    critic_hints = build_critic_hints(env_atoms, profile_atoms_by_env)
    trace_labels = build_trace_labels(env_atoms, profile_atoms_by_env)
    artifact_contract = build_artifact_contract(manifest, out_dir)
    compiler_summary = render_summary(manifest, envs, atoms, out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "bundle.manifest.json", bundle_manifest)
    write_json(out_dir / "atoms.json", atoms)
    write_json(out_dir / "retrieval_packet.json", retrieval_packet)
    write_json(out_dir / "critic_hints.json", critic_hints)
    write_json(out_dir / "trace_labels.json", trace_labels)
    write_json(out_dir / "artifact_contract.json", artifact_contract)
    (out_dir / "compiler_summary.md").write_text(compiler_summary, encoding="utf-8")

    print(str(out_dir / "bundle.manifest.json"))
    print(str(out_dir / "retrieval_packet.json"))
    print(str(out_dir / "critic_hints.json"))
    print(str(out_dir / "trace_labels.json"))
    print(str(out_dir / "compiler_summary.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
