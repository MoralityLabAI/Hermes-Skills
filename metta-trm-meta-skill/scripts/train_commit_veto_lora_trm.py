from __future__ import annotations

import argparse
import csv
import gc
import json
import math
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset


FEATURE_NAMES = [
    "raw_ready_for_runtime",
    "repaired_ready_for_runtime",
    "raw_overall",
    "repaired_overall",
    "repaired_files",
    "repaired_manifest",
    "repaired_contract",
    "repaired_retrieval",
    "repaired_repair",
    "repaired_trainer_export",
    "repair_count_scaled",
    "verifier_disagreement",
    "missing_files_scaled",
    "error_count_scaled",
    "high_repair_boundary",
    "near_threshold_boundary",
]

DECISION_TO_ID = {"veto_or_collect_more_data": 0, "commit_repaired_package": 1}
ID_TO_DECISION = {value: key for key, value in DECISION_TO_ID.items()}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count


def append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"ts": utc_now(), **event}
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def state_features(state: dict[str, Any]) -> list[float]:
    repaired_scores = dict(state.get("repaired_scores") or {})
    raw_scores = dict(state.get("raw_scores") or {})
    repaired_overall = float(repaired_scores.get("overall", state.get("repaired_overall", 0.0)))
    repair_count = float(state.get("repair_count", 0.0))
    return [
        1.0 if state.get("raw_ready_for_runtime") else 0.0,
        1.0 if state.get("repaired_ready_for_runtime") else 0.0,
        float(raw_scores.get("overall", state.get("raw_overall", 0.0))),
        repaired_overall,
        float(repaired_scores.get("files", 1.0)),
        float(repaired_scores.get("manifest", 1.0)),
        float(repaired_scores.get("contract", repaired_overall)),
        float(repaired_scores.get("retrieval", repaired_overall)),
        float(repaired_scores.get("repair", repaired_overall)),
        float(repaired_scores.get("trainer_export", 1.0)),
        min(repair_count / 20.0, 1.0),
        1.0 if state.get("verifier_disagreement") else 0.0,
        min(float(state.get("missing_files_count", 0.0)) / 5.0, 1.0),
        min(float(state.get("error_count", 0.0)) / 5.0, 1.0),
        1.0 if repair_count >= 8 else 0.0,
        1.0 if abs(repaired_overall - 0.85) < 0.08 else 0.0,
    ]


class FeatureRows(Dataset[tuple[torch.Tensor, torch.Tensor, torch.Tensor, str]]):
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, str]:
        row = self.rows[index]
        features = torch.tensor(state_features(dict(row.get("state") or {})), dtype=torch.float32)
        label = DECISION_TO_ID[str((row.get("label") or {}).get("decision"))]
        weight = float(row.get("loss_weight", 1.0))
        return features, torch.tensor(label, dtype=torch.long), torch.tensor(weight, dtype=torch.float32), str(row.get("row_id", index))


class TinyTRM(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, recursive_steps: int) -> None:
        super().__init__()
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        self.transition = nn.Linear(hidden_dim, hidden_dim)
        self.norm = nn.LayerNorm(hidden_dim)
        self.decision_head = nn.Linear(hidden_dim, 2)
        self.recursive_steps = recursive_steps

    def hidden(self, x: torch.Tensor) -> torch.Tensor:
        h = torch.tanh(self.input_proj(x))
        for _ in range(self.recursive_steps):
            h = self.norm(h + torch.tanh(self.transition(h)))
        return h

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.decision_head(self.hidden(x))


