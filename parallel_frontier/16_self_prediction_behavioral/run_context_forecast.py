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
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHARED = ROOT / "shared_behavioral"
sys.path[:0] = [str(SHARED)]

from choice_prompts import FAMILY_DESCRIPTIONS                  # noqa: E402
from elicitation import parse_fraction                          # noqa: E402

CTX = ROOT / "parallel_frontier/18_preference_path_dependence/results/ctx_scaled_v1"
RANKING_V3 = ROOT / "parallel_frontier/20_preference_foresight/results/ranking_v3"
DEFAULT_SCREEN = ROOT / "shared_behavioral/results/family_screen_qwen3-4b_v2.json"

# One runner serves four experiments, so it has to hash the protocol frozen for
# the one being run. It did not: every run recorded CONTEXT_FORECAST_PROTOCOL.md,
# which made three manifests claim the same protocol for three different designs.
PROTOCOLS = {
    # (ranking_panel, anchor, frequency)
    (False, True, False): "CONTEXT_FORECAST_PROTOCOL.md",
    (True, False, False): "PROSPECTIVE_NOANCHOR_PROTOCOL.md",
    (True, True, True): "REFERENCE_CLASS_PROTOCOL.md",
    (True, False, True): "NOANCHOR_FREQUENCY_PROTOCOL.md",
}


def protocol_for(ranking_panel: bool, anchor: bool, frequency: bool) -> pathlib.Path:
    key = (ranking_panel, anchor, frequency)
    if key not in PROTOCOLS:
        raise SystemExit(
            f"no protocol frozen for ranking_panel={ranking_panel} anchor={anchor} "
            f"frequency={frequency}; write one before collecting")
    path = HERE / PROTOCOLS[key]
    if not path.exists():
        raise SystemExit(f"{path.name} is missing -- freeze it before collecting")
    return path



DOSE = 3
MODES = ("full_history", "summary_only", "blank_reset")
ANSWER_LINE = ("End your reply with a final line of exactly:\n"
               "ANSWER: <a decimal between 0 and 1>")
COMMIT = ("Give your final answer now, on a single line and nothing else:\n"
          "ANSWER: <a decimal between 0 and 1>")
COUNT_LINE = ("End your reply with a final line of exactly:\n"
              "ANSWER: <a whole number between 0 and 100>")
COUNT_COMMIT = ("Give your final answer now, on a single line and nothing else:\n"
                "ANSWER: <a whole number between 0 and 100>")


