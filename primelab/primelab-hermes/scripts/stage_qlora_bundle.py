import argparse
import json
import tarfile
from pathlib import Path


DEFAULT_INCLUDE_PATHS = [
    "configs/qlora_conveyor.example.json",
    "requirements/qlora.txt",
    "scripts/build_qlora_dataset.py",
    "scripts/remote_qlora_conveyor.py",
    "scripts/run_prime_qlora_conveyor.sh",
    "scripts/stage_qlora_bundle.py",
    "scripts/train_qlora_sft.py",
    "src/primelab_hermes/qlora_conveyor.py",
    "src/primelab_hermes/trainer_compat.py",
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Create a minimal QLoRA conveyor bundle for Prime pods.")
    ap.add_argument("--root", type=str, default=".")
    ap.add_argument("--spec-json", type=str, default="configs/qlora_conveyor.example.json")
    ap.add_argument("--out", type=str, required=True)
    ap.add_argument("--data-root", type=str, required=True)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    spec_path = (root / args.spec_json).resolve()
    out_path = Path(args.out).resolve()
    data_root = Path(args.data_root).resolve()

    if not spec_path.exists():
        raise SystemExit(f"Missing spec json: {spec_path}")
    if not data_root.exists():
        raise SystemExit(f"Missing generated data root: {data_root}")

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    include_paths = list(DEFAULT_INCLUDE_PATHS)
    include_paths.append(str(spec_path.relative_to(root)).replace("\\", "/"))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"root": str(root), "out": str(out_path), "files": []}

    with tarfile.open(out_path, "w:gz") as tf:
        for rel in sorted(set(include_paths)):
            src = root / rel
            if not src.exists():
                raise SystemExit(f"Missing required bundle path: {src}")
            tf.add(src, arcname=rel)
            manifest["files"].append(rel)

        for path in sorted(data_root.rglob("*")):
            if path.is_file():
                arcname = path.relative_to(root).as_posix()
                tf.add(path, arcname=arcname)
                manifest["files"].append(arcname)

    manifest_path = out_path.with_suffix(out_path.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(out_path)
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
