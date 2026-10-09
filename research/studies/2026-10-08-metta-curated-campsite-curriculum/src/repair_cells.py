"""SPEC-R data layer: compile the repair-cell MeTTa package, build nearest-solution targets, apply the declared
symmetries, and turn a (puzzle, candidate) pair into per-cell channels for the raw and atoms framings."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import campsite
import metta_schema

PACKAGE = Path(__file__).resolve().parents[1] / "metta" / "campsite_repair_cells.metta"
N = 6


@lru_cache(maxsize=None)
def package() -> dict:
    out = {"raw": [], "atoms": [], "symmetries": []}
    for line in metta_schema._top_level(PACKAGE.read_text(encoding="utf-8")):
        m = re.fullmatch(r"\((raw-channel|cell-atom) (\S+) (\S+)\)", line)
        if m:
            out["raw" if m.group(1) == "raw-channel" else "atoms"].append((m.group(2), m.group(3)))
            continue
        m = re.fullmatch(r"\(symmetry (\S+)\)", line)
        if m:
            out["symmetries"].append(m.group(1))
    return out


def channels(framing: str) -> list[tuple[str, str]]:
    p = package()
    return p["raw"] + (p["atoms"] if framing == "atoms" else [])


# ---------------------------------------------------------------------------- grids


def normalise(task_grid, cand):
    """The candidate as an n x m grid; cells it lacks become 'M' (missing), extra cells are dropped."""
    n, m = len(task_grid), len(task_grid[0])
    out = []
    for r in range(n):
        row = cand[r] if isinstance(cand, list) and r < len(cand) and isinstance(cand[r], list) else []
        out.append([(row[c] if c < len(row) and row[c] in ("T", "X", "C") else "M") for c in range(m)])
    return out


def _ham(a, b):
    return sum(x != y for ra, rb in zip(a, b) for x, y in zip(ra, rb))


@lru_cache(maxsize=None)
def solutions(pool: str, puzzle_id: str) -> tuple:
    task, _ = campsite.task_by_id(pool)[puzzle_id]
    sols, _ = campsite.camp().solve_candidates(task, max_candidates=50, max_nodes=200000)
    return tuple(tuple(tuple(r) for r in s) for s in sols)


def nearest_solution(pool: str, puzzle_id: str, cand_norm) -> list[list[str]]:
    sols = solutions(pool, puzzle_id)
    best = min(sols, key=lambda s: _ham(s, cand_norm))
    return [list(r) for r in best]


# ---------------------------------------------------------------------------- symmetries


def transform(sym: str, trees, rows, cols, cand, target):
    """Apply a declared symmetry to the puzzle, candidate and target together."""
    def fr(g):
        return g[::-1]

    def fc(g):
        return [r[::-1] for r in g]

    def tp(g):
        return [list(x) for x in zip(*g)]

    if sym == "identity":
        return trees, rows, cols, cand, target
    if sym == "flip_rows":
        return fr(trees), rows[::-1], cols, fr(cand), fr(target)
    if sym == "flip_cols":
        return fc(trees), rows, cols[::-1], fc(cand), fc(target)
    if sym == "flip_both":
        return fr(fc(trees)), rows[::-1], cols[::-1], fr(fc(cand)), fr(fc(target))
    if sym == "transpose":
        return tp(trees), cols, rows, tp(cand), tp(target)
    raise ValueError(sym)


# ---------------------------------------------------------------------------- features


def _orth(r, c, n, m):
    return [(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= r + dr < n and 0 <= c + dc < m]


def _ring(r, c, n, m):
    return [(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr or dc) and 0 <= r + dr < n and 0 <= c + dc < m]


def cell_values(trees, rows, cols, cand) -> dict[str, list[list[float]]]:
    """Unscaled value of every channel the package may declare, on the n x m grid."""
    n, m = len(trees), len(trees[0])
    ptree = [[trees[r][c] == "T" for c in range(m)] for r in range(n)]
    tent = [[cand[r][c] == "C" for c in range(m)] for r in range(n)]
    elig = [[(not ptree[r][c]) and any(ptree[a][b] for a, b in _orth(r, c, n, m)) for c in range(m)] for r in range(n)]
    row_tents = [sum(tent[r]) for r in range(n)]
    col_tents = [sum(tent[r][c] for r in range(n)) for c in range(m)]
    row_elig = [sum(elig[r]) for r in range(n)]
    col_elig = [sum(elig[r][c] for r in range(n)) for c in range(m)]
    v = {
        "cand_tree": [[cand[r][c] == "T" for c in range(m)] for r in range(n)],
        "cand_empty": [[cand[r][c] == "X" for c in range(m)] for r in range(n)],
        "cand_tent": tent,
        "cand_missing": [[cand[r][c] == "M" for c in range(m)] for r in range(n)],
        "puzzle_tree": ptree,
        "valid_cell": [[True] * m for _ in range(n)],
        "row_target": [[rows[r]] * m for r in range(n)],
        "col_target": [[cols[c] for c in range(m)] for _ in range(n)],
        "eligible": elig,
        "row_deficit": [[rows[r] - row_tents[r]] * m for r in range(n)],
        "col_deficit": [[cols[c] - col_tents[c] for c in range(m)] for _ in range(n)],
        "row_slack": [[row_elig[r] - rows[r]] * m for r in range(n)],
        "col_slack": [[col_elig[c] - cols[c] for c in range(m)] for _ in range(n)],
        "touching_tent": [[tent[r][c] and any(tent[a][b] for a, b in _ring(r, c, n, m)) for c in range(m)] for r in range(n)],
        "unmatched_tent": [[tent[r][c] and not any(ptree[a][b] for a, b in _orth(r, c, n, m)) for c in range(m)] for r in range(n)],
        "tree_mismatch": [[ptree[r][c] != (cand[r][c] == "T") for c in range(m)] for r in range(n)],
    }
    return v


def encode(framing: str, trees, rows, cols, cand, target=None):
    """(features [36 x C], label [36], loss mask [36], valid [36]) on the padded 6x6 grid."""
    n, m = len(trees), len(trees[0])
    vals = cell_values(trees, rows, cols, cand)
    chans = channels(framing)
    missing = [name for name, _ in chans if name not in vals]
    if missing:
        raise KeyError(f"package declares channels the code does not compute: {missing}")
    feats, label, mask, valid = [], [], [], []
    for r in range(N):
        for c in range(N):
            inside = r < n and c < m
            feats.append([metta_schema.scale(vals[name][r][c], kind) if inside else 0.0 for name, kind in chans])
            valid.append(1.0 if inside else 0.0)
            mask.append(1.0 if inside and trees[r][c] != "T" else 0.0)
            label.append(1.0 if (inside and target is not None and target[r][c] == "C") else 0.0)
    return feats, label, mask, valid


def decode(trees, tent_logits) -> list[list[str]]:
    n, m = len(trees), len(trees[0])
    return [["T" if trees[r][c] == "T" else ("C" if tent_logits[r * N + c] > 0 else "X") for c in range(m)] for r in range(n)]
