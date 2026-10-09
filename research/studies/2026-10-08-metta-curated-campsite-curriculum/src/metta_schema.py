"""Compile the curriculum MeTTa package into a feature schema.

The package is the single source of the typed state: which atoms a row carries, in what order, and
how each is scaled. The compiler only reads the declarations; atom values are computed in Python by
`campsite.atom_values`. An atom the computer does not implement is an error, so the package cannot
silently drift from the code.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "metta" / "campsite_curriculum.metta"
FEATURE_KINDS = ("verifier-atom", "count-atom", "shape-atom")
SCALES = ("bool", "fraction", "signed3", "scaled3", "scaled6")


@dataclass(frozen=True)
class Atom:
    kind: str
    name: str
    scale: str


@dataclass(frozen=True)
class Schema:
    env: str
    atoms: tuple[Atom, ...]
    operators: tuple[tuple[str, str, str], ...]  # (name, code, required gate)
    menu: tuple[str, ...]
    buckets: tuple[str, ...]

    @property
    def feature_names(self) -> list[str]:
        return [a.name for a in self.atoms]


def _top_level(text: str) -> list[str]:
    lines = []
    for raw in text.splitlines():
        line = raw.split(";;", 1)[0].strip()
        if line:
            if not (line.startswith("(") and line.endswith(")")):
                raise ValueError(f"not one top-level atom per line: {raw!r}")
            lines.append(line)
    return lines


@lru_cache(maxsize=None)
def load(path: Path = PACKAGE) -> Schema:
    env, atoms, operators, menu, buckets = "", [], [], (), []
    for line in _top_level(path.read_text(encoding="utf-8")):
        head = line[1:].split(None, 1)[0]
        if head in FEATURE_KINDS:
            m = re.fullmatch(r"\((\S+) (\S+) (\S+)\)", line)
            if not m or m.group(3) not in SCALES:
                raise ValueError(f"bad feature atom: {line}")
            atoms.append(Atom(m.group(1), m.group(2), m.group(3)))
        elif head == "repair-operator":
            m = re.fullmatch(r"\(repair-operator (\S+) (\S+) \(requires (\S+)\)\)", line)
            if not m:
                raise ValueError(f"bad operator atom: {line}")
            operators.append((m.group(1), m.group(2), m.group(3)))
        elif head == "action-menu":
            menu = tuple(line[1:-1].split()[1:])
        elif head == "bucket":
            buckets.append(line[1:-1].split()[1])
        elif head == "curriculum-env":
            env = line[1:-1].split()[1]
    names = [a.name for a in atoms]
    if len(set(names)) != len(names):
        raise ValueError("duplicate feature atoms")
    if not menu or menu[0] != "commit" or menu[-1] != "reject":
        raise ValueError("action menu must start with commit and end with reject")
    return Schema(env, tuple(atoms), tuple(operators), menu, tuple(buckets))


def scale(value: float, kind: str) -> float:
    if kind == "bool":
        return 1.0 if value else 0.0
    if kind == "fraction":
        return max(0.0, min(1.0, float(value)))
    if kind == "signed3":
        return max(-1.0, min(1.0, float(value) / 3.0))
    if kind == "scaled3":
        return max(0.0, min(1.0, float(value) / 3.0))
    if kind == "scaled6":
        return max(0.0, min(1.0, float(value) / 6.0))
    raise ValueError(kind)