class LoRATRM(nn.Module):
    def __init__(self, base: TinyTRM, rank: int, alpha: float = 1.0) -> None:
        super().__init__()
        self.base = base
        for param in self.base.parameters():
            param.requires_grad = False
        hidden_dim = base.transition.in_features
        self.rank = rank
        self.alpha = alpha
        self.trans_a = nn.Parameter(torch.empty(rank, hidden_dim))
        self.trans_b = nn.Parameter(torch.zeros(hidden_dim, rank))
        self.head_a = nn.Parameter(torch.empty(rank, hidden_dim))
        self.head_b = nn.Parameter(torch.zeros(2, rank))
        nn.init.kaiming_uniform_(self.trans_a, a=math.sqrt(5))
        nn.init.kaiming_uniform_(self.head_a, a=math.sqrt(5))

    def transition_delta(self, h: torch.Tensor, disabled_rank: int | None = None) -> torch.Tensor:
        a = self.trans_a
        b = self.trans_b
        if disabled_rank is not None:
            a = a.clone()
            b = b.clone()
            a[disabled_rank, :] = 0.0
            b[:, disabled_rank] = 0.0
        return ((h @ a.t()) @ b.t()) * (self.alpha / max(1, self.rank))

    def head_delta(self, h: torch.Tensor, disabled_rank: int | None = None) -> torch.Tensor:
        a = self.head_a
        b = self.head_b
        if disabled_rank is not None:
            a = a.clone()
            b = b.clone()
            a[disabled_rank, :] = 0.0
            b[:, disabled_rank] = 0.0
        return ((h @ a.t()) @ b.t()) * (self.alpha / max(1, self.rank))

    def forward(self, x: torch.Tensor, disabled_rank: int | None = None, zero_adapter: bool = False) -> torch.Tensor:
        h = torch.tanh(self.base.input_proj(x))
        for _ in range(self.base.recursive_steps):
            delta = 0.0 if zero_adapter else self.transition_delta(h, disabled_rank)
            h = self.base.norm(h + torch.tanh(self.base.transition(h) + delta))
        logits = self.base.decision_head(h)
        if not zero_adapter:
            logits = logits + self.head_delta(h, disabled_rank)
        return logits


@dataclass
class TrainConfig:
    epochs: int
    batch_size: int
    lr: float
    checkpoint_interval: int
    timeout_seconds: int
    false_commit_cost: float = 1.0
    false_veto_cost: float = 1.0
    use_cost_sensitive_loss: bool = False


def weighted_loss(logits: torch.Tensor, labels: torch.Tensor, weights: torch.Tensor, cfg: TrainConfig) -> torch.Tensor:
    losses = nn.functional.cross_entropy(logits, labels, reduction="none")
    if cfg.use_cost_sensitive_loss:
        label_costs = torch.where(
            labels == 0,
            torch.full_like(weights, float(cfg.false_commit_cost)),
            torch.full_like(weights, float(cfg.false_veto_cost)),
        )
        weights = weights * label_costs
    return (losses * weights).mean()


def prediction_metrics(labels: list[int], commit_probs: list[float], threshold: float, false_commit_cost: float = 3.0, false_veto_cost: float = 1.0) -> dict[str, float]:
    total = len(labels)
    correct = 0
    veto_total = 0
    commit_total = 0
    false_commit = 0
    false_veto = 0
    for label, commit_prob in zip(labels, commit_probs):
        pred = 1 if commit_prob >= threshold else 0
        correct += int(pred == label)
        if label == 0:
            veto_total += 1
            false_commit += int(pred == 1)
        else:
            commit_total += 1
            false_veto += int(pred == 0)
    weighted_cost = false_commit_cost * false_commit + false_veto_cost * false_veto
    max_cost = false_commit_cost * max(1, veto_total) + false_veto_cost * max(1, commit_total)
    return {
        "threshold": round(threshold, 4),
        "accuracy": round(correct / total, 6) if total else 0.0,
        "false_commit_rate": round(false_commit / veto_total, 6) if veto_total else 0.0,
        "false_veto_rate": round(false_veto / commit_total, 6) if commit_total else 0.0,
        "weighted_error_cost": round(weighted_cost / max_cost, 6),
        "false_commit_count": float(false_commit),
        "false_veto_count": float(false_veto),
        "count": float(total),
    }


