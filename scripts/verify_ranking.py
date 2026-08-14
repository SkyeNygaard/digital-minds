#!/usr/bin/env python3
"""Verify a saved preference-foresight run without making model calls."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = ROOT / "parallel_frontier/20_preference_foresight/results/ranking_v2"


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def cell_key(row: dict) -> tuple:
    return tuple(row[k] for k in (
        "pair_id", "dose", "arm", "a_label", "presentation_order", "replicate"
    ))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(run_dir: Path) -> dict:
    plan = rows(run_dir / "planned_grid.jsonl")
    choices = rows(run_dir / "choices.jsonl")
    forecasts = rows(run_dir / "forecasts.jsonl")
    summary = json.loads((run_dir / "summary.json").read_text())

    plan_by_key = {cell_key(r): r for r in plan}
    choices_by_key = {cell_key(r): r for r in choices}
    planned_keys = set(plan_by_key)
    choice_keys = set(choices_by_key)

    count_key = lambda r: (r["pair_id"], r["dose"], r["arm"], r["a_label"],
                           r["presentation_order"])
    planned_counts = Counter(count_key(r) for r in plan)
    counts = Counter(count_key(r) for r in choices)
    forecast_keys = {(r["pair_id"], r["dose"]) for r in forecasts}
    expected_blocks = {
        (pair_id, dose, arm, label, order)
        for pair_id, dose in forecast_keys
        for arm in ("performed_preferred", "performed_other")
        for label in ("Q", "K")
        for order in ("QK", "KQ")
    }
    replicates = summary["replicates"]
    balanced = bool(expected_blocks) and all(
        set(block_counts) == expected_blocks
        and all(n == replicates for n in block_counts.values())
        for block_counts in (planned_counts, counts)
    )

    seed_matches = planned_keys == choice_keys and all(
        plan_by_key[key].get("seed") is not None
        and plan_by_key[key]["seed"] == choices_by_key[key].get("seed")
        for key in planned_keys
    )

    by_arm: dict[tuple, dict[str, list[bool]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in choices:
        by_arm[(row["pair_id"], row["dose"])][row["arm"]].append(
            bool(row["chose_preferred"])
        )
    forecast_by_key = {(r["pair_id"], r["dose"]): r for r in forecasts}
    observations = []
    for key, arms in by_arm.items():
        if set(arms) != {"performed_preferred", "performed_other"}:
            continue
        realized = (
            sum(arms["performed_preferred"]) / len(arms["performed_preferred"])
            - sum(arms["performed_other"]) / len(arms["performed_other"])
        )
        predicted = forecast_by_key[key]["predicted_change"]
        observations.append((predicted, realized, predicted - realized))

    mean_predicted = sum(x[0] for x in observations) / len(observations)
    mean_realized = sum(x[1] for x in observations) / len(observations)
    mean_error = sum(x[2] for x in observations) / len(observations)
    model_mse = sum(x[2] ** 2 for x in observations) / len(observations)
    no_shift_mse = sum(x[1] ** 2 for x in observations) / len(observations)
    fixed_mse = sum((1.0 - x[1]) ** 2 for x in observations) / len(observations)
    headline = summary["headline"]

    checks = {
        "plan_keys_unique": len(plan_by_key) == len(plan),
        "choice_keys_unique": len(choices_by_key) == len(choices),
        "grid_complete": planned_keys == choice_keys,
        "grid_balanced": balanced,
        "seed_mapping_matches_plan": seed_matches,
        "raw_choice_replies_present": all(r.get("raw") for r in choices),
        "raw_forecast_replies_present": all(r.get("raw") for r in forecasts),
        "summary_observation_count_matches": (
            headline["n_observations"] == len(observations)
        ),
        "summary_mean_predicted_matches": abs(
            headline["mean_predicted_change"] - mean_predicted
        ) < 1e-12,
        "summary_mean_realized_matches": abs(
            headline["mean_realized_change"] - mean_realized
        ) < 1e-12,
        "summary_mean_error_matches": abs(headline["mean_error"] - mean_error) < 1e-12,
        "summary_model_mse_matches": abs(
            headline["model_forecast_mse"] - model_mse
        ) < 1e-12,
        "summary_no_shift_mse_matches": abs(
            headline["no_shift_mse"] - no_shift_mse
        ) < 1e-12,
        "summary_fixed_mse_matches": abs(
            headline["fixed_full_repeat_mse"] - fixed_mse
        ) < 1e-12,
        "treatment_cells_at_least_95pct_correct": (
            sum(bool(r["treatment_all_correct"]) for r in choices) / len(choices)
            >= 0.95
        ),
        "post_tasks_at_least_95pct_correct": (
            sum(bool(r["post_task_correct"]) for r in choices) / len(choices)
            >= 0.95
        ),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "n_planned_cells": len(plan),
        "n_recorded_cells": len(choices),
        "n_forecasts": len(forecasts),
        "recomputed": {
            "mean_predicted_change": mean_predicted,
            "mean_realized_change": mean_realized,
            "mean_error": mean_error,
            "model_forecast_mse": model_mse,
            "no_shift_mse": no_shift_mse,
            "fixed_full_repeat_mse": fixed_mse,
        },
        "verifier_sha256": sha256(Path(__file__)),
        "provenance_note": (
            "This is an offline check of saved artifacts. The run loaded an "
            "intermediate uncommitted runner revision whose exact source hash was "
            "not captured; current experiment source may differ."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path, nargs="?", default=DEFAULT_RUN)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = verify(args.run_dir)
    text = json.dumps(result, indent=2) + "\n"
    if args.write:
        (args.run_dir / "verification.json").write_text(text)
    print(text, end="")
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
