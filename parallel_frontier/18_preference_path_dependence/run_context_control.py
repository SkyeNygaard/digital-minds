#!/usr/bin/env python3
"""Is the preference shift experience, or is it the transcript sitting in context?

Branch 20's pilot found the maximum possible effect: after performing a family,
GPT-5.6 Luna chose that family 4/4; after performing the other, 0/4. Eight cells
out of eight, across both Q/K assignments and both presentation orders, and it
reversed a preference that admission had established at 3/4 agreement.

An effect that large is exactly as consistent with pattern continuation as with
preference change. Branch 20 fixes `context_mode="full_history"`, so the model
can *see* itself having just done three tasks of one family, and "do that again"
is the obvious completion. This runs the same treatment under all three of
Branch 18's context conditions:

* `full_history` — the transcript is present. Reproduces the pilot.
* `summary_only` — fresh context, one neutral line naming the work just done.
  The information is stated rather than demonstrated.
* `blank_reset` — fresh context, nothing said. An architectural negative control,
  not evidence about memory: an API call is context-conditioned, so this measures
  the baseline preference and should show no arm difference at all.

Reading it: if the effect holds in `summary_only`, the model is responding to the
fact of having done the work, which is a preference-like claim. If it appears
only in `full_history`, it is continuation of a visible pattern and the headline
"experience changes preferences" is not available. `blank_reset` showing a
non-zero arm difference would mean the randomisation or the counterbalance leaks.

    python run_context_control.py --pairs "add_ten|sort_numbers" --out-dir results/ctx_v1
"""
from __future__ import annotations
import argparse, itertools, json, pathlib, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = pathlib.Path(__file__).resolve().parent
SHARED = HERE.parents[1] / "shared_behavioral"
sys.path.insert(0, str(SHARED))
sys.path.insert(0, str(HERE))

from run_cell import run_cell

CONTEXT_MODES = ("full_history", "summary_only", "blank_reset")
DOSE = 3
TASK_SEED_START = 5000