def train_model(
    model: nn.Module,
    train_rows: list[dict[str, Any]],
    val_rows: list[dict[str, Any]],
    out_dir: Path,
    cfg: TrainConfig,
    device: torch.device,
    event_log: Path,
) -> dict[str, Any]:
    train_loader = DataLoader(FeatureRows(train_rows), batch_size=cfg.batch_size, shuffle=True)
    optimizer = torch.optim.AdamW((param for param in model.parameters() if param.requires_grad), lr=cfg.lr)
    model.to(device)
    start = time.time()
    step = 0
    best = {"val_accuracy": -1.0, "step": 0}
    for epoch in range(cfg.epochs):
        model.train()
        for features, labels, weights, _row_ids in train_loader:
            if time.time() - start > cfg.timeout_seconds:
                append_event(event_log, {"event": "abort", "reason": "timeout", "step": step})
                return {"status": "aborted", "reason": "timeout", "steps_completed": step, **best}
            features = features.to(device)
            labels = labels.to(device)
            weights = weights.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = weighted_loss(model(features), labels, weights, cfg)
            loss.backward()
            optimizer.step()
            step += 1
            if step % cfg.checkpoint_interval == 0:
                metrics = evaluate_model(model, val_rows, cfg.batch_size, device)
                append_event(event_log, {"event": "checkpoint", "step": step, "epoch": epoch, **metrics})
                if metrics["accuracy"] > best["val_accuracy"]:
                    best = {"val_accuracy": metrics["accuracy"], "step": step}
                    torch.save(model.state_dict(), out_dir / "best.pt")
    metrics = evaluate_model(model, val_rows, cfg.batch_size, device)
    if metrics["accuracy"] > best["val_accuracy"]:
        best = {"val_accuracy": metrics["accuracy"], "step": step}
    torch.save(model.state_dict(), out_dir / "final.pt")
    append_event(event_log, {"event": "complete", "step": step, **metrics})
    return {"status": "completed", "steps_completed": step, "final_metrics": metrics, **best}


@torch.no_grad()
def evaluate_model(
    model: nn.Module,
    rows: list[dict[str, Any]],
    batch_size: int,
    device: torch.device,
    disabled_rank: int | None = None,
    zero_adapter: bool = False,
) -> dict[str, float]:
    loader = DataLoader(FeatureRows(rows), batch_size=batch_size, shuffle=False)
    model.eval()
    total = 0
    correct = 0
    veto_total = 0
    commit_total = 0
    false_commit = 0
    false_veto = 0
    boundary_total = 0
    boundary_correct = 0
    for features, labels, _weights, _row_ids in loader:
        features = features.to(device)
        labels = labels.to(device)
        if isinstance(model, LoRATRM):
            logits = model(features, disabled_rank=disabled_rank, zero_adapter=zero_adapter)
        else:
            logits = model(features)
        pred = torch.argmax(logits, dim=-1)
        total += int(labels.numel())
        correct += int((pred == labels).sum().item())
        veto_mask = labels == 0
        commit_mask = labels == 1
        veto_total += int(veto_mask.sum().item())
        commit_total += int(commit_mask.sum().item())
        false_commit += int(((pred == 1) & veto_mask).sum().item())
        false_veto += int(((pred == 0) & commit_mask).sum().item())
        boundary_mask = features[:, FEATURE_NAMES.index("high_repair_boundary")] + features[:, FEATURE_NAMES.index("near_threshold_boundary")] + features[:, FEATURE_NAMES.index("verifier_disagreement")] > 0
        boundary_total += int(boundary_mask.sum().item())
        boundary_correct += int(((pred == labels) & boundary_mask).sum().item())
    return {
        "accuracy": round(correct / total, 6) if total else 0.0,
        "false_commit_rate": round(false_commit / veto_total, 6) if veto_total else 0.0,
        "false_veto_rate": round(false_veto / commit_total, 6) if commit_total else 0.0,
        "boundary_accuracy": round(boundary_correct / boundary_total, 6) if boundary_total else 0.0,
        "count": float(total),
    }


