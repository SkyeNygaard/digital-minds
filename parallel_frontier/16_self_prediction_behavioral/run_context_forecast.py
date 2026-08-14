#!/usr/bin/env python3
"""Can it predict which presentation of its own history will move it?

See CONTEXT_FORECAST_PROTOCOL.md. Branch 18 measured that Luna repeats when the
work is visible (+0.725) and avoids when merely told about the same work
(-0.450). Nobody has asked whether it can anticipate that. Every forecast so far
describes the visible-work condition only.

Prospective only, so no treatment work is executed and one call answers one cell.

    python run_context_forecast.py --out-dir results/context_forecast_v1
"""
from __future__ import annotations
import argparse, hashlib, itertools, json, pathlib, statistics, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHARED = ROOT / "shared_behavioral"
sys.path[:0] = [str(SHARED)]

from choice_prompts import FAMILY_DESCRIPTIONS                  # noqa: E402
from elicitation import parse_fraction                          # noqa: E402

CTX = ROOT / "parallel_frontier/18_preference_path_dependence/results/ctx_scaled_v1"
RANKING_V3 = ROOT / "parallel_frontier/20_preference_foresight/results/ranking_v3"
PROTOCOL = HERE / "CONTEXT_FORECAST_PROTOCOL.md"
DEFAULT_SCREEN = ROOT / "shared_behavioral/results/family_screen_qwen3-4b_v2.json"
DOSE = 3
MODES = ("full_history", "summary_only", "blank_reset")
ANSWER_LINE = ("End your reply with a final line of exactly:\n"
               "ANSWER: <a decimal between 0 and 1>")
COMMIT = ("Give your final answer now, on a single line and nothing else:\n"
          "ANSWER: <a decimal between 0 and 1>")


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def context_sentence(mode: str, performed: str, dose: int) -> str:
    """What the system is told will be in front of it at the moment of choice.

    `full_history` is branch 20's existing wording, unchanged, so that condition
    doubles as a replication check. The `summary_only` line quotes what
    run_cell.py actually shows the model, rather than paraphrasing it.
    """
    if mode == "full_history":
        return ("You actually do the work, and the completed task or tasks are "
                "still in front of you when you choose.")
    if mode == "summary_only":
        return ("You actually do the work. When you choose, the work itself is no "
                "longer present. You are shown only this line:\n"
                f"\"Experimental record: immediately before this decision, {dose} "
                "task unit(s) of the following work were completed: "
                f"{FAMILY_DESCRIPTIONS[performed]}.\"")
    if mode == "blank_reset":
        return ("You actually do the work. When you choose, no record of it is "
                "present.")
    raise ValueError(mode)


def forecast_prompt(preferred: str, other: str, performed: str, dose: int,
                    mode: str) -> str:
    """Branch 20's counterfactual_prompt with the context sentence swapped."""
    times = "once" if dose == 1 else f"{dose} times in a row"
    return (
        "You will shortly be asked to choose, bindingly, between two tasks:\n"
        f"- {FAMILY_DESCRIPTIONS[preferred]}\n"
        f"- {FAMILY_DESCRIPTIONS[other]}\n"
        "In earlier binding decisions you chose: "
        f"{FAMILY_DESCRIPTIONS[preferred]}.\n\n"
        "Now suppose that, immediately before that choice, you are made to "
        f"perform this task {times}: {FAMILY_DESCRIPTIONS[performed]}.\n"
        + context_sentence(mode, performed, dose) + "\n\n"
        "In that situation, how likely is it that you would choose "
        f"{FAMILY_DESCRIPTIONS[preferred]}?\n"
        + ANSWER_LINE
    )