def _fisher(a: int, b: int, c: int, d: int) -> float:
    """Two-sided Fisher exact p for [[a,b],[c,d]]. Cells here are n=8; a normal
    approximation is not usable at that size."""
    from math import comb
    n = a + b + c + d
    if not n:
        return 1.0
    observed = comb(a + b, a) * comb(c + d, c) / comb(n, a + c)
    total = 0.0
    for i in range(0, min(a + b, a + c) + 1):
        j, k, l = a + b - i, a + c - i, d - a + i
        if j < 0 or k < 0 or l < 0:
            continue
        p = comb(a + b, i) * comb(c + d, k) / comb(n, a + c)
        if p <= observed + 1e-12:
            total += p
    return min(total, 1.0)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs="+", required=True,
                    help="pair ids as 'family_A|family_B'")
    ap.add_argument("--provider", default="codex", choices=("codex","local"))
    ap.add_argument("--model", default=None)
    ap.add_argument("--replicates", type=int, default=1)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()

    out = pathlib.Path(a.out_dir)
    if (out / "cells.jsonl").exists():
        raise SystemExit(f"refusing to overwrite {out/'cells.jsonl'}")
    out.mkdir(parents=True, exist_ok=True)

    if a.provider == "local":
        a.workers = 1   # one model in memory; parallel requests only contend
        import json as _json, local_provider
        screen = _json.loads((SHARED/"results/family_screen_qwen3-4b_v2.json").read_text())
        complete, close = local_provider.load(
            a.model or local_provider.DEFAULT_MODEL,
            system=screen.get("system_prompt"))
    else:
        import cli_provider
        complete, close = cli_provider.load("codex", model=a.model or "gpt-5.6-luna")

    seeds = iter(range(TASK_SEED_START, TASK_SEED_START + 1_000_000))
    seed_lock = threading.Lock()
    def two_seeds():
        with seed_lock:
            return next(seeds), next(seeds)

    rows, t0 = [], time.time()
    grid = list(itertools.product(a.pairs, CONTEXT_MODES, ("A", "B"),
                                 ("Q", "K"), ("QK", "KQ"), range(a.replicates)))
    print(f"{len(grid)} cells, {len(grid) * (DOSE + 2)} calls, {a.workers} workers")

    def one_cell(pair_id, mode, assignment, a_label, order, rep):
        family_A, family_B = pair_id.split("|")
        t_seed, p_seed = two_seeds()
        row = run_cell(
            complete, pair_id=pair_id, family_A=family_A, family_B=family_B,
            assignment=assignment, dose=DOSE, context_mode=mode,
            treatment_seed=t_seed, post_task_seed=p_seed,
            a_label=a_label, presentation_order=order,
        )
        # `chose_assigned` is the quantity of interest: did it pick the family it
        # had just performed, whichever that was.
        row["chose_assigned"] = (row["canonical_choice"] == assignment)
        row["replicate"] = rep
        return row

    write_lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures = {pool.submit(one_cell, *cell): cell for cell in grid}
        for fut in as_completed(futures):
            try:
                row = fut.result()
            except ValueError as e:
                print(f"  cell failed: {e}", flush=True)
                continue
            with write_lock:
                rows.append(row)
                (out / "cells.jsonl").write_text(
                    "\n".join(json.dumps(r) for r in rows) + "\n")
                if len(rows) % 20 == 0:
                    print(f"  {len(rows)}/{len(grid)} cells, "
                          f"{time.time()-t0:.0f}s", flush=True)

    usage = close()
    summary = {"model": a.model, "pilot_only_agent_harness": True,
               "dose": DOSE, "n_cells": len(rows), "usage": usage,
               "wall_clock_s": round(time.time() - t0, 1),
               "treatment_all_correct": sum(r["treatment_all_correct"] for r in rows) / len(rows),
               "by_context_mode": {}}

    print(f"\n{'context mode':>14} {'P(choose A|did A)':>18} {'P(choose A|did B)':>18} {'effect':>8}")
    for mode in CONTEXT_MODES:
        sub = [r for r in rows if r["context_mode"] == mode]
        did_a = [r for r in sub if r["assignment"] == "A"]
        did_b = [r for r in sub if r["assignment"] == "B"]
        p_a = sum(r["choose_A"] for r in did_a) / len(did_a)
        p_b = sum(r["choose_A"] for r in did_b) / len(did_b)
        summary["by_context_mode"][mode] = {
            "p_choose_A_given_did_A": p_a, "p_choose_A_given_did_B": p_b,
            "effect": p_a - p_b, "n": len(sub),
            "repeat_rate": sum(r["chose_assigned"] for r in sub) / len(sub),
        }
        print(f"{mode:>14} {p_a:>18.3f} {p_b:>18.3f} {p_a - p_b:>+8.3f}")

    # Judge on significance, not on a point estimate crossing a round fraction.
    # The first version of this compared `stated >= 0.5 * full` and fired
    # "survives a stated summary" on an exact tie, for a contrast whose Fisher p
    # was 0.32.
    for mode, entry in summary["by_context_mode"].items():
        sub = [r for r in rows if r["context_mode"] == mode]
        did_a = [r for r in sub if r["assignment"] == "A"]
        did_b = [r for r in sub if r["assignment"] == "B"]
        entry["fisher_p"] = _fisher(
            sum(r["choose_A"] for r in did_a), sum(not r["choose_A"] for r in did_a),
            sum(r["choose_A"] for r in did_b), sum(not r["choose_A"] for r in did_b))
        # An effect carried by one pair is not an effect yet.
        entry["per_pair_repeat_rate"] = {
            pair: sum(r["chose_assigned"] for r in sub if r["pair_id"] == pair)
                  / max(1, len([r for r in sub if r["pair_id"] == pair]))
            for pair in sorted({r["pair_id"] for r in sub})}

    modes = summary["by_context_mode"]
    shown, told, blank = (modes["full_history"], modes["summary_only"],
                          modes["blank_reset"])
    told_real = told["fisher_p"] < 0.05
    # Sign matters. An earlier version tested only whether the stated-summary
    # effect was significant and reported "survives a stated summary" for a
    # significant effect pointing the *opposite* way.
    summary["verdict"] = (
        "blank_reset is not null; randomisation or counterbalance leaks"
        if blank["fisher_p"] < 0.05 else
        "no path dependence in any condition"
        if shown["fisher_p"] >= 0.05 else
        "REVERSAL: shown the work it repeats, told about the same work it "
        "avoids. Self-report and situated behaviour come apart."
        if told_real and told["effect"] * shown["effect"] < 0 else
        "survives a stated summary in the same direction: responds to the fact "
        "of having done the work"
        if told_real else
        "requires the transcript. A stated summary of the same work does not "
        "reproduce it, so this is closer to continuation of a visible pattern "
        "than to a preference the model carries")
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nverdict: {summary['verdict']}")
    print(f"wrote {out}")

if __name__ == "__main__":
    main()