@torch.no_grad()
def collect_commit_probs(
    model: nn.Module,
    rows: list[dict[str, Any]],
    batch_size: int,
    device: torch.device,
    disabled_rank: int | None = None,
    zero_adapter: bool = False,
) -> tuple[list[int], list[float]]:
    loader = DataLoader(FeatureRows(rows), batch_size=batch_size, shuffle=False)
    model.eval()
    labels_out: list[int] = []
    probs_out: list[float] = []
    for features, labels, _weights, _row_ids in loader:
        features = features.to(device)
        if isinstance(model, LoRATRM):
            logits = model(features, disabled_rank=disabled_rank, zero_adapter=zero_adapter)
        else:
            logits = model(features)
        probs = torch.softmax(logits, dim=-1)[:, 1].detach().cpu().tolist()
        labels_out.extend(int(value) for value in labels.tolist())
        probs_out.extend(float(value) for value in probs)
    return labels_out, probs_out


def tune_threshold(
    model: nn.Module,
    val_rows: list[dict[str, Any]],
    batch_size: int,
    device: torch.device,
    false_commit_cost: float,
    false_veto_cost: float,
    max_false_veto_rate: float,
    min_accuracy: float | None = None,
) -> dict[str, float]:
    labels, probs = collect_commit_probs(model, val_rows, batch_size, device)
    candidates = [round(0.05 + index * 0.01, 4) for index in range(91)]
    scored = [prediction_metrics(labels, probs, threshold, false_commit_cost, false_veto_cost) for threshold in candidates]
    feasible = [
        row for row in scored
        if row["false_veto_rate"] <= max_false_veto_rate
        and (min_accuracy is None or row["accuracy"] >= min_accuracy)
    ]
    pool = feasible if feasible else scored
    return min(pool, key=lambda row: (row["false_commit_rate"], row["weighted_error_cost"], -row["accuracy"]))


def threshold_frontier(
    model: nn.Module,
    rows: list[dict[str, Any]],
    batch_size: int,
    device: torch.device,
    false_commit_cost: float,
    false_veto_cost: float,
) -> list[dict[str, float]]:
    labels, probs = collect_commit_probs(model, rows, batch_size, device)
    return [
        prediction_metrics(labels, probs, round(0.05 + index * 0.01, 4), false_commit_cost, false_veto_cost)
        for index in range(91)
    ]


def best_frontier_under_budget(frontier: list[dict[str, float]], base_metrics: dict[str, float], false_veto_budget: float) -> dict[str, float]:
    max_false_veto = float(base_metrics["false_veto_rate"]) + false_veto_budget
    min_accuracy = float(base_metrics["accuracy"]) - 0.01
    feasible = [
        row for row in frontier
        if row["false_veto_rate"] <= max_false_veto and row["accuracy"] >= min_accuracy
    ]
    pool = feasible if feasible else frontier
    return min(pool, key=lambda row: (row["false_commit_rate"], row["weighted_error_cost"], -row["accuracy"]))


def evaluate_at_threshold(
    model: nn.Module,
    rows: list[dict[str, Any]],
    batch_size: int,
    device: torch.device,
    threshold: float,
    false_commit_cost: float,
    false_veto_cost: float,
) -> dict[str, float]:
    labels, probs = collect_commit_probs(model, rows, batch_size, device)
    return prediction_metrics(labels, probs, threshold, false_commit_cost, false_veto_cost)


def adapter_param_count(model: LoRATRM) -> int:
    return sum(param.numel() for name, param in model.named_parameters() if param.requires_grad and not name.startswith("base."))


def total_param_count(model: nn.Module) -> int:
    return sum(param.numel() for param in model.parameters())


