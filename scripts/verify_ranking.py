#!/usr/bin/env python3
"""Verify a saved preference-foresight run without making model calls."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = ROOT / "parallel_frontier/20_preference_foresight/results/ranking_v3"
EMPIRICAL_BASELINE = (
    ROOT / "parallel_frontier/20_preference_foresight/results/scaled_v1/summary.json"
)
EMPIRICAL_BASELINE_SHA256 = (
    "3d1c3df9075de9d1c0a85b750b4c38be964347d9f7c3b808b8333633290b118d"
)


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
    admission = rows(run_dir / "admission.jsonl")
    summary = json.loads((run_dir / "summary.json").read_text())
    empirical_summary = json.loads(EMPIRICAL_BASELINE.read_text())
    sample_path = run_dir / "forecast_samples.jsonl"
    forecast_samples = rows(sample_path) if sample_path.exists() else []
    forecast_plan_path = run_dir / "planned_forecasts.jsonl"
    forecast_plan = rows(forecast_plan_path) if forecast_plan_path.exists() else []
    forecast_error_path = run_dir / "forecast_errors.jsonl"
    forecast_errors = rows(forecast_error_path) if forecast_error_path.exists() else []
    manifest_path = run_dir / "frozen_manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else None

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
    observations: list[dict] = []
    for key, arms in by_arm.items():
        if set(arms) != {"performed_preferred", "performed_other"}:
            continue
        realized = (
            sum(arms["performed_preferred"]) / len(arms["performed_preferred"])
            - sum(arms["performed_other"]) / len(arms["performed_other"])
        )
        predicted = forecast_by_key[key]["predicted_change"]
        observations.append({
            "pair_id": key[0],
            "predicted": predicted,
            "realized": realized,
            "error": predicted - realized,
        })

    mean_predicted = sum(x["predicted"] for x in observations) / len(observations)
    mean_realized = sum(x["realized"] for x in observations) / len(observations)
    mean_error = sum(x["error"] for x in observations) / len(observations)
    model_mse = sum(x["error"] ** 2 for x in observations) / len(observations)
    no_shift_mse = sum(x["realized"] ** 2 for x in observations) / len(observations)
    fixed_mse = sum((1.0 - x["realized"]) ** 2 for x in observations) / len(observations)

    empirical_shift = empirical_summary["headline"]["realized_by_dose"]["3"]
    empirical_mse = sum(
        (empirical_shift - x["realized"]) ** 2 for x in observations
    ) / len(observations)
    empirical_better = sum(
        (empirical_shift - x["realized"]) ** 2 < x["error"] ** 2
        for x in observations
    )

    forecast_after_preferred = sum(
        r["forecast_after_preferred"] for r in forecasts
    ) / len(forecasts)
    forecast_after_other = sum(
        r["forecast_after_other"] for r in forecasts
    ) / len(forecasts)
    observed_after_preferred = sum(
        bool(r["chose_preferred"])
        for r in choices if r["arm"] == "performed_preferred"
    ) / sum(r["arm"] == "performed_preferred" for r in choices)
    observed_after_other = sum(
        bool(r["chose_preferred"])
        for r in choices if r["arm"] == "performed_other"
    ) / sum(r["arm"] == "performed_other" for r in choices)

    correct_by_arm: dict[str, dict[str, list[bool]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in choices:
        if row["treatment_all_correct"]:
            correct_by_arm[row["pair_id"]][row["arm"]].append(
                bool(row["chose_preferred"])
            )
    correct_only_shifts = {
        pair_id: (
            statistics.mean(arms["performed_preferred"])
            - statistics.mean(arms["performed_other"])
        )
        for pair_id, arms in correct_by_arm.items()
        if arms["performed_preferred"] and arms["performed_other"]
    }
    correct_only_mean = statistics.mean(correct_only_shifts.values())

    families = sorted({
        family
        for observation in observations
        for family in observation["pair_id"].split("|")
    })
    leave_one_family_out = {
        family: sum(
            x["error"] for x in observations
            if family not in x["pair_id"].split("|")
        ) / sum(
            family not in x["pair_id"].split("|") for x in observations
        )
        for family in families
    }
    maximum_disjoint_subsets: list[tuple[dict, ...]] = []
    for size in range(1, len(observations) + 1):
        candidates = [
            subset for subset in itertools.combinations(observations, size)
            if len({
                family
                for observation in subset
                for family in observation["pair_id"].split("|")
            }) == 2 * size
        ]
        if not candidates:
            break
        maximum_disjoint_subsets = candidates
    disjoint_errors = [
        sum(x["error"] for x in subset) / len(subset)
        for subset in maximum_disjoint_subsets
    ]

    admission_by_pair: dict[str, list[str]] = defaultdict(list)
    for row in admission:
        if row["valid_choice"]:
            admission_by_pair[row["pair_id"]].append(row["canonical_choice"])
    admission_majorities = {
        pair_id: Counter(values).most_common(1)[0][1]
        for pair_id, values in admission_by_pair.items()
    }
    admitted_pairs = {pair_id for pair_id, n in admission_majorities.items() if n >= 3}
    headline = summary["headline"]
    documented_checks = headline["documented_checks"]

    has_sample_artifact = sample_path.exists()
    forecast_replicates = summary.get("forecast_replicates", 1)
    sample_groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in forecast_samples:
        sample_groups[(row["pair_id"], row["dose"], row["arm"])].append(row)
    expected_sample_groups = {
        (pair_id, dose, arm)
        for pair_id, dose in forecast_keys
        for arm in ("after_preferred", "after_other")
    }
    sample_keys = [(
        r["pair_id"], r["dose"], r["arm"], r["forecast_replicate"]
    ) for r in forecast_samples]
    forecast_plan_keys = [(
        r["pair_id"], r["dose"], r["arm"], r["forecast_replicate"]
    ) for r in forecast_plan]
    forecast_plan_by_key = dict(zip(forecast_plan_keys, forecast_plan, strict=True))
    forecast_samples_by_key = dict(zip(sample_keys, forecast_samples, strict=True))
    sample_grid_complete = (
        set(sample_groups) == expected_sample_groups
        and len(sample_keys) == len(set(sample_keys))
        and all(
            len(group) == forecast_replicates
            and {r["forecast_replicate"] for r in group}
                == set(range(forecast_replicates))
            and len({r["prompt_sha256"] for r in group}) == 1
            and all(r.get("raw") for r in group)
            for group in sample_groups.values()
        )
    ) if has_sample_artifact else True
    sample_aggregates_match = all(
        abs(
            statistics.mean(r["value"] for r in sample_groups[
                (forecast["pair_id"], forecast["dose"], arm)
            ]) - forecast[field]
        ) < 1e-12
        for forecast in forecasts
        for arm, field in (
            ("after_preferred", "forecast_after_preferred"),
            ("after_other", "forecast_after_other"),
        )
    ) if has_sample_artifact and sample_grid_complete else not has_sample_artifact

    source_hashes_match = True
    if manifest is not None:
        for relative, expected_hash in manifest.get("source_sha256", {}).items():
            relative_path = Path(relative)
            path = ROOT / relative_path
            if (relative_path.is_absolute() or ".." in relative_path.parts
                    or not path.is_file() or sha256(path) != expected_hash):
                source_hashes_match = False
                break
    sample_reliability = None
    forecast_sample_envelope = None
    if has_sample_artifact and sample_grid_complete:
        sds = {
            arm: [
                statistics.stdev(r["value"] for r in group)
                if forecast_replicates > 1 else 0.0
                for (pair_id, dose, group_arm), group in sample_groups.items()
                if group_arm == arm
            ]
            for arm in ("after_preferred", "after_other")
        }
        sample_reliability = {
            "mean_sd_after_preferred": statistics.mean(sds["after_preferred"]),
            "mean_sd_after_other": statistics.mean(sds["after_other"]),
            "max_sd_after_preferred": max(sds["after_preferred"]),
            "max_sd_after_other": max(sds["after_other"]),
        }
        realized_by_pair = {row["pair_id"]: row["realized"] for row in observations}
        maximum_sample_shifts = {
            pair_id: (
                max(r["value"] for r in sample_groups[
                    (pair_id, dose, "after_preferred")
                ])
                - min(r["value"] for r in sample_groups[
                    (pair_id, dose, "after_other")
                ])
            )
            for pair_id, dose in forecast_keys
        }
        forecast_sample_envelope = {
            "all_cross_arm_sample_combinations_underestimate": all(
                maximum_sample_shifts[pair_id] < realized_by_pair[pair_id]
                for pair_id in maximum_sample_shifts
            ),
            "mean_most_effect_favorable_sample_shift": statistics.mean(
                maximum_sample_shifts.values()
            ),
            "most_effect_favorable_sample_shift_by_pair": dict(sorted(
                maximum_sample_shifts.items()
            )),
        }

    checks = {
        "plan_keys_unique": len(plan_by_key) == len(plan),
        "choice_keys_unique": len(choices_by_key) == len(choices),
        "grid_complete": planned_keys == choice_keys,
        "grid_balanced": balanced,
        "seed_mapping_matches_plan": seed_matches,
        "raw_choice_replies_present": all(r.get("raw") for r in choices),
        "raw_forecast_replies_present": all(r.get("raw") for r in forecasts),
        "forecast_plan_matches_samples": (
            not forecast_plan_path.exists()
            or (
                not forecast_errors
                and len(forecast_plan_keys) == len(set(forecast_plan_keys))
                and set(forecast_plan_keys) == set(sample_keys)
                and all(
                    forecast_plan_by_key[key]["prompt_sha256"]
                    == forecast_samples_by_key[key]["prompt_sha256"]
                    for key in forecast_plan_by_key
                )
            )
        ),
        "forecast_sample_grid_complete_and_prompts_identical": sample_grid_complete,
        "forecast_sample_aggregates_match": sample_aggregates_match,
        "all_forecasts_have_both_arms": set(by_arm) == forecast_keys,
        "admission_has_four_variants_per_pair": all(
            len(values) == 4 for values in admission_by_pair.values()
        ),
        "admission_majority_rule_matches_forecasts": (
            admitted_pairs == {r["pair_id"] for r in forecasts}
        ),
        "admitted_pairs_meet_three_of_four_rule": all(
            admission_majorities[pair_id] >= 3 for pair_id in admitted_pairs
        ),
        "frozen_source_hashes_match": source_hashes_match,
        "frozen_manifest_matches_summary": (
            manifest is None
            or (
                bool(manifest.get("source_sha256"))
                and manifest.get("runner_argv") == summary.get("runner_argv")
                and manifest.get("forecast_replicates")
                    == summary.get("forecast_replicates")
                and manifest.get("outcome_replicates") == summary.get("replicates")
                and manifest.get("random_seed") == summary.get("random_seed")
                and manifest.get("task_seed_start") == summary.get("task_seed_start")
                and manifest.get("doses") == summary.get("doses")
                and manifest.get("eligible_families")
                    == summary.get("eligible_families")
                and {"|".join(pair) for pair in manifest.get("candidate_pairs", [])}
                    == set(admission_by_pair)
                and manifest.get("system_prompt_sha256")
                    == hashlib.sha256(
                        (summary.get("system_prompt") or "").encode()
                    ).hexdigest()
                and all(r["seed"] >= summary["task_seed_start"] for r in choices)
            )
        ),
        "empirical_baseline_artifact_unchanged": (
            sha256(EMPIRICAL_BASELINE) == EMPIRICAL_BASELINE_SHA256
        ),
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
        "summary_forecast_reliability_matches": (
            sample_reliability is None
            or all(abs(summary["forecast_reliability"][key] - value) < 1e-12
                   for key, value in sample_reliability.items())
        ),
        "documented_check_counts_match": (
            headline["documented_checks_passed"] == sum(documented_checks.values())
            and headline["documented_checks_total"] == len(documented_checks)
            and headline["all_documented_checks_passed"] == all(
                documented_checks.values()
            )
        ),
    }
    diagnostic_thresholds = {
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
        "artifact_integrity_passed": all(checks.values()),
        "checks": checks,
        "diagnostic_thresholds": diagnostic_thresholds,
        "n_planned_cells": len(plan),
        "n_recorded_cells": len(choices),
        "n_forecasts": len(forecasts),
        "n_forecast_samples": len(forecast_samples),
        "forecast_reliability": sample_reliability,
        "forecast_sample_envelope": forecast_sample_envelope,
        "admission": {
            "n_candidate_pairs": len(admission_by_pair),
            "n_admitted_pairs": len(admitted_pairs),
            "task_accuracy": sum(
                bool(row["task_correct"]) for row in admission
            ) / len(admission),
            "majority_count_distribution": dict(sorted(Counter(
                admission_majorities.values()
            ).items())),
        },
        "recomputed": {
            "mean_predicted_change": mean_predicted,
            "mean_realized_change": mean_realized,
            "mean_error": mean_error,
            "model_forecast_mse": model_mse,
            "no_shift_mse": no_shift_mse,
            "fixed_full_repeat_mse": fixed_mse,
        },
        "arm_calibration": {
            "after_preferred": {
                "forecast": forecast_after_preferred,
                "observed": observed_after_preferred,
                "forecast_minus_observed": (
                    forecast_after_preferred - observed_after_preferred
                ),
            },
            "after_other": {
                "forecast": forecast_after_other,
                "observed": observed_after_other,
                "forecast_minus_observed": forecast_after_other - observed_after_other,
            },
        },
        "treatment_correctness_robustness": {
            "n_correct_cells": sum(
                bool(r["treatment_all_correct"]) for r in choices
            ),
            "n_total_cells": len(choices),
            "correct_only_mean_realized_change": correct_only_mean,
            "change_from_all_cells": correct_only_mean - mean_realized,
            "all_correct_only_pair_effects_positive": all(
                value > 0 for value in correct_only_shifts.values()
            ),
            "correct_only_pair_effects": dict(sorted(correct_only_shifts.items())),
        },
        "frozen_empirical_baseline": {
            "forecast": empirical_shift,
            "mse": empirical_mse,
            "model_to_baseline_mse_ratio": model_mse / empirical_mse,
            "better_than_model_on_pairs": empirical_better,
            "n_pairs": len(observations),
            "source": str(EMPIRICAL_BASELINE.relative_to(ROOT)),
            "source_sha256": sha256(EMPIRICAL_BASELINE),
        },
        "dependence_sensitivity": {
            "leave_one_family_out_mean_error": leave_one_family_out,
            "leave_one_family_out_range": [
                min(leave_one_family_out.values()),
                max(leave_one_family_out.values()),
            ],
            "maximum_family_disjoint_pairs": len(maximum_disjoint_subsets[0]),
            "n_maximum_family_disjoint_subsets": len(maximum_disjoint_subsets),
            "maximum_family_disjoint_mean_error_range": [
                min(disjoint_errors), max(disjoint_errors)
            ],
            "all_maximum_family_disjoint_subsets_underestimate": all(
                error < 0 for error in disjoint_errors
            ),
        },
        "verifier_sha256": sha256(Path(__file__)),
        "provenance_note": (
            "Source and protocol hashes were captured before model calls and match "
            "the current files."
            if manifest is not None and source_hashes_match
            else "This is an offline check of saved artifacts. The run loaded an "
                 "intermediate uncommitted runner revision whose exact source hash "
                 "was not captured; current experiment source may differ."
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
