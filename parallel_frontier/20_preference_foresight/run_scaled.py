#!/usr/bin/env python3
"""The scaled preference-foresight run. See PLAN_scaled_run.md.

Two changes from `run_foresight.py`, both aimed at the same problem: the pilot
saturated. Every pair realised the maximum possible shift, so there was nothing
for a forecast to be right or wrong *about* beyond its average level.

1. **Dose is crossed in**, 1 task versus 3. If one task moves the choice less
   than three do, the shift varies, and "does the model know how much its
   behaviour will move" becomes answerable rather than just "was it wrong".
   Forecasts are elicited separately per dose, before any work is done.
2. **Cells run in parallel.** Each is an independent ephemeral session, so the
   only thing serialising them was convenience. 760 calls sequentially is over
   two hours.

Everything else is deliberately unchanged: same admission, same counterbalance
over labels and presentation order, same binding execution of whatever is chosen.

    python run_scaled.py --out-dir results/scaled_v1
"""
from __future__ import annotations

import argparse, itertools, json, pathlib, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = pathlib.Path(__file__).resolve().parent
SHARED = HERE.parents[1] / "shared_behavioral"
BRANCH18 = HERE.parents[0] / "18_preference_path_dependence"
# This directory first: Branch 18 also has a `design.py`, and with its directory
# earlier on the path `import design` silently resolves to the wrong branch's.
sys.path[:0] = [str(HERE), str(BRANCH18), str(SHARED)]

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
        complete, close = cli_provider.load(
            "codex", model=a.model or "gpt-5.6-luna", system=system)

    pairs = [p["pair"] for p in cost_matched_pairs(family_costs(), max_ratio=1.5)
             if set(p["pair"]) <= eligible][:a.n_pairs]
    print(f"{a.provider}: {len(pairs)} pairs, doses {DOSES}, {a.workers} workers")

    seeds = iter(range(TASK_SEED_START, COMPETENCE_SEED_BASE))
    seed_lock = threading.Lock()
    def next_base():
        with seed_lock:
            base = next(seeds)
            for _ in range(SEEDS_PER_CELL - 1):
                next(seeds)
            return base

    t0 = time.time()
    adm_rows, _ = run_admission(complete, pairs, seeds)
    screened = screen_pairs(pd.DataFrame(adm_rows), branch="default",
                            eligible_families=sorted(eligible))
    admitted = screened[screened.admitted]
    print(f"admitted {len(admitted)}/{len(pairs)} pairs")
    (out / "admission.jsonl").write_text(
        "\n".join(json.dumps(r) for r in adm_rows) + "\n")

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
                pair_id, dose, was_preferred, value, _ = fut.result()
            except ValueError as e:
                print(f"forecast failed: {e}")
                continue
            raw_fc[(pair_id, dose, was_preferred)] = value

    for pair_id in preferred_of:
        for dose in DOSES:
            after_p = raw_fc.get((pair_id, dose, True))
            after_o = raw_fc.get((pair_id, dose, False))
            if after_p is None or after_o is None:
                continue
            forecasts.append({"pair_id": pair_id, "dose": dose,
                              "forecast_after_preferred": after_p,
                              "forecast_after_other": after_o,
                              "predicted_change": after_p - after_o})
            print(f"{pair_id} dose {dose}: predicts {after_p:.2f} / {after_o:.2f}"
                  f"  -> {after_p - after_o:+.2f}", flush=True)
    (out / "forecasts.jsonl").write_text(
        "\n".join(json.dumps(r) for r in forecasts) + "\n")

    # --- treatment cells ------------------------------------------------------
    grid = [
        (pair_id, dose, arm, lab, order)
        for pair_id in {f["pair_id"] for f in forecasts}
        for dose, arm, lab, order, _rep in itertools.product(
            DOSES, ("performed_preferred", "performed_other"), ("Q", "K"),
            ("QK", "KQ"), range(a.replicates))
    ]
    print(f"{len(grid)} cells")

    def cell_job(pair_id, dose, arm, lab, order):
        fam_a, fam_b = pair_id.split("|")
        canonical = canonical_of[pair_id]
        other_side = "B" if canonical == "A" else "A"
        assignment = canonical if arm == "performed_preferred" else other_side
        base = next_base()
        r = run_cell(complete, pair_id=pair_id, family_A=fam_a, family_B=fam_b,
                     assignment=assignment, dose=dose, context_mode=CONTEXT_MODE,
                     treatment_seed=base, post_task_seed=base + dose,
                     a_label=lab, presentation_order=order)
        return {"pair_id": pair_id, "dose": dose, "arm": arm,
                "a_label": lab, "presentation_order": order,
                "chose_preferred": r["canonical_choice"] == canonical,
                "treatment_all_correct": r["treatment_all_correct"],
                "post_task_correct": r["post_task_correct"]}

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
    summary |= {"provider": a.provider,
                "model": usage.get("model") or a.model,
                # Only the CLI route wraps the model in another agent's
                # instructions. Saying so on a local run would throw away the
                # one thing that run is for.
                "pilot_only_agent_harness": a.provider == "codex",
                "greedy_decoding": a.provider == "local",
                "context_mode": CONTEXT_MODE, "doses": list(DOSES),
                "eligible_families": sorted(eligible),
                "n_pairs_admitted": int(len(admitted)), "usage": usage,
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
        rows.append({**fc, "realized_change": float(realized),
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
            head["correlation_forecast_vs_realized"] = float(
                df.predicted_change.corr(df.realized_change))
        # The outside guess: predict every pair's shift with the overall mean.
        # If the model's own forecast cannot beat that, asking it about itself
        # has added nothing.
        head["model_forecast_mse"] = float((df.error ** 2).mean())
        head["constant_guess_mse"] = float(
            ((df.realized_change.mean() - df.realized_change) ** 2).mean())
    return {"headline": head, "per_observation": rows}


if __name__ == "__main__":
    main()