def audit_lora(model: LoRATRM, rows: list[dict[str, Any]], batch_size: int, device: torch.device) -> dict[str, Any]:
    full = evaluate_model(model, rows, batch_size, device)
    zeroed = evaluate_model(model, rows, batch_size, device, zero_adapter=True)
    rank_ablations = []
    for rank_index in range(model.rank):
        metrics = evaluate_model(model, rows, batch_size, device, disabled_rank=rank_index)
        rank_ablations.append(
            {
                "rank_index": rank_index,
                "metrics": metrics,
                "accuracy_drop": round(full["accuracy"] - metrics["accuracy"], 6),
                "false_commit_delta": round(metrics["false_commit_rate"] - full["false_commit_rate"], 6),
            }
        )
    with torch.no_grad():
        trans_delta = model.trans_b @ model.trans_a
        singular_values = torch.linalg.svdvals(trans_delta.detach().cpu()).tolist()
    return {
        "full": full,
        "zero_adapter": zeroed,
        "zero_adapter_accuracy_drop": round(full["accuracy"] - zeroed["accuracy"], 6),
        "rank_ablations": rank_ablations,
        "transition_delta_top_singular_values": [round(float(value), 8) for value in singular_values[: min(8, len(singular_values))]],
        "adapter_param_count": adapter_param_count(model),
        "total_param_count_with_base": total_param_count(model),
    }


def load_rows(path: Path, max_rows: int | None = None) -> list[dict[str, Any]]:
    rows = read_jsonl(path)
    return rows[:max_rows] if max_rows else rows