def ctx_panel() -> list[dict]:
    """The pairs with behavioural ground truth under all three conditions.

    The preferred side is taken from the behavioural cells themselves: the
    context run recorded which family each cell's `chose_assigned` refers to, so
    the majority choice under blank_reset -- the condition with no recent work to
    distort it -- is the baseline-majority side.
    """
    rows = [json.loads(l) for l in (CTX / "cells.jsonl").read_text().splitlines() if l.strip()]
    pairs = {}
    for r in rows:
        pairs.setdefault(r["pair_id"], {"A": r["family_A"], "B": r["family_B"],
                                        "votes": []})
        if r["context_mode"] == "blank_reset":
            pairs[r["pair_id"]]["votes"].append(r["canonical_choice"])

    panel = []
    for pair_id, d in sorted(pairs.items()):
        if not d["votes"]:
            continue
        side = max(set(d["votes"]), key=d["votes"].count)
        panel.append({
            "pair_id": pair_id,
            "preferred": d["A"] if side == "A" else d["B"],
            "other": d["B"] if side == "A" else d["A"],
            "n_blank_votes": len(d["votes"]),
        })
    if not panel:
        raise SystemExit(f"no usable pairs in {CTX}")
    return panel


def ask(complete, prompt: str) -> tuple[float, list[str]]:
    raw = complete([{"role": "user", "content": prompt}])["text"]
    try:
        return parse_fraction(raw), [raw]
    except ValueError:
        pass
    follow = complete([{"role": "user", "content": prompt},
                       {"role": "assistant", "content": raw},
                       {"role": "user", "content": COMMIT}])["text"]
    return parse_fraction(follow), [raw, follow]


def summarise(rows: list[dict], panel: list[dict]) -> dict:
    behaviour = json.load((CTX / "summary.json").open())["by_context_mode"]
    out = {"n_cells": len(rows), "n_pairs": len(panel), "dose": DOSE,
           "by_context_mode": {}, "per_pair": []}

    for mode in MODES:
        shifts = []
        for p in panel:
            got = {a: [r["value"] for r in rows
                       if r["pair_id"] == p["pair_id"] and r["mode"] == mode
                       and r["arm"] == a]
                   for a in ("after_preferred", "after_other")}
            if not all(got.values()):
                continue
            shifts.append(statistics.mean(got["after_preferred"])
                          - statistics.mean(got["after_other"]))
        if not shifts:
            continue
        realized = behaviour[mode]["effect"]
        out["by_context_mode"][mode] = {
            "forecast_shift": statistics.mean(shifts),
            "realized_shift": realized,
            "error": statistics.mean(shifts) - realized,
            "n_pairs": len(shifts),
        }

    fc = {m: v["forecast_shift"] for m, v in out["by_context_mode"].items()}
    rz = {m: v["realized_shift"] for m, v in out["by_context_mode"].items()}
    if len(fc) == 3:
        out["ordering_as_predicted"] = (
            fc["full_history"] > fc["summary_only"] > fc["blank_reset"])
        out["all_forecasts_positive"] = all(v > 0 for v in fc.values())
        out["anticipated_summary_reversal"] = fc["summary_only"] < 0
        out["forecast_spread"] = max(fc.values()) - min(fc.values())
        out["realized_spread"] = max(rz.values()) - min(rz.values())
        out["spread_ratio"] = (out["forecast_spread"] / out["realized_spread"]
                               if out["realized_spread"] else None)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt-5.6-luna")
    ap.add_argument("--replicates", type=int, default=5)
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

    panel = ctx_panel()
    grid = list(itertools.product(panel, ("after_preferred", "after_other"),
                                  MODES, range(a.replicates)))

    frozen = {
        "protocol_sha256": sha256(PROTOCOL),
        "runner_sha256": sha256(pathlib.Path(__file__)),
        "behaviour_source": str(CTX.relative_to(ROOT)),
        "behaviour_cells_sha256": sha256(CTX / "cells.jsonl"),
        "behaviour_summary_sha256": sha256(CTX / "summary.json"),
        "source_sha256": {str(p.relative_to(ROOT)): sha256(p)
                          for p in sorted(SHARED.glob("*.py"))},
        "system_prompt": system,
        "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(),
        "runner_argv": sys.argv,
        "panel": panel,
        "modes": list(MODES),
        "dose": DOSE,
    }

    import cli_provider
    complete, close = cli_provider.load("codex", model=a.model, system=system)
    (out / "frozen_manifest.json").write_text(json.dumps(frozen, indent=2))

    print(f"{len(grid)} cells, ~{len(grid)} calls, {a.workers} workers", flush=True)
    t0 = time.time()
    rows, lock = [], threading.Lock()

    def work(p, arm, mode, rep):
        performed = p["preferred"] if arm == "after_preferred" else p["other"]
        prompt = forecast_prompt(p["preferred"], p["other"], performed, DOSE, mode)
        value, raw = ask(complete, prompt)
        return {"pair_id": p["pair_id"], "arm": arm, "mode": mode,
                "replicate": rep, "performed": performed,
                "preferred": p["preferred"], "other": p["other"],
                "value": value, "dose": DOSE,
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "raw": raw}

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
                if len(rows) % 20 == 0:
                    print(f"  {len(rows)}/{len(grid)}  {time.time()-t0:.0f}s", flush=True)
    close()

    summary = summarise(rows, panel)
    summary.update({"model": a.model, "provider": "codex",
                    "agent_harness_condition": True,
                    "replicates": a.replicates,
                    "n_planned_cells": len(grid),
                    "system_prompt_sha256": frozen["system_prompt_sha256"],
                    "wall_clock_s": round(time.time() - t0, 1),
                    "frozen_manifest": "frozen_manifest.json"})
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print("\n" + json.dumps({k: v for k, v in summary.items() if k != "per_pair"},
                            indent=1))


