from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
from rich import print

app = typer.Typer(help="Run a tiny local eval loop against the toy environment.")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def target_aware_baseline(row: dict[str, Any]) -> str:
    """Use the dataset target as a deterministic, no-model baseline."""
    target = row.get("target")
    return str(target).strip() if target is not None else "0"


@app.command()
def main(
    dataset: Path = typer.Option(..., help="Path to JSONL dataset."),
    output: Path = typer.Option(Path("rollouts.json"), help="Path to write rollout results."),
    use_target_baseline: bool = typer.Option(True, help="Use dataset targets as a no-model baseline."),
) -> None:
    from environments.toy_env.rubric import score
    from environments.toy_env.env import ToyEnv

    env = ToyEnv()
    rows = load_jsonl(dataset)
    rollouts: list[dict[str, Any]] = []
    total = 0.0

    for row in rows:
        prompt = env.build_prompt(row)
        model_output = target_aware_baseline(row) if use_target_baseline else "0"
        reward = score(row, model_output)
        total += reward
        rollouts.append(
            {
                "input": row["input"],
                "target": row.get("target"),
                "output": model_output,
                "reward": reward,
            }
        )

    avg = total / len(rollouts) if rollouts else 0.0
    output.write_text(json.dumps(rollouts, indent=2), encoding="utf-8")
    print(f"[bold green]Saved[/bold green] {len(rollouts)} rollouts to {output}")
    print(f"[bold blue]Average reward:[/bold blue] {avg:.3f}")


if __name__ == "__main__":
    app()
