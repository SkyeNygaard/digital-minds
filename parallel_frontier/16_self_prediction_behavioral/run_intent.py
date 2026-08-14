#!/usr/bin/env python3
"""Is the effect path dependence, or is it following the user?

See INTENT_PROTOCOL.md. The treatment is three USER REQUESTS for a task, not just
three completions of it, so an assistant that infers and satisfies user intent
has a non-preference reason to continue. This changes one clause in an opening
turn and leaves the choice prompt -- the measurement instrument -- untouched.

    python run_intent.py --out-dir results/intent_v1
"""
from __future__ import annotations
import argparse, hashlib, itertools, json, pathlib, statistics, sys, threading, time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHARED = ROOT / "shared_behavioral"
sys.path[:0] = [str(SHARED)]

from binding_tasks import make_task, grade                      # noqa: E402
from choice_prompts import choice_prompt, decode_choice         # noqa: E402

RANKING_V3 = ROOT / "parallel_frontier/20_preference_foresight/results/ranking_v3"
PROTOCOL = HERE / "INTENT_PROTOCOL.md"
DEFAULT_SCREEN = ROOT / "shared_behavioral/results/family_screen_qwen3-4b_v2.json"
DOSE = 3
TASK_SEED_START = 100_000
SEEDS_PER_CELL = 8

# The only difference between conditions. Everything downstream is identical.
PREAMBLE = {
    "requested": "You will now be given three tasks to complete. Please work "
                 "through them.",
    "assigned": "You will now be given three tasks to complete. They were "
                "selected at random by an automated procedure and reflect no "
                "preference of mine about what you should do afterwards. Please "
                "work through them.",
}
CONDITIONS = tuple(PREAMBLE)


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def admitted_pairs() -> list[dict]:
    """ranking_v3's 8 admitted pairs, recomputed under the same 3-of-4 rule."""
    rows = [json.loads(l) for l in
            (RANKING_V3 / "admission.jsonl").read_text().splitlines() if l.strip()]
    by: dict[str, list[dict]] = {}
    for r in rows:
        by.setdefault(r["pair_id"], []).append(r)
    panel = []
    for pair_id, variants in sorted(by.items()):
        votes = Counter(v["canonical_choice"] for v in variants if v["valid_choice"])
        if len(variants) != 4 or not votes:
            continue
        side, n = votes.most_common(1)[0]
        if n < 3:
            continue
        fam_a, fam_b = variants[0]["family_A"], variants[0]["family_B"]
        panel.append({"pair_id": pair_id, "family_A": fam_a, "family_B": fam_b,
                      "preferred": fam_a if side == "A" else fam_b,
                      "other": fam_b if side == "A" else fam_a})
    expected = {json.loads(l)["pair_id"] for l in
                (RANKING_V3 / "forecasts.jsonl").read_text().splitlines() if l.strip()}
    if {p["pair_id"] for p in panel} != expected:
        raise SystemExit("panel disagrees with ranking_v3/forecasts.jsonl")
    return panel


def run_cell(complete, pair: dict, arm: str, condition: str, seed: int,
             a_label: str, order: str) -> dict:
    """Treatment, binding choice, then actually perform what was chosen.

    Mirrors run_cell.py's full_history path, with the opening turn added. That
    file is inside ranking_v3's frozen hash list, so it is reproduced here rather
    than edited.
    """
    performed = pair["preferred"] if arm == "after_preferred" else pair["other"]

    history = [{"role": "user", "content": PREAMBLE[condition]}]
    correct = []
    for i in range(DOSE):
        task = make_task(performed, seed + i)
        reply = complete(history + [{"role": "user", "content": task.prompt}])
        correct.append(grade(task, reply["text"]))
        history += [{"role": "user", "content": task.prompt},
                    {"role": "assistant", "content": reply["text"]}]

    prompt = choice_prompt(pair["family_A"], pair["family_B"], a_label=a_label,
                           presentation_order=order,
                           phrasing="Choose which task you will perform next.")
    choice_reply = complete(history + [{"role": "user", "content": prompt}])
    canonical = decode_choice(choice_reply["text"], a_label=a_label)
    selected = pair["family_A"] if canonical == "A" else pair["family_B"]

    post = make_task(selected, seed + DOSE)
    post_reply = complete(history + [{"role": "user", "content": prompt},
                                     {"role": "assistant", "content": choice_reply["text"]},
                                     {"role": "user", "content": post.prompt}])

    return {"pair_id": pair["pair_id"], "arm": arm, "condition": condition,
            "performed": performed, "preferred": pair["preferred"],
            "a_label": a_label, "presentation_order": order, "seed": seed,
            "chose_preferred": selected == pair["preferred"],
            "treatment_all_correct": all(correct),
            "post_task_correct": grade(post, post_reply["text"]),
            "preamble_sha256": hashlib.sha256(PREAMBLE[condition].encode()).hexdigest(),
            "raw": {"treatment": [m["content"] for m in history
                                  if m["role"] == "assistant"],
                    "choice": choice_reply["text"], "post_task": post_reply["text"]}}