def write_metrics_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_frontier_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = ["model", "rank", "split", "threshold", "accuracy", "false_commit_rate", "false_veto_rate", "weighted_error_cost", "false_commit_count", "false_veto_count", "count"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def parse_ranks(value: str) -> list[int]:
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train tiny LoRA adapters for commit/veto TRM feature steering.")
    parser.add_argument("--train", required=True)
    parser.add_argument("--val", required=True)
    parser.add_argument("--heldout", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--hidden-dim", type=int, default=2048)
    parser.add_argument("--recursive-steps", type=int, default=4)
    parser.add_argument("--base-epochs", type=int, default=8)
    parser.add_argument("--lora-epochs", type=int, default=6)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=2e-3)
    parser.add_argument("--lora-lr", type=float, default=5e-3)
    parser.add_argument("--ranks", default="1,2,4")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    parser.add_argument("--max-train-rows", type=int)
    parser.add_argument("--max-val-rows", type=int)
    parser.add_argument("--max-heldout-rows", type=int)
    parser.add_argument("--checkpoint-interval", type=int, default=250)
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    parser.add_argument("--ram-cap-mb", type=int, default=2048)
    parser.add_argument("--cpu-pct", type=int, default=50)
    parser.add_argument("--io-mb-s", type=int, default=50)
    parser.add_argument("--false-commit-cost", type=float, default=3.0)
    parser.add_argument("--false-veto-cost", type=float, default=1.0)
    parser.add_argument("--max-false-veto-rate", type=float, default=0.08)
    parser.add_argument("--false-veto-budget", type=float, default=0.025)
    parser.add_argument("--use-cost-sensitive-loss", action="store_true")
    parser.add_argument("--cost-sensitive-lora-only", action="store_true")
    parser.add_argument("--seed", type=int, default=20260506)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    torch.manual_seed(args.seed)
    torch.set_num_threads(max(1, int((os.cpu_count() or 2) * args.cpu_pct / 100)))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    event_log = out_dir / "events.jsonl"
    append_event(
        event_log,
        {
            "event": "start",
            "caps": {"ram_mb": args.ram_cap_mb, "cpu_pct": args.cpu_pct, "io_mb_s": args.io_mb_s},
            "hard_cap_enforced": False,
            "hard_cap_note": "This trainer records caps and limits torch CPU threads; run under WSL ulimit or Windows Job Object wrapper for OS-enforced caps.",
        },
    )
    train_rows = load_rows(Path(args.train), args.max_train_rows)
    val_rows = load_rows(Path(args.val), args.max_val_rows)
    heldout_rows = load_rows(Path(args.heldout), args.max_heldout_rows)
    device = torch.device("cuda" if args.device == "cuda" and torch.cuda.is_available() else "cpu")
    base_dir = out_dir / "base_trm"
    base_dir.mkdir(exist_ok=True)
    base = TinyTRM(len(FEATURE_NAMES), args.hidden_dim, args.recursive_steps)
    base_summary = train_model(
        base,
        train_rows,
        val_rows,
        base_dir,
        TrainConfig(
            args.base_epochs,
            args.batch_size,
            args.lr,
            args.checkpoint_interval,
            args.timeout_seconds,
            args.false_commit_cost,
            args.false_veto_cost,
            args.use_cost_sensitive_loss and not args.cost_sensitive_lora_only,
        ),
        device,
        event_log,
    )
    base_metrics = {
        "val": evaluate_model(base, val_rows, args.batch_size, device),
        "heldout": evaluate_model(base, heldout_rows, args.batch_size, device),
    }
    base_threshold = tune_threshold(
        base,
        val_rows,
        args.batch_size,
        device,
        args.false_commit_cost,
        args.false_veto_cost,
        args.max_false_veto_rate,
        min_accuracy=max(0.0, base_metrics["val"]["accuracy"] - 0.01),
    )
    base_tuned_metrics = {
        "val": base_threshold,
        "heldout": evaluate_at_threshold(base, heldout_rows, args.batch_size, device, base_threshold["threshold"], args.false_commit_cost, args.false_veto_cost),
    }
    torch.save(base.state_dict(), base_dir / "base_final.pt")
    metric_rows: list[dict[str, Any]] = [
        {"model": "base_trm", "rank": 0, "decision_rule": "argmax", "split": split, **metrics}
        for split, metrics in base_metrics.items()
    ]
    metric_rows.extend(
        {"model": "base_trm", "rank": 0, "decision_rule": "tuned_threshold", "split": split, **metrics}
        for split, metrics in base_tuned_metrics.items()
    )
    frontier_rows: list[dict[str, Any]] = []
    base_heldout_frontier = threshold_frontier(base, heldout_rows, args.batch_size, device, args.false_commit_cost, args.false_veto_cost)
    base_budget_best = best_frontier_under_budget(base_heldout_frontier, base_metrics["heldout"], args.false_veto_budget)
    frontier_rows.extend({"model": "base_trm", "rank": 0, "split": "heldout", **row} for row in base_heldout_frontier)
    lora_summaries: dict[str, Any] = {}
    for rank in parse_ranks(args.ranks):
        lora_dir = out_dir / f"lora_rank_{rank}"
        lora_dir.mkdir(exist_ok=True)
        frozen_base = TinyTRM(len(FEATURE_NAMES), args.hidden_dim, args.recursive_steps)
        frozen_base.load_state_dict(base.state_dict())
        lora = LoRATRM(frozen_base, rank=rank)
        lora_summary = train_model(
            lora,
            train_rows,
            val_rows,
            lora_dir,
            TrainConfig(
                args.lora_epochs,
                args.batch_size,
                args.lora_lr,
                args.checkpoint_interval,
                args.timeout_seconds,
            args.false_commit_cost,
            args.false_veto_cost,
            args.use_cost_sensitive_loss,
            ),
            device,
            event_log,
        )
        val_metrics = evaluate_model(lora, val_rows, args.batch_size, device)
        heldout_metrics = evaluate_model(lora, heldout_rows, args.batch_size, device)
        threshold = tune_threshold(
            lora,
            val_rows,
            args.batch_size,
            device,
            args.false_commit_cost,
            args.false_veto_cost,
            args.max_false_veto_rate,
            min_accuracy=max(0.0, val_metrics["accuracy"] - 0.01),
        )
        tuned_metrics = {
            "val": threshold,
            "heldout": evaluate_at_threshold(lora, heldout_rows, args.batch_size, device, threshold["threshold"], args.false_commit_cost, args.false_veto_cost),
        }
        heldout_frontier = threshold_frontier(lora, heldout_rows, args.batch_size, device, args.false_commit_cost, args.false_veto_cost)
        budget_best = best_frontier_under_budget(heldout_frontier, base_metrics["heldout"], args.false_veto_budget)
        frontier_rows.extend({"model": "lora_trm", "rank": rank, "split": "heldout", **row} for row in heldout_frontier)
        audit = audit_lora(lora, heldout_rows, args.batch_size, device)
        write_json(lora_dir / "vpd_style_audit.json", audit)
        write_json(lora_dir / "threshold_tuning.json", {"selected": threshold, "heldout": tuned_metrics["heldout"], "heldout_budget_best": budget_best})
        torch.save(lora.state_dict(), lora_dir / "lora_final.pt")
        lora_summaries[str(rank)] = {
            "train_summary": lora_summary,
            "val": val_metrics,
            "heldout": heldout_metrics,
            "threshold_tuning": tuned_metrics,
            "heldout_budget_best": budget_best,
            "audit": audit,
        }
        metric_rows.append({"model": "lora_trm", "rank": rank, "decision_rule": "argmax", "split": "val", **val_metrics})
        metric_rows.append({"model": "lora_trm", "rank": rank, "decision_rule": "argmax", "split": "heldout", **heldout_metrics})
        metric_rows.append({"model": "lora_trm", "rank": rank, "decision_rule": "tuned_threshold", "split": "val", **tuned_metrics["val"]})
        metric_rows.append({"model": "lora_trm", "rank": rank, "decision_rule": "tuned_threshold", "split": "heldout", **tuned_metrics["heldout"]})
        metric_rows.append({"model": "lora_trm", "rank": rank, "decision_rule": "heldout_frontier_budget_oracle", "split": "heldout", **budget_best})
        metric_rows.append({"model": "lora_zero_adapter", "rank": rank, "decision_rule": "argmax", "split": "heldout", **audit["zero_adapter"]})
    write_metrics_csv(out_dir / "metrics.csv", metric_rows)
    write_frontier_csv(out_dir / "threshold_frontier_heldout.csv", frontier_rows)
    summary = {
        "generated_at_utc": utc_now(),
        "status": "completed",
        "feature": "commit_veto_threshold",
        "feature_names": FEATURE_NAMES,
        "device": str(device),
        "torch_version": torch.__version__,
        "row_counts": {"train": len(train_rows), "val": len(val_rows), "heldout": len(heldout_rows)},
        "model_config": {"hidden_dim": args.hidden_dim, "recursive_steps": args.recursive_steps, "base_param_count": total_param_count(base)},
        "base_summary": base_summary,
        "base_metrics": base_metrics,
        "base_threshold_tuning": base_tuned_metrics,
        "base_heldout_budget_best": base_budget_best,
        "lora_summaries": lora_summaries,
        "metrics_csv": str(out_dir / "metrics.csv"),
        "threshold_frontier_csv": str(out_dir / "threshold_frontier_heldout.csv"),
        "event_log": str(event_log),
        "caps": {"ram_mb": args.ram_cap_mb, "cpu_pct": args.cpu_pct, "io_mb_s": args.io_mb_s, "hard_cap_enforced": False},
        "cost_model": {
            "false_commit_cost": args.false_commit_cost,
            "false_veto_cost": args.false_veto_cost,
            "max_false_veto_rate": args.max_false_veto_rate,
            "false_veto_budget": args.false_veto_budget,
            "use_cost_sensitive_loss": args.use_cost_sensitive_loss,
            "cost_sensitive_lora_only": args.cost_sensitive_lora_only,
        },
    }
    write_json(out_dir / "summary.json", summary)
    write_jsonl(
        out_dir / "next_row_recommendations.jsonl",
        [
            {"recommendation": "more_false_commit_boundary_rows", "priority": "high"},
            {"recommendation": "more_verifier_disagreement_rows", "priority": "high"},
            {"recommendation": "more_safe_commit_rows", "priority": "medium"},
        ],
    )
    if device.type == "cuda":
        torch.cuda.synchronize()
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    gc.collect()
    print(out_dir)
    print(json.dumps({"base_heldout": base_metrics["heldout"], "metrics_csv": str(out_dir / "metrics.csv")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
