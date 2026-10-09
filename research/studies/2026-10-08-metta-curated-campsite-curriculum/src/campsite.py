"""Campsite environment layer: puzzles, verifier, Hermes-Skills repair operators, candidates, and
the typed (MeTTa-declared) and raw state of a candidate."""

from __future__ import annotations

import itertools
import random
from functools import lru_cache

from common import git_show, head_module, hermes_lite_campsite
import metta_schema

POOLS = {  # name: (puzzles, 6x6 share, seed)
    "shots": (4, 0, 20261107),
    "train": (300, 60, 20261108),
    "val": (60, 12, 20261109),
    "test": (150, 30, 20261110),
    "train2": (700, 140, 20261111),  # SPEC-R: extra training puzzles for the repair TRM (disjoint from all above)
    "test2": (150, 30, 20261112),    # SPEC-R addendum R-A3: fresh confirmation test pool
}
REPAIR_SCRIPT = "research/scripts/run_intellect3_camp_gate_micro_env.py"
DEFECTS = ("correct", "drop_tent", "extra_tent", "move_in_row", "move_any", "swap_rect", "tree_mutation", "bad_shape")
MAX_N = 6
RULES = (
    "Campsite puzzle. The grid shows trees (T) and empty cells (X). Place exactly one tent (C) for every tree, in a "
    "cell orthogonally adjacent to its tree, so that every tree is paired with its own adjacent tent. Tents never touch "
    "each other, not even diagonally. The number of tents in each row and each column must equal the numbers given. "
    "Trees stay where they are."
)


@lru_cache(maxsize=None)
def skills():
    return head_module(REPAIR_SCRIPT, "hermes_skills_camp_gate_micro_env")


def camp():
    return hermes_lite_campsite()


# ---------------------------------------------------------------------------- puzzles


def _check_public(task, gold) -> None:
    """The projections read the expected grid for shape and T/C counts only; those must be public."""
    s = skills()
    if s.row_signature(gold, "C") != task.row_constraints or s.col_signature(gold, "C") != task.col_constraints:
        raise RuntimeError(f"{task.task_id}: solver grid C counts differ from the constraints")
    if s.row_signature(gold, "T") != s.row_signature(task.grid, "T") or s.col_signature(gold, "T") != s.col_signature(task.grid, "T"):
        raise RuntimeError(f"{task.task_id}: solver grid T counts differ from the puzzle")


@lru_cache(maxsize=None)
def puzzles(pool: str) -> tuple:
    """(task, solver grid) pairs. Pools are disjoint by puzzle hash: a later pool drops any puzzle an
    earlier pool holds. The solver grid is one valid solution, used only for its public counts."""
    count, shift, seed = POOLS[pool]
    earlier = list(POOLS)[: list(POOLS).index(pool)]
    taken = {task.hash for p in earlier for task, _ in puzzles(p)}
    out = []
    for task in camp().generate_unseen_tasks(count, seed=seed, include_size_shift=shift):
        if task.hash in taken:
            continue
        gold = camp().solve_candidates(task, max_candidates=1)[0][0]
        _check_public(task, gold)
        out.append((task, gold))
    return tuple(out)


def task_by_id(pool: str):
    return {task.task_id: (task, gold) for task, gold in puzzles(pool)}


# ---------------------------------------------------------------------------- verifier and repair


def verify(task, grid) -> dict:
    return camp().verify_candidate(task, grid)


def passes(task, grid) -> bool:
    return grid is not None and bool(verify(task, grid)["official_pass"])


def rectangular(task, grid) -> bool:
    n, m = len(task.grid), len(task.grid[0])
    return isinstance(grid, list) and len(grid) == n and all(isinstance(r, list) and len(r) == m for r in grid)


def repair(task, gold, grid, operator: str):
    """A Hermes-Skills projection of the candidate, or None when its precondition (shape) fails."""
    if not rectangular(task, grid) or any(c not in ("T", "X", "C") for row in grid for c in row):
        return None
    fn = skills().c_only_projection if operator == "c_repair" else skills().dual_signature_projection
    return fn(grid, gold)


def operators() -> tuple[str, ...]:
    return tuple(name for name, _, _ in metta_schema.load().operators)


# ---------------------------------------------------------------------------- candidates


def _cells(grid, symbol):
    return [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == symbol]


def _near_tree(grid, r, c):
    n, m = len(grid), len(grid[0])
    return any(0 <= r + dr < n and 0 <= c + dc < m and grid[r + dr][c + dc] == "T" for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))


def synthetic(task, gold, kind: str, rng: random.Random):
    """The jev-qwen U4 defect types, ported."""
    g = [list(row) for row in gold]
    n, m = len(g), len(g[0])
    tents = _cells(g, "C")
    free = [(r, c) for r, c in _cells(g, "X") if _near_tree(task.grid, r, c)]
    if kind == "correct":
        return g
    if kind == "drop_tent":
        r, c = rng.choice(tents)
        g[r][c] = "X"
    elif kind == "extra_tent":
        if not free:
            return None
        r, c = rng.choice(free)
        g[r][c] = "C"
    elif kind == "move_in_row":
        r, c = rng.choice(tents)
        options = [(r, cc) for cc in range(m) if g[r][cc] == "X"]
        if not options:
            return None
        rr, cc = rng.choice(options)
        g[r][c], g[rr][cc] = "X", "C"
    elif kind == "move_any":
        r, c = rng.choice(tents)
        options = [(rr, cc) for rr, cc in free if rr != r and cc != c]
        if not options:
            return None
        rr, cc = rng.choice(options)
        g[r][c], g[rr][cc] = "X", "C"
    elif kind == "swap_rect":
        pairs = [(a, b) for a, b in itertools.combinations(tents, 2)
                 if a[0] != b[0] and a[1] != b[1] and g[a[0]][b[1]] == "X" and g[b[0]][a[1]] == "X"]
        if not pairs:
            return None
        (r1, c1), (r2, c2) = rng.choice(pairs)
        g[r1][c1], g[r2][c2], g[r1][c2], g[r2][c1] = "X", "X", "C", "C"
    elif kind == "tree_mutation":
        r, c = rng.choice(_cells(g, "T"))
        g[r][c] = "X"
    elif kind == "bad_shape":
        r = rng.randrange(n)
        g[r] = g[r][:-1]
    else:
        raise ValueError(kind)
    return g