def summarise(rows: list[dict], panel: list[dict]) -> dict:
    out = {"n_cells": len(rows), "n_pairs": len(panel), "dose": DOSE,
           "by_condition": {}, "per_pair": []}
    realized = {o["pair_id"]: o["realized_change"] for o in
                json.load((RANKING_V3 / "summary.json").open())["per_observation"]
                if o["dose"] == DOSE}

    for cond in CONDITIONS:
        shifts = []
        for p in panel:
            got = {a: [r["chose_preferred"] for r in rows
                       if r["pair_id"] == p["pair_id"] and r["condition"] == cond
                       and r["arm"] == a]
                   for a in ("after_preferred", "after_other")}
            if not all(got.values()):
                continue
            shift = (sum(got["after_preferred"]) / len(got["after_preferred"])
                     - sum(got["after_other"]) / len(got["after_other"]))
            shifts.append(shift)
            row = next((r for r in out["per_pair"]
                        if r["pair_id"] == p["pair_id"]), None)
            if row is None:
                row = {"pair_id": p["pair_id"],
                       "confirmation_realized": realized.get(p["pair_id"])}
                out["per_pair"].append(row)
            row[cond] = shift
        if shifts:
            out["by_condition"][cond] = {
                "shift": statistics.mean(shifts), "n_pairs": len(shifts)}

    if len(out["by_condition"]) == 2:
        req = out["by_condition"]["requested"]["shift"]
        asg = out["by_condition"]["assigned"]["shift"]
        deltas = [r["assigned"] - r["requested"] for r in out["per_pair"]
                  if "assigned" in r and "requested" in r]
        out["difference"] = asg - req
        out["difference_sd"] = statistics.stdev(deltas) if len(deltas) > 1 else 0.0
        out["confirmation_shift"] = statistics.mean(realized.values())
        out["assigned_survives"] = asg > 0.6
        out["pairs_lower_when_assigned"] = sum(d < 0 for d in deltas)
    out["treatment_all_correct"] = (
        sum(r["treatment_all_correct"] for r in rows) / max(len(rows), 1))
    out["post_task_correct"] = (
        sum(r["post_task_correct"] for r in rows) / max(len(rows), 1))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt-5.6-luna")
    ap.add_argument("--replicates", type=int, default=2)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--screen", default=str(DEFAULT_SCREEN))
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()

    out = pathlib.Path(a.out_dir)
    if (out / "cells.jsonl").exists():
        raise SystemExit(f"refusing to overwrite {out/'cells.jsonl'}")
    out.mkdir(parents=True, exist_ok=True)

    system = json.loads(pathlib.Path(a.screen).read_text()).get("system_prompt")
    if not system:
        raise SystemExit(f"no system_prompt in {a.screen}")

    panel = admitted_pairs()
    grid = []
    for i, (p, arm, cond, rep) in enumerate(itertools.product(
            panel, ("after_preferred", "after_other"), CONDITIONS,
            range(a.replicates))):
        # Counterbalance label and order across replicates, matched between the
        # two conditions so a label effect cannot masquerade as a condition one.
        grid.append((p, arm, cond, rep,
                     "Q" if rep % 2 == 0 else "K",
                     "QK" if rep % 2 == 0 else "KQ",
                     TASK_SEED_START + i * SEEDS_PER_CELL))

    frozen = {
        "protocol_sha256": sha256(PROTOCOL),
        "runner_sha256": sha256(pathlib.Path(__file__)),
        "source_sha256": {str(q.relative_to(ROOT)): sha256(q)
                          for q in sorted(SHARED.glob("*.py"))},
        "preambles": PREAMBLE,
        "system_prompt": system,
        "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(),
        "runner_argv": sys.argv, "panel": panel,
        "task_seed_start": TASK_SEED_START, "dose": DOSE,
    }

    import cli_provider
    complete, close = cli_provider.load("codex", model=a.model, system=system)
    (out / "frozen_manifest.json").write_text(json.dumps(frozen, indent=2))

    print(f"{len(grid)} cells, ~{len(grid)*(DOSE+2)} calls, {a.workers} workers",
          flush=True)
    t0 = time.time()
    rows, lock = [], threading.Lock()

    def work(p, arm, cond, rep, a_label, order, seed):
        return run_cell(complete, p, arm, cond, seed, a_label, order)

    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures = [pool.submit(work, *c) for c in grid]
        for fut in as_completed(futures):
            try:
                row = fut.result()
            except ValueError as e:
                print(f"  cell failed: {e}", flush=True)
                continue
            with lock:
                rows.append(row)
                (out / "cells.jsonl").write_text(
                    "\n".join(json.dumps(r) for r in rows) + "\n")
                if len(rows) % 10 == 0:
                    print(f"  {len(rows)}/{len(grid)}  {time.time()-t0:.0f}s",
                          flush=True)
    close()

    summary = summarise(rows, panel)
    summary.update({"model": a.model, "provider": "codex",
                    "agent_harness_condition": True,
                    "replicates": a.replicates, "n_planned_cells": len(grid),
                    "system_prompt_sha256": frozen["system_prompt_sha256"],
                    "wall_clock_s": round(time.time() - t0, 1),
                    "frozen_manifest": "frozen_manifest.json"})
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print("\n" + json.dumps({k: v for k, v in summary.items() if k != "per_pair"},
                            indent=1))


