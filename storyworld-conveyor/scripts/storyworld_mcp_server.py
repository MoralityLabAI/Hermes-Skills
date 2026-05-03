from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_STATE_PATH = Path("working_world_state.json")


def _tokenize(text: str) -> List[str]:
    return [token for token in re.findall(r"[A-Za-z0-9_]+", str(text).lower()) if token]


def _safe_json_loads(text: str) -> Dict[str, Any]:
    try:
        payload = json.loads(text)
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except Exception:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8-sig")


def _read_json_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return _read_text(path)
    return json.dumps(payload, indent=2, ensure_ascii=True)


def _estimate_tokens(text: str) -> int:
    return max(1, len(_tokenize(text)))


def _excerpt(text: str, limit: int = 420) -> str:
    compact = re.sub(r"\s+", " ", str(text)).strip()
    if len(compact) <= limit:
        return compact
    return compact[: max(0, limit - 3)].rstrip() + "..."


@dataclass(frozen=True)
class IndexHit:
    encounter_id: str
    score: float
    excerpt: str
    metadata: Dict[str, Any]


class StoryworldIndex:
    def __init__(self, index_root: str | Path, state_path: str | Path | None = None) -> None:
        self.index_root = Path(index_root).expanduser().resolve()
        self.state_path = Path(state_path).expanduser().resolve() if state_path else DEFAULT_STATE_PATH.resolve()
        self.encounters_path = self._resolve_index_file("encounters.jsonl")
        self.world_card_path = self._resolve_index_file("world_card.txt")
        self.report_root = self._resolve_report_root()
        self.monte_carlo_path = self._resolve_report_file(["monte_carlo_overnight.txt", "monte_carlo.txt"])
        self.quality_report_path = self._resolve_report_file(["quality_gate_overnight.json", "quality_gate.json"])
        self.rebalance_advice_path = self._resolve_report_file(
            ["trm_advice.generated.json", "trm_constraints.json", "trm_rebalance_advice.json"]
        )
        self.phase_state_path = self._resolve_report_file(["phase_state.json"])
        self._encounter_rows = _load_jsonl(self.encounters_path)
        self._world_card = _read_text(self.world_card_path)
        self._monte_carlo_report = _read_text(self.monte_carlo_path)
        self._quality_report = _read_json_text(self.quality_report_path)
        self._rebalance_advice = _read_json_text(self.rebalance_advice_path)
        self._phase_state = _read_json_text(self.phase_state_path)
        self._encounter_index = self._build_encounter_index(self._encounter_rows)
        self._namespace_index = self._build_namespace_index(
            self._encounter_rows,
            self._world_card,
            self._monte_carlo_report,
            self._quality_report,
            self._rebalance_advice,
            self._phase_state,
        )

    def _resolve_index_file(self, filename: str) -> Path:
        candidates = [
            self.index_root / filename,
            self.index_root / "encounter_index" / filename,
            self.index_root / "indices" / "encounter_index" / filename,
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()
        return candidates[0].resolve()

    def _resolve_report_root(self) -> Path:
        candidates = [
            self.index_root / "reports",
            self.index_root.parent / "reports",
            self.index_root.parent.parent / "reports",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()
        return candidates[0].resolve()

    def _resolve_report_file(self, filenames: List[str]) -> Path:
        roots = [self.report_root, self.index_root, self.index_root.parent, self.index_root.parent.parent]
        for root in roots:
            for filename in filenames:
                candidate = root / filename
                if candidate.exists():
                    return candidate.resolve()
        return (self.report_root / filenames[0]).resolve()

    @staticmethod
    def _build_encounter_index(rows: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        index: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            encounter_id = str(row.get("encounter_id", "") or "").strip()
            if not encounter_id:
                continue
            index[encounter_id] = row
        return index

    @staticmethod
    def _build_namespace_index(
        rows: Iterable[Dict[str, Any]],
        world_card: str,
        monte_carlo_report: str,
        quality_report: str,
        rebalance_advice: str,
        phase_state: str,
    ) -> Dict[str, str]:
        namespace_chunks: Dict[str, List[str]] = {
            "world_card": [_excerpt(world_card, 4000)] if world_card else [],
            "encounters": [],
            "scene_cards": [],
            "monte_carlo": [_excerpt(monte_carlo_report, 2500)] if monte_carlo_report else [],
            "quality_gate": [_excerpt(quality_report, 2500)] if quality_report else [],
            "rebalance_advice": [_excerpt(rebalance_advice, 2500)] if rebalance_advice else [],
            "phase_state": [_excerpt(phase_state, 1200)] if phase_state else [],
        }
        for row in rows:
            encounter_id = str(row.get("encounter_id", "") or "").strip()
            block = str(row.get("block", "") or "")
            option_labels = row.get("option_labels", [])
            consequences = row.get("consequences", [])
            namespace_chunks["encounters"].append(
                " | ".join(
                    [
                        encounter_id,
                        _excerpt(block, 500),
                        f"options={option_labels}",
                        f"consequences={consequences}",
                    ]
                )
            )
            if encounter_id.startswith("page_scene_"):
                namespace_chunks["scene_cards"].append(_excerpt(block, 500))
        return {key: "\n".join(value) for key, value in namespace_chunks.items()}

    @staticmethod
    def _score_text(query_tokens: List[str], *texts: str) -> float:
        if not query_tokens:
            return 0.0
        bag = set()
        score = 0.0
        for text in texts:
            bag.update(_tokenize(text))
        for token in query_tokens:
            if token in bag:
                score += 1.0
        return score

    def _rank_hits(self, query: str, namespace: str | None = None, top_k: int = 3) -> List[IndexHit]:
        query_tokens = _tokenize(query)
        namespace_tokens = _tokenize(namespace or "")
        hits: List[IndexHit] = []
        for encounter_id, row in self._encounter_index.items():
            block = str(row.get("block", "") or "")
            option_labels = " ".join(str(item) for item in row.get("option_labels", []))
            consequences = " ".join(str(item) for item in row.get("consequences", []))
            metadata_blob = json.dumps(row, ensure_ascii=True, sort_keys=True)
            score = self._score_text(query_tokens, encounter_id, block, option_labels, consequences, metadata_blob)
            if encounter_id.lower() in query.lower():
                score += 6.0
            if namespace_tokens and any(token in encounter_id.lower() or token in block.lower() for token in namespace_tokens):
                score += 1.5
            if score <= 0.0:
                continue
            hits.append(
                IndexHit(
                    encounter_id=encounter_id,
                    score=score,
                    excerpt=_excerpt(block or metadata_blob),
                    metadata={
                        "option_labels": row.get("option_labels", []),
                        "consequences": row.get("consequences", []),
                        "reaction_count": row.get("reaction_count"),
                        "turn_span": row.get("turn_span"),
                    },
                )
            )
        hits.sort(key=lambda item: (-item.score, item.encounter_id))
        return hits[:top_k]

    def describe(self) -> Dict[str, Any]:
        scene_count = sum(1 for encounter_id in self._encounter_index if encounter_id.startswith("page_scene_"))
        terminal_count = sum(1 for encounter_id in self._encounter_index if encounter_id.startswith("page_end_"))
        report_namespaces = [name for name, value in self._namespace_index.items() if name not in {"encounters", "scene_cards"} and value]
        return {
            "index_root": str(self.index_root),
            "encounters_path": str(self.encounters_path),
            "world_card_path": str(self.world_card_path),
            "report_root": str(self.report_root),
            "monte_carlo_path": str(self.monte_carlo_path),
            "quality_report_path": str(self.quality_report_path),
            "rebalance_advice_path": str(self.rebalance_advice_path),
            "encounter_count": len(self._encounter_index),
            "scene_count": scene_count,
            "terminal_count": terminal_count,
            "world_card_tokens_est": _estimate_tokens(self._world_card),
            "report_namespaces": report_namespaces,
            "sample_encounter_ids": list(sorted(self._encounter_index))[:8],
        }

    def load_state(self) -> Dict[str, Any]:
        if self.state_path.exists():
            try:
                payload = json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                payload = {}
            if isinstance(payload, dict):
                return payload
        return {"current_node": "start", "inventory": [], "relationships": {}}

    def save_state(self, state: Dict[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(state, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")

    def get_encounter_card(self, encounter_id: str) -> Dict[str, Any]:
        encounter_id = str(encounter_id).strip()
        row = self._encounter_index.get(encounter_id)
        if row is None:
            ranked = self._rank_hits(encounter_id, namespace="encounters", top_k=1)
            if ranked:
                row = self._encounter_index.get(ranked[0].encounter_id)
        if row is None:
            return {
                "tool": "get_encounter_card",
                "encounter_id": encounter_id,
                "found": False,
                "index_root": str(self.index_root),
                "message": "No encounter card matched the requested id.",
                "top_hits": [
                    {
                        "encounter_id": hit.encounter_id,
                        "score": hit.score,
                        "excerpt": hit.excerpt,
                        "metadata": hit.metadata,
                    }
                    for hit in self._rank_hits(encounter_id, namespace="encounters", top_k=3)
                ],
            }
        return {
            "tool": "get_encounter_card",
            "encounter_id": encounter_id,
            "found": True,
            "index_root": str(self.index_root),
            "encounter": {
                "encounter_id": row.get("encounter_id"),
                "turn_span": row.get("turn_span"),
                "reaction_count": row.get("reaction_count"),
                "option_labels": row.get("option_labels", []),
                "consequences": row.get("consequences", []),
            },
            "card": _excerpt(row.get("block", ""), 280),
            "card_excerpt": _excerpt(row.get("block", ""), 280),
            "top_hits": [
                {
                    "encounter_id": hit.encounter_id,
                    "score": hit.score,
                    "excerpt": hit.excerpt,
                    "metadata": hit.metadata,
                }
                for hit in self._rank_hits(encounter_id, namespace="encounters", top_k=3)
            ],
        }

    def query_lore_index(self, namespace: str, query: str, top_k: int = 3) -> Dict[str, Any]:
        namespace = str(namespace or "world_card").strip() or "world_card"
        query = str(query or "").strip()
        namespace_key = namespace.lower()
        namespace_aliases = {
            "lore": "world_card",
            "world": "world_card",
            "bible": "world_card",
            "mc": "monte_carlo",
            "montecarlo": "monte_carlo",
            "quality": "quality_gate",
            "qualitygate": "quality_gate",
            "rebalance": "rebalance_advice",
            "pathing": "rebalance_advice",
            "formula": "rebalance_advice",
            "ending": "rebalance_advice",
            "state": "phase_state",
            "constraints": "rebalance_advice",
        }
        canonical_namespace = namespace_aliases.get(namespace_key, namespace_key)
        namespace_blob = self._namespace_index.get(canonical_namespace)
        namespace_match = namespace_blob if namespace_blob is not None else self._namespace_index.get("world_card", "")
        worldish = canonical_namespace in {"world_card"}
        reportish = canonical_namespace in {"monte_carlo", "quality_gate", "rebalance_advice", "phase_state"}
        hits = [] if worldish or reportish else self._rank_hits(f"{canonical_namespace} {query}", namespace=canonical_namespace, top_k=top_k)
        payload = {
            "tool": "query_lore_index",
            "namespace": canonical_namespace,
            "namespace_request": namespace,
            "query": query,
            "index_root": str(self.index_root),
            "world_card_excerpt": _excerpt(self._world_card, 240),
            "namespace_excerpt": _excerpt(namespace_match, 240),
            "top_hits": [
                {
                    "encounter_id": hit.encounter_id,
                    "score": hit.score,
                    "excerpt": hit.excerpt,
                    "metadata": hit.metadata,
                }
                for hit in hits
            ],
            "match_count": len(hits),
        }
        if worldish:
            payload["recommended_card"] = _excerpt(self._world_card, 240)
        elif reportish:
            payload["recommended_report"] = _excerpt(namespace_match, 240)
        return payload

    def update_state(self, delta: Dict[str, Any]) -> Dict[str, Any]:
        state = self.load_state()
        if isinstance(delta, dict):
            state.update(delta)
        self.save_state(state)
        return {"status": "ok", "state": state}

    def evaluate_secret_ending(self) -> Dict[str, Any]:
        state = self.load_state()
        inventory = state.get("inventory", [])
        relationships = state.get("relationships", {})
        proximity = 0.5
        if isinstance(inventory, list):
            proximity += min(0.2, 0.05 * len(inventory))
        if isinstance(relationships, dict):
            proximity += min(0.2, 0.03 * len(relationships))
        return {
            "proximity": round(min(1.0, proximity), 3),
            "missing_predicates": ["oath_broken", "witness_alignment"],
        }

    def advance_scene(self, action_taken: str) -> Dict[str, Any]:
        state = self.load_state()
        state["last_action"] = str(action_taken)
        current_node = str(state.get("current_node", "start"))
        state["current_node"] = f"{current_node}:advanced"
        self.save_state(state)
        return {"status": "ok", "next_node": state["current_node"]}


def build_server(index: StoryworldIndex):
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as exc:  # pragma: no cover - runtime dependency
        raise SystemExit(f"Missing MCP runtime dependency: {exc}")

    mcp = FastMCP("Storyworld-Builder")

    @mcp.tool()
    async def get_encounter_card(encounter_id: str) -> str:
        return json.dumps(index.get_encounter_card(encounter_id), indent=2, ensure_ascii=True)

    @mcp.tool()
    async def query_lore_index(namespace: str, query: str) -> str:
        return json.dumps(index.query_lore_index(namespace, query), indent=2, ensure_ascii=True)

    @mcp.tool()
    async def update_state(delta: dict) -> str:
        return json.dumps(index.update_state(delta), indent=2, ensure_ascii=True)

    @mcp.tool()
    async def evaluate_secret_ending() -> dict:
        return index.evaluate_secret_ending()

    @mcp.tool()
    async def advance_scene(action_taken: str) -> str:
        return json.dumps(index.advance_scene(action_taken), indent=2, ensure_ascii=True)

    @mcp.resource("lore://world-bible")
    def get_world_bible() -> str:
        return _excerpt(index._world_card, 4000)

    @mcp.resource("lore://monte-carlo")
    def get_monte_carlo_report() -> str:
        return _excerpt(index._monte_carlo_report, 4000)

    @mcp.resource("lore://quality-gate")
    def get_quality_report() -> str:
        return _excerpt(index._quality_report, 4000)

    @mcp.resource("lore://rebalance-advice")
    def get_rebalance_advice() -> str:
        return _excerpt(index._rebalance_advice, 4000)

    @mcp.resource("state://current-player")
    def get_player_status() -> str:
        return json.dumps(index.load_state(), indent=2, ensure_ascii=True)

    return mcp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Index-backed MCP server for Hermes storyworld routing.")
    parser.add_argument(
        "--index-root",
        default=os.environ.get("STORYWORLD_INDEX_ROOT", ""),
        help="Path to the encounter index directory or its parent.",
    )
    parser.add_argument(
        "--state-path",
        default=str(DEFAULT_STATE_PATH),
        help="Path to the mutable state JSON file used by the MCP tools.",
    )
    parser.add_argument("--summary", action="store_true", help="Print the loaded index summary and exit.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.index_root:
        raise SystemExit("--index-root is required (or set STORYWORLD_INDEX_ROOT).")
    index = StoryworldIndex(args.index_root, args.state_path)
    if args.summary:
        print(json.dumps(index.describe(), indent=2, ensure_ascii=True))
        return 0
    server = build_server(index)
    server.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
