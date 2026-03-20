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


def fake_model(prompt: str) -> str:
    """Very dumb baseline model.

    It tries to return the last token if numeric; otherwise returns 0.
    This is purely for sanity checking the environment and rollout format.
    """
    tokens = prompt.strip().split()
    last = tokens[-1] if tokens else "0"
    return last if last.isdigit() else "0"


@app.command()
def main(
    dataset: Path = typer.Option(..., help="Path to JSONL dataset."),
    output: Path = typer.Option(Path("rollouts.json"), help="Path to write rollout results."),
) -> None:
    from environments.toy_env.rubric import score
    from environments.toy_env.env import ToyEnv

    env = ToyEnv()
    rows = load_jsonl(dataset)
    rollouts: list[dict[str, Any]] = []
    total = 0.0

    for row in rows:
        prompt = env.build_prompt(row)
        model_output = fake_model(prompt)
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