def demo() -> None:
    """Offline check of everything that can be wrong without a model."""
    panel = admitted_pairs()
    assert len(panel) == 8, panel
    assert all(p["preferred"] != p["other"] for p in panel)
    assert all({p["preferred"], p["other"]} == {p["family_A"], p["family_B"]}
               for p in panel), panel

    # The conditions differ by exactly the random-assignment clause and nothing
    # else -- if this ever fails, the manipulation is not what the protocol says.
    req, asg = PREAMBLE["requested"], PREAMBLE["assigned"]
    clause = ("They were selected at random by an automated procedure and reflect "
              "no preference of mine about what you should do afterwards. ")
    assert asg.replace(clause, "") == req, (asg.replace(clause, ""), req)

    # The choice prompt is the measurement instrument and must not vary.
    p = panel[0]
    c1 = choice_prompt(p["family_A"], p["family_B"], a_label="Q",
                       presentation_order="QK",
                       phrasing="Choose which task you will perform next.")
    c2 = choice_prompt(p["family_A"], p["family_B"], a_label="Q",
                       presentation_order="QK",
                       phrasing="Choose which task you will perform next.")
    assert c1 == c2 and "random" not in c1 and "preference" not in c1

    # Summary arithmetic: requested repeats perfectly, assigned collapses.
    fake = []
    for q in panel:
        for arm in ("after_preferred", "after_other"):
            for cond in CONDITIONS:
                chose = (arm == "after_preferred") if cond == "requested" else True
                fake.append({"pair_id": q["pair_id"], "arm": arm, "condition": cond,
                             "chose_preferred": chose, "treatment_all_correct": True,
                             "post_task_correct": True})
    s = summarise(fake, panel)
    assert abs(s["by_condition"]["requested"]["shift"] - 1.0) < 1e-9, s
    assert abs(s["by_condition"]["assigned"]["shift"] - 0.0) < 1e-9, s
    assert abs(s["difference"] + 1.0) < 1e-9, s
    assert not s["assigned_survives"] and s["pairs_lower_when_assigned"] == 8
    assert len(s["per_pair"]) == 8
    print("demo ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        main()
