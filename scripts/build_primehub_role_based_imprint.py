from __future__ import annotations

import argparse
import json
from pathlib import Path

from primehub_role_imprint import (
    DEFAULT_MATRIX_ROOT,
    build_payload,
    render_markdown,
    write_json,
    write_text,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a role-based Primehub TRM imprint from the latest cluster matrix.")
    parser.add_argument("--matrix-root", default=str(DEFAULT_MATRIX_ROOT))
    parser.add_argument("--output-json", default="")
    parser.add_argument("--output-md", default="")
    parser.add_argument("--cluster", action="append", default=[])
    args = parser.parse_args()

    matrix_root = Path(args.matrix_root).resolve()
    output_json = Path(args.output_json).resolve() if args.output_json else matrix_root / "role_based_imprint.json"
    output_md = Path(args.output_md).resolve() if args.output_md else matrix_root / "role_based_imprint.md"

    payload = build_payload(matrix_root=matrix_root, cluster_ids=args.cluster or None)
    write_json(output_json, payload)
    write_text(output_md, render_markdown(payload))
    print(json.dumps({"output_json": str(output_json), "output_md": str(output_md), "clusters": sorted((payload.get("cluster_cards") or {}).keys())}, indent=2))


if __name__ == "__main__":
    main()