def grid_text(grid) -> str:
    return "\n".join(" ".join(row) for row in grid)


def puzzle_text(task) -> str:
    return "\n".join(["Puzzle:", grid_text(task.grid), f"Row tents: {' '.join(map(str, task.row_constraints))}",
                      f"Column tents: {' '.join(map(str, task.col_constraints))}"])


def propose_prompt(task) -> str:
    lines = [RULES + " Solve the puzzle: write the completed grid with one tent (C) for every tree, one row per line, "
             "cells separated by spaces.", ""]
    for shot, gold in puzzles("shots")[:3]:
        lines += [puzzle_text(shot), "Solution:", grid_text(gold), ""]
    return "\n".join(lines + [puzzle_text(task), "Solution:"]) + "\n"


def parse_grid(text: str, n_rows: int):
    """The jev-qwen U4/U5 parser: leading lines of T/X/C cells, up to n_rows."""
    rows = []
    for line in text.split("\n"):
        if not line.strip():
            if rows:
                break
            continue
        cells = line.split()
        if any(cell not in ("T", "X", "C") for cell in cells):
            break
        rows.append(cells)
        if len(rows) == n_rows:
            break
    return rows or None


# ---------------------------------------------------------------------------- typed (MeTTa) and raw state


def _counts(task, grid):
    n, m = len(task.grid), len(task.grid[0])
    rows = [sum(c == "C" for c in row) for row in grid]
    cols = [sum(grid[r][c] == "C" for r in range(n)) for c in range(m)]
    return rows, cols


def atom_values(task, grid) -> dict[str, float]:
    """Unscaled value of every atom the package may declare, for one candidate."""
    v = verify(task, grid) if grid is not None else {"gates": {}, "failed_gates": list(range(7))}
    gates = {g: bool(v["gates"].get(g, False)) for g in
             ("syntax_valid", "shape_match", "trees_unchanged", "row_counts_match", "col_counts_match",
              "no_tent_touching", "perfect_tree_matching")}
    n, m = len(task.grid), len(task.grid[0])
    trees = max(1, sum(c == "T" for row in task.grid for c in row))
    total_target = sum(task.row_constraints)
    tents_in = sum(c == "C" for row in (grid or []) for c in row)
    out = dict(gates)
    out.update({"tent_surplus": tents_in - total_target, "failed_gates": len(v["failed_gates"]) / 7.0,
                "grid_rows": n, "grid_cols": m})
    if gates["shape_match"] and gates["syntax_valid"]:
        rows, cols = _counts(task, grid)
        out["rows_off"] = sum(a != b for a, b in zip(rows, task.row_constraints)) / n
        out["cols_off"] = sum(a != b for a, b in zip(cols, task.col_constraints)) / m
        out["moved_trees"] = sum((task.grid[r][c] == "T") != (grid[r][c] == "T") for r in range(n) for c in range(m)) / trees
        tents = _cells(grid, "C")
        out["touching_pairs"] = sum(1 for (a, b), (c, d) in itertools.combinations(tents, 2) if max(abs(a - c), abs(b - d)) == 1)
        out["unmatched_tents"] = (sum(1 for r, c in tents if not _near_tree(grid, r, c)) / len(tents)) if tents else 0.0
    else:
        out.update({"rows_off": 1.0, "cols_off": 1.0, "moved_trees": 1.0, "touching_pairs": 3.0, "unmatched_tents": 1.0})
    return out


def typed_features(task, grid) -> list[float]:
    values = atom_values(task, grid)
    schema = metta_schema.load()
    missing = [a.name for a in schema.atoms if a.name not in values]
    if missing:
        raise KeyError(f"package declares atoms the code does not compute: {missing}")
    return [metta_schema.scale(values[a.name], a.scale) for a in schema.atoms]


def raw_features(task, grid) -> list[float]:
    """Padded one-hot cells, no derived atom: candidate (T, X, C, missing), puzzle trees, valid mask,
    row and column targets."""
    n, m = len(task.grid), len(task.grid[0])
    cand, trees, mask = [], [], []
    for r in range(MAX_N):
        for c in range(MAX_N):
            inside = r < n and c < m
            cell = None
            if grid is not None and r < len(grid) and isinstance(grid[r], list) and c < len(grid[r]):
                cell = grid[r][c]
            cand += [float(cell == "T"), float(cell == "X"), float(cell == "C"), float(cell not in ("T", "X", "C"))]
            trees.append(float(inside and task.grid[r][c] == "T"))
            mask.append(float(inside))
    rows = [task.row_constraints[r] / 3.0 if r < n else 0.0 for r in range(MAX_N)]
    cols = [task.col_constraints[c] / 3.0 if c < m else 0.0 for c in range(MAX_N)]
    return cand + trees + mask + rows + cols


def source_hash() -> str:
    import hashlib

    return hashlib.sha256(git_show(REPAIR_SCRIPT).encode("utf-8")).hexdigest()[:16]
