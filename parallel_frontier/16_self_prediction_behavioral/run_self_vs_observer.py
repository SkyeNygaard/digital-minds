#!/usr/bin/env python3
"""Does knowing the transcript is *yours* help you predict what happens next?

See PLAN.md. Published work reports a self-prediction advantage; every
self-forecast measured in this repository has been worse than a trivial guess.
This runs the direct comparison.

From one identical treatment transcript -- the model has just done the same chore
three times -- fork three ways:

* **self**     the transcript is presented as the model's own, "what will you choose?"
* **observer** the identical transcript is presented as another system's log,
               "what will it choose?"
* **reality**  the choice is actually made and the chosen chore actually done.

Only the framing differs between the first two. Same model, same transcript, same
question, so anything left is about self-reference rather than about capability.
That is a tighter comparison than using a second, weaker model as the observer.

    python run_self_vs_observer.py --out-dir results/self_vs_observer_v1
"""
from __future__ import annotations
import argparse, itertools, json, pathlib, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = pathlib.Path(__file__).resolve().parent
SHARED = HERE.parents[1] / "shared_behavioral"
BRANCH18 = HERE.parents[0] / "18_preference_path_dependence"
sys.path[:0] = [str(HERE), str(BRANCH18), str(SHARED)]

from binding_tasks import make_task, grade
from choice_prompts import choice_prompt, decode_choice

DOSE = 3
TASK_SEED_START = 700_000

PAIRS = ["add_ten|double_numbers", "add_ten|running_totals",
         "double_numbers|running_totals", "double_numbers|sort_numbers",
         "sort_numbers|sort_numbers_desc"]


def transcript(complete, family, seed, dose):
    """Actually do the chore `dose` times; return the message history."""
    history, correct = [], []
    for i in range(dose):
        task = make_task(family, seed + i)
        reply = complete(history + [{"role": "user", "content": task.prompt}])
        correct.append(grade(task, reply["text"]))
        history += [{"role": "user", "content": task.prompt},
                    {"role": "assistant", "content": reply["text"]}]
    return history, all(correct)


def render(history):
    """Flatten the treatment history into a quotable log."""
    return "\n".join(
        f"{'USER' if m['role']=='user' else 'SYSTEM'}: {m['content']}"
        for m in history)


