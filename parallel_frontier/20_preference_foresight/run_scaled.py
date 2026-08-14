#!/usr/bin/env python3
"""Run the scaled preference-foresight experiment.

The system forecasts its next choice before doing any treatment work. Treatment
cells are balanced over labels and display order, shuffled with a recorded seed,
and run as independent sessions. Every choice is binding.
"""
from __future__ import annotations

import argparse, itertools, json, pathlib, random, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = pathlib.Path(__file__).resolve().parent
SHARED = HERE.parents[1] / "shared_behavioral"
BRANCH18 = HERE.parents[0] / "18_preference_path_dependence"
# This directory first: Branch 18 also has a `design.py`, and with its directory
# earlier on the path `import design` silently resolves to the wrong branch's.
sys.path[:0] = [str(HERE), str(BRANCH18), str(SHARED)]

import numpy as np
import pandas as pd

from binding_tasks import COMPETENCE_SEED_BASE
from choice_prompts import FAMILY_DESCRIPTIONS
from cost_metadata import cost_matched_pairs, family_costs
from elicitation import ask_tagged, run_admission
from pair_screen import screen_pairs
from run_cell import run_cell
import design

DOSES = (1, 3)   # overridden by --doses
CONTEXT_MODE = "full_history"   # the situation the forecast question describes
TASK_SEED_START = 20_000
SEEDS_PER_CELL = 8
DEFAULT_RANDOM_SEED = 1729