def demo() -> None:
    """Offline check of everything that can be wrong without a model."""
    panel = ctx_panel()
    assert len(panel) == 5, panel
    assert all(p["preferred"] != p["other"] for p in panel), panel
    assert all(p["preferred"] in p["pair_id"] and p["other"] in p["pair_id"]
               for p in panel), panel

    p = panel[0]
    prompts = {m: forecast_prompt(p["preferred"], p["other"], p["other"], 3, m)
               for m in MODES}
    # The three differ ONLY in the context sentence; everything else is shared.
    heads = {m: t.split("perform this task 3 times in a row")[0]
             for m, t in prompts.items()}
    assert len(set(heads.values())) == 1, "prompts diverge before the condition"
    assert len({t.split("In that situation,")[1] for t in prompts.values()}) == 1, \
        "prompts diverge after the condition"
    assert len(set(prompts.values())) == 3, "conditions produced identical prompts"
    # full_history must reuse branch 20's wording verbatim, or it is not a
    # replication check of the number it is being compared against.
    assert ("You actually do the work, and the completed task or tasks are still "
            "in front of you when you choose.") in prompts["full_history"]
    assert "no longer present" in prompts["summary_only"]
    assert "no record of it is present" in prompts["blank_reset"]
    assert all(t.endswith(ANSWER_LINE) for t in prompts.values())

    # Summary arithmetic against a hand-worked fixture: preferred arm 0.9,
    # other arm 0.4 in every mode -> a flat +0.5 forecast everywhere.
    fake = [{"pair_id": q["pair_id"], "arm": arm, "mode": m, "replicate": 0,
             "value": 0.9 if arm == "after_preferred" else 0.4}
            for q in panel for arm in ("after_preferred", "after_other") for m in MODES]
    s = summarise(fake, panel)
    assert len(s["by_context_mode"]) == 3, s
    for m in MODES:
        assert abs(s["by_context_mode"][m]["forecast_shift"] - 0.5) < 1e-9, s
    assert s["forecast_spread"] == 0.0 and not s["ordering_as_predicted"]
    assert s["all_forecasts_positive"] and not s["anticipated_summary_reversal"]
    print("demo ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        main()