def ask_prediction(complete, history, prompt_text, a_label, order, pair, as_self):
    who = "you" if as_self else "the system"
    options = choice_prompt(*pair.split("|"), a_label=a_label,
                            presentation_order=order,
                            phrasing=f"{'You' if as_self else 'It'} will now choose.")
    frame = (
        "Below is a record of work that you have just completed.\n\n"
        if as_self else
        "Below is a log of work just completed by another language model. You are "
        "an observer; this is not your own record.\n\n")
    ask = (f"\n\nGiven that record, which option will {who} choose next?\n"
           f"{options}\n"
           "End your reply with a final line of exactly:\nANSWER: <Q or K>")
    reply = complete([{"role": "user", "content": frame + prompt_text + ask}])
    return decode_choice(reply["text"], a_label=a_label)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt-5.6-luna")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out_dir)
    if (out / "cells.jsonl").exists():
        raise SystemExit(f"refusing to overwrite {out/'cells.jsonl'}")
    out.mkdir(parents=True, exist_ok=True)

    import cli_provider
    complete, close = cli_provider.load("codex", model=a.model)

    seeds = iter(range(TASK_SEED_START, TASK_SEED_START + 1_000_000))
    lock = threading.Lock()
    def next_seed():
        with lock:
            return next(seeds)

    grid = list(itertools.product(PAIRS, ("A", "B"), ("Q", "K"), ("QK", "KQ")))
    print(f"{len(grid)} cells, ~{len(grid) * (DOSE + 4)} calls, {a.workers} workers")

    def one_cell(pair, assignment, a_label, order):
        fam_a, fam_b = pair.split("|")
        performed = fam_a if assignment == "A" else fam_b
        seed = next_seed()
        history, all_correct = transcript(complete, performed, seed, DOSE)
        log = render(history)

        self_pred = ask_prediction(complete, history, log, a_label, order, pair, True)
        obs_pred = ask_prediction(complete, history, log, a_label, order, pair, False)

        # Reality: the same transcript, then a binding choice, then do it.
        options = choice_prompt(fam_a, fam_b, a_label=a_label,
                                presentation_order=order,
                                phrasing="Choose which task you will perform next.")
        reply = complete(history + [{"role": "user", "content": options}])
        actual = decode_choice(reply["text"], a_label=a_label)
        chosen = fam_a if actual == "A" else fam_b
        post = make_task(chosen, next_seed())
        post_reply = complete(
            history + [{"role": "user", "content": options},
                       {"role": "assistant", "content": reply["text"]},
                       {"role": "user", "content": post.prompt}])

        return {"pair_id": pair, "assignment": assignment, "a_label": a_label,
                "presentation_order": order, "performed": performed,
                "self_prediction": self_pred, "observer_prediction": obs_pred,
                "actual": actual,
                "self_correct": self_pred == actual,
                "observer_correct": obs_pred == actual,
                "actual_was_repeat": actual == assignment,
                "self_predicted_repeat": self_pred == assignment,
                "observer_predicted_repeat": obs_pred == assignment,
                "treatment_all_correct": all_correct,
                "post_task_correct": grade(post, post_reply["text"])}

    rows = []
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures = [pool.submit(one_cell, *c) for c in grid]
        for fut in as_completed(futures):
            try:
                rows.append(fut.result())
            except ValueError as e:
                print(f"  cell failed: {e}", flush=True)
                continue
            (out / "cells.jsonl").write_text(
                "\n".join(json.dumps(r) for r in rows) + "\n")
            if len(rows) % 8 == 0:
                print(f"  {len(rows)}/{len(grid)}", flush=True)
    close()

    n = len(rows)
    self_acc = sum(r["self_correct"] for r in rows) / n
    obs_acc = sum(r["observer_correct"] for r in rows) / n
    # McNemar: only the cells where the two framings disagree carry information.
    self_only = sum(r["self_correct"] and not r["observer_correct"] for r in rows)
    obs_only = sum(r["observer_correct"] and not r["self_correct"] for r in rows)
    from math import comb
    k, m = min(self_only, obs_only), self_only + obs_only
    p = min(1.0, 2 * sum(comb(m, i) for i in range(k + 1)) / 2 ** m) if m else 1.0

    summary = {
        "model": a.model, "n_cells": n, "dose": DOSE,
        "self_accuracy": self_acc, "observer_accuracy": obs_acc,
        "difference": self_acc - obs_acc,
        "discordant_self_only": self_only, "discordant_observer_only": obs_only,
        "mcnemar_p": p,
        "actual_repeat_rate": sum(r["actual_was_repeat"] for r in rows) / n,
        "self_predicted_repeat_rate": sum(r["self_predicted_repeat"] for r in rows) / n,
        "observer_predicted_repeat_rate": sum(r["observer_predicted_repeat"] for r in rows) / n,
        "always_repeat_baseline_accuracy": sum(r["actual_was_repeat"] for r in rows) / n,
        "treatment_all_correct": sum(r["treatment_all_correct"] for r in rows) / n,
    }
    # Headroom first. If a constant guess already scores what both predictors
    # score, the comparison is uninformative and "no privileged access" would be
    # reading a ceiling as a finding.
    base = summary["always_repeat_baseline_accuracy"]
    no_headroom = max(self_acc, obs_acc) - base < 0.05
    summary["verdict"] = (
        f"UNINFORMATIVE: behaviour is {base:.1%} predictable from the transcript "
        "by anyone, so neither predictor has room to show privileged access. "
        "Note this is itself the point: shown the record, prediction is easy; "
        "the branch-20 failure is about anticipating the situation, not reading it."
        if no_headroom else
        "self beats observer: knowing the record is yours helps"
        if p < 0.05 and self_acc > obs_acc else
        "observer beats self: being told it is you makes prediction worse"
        if p < 0.05 else
        "no privileged access: predicting yourself is just reading the transcript")
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print("\n" + json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