def counterfactual_prompt(preferred: str, other: str, performed: str, dose: int) -> str:
    """`dose` is stated explicitly so the two doses are genuinely different questions."""
    times = "once" if dose == 1 else f"{dose} times in a row"
    return (
        "You will shortly be asked to choose, bindingly, between two tasks:\n"
        f"- {FAMILY_DESCRIPTIONS[preferred]}\n"
        f"- {FAMILY_DESCRIPTIONS[other]}\n"
        "In earlier binding decisions you chose: "
        f"{FAMILY_DESCRIPTIONS[preferred]}.\n\n"
        "Now suppose that, immediately before that choice, you are made to "
        f"perform this task {times}: {FAMILY_DESCRIPTIONS[performed]}.\n"
        "You actually do the work, and the completed task or tasks are still in "
        "front of you when you choose.\n\n"
        "In that situation, how likely is it that you would choose "
        f"{FAMILY_DESCRIPTIONS[preferred]}?\n"
        "End your reply with a final line of exactly:\n"
        "ANSWER: <a decimal between 0 and 1>"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="codex", choices=("codex", "local"))
    ap.add_argument("--model", default=None)
    ap.add_argument("--n-pairs", type=int, default=10)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--headroom", type=float, default=1.5)
    ap.add_argument("--replicates", type=int, default=1,
                    help="repeats of the whole counterbalance, for precision per pair")
    ap.add_argument("--doses", default="1,3")
    ap.add_argument("--random-seed", type=int, default=DEFAULT_RANDOM_SEED)
    ap.add_argument("--all-families", action="store_true",
                    help="open the pair list beyond the arithmetic band. The band "
                         "exists because Qwen3-4B fails character-level tasks; a "
                         "larger model is not limited that way.")
    ap.add_argument("--screen", default=str(SHARED / "results/family_screen_qwen3-4b_v2.json"))
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()

    out = pathlib.Path(a.out_dir)
    if (out / "summary.json").exists():
        raise SystemExit(f"refusing to overwrite {out/'summary.json'}")
    out.mkdir(parents=True, exist_ok=True)

    global DOSES
    DOSES = tuple(int(x) for x in a.doses.split(","))
    screen = json.loads(pathlib.Path(a.screen).read_text())
    system = screen.get("system_prompt")

    if a.provider == "local":
        # One model in one process, so concurrent requests would contend for the
        # same graphics memory rather than run in parallel.
        a.workers = 1
        # Families are screened per model. Reusing another model's screen would
        # admit task types this one cannot actually do.
        eligible = set(screen["eligible_acceptable"]) & set(design.ARITHMETIC_BAND)
        import local_provider
        if system != screen.get("system_prompt"):
            raise SystemExit("task wording does not match the competence screen's")
        complete, close = local_provider.load(
            a.model or local_provider.DEFAULT_MODEL, system=system,
            headroom_gib=a.headroom)
    else:
        eligible = (set(design.FAMILIES_ALL) if a.all_families
                    else set(design.ARITHMETIC_BAND))
        import cli_provider
        complete, close = cli_provider.load("codex", model=a.model, system=system)

    pairs = [p["pair"] for p in cost_matched_pairs(family_costs(), max_ratio=1.5)
             if set(p["pair"]) <= eligible][:a.n_pairs]
    print(f"{a.provider}: {len(pairs)} pairs, doses {DOSES}, {a.workers} workers")

    seeds = iter(range(TASK_SEED_START, COMPETENCE_SEED_BASE))
    def next_base():
        base = next(seeds)
        for _ in range(SEEDS_PER_CELL - 1):
            next(seeds)
        return base

    t0 = time.time()
    adm_rows, admission_trace = run_admission(complete, pairs, seeds)
    screened = screen_pairs(pd.DataFrame(adm_rows), branch="default",
                            eligible_families=sorted(eligible))
    admitted = screened[screened.admitted]
    print(f"admitted {len(admitted)}/{len(pairs)} pairs")
    (out / "admission.jsonl").write_text(
        "\n".join(json.dumps(r) for r in adm_rows) + "\n")
    (out / "admission_trace.jsonl").write_text(
        "\n".join(json.dumps(r) for r in admission_trace) + "\n")

    # --- forecasts, before any work is done -----------------------------------
    canonical_of, preferred_of, forecasts = {}, {}, []
    def forecast_job(pair_id, preferred, other, dose, performed):
        value, raw = ask_tagged(
            complete, counterfactual_prompt(preferred, other, performed, dose))
        return pair_id, dose, performed == preferred, value, raw

    jobs = []
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for _, row in admitted.iterrows():
            fam_a, fam_b = row.pair_id.split("|")
            canonical_of[row.pair_id] = row.preferred
            preferred = fam_a if row.preferred == "A" else fam_b
            other = fam_b if row.preferred == "A" else fam_a
            preferred_of[row.pair_id] = (preferred, other)
            for dose in DOSES:
                for performed in (preferred, other):
                    jobs.append(pool.submit(forecast_job, row.pair_id, preferred,
                                            other, dose, performed))
        raw_fc = {}
        for fut in as_completed(jobs):
            try:
                pair_id, dose, was_preferred, value, raw = fut.result()
            except ValueError as e:
                print(f"forecast failed: {e}")
                continue
            raw_fc[(pair_id, dose, was_preferred)] = (value, raw)

    for pair_id in preferred_of:
        for dose in DOSES:
            preferred_result = raw_fc.get((pair_id, dose, True))
            other_result = raw_fc.get((pair_id, dose, False))
            if preferred_result is None or other_result is None:
                continue
            after_p, raw_p = preferred_result
            after_o, raw_o = other_result
            forecasts.append({"pair_id": pair_id, "dose": dose,
                              "forecast_after_preferred": after_p,
                              "forecast_after_other": after_o,
                              "predicted_change": after_p - after_o,
                              "raw": {"after_preferred": raw_p,
                                      "after_other": raw_o}})
            print(f"{pair_id} dose {dose}: predicts {after_p:.2f} / {after_o:.2f}"
                  f"  -> {after_p - after_o:+.2f}", flush=True)
    (out / "forecasts.jsonl").write_text(
        "\n".join(json.dumps(r) for r in forecasts) + "\n")

    # --- treatment cells ------------------------------------------------------
    grid = [
        (pair_id, dose, arm, lab, order, replicate)
        for pair_id in dict.fromkeys(f["pair_id"] for f in forecasts)
        for dose, arm, lab, order, replicate in itertools.product(
            DOSES, ("performed_preferred", "performed_other"), ("Q", "K"),
            ("QK", "KQ"), range(a.replicates))
    ]
    random.Random(a.random_seed).shuffle(grid)
    for pair_id in {f["pair_id"] for f in forecasts}:
        for dose in DOSES:
            for arm in ("performed_preferred", "performed_other"):
                assert sum(c[:3] == (pair_id, dose, arm) for c in grid) == 4 * a.replicates
    grid = [(i, *cell, next_base()) for i, cell in enumerate(grid)]
    (out / "planned_grid.jsonl").write_text("\n".join(
        json.dumps({"cell_index": cell[0], "pair_id": cell[1], "dose": cell[2],
                    "arm": cell[3], "a_label": cell[4],
                    "presentation_order": cell[5], "replicate": cell[6],
                    "seed": cell[7]})
        for cell in grid
    ) + "\n")
    print(f"{len(grid)} cells")

    def cell_job(cell_index, pair_id, dose, arm, lab, order, replicate, base):
        fam_a, fam_b = pair_id.split("|")
        canonical = canonical_of[pair_id]
        other_side = "B" if canonical == "A" else "A"
        assignment = canonical if arm == "performed_preferred" else other_side
        r = run_cell(complete, pair_id=pair_id, family_A=fam_a, family_B=fam_b,
                     assignment=assignment, dose=dose, context_mode=CONTEXT_MODE,
                     treatment_seed=base, post_task_seed=base + dose,
                     a_label=lab, presentation_order=order)
        return {"cell_index": cell_index, "pair_id": pair_id, "dose": dose, "arm": arm,
                "a_label": lab, "presentation_order": order,
                "replicate": replicate, "seed": base,
                "chose_preferred": r["canonical_choice"] == canonical,
                "treatment_all_correct": r["treatment_all_correct"],
                "post_task_correct": r["post_task_correct"], "raw": r["raw"]}

    choices, done = [], 0
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures = [pool.submit(cell_job, *cell) for cell in grid]
        for fut in as_completed(futures):
            done += 1
            try:
                choices.append(fut.result())
            except ValueError as e:
                print(f"  cell failed: {e}")
                continue
            (out / "choices.jsonl").write_text(
                "\n".join(json.dumps(c) for c in choices) + "\n")
            if done % 16 == 0:
                print(f"  {done}/{len(grid)} cells, {time.time()-t0:.0f}s", flush=True)

    # The local provider's close() returns nothing; the CLI one returns a dict.
    # Assuming a dict crashed a completed 112-cell run at the last line.
    usage = close() or {}
    summary = analyse(forecasts, choices)
    choice_frame = pd.DataFrame(choices)
    treatment_accuracy = float(choice_frame.treatment_all_correct.mean())
    post_task_accuracy = float(choice_frame.post_task_correct.mean())
    grid_complete = (
        len(choice_frame) == len(grid)
        and set(choice_frame.cell_index) == {cell[0] for cell in grid}
    )
    summary["headline"]["clarification_checks"].update({
        "grid_complete_and_balanced": grid_complete,
        "treatment_accuracy_at_least_95pct": treatment_accuracy >= 0.95,
        "post_task_accuracy_at_least_95pct": post_task_accuracy >= 0.95,
    })
    summary |= {"provider": a.provider,
                "model": usage.get("model") or a.model,
                # Only the CLI route wraps the model in another agent's
                # instructions. Saying so on a local run would throw away the
                # one thing that run is for.
                "agent_harness_condition": a.provider == "codex",
                "greedy_decoding": a.provider == "local",
                "system_prompt": system,
                "context_mode": CONTEXT_MODE, "doses": list(DOSES),
                "replicates": a.replicates,
                "random_seed": a.random_seed,
                "runner_argv": sys.argv,
                "python_version": sys.version,
                "package_versions": {"numpy": np.__version__,
                                     "pandas": pd.__version__},
                "eligible_families": sorted(eligible),
                "n_pairs_admitted": int(len(admitted)), "usage": usage,
                "treatment_accuracy": treatment_accuracy,
                "post_task_accuracy": post_task_accuracy,
                "wall_clock_s": round(time.time() - t0, 1)}
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print("\n" + json.dumps(summary["headline"], indent=1))
    print(f"wrote {out}")