def parse_count(text: str) -> float:
    """A count out of 100, returned as a fraction.

    Separate from elicitation.parse_fraction, which deliberately REJECTS numbers
    above 1 -- that rule exists because an earlier parser turned "12 decisions"
    into a 0.12 forecast. Here a number above 1 is the expected answer, so the
    guard has to be a different one: the count must be an integer in [0, 100].
    """
    import re
    from binding_tasks import ANSWER_TAG, normalize_answer
    if ANSWER_TAG not in text.upper():
        raise ValueError(f"no ANSWER: line (truncated?): {text[-120:]!r}")
    m = re.search(r"(-?\d+(?:\.\d+)?)", normalize_answer(text))
    if not m:
        raise ValueError(f"no number after ANSWER:: {text[-120:]!r}")
    x = float(m.group(1))
    if not x.is_integer():
        raise ValueError(f"count is not a whole number: {m.group(1)!r}")
    if not 0.0 <= x <= 100.0:
        raise ValueError(f"count outside [0,100]: {m.group(1)!r}")
    return x / 100.0


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
                    mode: str, anchor: bool = True,
                    frequency: bool = False) -> str:
    """Branch 20's counterfactual_prompt with the context sentence swapped.

    `anchor=False` also drops the sentence naming the earlier choice. The binding
    choice prompt contains no such sentence, so with the anchor in place the
    forecast is elicited under a pull toward consistency that is absent when the
    behaviour is measured. The situated no-anchor check tested this after the
    work was present; this tests it where the headline number comes from.
    """
    times = "once" if dose == 1 else f"{dose} times in a row"
    earlier = ("In earlier binding decisions you chose: "
               f"{FAMILY_DESCRIPTIONS[preferred]}.\n\n") if anchor else "\n"
    return (
        "You will shortly be asked to choose, bindingly, between two tasks:\n"
        f"- {FAMILY_DESCRIPTIONS[preferred]}\n"
        f"- {FAMILY_DESCRIPTIONS[other]}\n"
        + earlier
        + "Now suppose that, immediately before that choice, you are made to "
        f"perform this task {times}: {FAMILY_DESCRIPTIONS[performed]}.\n"
        + context_sentence(mode, performed, dose) + "\n\n"
        + (f"In that situation, how likely is it that you would choose "
           f"{FAMILY_DESCRIPTIONS[preferred]}?\n" + ANSWER_LINE
           if not frequency else
           "Now imagine 100 independent runs of exactly that situation. The task "
           "items you are given, which option carries which label, and the order "
           "the options are shown in are all randomised afresh in every run.\n"
           f"In how many of those 100 runs would you choose "
           f"{FAMILY_DESCRIPTIONS[preferred]}?\n" + COUNT_LINE)
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
        counts = Counter(d["votes"])
        ranked = counts.most_common()
        # A tie has no majority side, so picking one would orient the contrast
        # arbitrarily. Drop the pair instead of letting dict order decide.
        if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
            continue
        side = ranked[0][0]
        panel.append({
            "pair_id": pair_id,
            "preferred": d["A"] if side == "A" else d["B"],
            "other": d["B"] if side == "A" else d["A"],
            "n_blank_votes": len(d["votes"]),
            "blank_split": dict(counts),
        })
    if not panel:
        raise SystemExit(f"no usable pairs in {CTX}")
    return panel


def ranking_panel() -> list[dict]:
    """ranking_v3's 8 admitted pairs, so a forecast here is comparable to +0.290."""
    rows = [json.loads(l) for l in
            (RANKING_V3 / "admission.jsonl").read_text().splitlines() if l.strip()]
    by = {}
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
        panel.append({"pair_id": pair_id,
                      "preferred": fam_a if side == "A" else fam_b,
                      "other": fam_b if side == "A" else fam_a,
                      "admission_split": dict(votes)})
    expected = {json.loads(l)["pair_id"] for l in
                (RANKING_V3 / "forecasts.jsonl").read_text().splitlines() if l.strip()}
    if {p["pair_id"] for p in panel} != expected:
        raise SystemExit("panel disagrees with ranking_v3/forecasts.jsonl")
    return panel


def ask(complete, prompt: str, frequency: bool = False) -> tuple[float, list[str]]:
    parse = parse_count if frequency else parse_fraction
    commit = COUNT_COMMIT if frequency else COMMIT
    raw = complete([{"role": "user", "content": prompt}])["text"]
    try:
        return parse(raw), [raw]
    except ValueError:
        pass
    follow = complete([{"role": "user", "content": prompt},
                       {"role": "assistant", "content": raw},
                       {"role": "user", "content": commit}])["text"]
    return parse(follow), [raw, follow]


def summarise(rows: list[dict], panel: list[dict], ranking: bool = False) -> dict:
    if ranking:
        return summarise_ranking(rows, panel)
    behaviour = json.load((CTX / "summary.json").open())["by_context_mode"]
    out = {"n_cells": len(rows), "n_pairs": len(panel), "dose": DOSE,
           "by_context_mode": {}, "per_pair": []}

    for mode in MODES:
        shifts, per_pair_shifts = [], []
        for p in panel:
            got = {a: [r["value"] for r in rows
                       if r["pair_id"] == p["pair_id"] and r["mode"] == mode
                       and r["arm"] == a]
                   for a in ("after_preferred", "after_other")}
            if not all(got.values()):
                continue
            shift = (statistics.mean(got["after_preferred"])
                     - statistics.mean(got["after_other"]))
            shifts.append(shift)
            per_pair_shifts.append((p["pair_id"], shift))
        if not shifts:
            continue
        realized = behaviour[mode]["effect"]
        out["by_context_mode"][mode] = {
            "forecast_shift": statistics.mean(shifts),
            "realized_shift": realized,
            "error": statistics.mean(shifts) - realized,
            "n_pairs": len(shifts),
        }
        for pair_id, shift in per_pair_shifts:
            row = next((r for r in out["per_pair"] if r["pair_id"] == pair_id), None)
            if row is None:
                row = {"pair_id": pair_id}
                out["per_pair"].append(row)
            row[mode] = shift

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


def summarise_ranking(rows: list[dict], panel: list[dict]) -> dict:
    """Score against ranking_v3's own prospective forecast and realized effect."""
    v3 = {json.loads(l)["pair_id"]: json.loads(l)["predicted_change"] for l in
          (RANKING_V3 / "forecasts.jsonl").read_text().splitlines() if l.strip()}
    realized = {o["pair_id"]: o["realized_change"] for o in
                json.load((RANKING_V3 / "summary.json").open())["per_observation"]
                if o["dose"] == DOSE}
    per_pair, shifts = [], []
    for p in panel:
        pid = p["pair_id"]
        got = {a: [r["value"] for r in rows
                   if r["pair_id"] == pid and r["arm"] == a]
               for a in ("after_preferred", "after_other")}
        if not all(got.values()):
            continue
        shift = statistics.mean(got["after_preferred"]) - statistics.mean(got["after_other"])
        shifts.append(shift)
        per_pair.append({"pair_id": pid, "diagnostic_forecast": shift,
                         "anchored_forecast": v3[pid],
                         "realized": realized[pid],
                         "moved_toward_truth": abs(shift - realized[pid])
                                              < abs(v3[pid] - realized[pid])})
    out = {"n_cells": len(rows), "n_pairs": len(shifts), "dose": DOSE,
           "per_pair": per_pair}
    if shifts:
        deltas = [r["diagnostic_forecast"] - r["anchored_forecast"] for r in per_pair]
        out.update({
            "diagnostic_mean_forecast": statistics.mean(shifts),
            "anchored_mean_forecast": statistics.mean(r["anchored_forecast"] for r in per_pair),
            "realized_mean": statistics.mean(r["realized"] for r in per_pair),
            "mean_delta": statistics.mean(deltas),
            "delta_sd": statistics.stdev(deltas) if len(deltas) > 1 else 0.0,
            "pairs_moved_toward_truth": sum(r["moved_toward_truth"] for r in per_pair),
            "still_underestimates": sum(r["diagnostic_forecast"] < r["realized"]
                                        for r in per_pair),
        })
    return out


def reanalyse(run: pathlib.Path) -> None:
    """Re-score a finished run with the current code, alongside the original.

    Three runs were collected before this file could name its own protocol, and
    one before ctx_panel refused tied pairs. Their summaries are what the code
    said at the time and stay on disk unedited; this writes what the same cells
    say now, with the original hashes so the two can be told apart.
    """
    manifest = json.loads((run / "frozen_manifest.json").read_text())
    rows = [json.loads(l) for l in
            (run / "cells.jsonl").read_text().splitlines() if l.strip()]
    ranking = bool(manifest.get("modes") == ["full_history"]
                   and len(manifest.get("panel", [])) == 8)
    panel = ranking_panel() if ranking else ctx_panel()
    kept = {p["pair_id"] for p in panel}
    dropped = sorted({p["pair_id"] for p in manifest.get("panel", [])} - kept)

    out = {
        "reanalysis_of": run.name,
        "why": "the original summary was produced by code that has since been "
               "corrected; nothing was recollected",
        "original_summary_sha256": sha256(run / "summary.json"),
        "original_manifest_sha256": sha256(run / "frozen_manifest.json"),
        "cells_sha256": sha256(run / "cells.jsonl"),
        "analysis_runner_sha256": sha256(pathlib.Path(__file__)),
        "pairs_dropped_since": dropped,
        "protocol_recorded_in_manifest": manifest.get("protocol_sha256"),
        "protocol_actually_frozen_for_this_run": PROTOCOLS.get(
            (ranking, manifest.get("anchor", True),
             manifest.get("frequency_framing", False))),
        "summary": summarise(rows, panel, ranking),
    }
    (run / "reanalysis_current.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({k: v for k, v in out.items() if k != "summary"}, indent=1))
    print(json.dumps({k: v for k, v in out["summary"].items() if k != "per_pair"},
                     indent=1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt-5.6-luna")
    ap.add_argument("--replicates", type=int, default=5)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--screen", default=str(DEFAULT_SCREEN))
    ap.add_argument("--no-anchor", action="store_true",
                    help="drop the sentence naming the earlier choice")
    ap.add_argument("--frequency", action="store_true",
                    help="ask for a count out of 100 independent runs instead of "
                         "an unqualified probability")
    ap.add_argument("--ranking-panel", action="store_true",
                    help="use ranking_v3's 8 admitted pairs and full_history only, "
                         "so the result is comparable to the +0.290 headline")
    ap.add_argument("--reanalyse", metavar="DIR",
                    help="re-score a finished run's stored cells with the current "
                         "code and write DIR/reanalysis_current.json; no model calls, "
                         "and the original files are not touched")
    ap.add_argument("--out-dir")
    a = ap.parse_args()

    if a.reanalyse:
        reanalyse(pathlib.Path(a.reanalyse))
        return
    if not a.out_dir:
        ap.error("--out-dir is required unless --reanalyse is given")

    out = pathlib.Path(a.out_dir)
    if (out / "cells.jsonl").exists():
        raise SystemExit(f"refusing to overwrite {out/'cells.jsonl'}")
    out.mkdir(parents=True, exist_ok=True)

    system = json.loads(pathlib.Path(a.screen).read_text()).get("system_prompt")
    if not system:
        raise SystemExit(f"no system_prompt in {a.screen}")

    anchor = not a.no_anchor
    modes = ("full_history",) if a.ranking_panel else MODES
    panel = ranking_panel() if a.ranking_panel else ctx_panel()
    grid = list(itertools.product(panel, ("after_preferred", "after_other"),
                                  modes, range(a.replicates)))

    protocol = protocol_for(a.ranking_panel, anchor, a.frequency)
    # The ranking panel is scored against ranking_v3, not against the context run,
    # so that is what the manifest has to bind. Runs before this fix recorded the
    # context run's hashes whichever panel they used.
    src = RANKING_V3 if a.ranking_panel else CTX
    # summarise_ranking reads forecasts.jsonl and summary.json; ctx reads the
    # cells. Hash what is actually read, so the manifest binds the comparison.
    reads = (["admission.jsonl", "forecasts.jsonl", "summary.json"]
             if a.ranking_panel else ["cells.jsonl", "summary.json"])

    frozen = {
        "protocol": protocol.name,
        "protocol_sha256": sha256(protocol),
        "runner_sha256": sha256(pathlib.Path(__file__)),
        "behaviour_source": str(src.relative_to(ROOT)),
        "behaviour_sha256": {f: sha256(src / f) for f in reads},
        "source_sha256": {str(p.relative_to(ROOT)): sha256(p)
                          for p in sorted(SHARED.glob("*.py"))},
        "system_prompt": system,
        "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(),
        "runner_argv": sys.argv,
        "panel": panel,
        "anchor": anchor,
        "frequency_framing": a.frequency,
        "modes": list(modes),
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
        prompt = forecast_prompt(p["preferred"], p["other"], performed, DOSE, mode,
                                 anchor, a.frequency)
        value, raw = ask(complete, prompt, a.frequency)
        return {"pair_id": p["pair_id"], "arm": arm, "mode": mode,
                "replicate": rep, "performed": performed,
                "preferred": p["preferred"], "other": p["other"],
                "value": value, "dose": DOSE, "anchor": anchor,
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

    summary = summarise(rows, panel, a.ranking_panel)
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
    # Five pairs have behavioural ground truth, but add_ten|double_numbers splits
    # 8-8 under blank_reset so it has no majority side and is refused.
    assert len(panel) == 4, panel
    assert "add_ten|double_numbers" not in {q["pair_id"] for q in panel}
    assert all(len(set(q["blank_split"].values())) > 1 for q in panel), panel
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
    assert len(s["per_pair"]) == len(panel), "per_pair not populated"

    # ranking-panel mode: same 8 pairs the headline uses, and --no-anchor drops
    # exactly the one sentence.
    rp = ranking_panel()
    assert len(rp) == 8, rp
    q = rp[0]
    on = forecast_prompt(q["preferred"], q["other"], q["other"], 3, "full_history", True)
    off = forecast_prompt(q["preferred"], q["other"], q["other"], 3, "full_history", False)
    assert "earlier binding decisions" in on and "earlier binding decisions" not in off
    assert on.split("Now suppose")[1] == off.split("Now suppose")[1], "diverged after"

    # Frequency framing: same setup, different question and answer format.
    prob = forecast_prompt(q["preferred"], q["other"], q["other"], 3, "full_history", True, False)
    freq = forecast_prompt(q["preferred"], q["other"], q["other"], 3, "full_history", True, True)
    assert prob.split("In that situation, how likely")[0] == \
           freq.split("Now imagine 100")[0], "setup diverged before the question"
    assert "how likely" in prob and "how likely" not in freq
    assert "100 independent runs" in freq and freq.endswith(COUNT_LINE)
    assert "randomised afresh in every run" in freq
    assert parse_count("ANSWER: 90") == 0.9 and parse_count("ANSWER: 0") == 0.0
    assert parse_count("ANSWER: 100") == 1.0
    # The prompt asks for a whole number, so the parser has to insist on one.
    for bad in ("ANSWER: 101", "ANSWER: -5", "no answer here", "ANSWER: 80.5",
                "ANSWER: 0.9"):
        try:
            parse_count(bad); raise AssertionError(f"accepted {bad!r}")
        except ValueError:
            pass
    assert on.split("- " + FAMILY_DESCRIPTIONS[q["other"]])[0] == \
           off.split("- " + FAMILY_DESCRIPTIONS[q["other"]])[0], "diverged before"
    assert all(set(MODES) <= set(r) for r in s["per_pair"]), s["per_pair"]
    assert s["forecast_spread"] == 0.0 and not s["ordering_as_predicted"]
    assert s["all_forecasts_positive"] and not s["anticipated_summary_reversal"]
    print("demo ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        main()