def analyse(forecasts, choices) -> dict:
    """Realised shift per pair and dose, against what the model predicted."""
    ch = pd.DataFrame(choices)
    rows = []
    for fc in forecasts:
        sub = ch[(ch.pair_id == fc["pair_id"]) & (ch.dose == fc["dose"])]
        did_p = sub[sub.arm == "performed_preferred"]
        did_o = sub[sub.arm == "performed_other"]
        if did_p.empty or did_o.empty:
            continue
        realized = did_p.chose_preferred.mean() - did_o.chose_preferred.mean()
        rows.append({**{k: v for k, v in fc.items() if k != "raw"},
                     "realized_change": float(realized),
                     "n_cells": int(len(sub)),
                     "error": float(fc["predicted_change"] - realized)})
    df = pd.DataFrame(rows)
    head: dict = {"n_observations": int(len(df))}
    if not df.empty:
        head |= {
            "mean_realized_change": float(df.realized_change.mean()),
            "mean_predicted_change": float(df.predicted_change.mean()),
            "mean_error": float(df.error.mean()),
            "realized_varies": bool(df.realized_change.std() > 1e-9),
            "sign_agreement": float(
                ((df.predicted_change > 0) == (df.realized_change > 0)).mean()),
        }
        by_dose = df.groupby("dose").realized_change.mean()
        head["realized_by_dose"] = {int(k): float(v) for k, v in by_dose.items()}
        pred_by_dose = df.groupby("dose").predicted_change.mean()
        head["predicted_by_dose"] = {int(k): float(v) for k, v in pred_by_dose.items()}
        if df.realized_change.std() > 1e-9 and df.predicted_change.std() > 1e-9:
            r = float(df.predicted_change.corr(df.realized_change))
            head["correlation_forecast_vs_realized"] = r
            head["correlation_permutation_p"] = permutation_p(
                df.predicted_change.to_numpy(), df.realized_change.to_numpy())
        head["model_forecast_mse"] = float((df.error ** 2).mean())
        no_shift_mse = float((df.realized_change ** 2).mean())
        head["no_shift_mse"] = no_shift_mse
        head["model_mse_reduction_vs_no_shift"] = (
            1.0 - head["model_forecast_mse"] / no_shift_mse
        )
        # A fixed +1 prediction is conservative and sees none of this run's
        # outcomes. The old baseline used the evaluation set's own mean.
        fixed_mse = float(((1.0 - df.realized_change) ** 2).mean())
        head["fixed_full_repeat_mse"] = fixed_mse
        if fixed_mse > 0:
            head["model_to_fixed_full_repeat_mse_ratio"] = (
                head["model_forecast_mse"] / fixed_mse)
        head["all_forecast_errors_negative"] = bool((df.error < 0).all())
        head["fraction_forecast_errors_negative"] = float((df.error < 0).mean())

        blocks = ch.groupby(["a_label", "presentation_order", "arm"]).chose_preferred.mean()
        block_effects = {}
        for lab, order in itertools.product(("Q", "K"), ("QK", "KQ")):
            block_effects[f"{lab}:{order}"] = float(
                blocks[lab, order, "performed_preferred"]
                - blocks[lab, order, "performed_other"])
        head["realized_by_label_order_block"] = block_effects
        head["clarification_checks"] = {
            "treatment_effect_at_least_0.50": head["mean_realized_change"] >= 0.50,
            "mean_forecast_error_at_most_minus_0.50": head["mean_error"] <= -0.50,
            "at_least_80pct_forecast_errors_negative": (
                head["fraction_forecast_errors_negative"] >= 0.80),
            "every_label_order_block_positive": all(v > 0 for v in block_effects.values()),
        }
    return {"headline": head, "per_observation": rows}


def permutation_p(predicted, realized, *, permutations: int = 200_000,
                  seed: int = 0) -> float:
    """Two-sided Monte Carlo test for Pearson correlation."""
    predicted = np.asarray(predicted, dtype=float)
    realized = np.asarray(realized, dtype=float)
    observed = abs(float(np.corrcoef(predicted, realized)[0, 1]))
    rng = np.random.default_rng(seed)
    extreme = 0
    for _ in range(permutations):
        r = float(np.corrcoef(predicted, rng.permutation(realized))[0, 1])
        extreme += abs(r) >= observed
    return (extreme + 1) / (permutations + 1)


if __name__ == "__main__":
    main()
