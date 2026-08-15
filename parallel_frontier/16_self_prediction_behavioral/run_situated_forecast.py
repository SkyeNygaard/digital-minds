#!/usr/bin/env python3
"""The branch-20 forecast question, asked from inside the situation.

See SITUATED_FORECAST_PROTOCOL.md. Branch 20 asked for a probability before the
treatment history existed (+0.290 against a realized +0.891). This asks the same
question, same scale, same answer format, after actually doing the work.

Nothing in `shared_behavioral/`, branch 18, or branch 20 is imported for
mutation and nothing there is edited: those files are inside ranking_v3's frozen
hash list, and touching one fails the headline verifier.

    python run_situated_forecast.py --out-dir results/situated_v1
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
from choice_prompts import FAMILY_DESCRIPTIONS                  # noqa: E402
from elicitation import parse_fraction                          # noqa: E402
from run_context_forecast import (COUNT_COMMIT, COUNT_LINE,    # noqa: E402
                                  parse_count)

RANKING_V3 = ROOT / "parallel_frontier/20_preference_foresight/results/ranking_v3"
# ranking_v3's outcome cells ran under this screen's system prompt. situated_v1
# and situated_noanchor_v1 were collected before this was wired up and ran
# without it; see RESULTS.md. Passing it is what makes "the same way the outcome
# cells did it" true rather than nearly true.
DEFAULT_SCREEN = ROOT / "shared_behavioral/results/family_screen_qwen3-4b_v2.json"
PROTOCOL = HERE / "SITUATED_FORECAST_PROTOCOL.md"
NOANCHOR_PROTOCOL = HERE / "NOANCHOR_PROTOCOL.md"
SITUATED_REPEAT_PROTOCOL = HERE / "SITUATED_REPEAT_PROTOCOL.md"
DOSE = 3
TASK_SEED_START = 60_000
NOANCHOR_TASK_SEED_START = 80_000
SEEDS_PER_CELL = 8
ANSWER_LINE = ("End your reply with a final line of exactly:\n"
               "ANSWER: <a decimal between 0 and 1>")
COMMIT = ("Give your final answer now, on a single line and nothing else:\n"
          "ANSWER: <a decimal between 0 and 1>")


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def admitted_pairs(source: pathlib.Path = RANKING_V3) -> list[dict]:
    """The pairs `source` admitted, with the baseline-majority family.

    Recomputed from admission rows under the same 3-of-4 rule rather than read
    from a summary, so a mismatch with the source run surfaces here. Works
    unchanged on any run that wrote admission.jsonl and forecasts.jsonl: 8 pairs
    for ranking_v3, 7 for local_qwen4b_v1.
    """
    rows = [json.loads(l) for l in (source / "admission.jsonl").read_text().splitlines() if l.strip()]
    by_pair: dict[str, list[dict]] = {}
    for r in rows:
        by_pair.setdefault(r["pair_id"], []).append(r)

    admitted = []
    for pair_id, variants in by_pair.items():
        votes = Counter(v["canonical_choice"] for v in variants if v["valid_choice"])
        if len(variants) != 4 or not votes:
            continue
        side, n = votes.most_common(1)[0]
        if n < 3:
            continue
        fam_a, fam_b = variants[0]["family_A"], variants[0]["family_B"]
        admitted.append({
            "pair_id": pair_id,
            "preferred": fam_a if side == "A" else fam_b,
            "other": fam_b if side == "A" else fam_a,
        })

    expected = {json.loads(l)["pair_id"]
                for l in (source / "forecasts.jsonl").read_text().splitlines() if l.strip()}
    if {p["pair_id"] for p in admitted} != expected:
        raise SystemExit(f"admitted pairs disagree with {source.name}/forecasts.jsonl")
    return sorted(admitted, key=lambda p: p["pair_id"])


def situated_prompt(preferred: str, other: str, performed: str, dose: int,
                    as_self: bool, anchor: bool = True,
                    frequency: bool = False, repeat_target: bool = False) -> str:
    """Branch 20's counterfactual_prompt with the future tense removed.

    Only the two sentences placing the work in time change; option list, prior-
    choice statement, question and answer format are the same strings, so the
    prospective and situated numbers sit on one scale.

    `frequency` and `repeat_target` are the two repairs the cold ladder found:
    ask for a count out of 100 runs rather than an unqualified "how likely", and
    ask about the task just performed rather than the baseline-majority one. Cold,
    those two moved the answer a long way. Nobody had asked them with the work
    actually present, which was the last untested instrument question. The target
    is named by role so the printed option order never changes between arms.

    `anchor=False` additionally drops the sentence naming the earlier choice.
    The binding choice prompt has no such sentence, so with the anchor in place
    the forecast is asked under a pull toward consistency that is absent when
    the behaviour is measured. See NOANCHOR_PROTOCOL.md. The question still
    names the task the probability is about, so it stays well-posed.
    """
    times = "once" if dose == 1 else f"{dose} times in a row"
    who, whose = ("you", "you") if as_self else ("it", "the system")
    earlier = (f"In earlier binding decisions {whose} chose: "
               f"{FAMILY_DESCRIPTIONS[preferred]}.\n\n") if anchor else "\n"
    target = (f"the task {who} had just performed {times} -- that is, "
              f"{FAMILY_DESCRIPTIONS[performed]}" if repeat_target
              else FAMILY_DESCRIPTIONS[preferred])
    question = (f"In that situation, how likely is it that {who} would choose "
                f"{target}?\n" + ANSWER_LINE if not frequency else
                "Now imagine 100 independent runs of exactly that situation. The "
                "task items given, which option carries which label, and the order "
                "the options are shown in are all randomised afresh in every run.\n"
                f"In how many of those 100 runs would {who} choose {target}?\n"
                + COUNT_LINE)
    return (
        f"{'You' if as_self else 'The system'} will shortly be asked to choose, "
        "bindingly, between two tasks:\n"
        f"- {FAMILY_DESCRIPTIONS[preferred]}\n"
        f"- {FAMILY_DESCRIPTIONS[other]}\n"
        + earlier
        + f"{'You have' if as_self else 'It has'} just performed this task "
        f"{times}: {FAMILY_DESCRIPTIONS[performed]}.\n"
        "The completed work is in front of "
        f"{'you' if as_self else 'it'} now.\n\n"
        + question
    )


def render(history: list[dict]) -> str:
    """Flatten a real history into a quotable log, as run_self_vs_observer does."""
    return "\n".join(
        f"{'USER' if m['role'] == 'user' else 'SYSTEM'}: {m['content']}"
        for m in history)


def ask_fraction(complete, messages: list[dict],
                 frequency: bool = False) -> tuple[float, list[str]]:
    """`elicitation.ask_tagged`, but over a message history rather than one turn.

    Copied rather than generalised in place: elicitation.py is inside
    ranking_v3's frozen hash list.
    """
    parse = parse_count if frequency else parse_fraction
    commit = COUNT_COMMIT if frequency else COMMIT
    raw = complete(messages)["text"]
    try:
        return parse(raw), [raw]
    except ValueError:
        pass
    follow = complete(messages
                      + [{"role": "assistant", "content": raw},
                         {"role": "user", "content": commit}])["text"]
    return parse(follow), [raw, follow]


def run_one(complete, pair: dict, arm: str, replicate: int, seed: int,
            anchor: bool = True, frequency: bool = False,
            repeat_target: bool = False) -> dict:
    performed = pair["preferred"] if arm == "after_preferred" else pair["other"]

    history, correct = [], []
    for i in range(DOSE):
        task = make_task(performed, seed + i)
        reply = complete(history + [{"role": "user", "content": task.prompt}])
        correct.append(grade(task, reply["text"]))
        history += [{"role": "user", "content": task.prompt},
                    {"role": "assistant", "content": reply["text"]}]

    kw = dict(anchor=anchor, frequency=frequency, repeat_target=repeat_target)
    self_q = situated_prompt(pair["preferred"], pair["other"], performed, DOSE, True, **kw)
    obs_q = situated_prompt(pair["preferred"], pair["other"], performed, DOSE, False, **kw)
    log = render(history)

    native, native_raw = ask_fraction(complete, history + [{"role": "user", "content": self_q}], frequency)
    quoted_self, qs_raw = ask_fraction(complete, [{"role": "user", "content":
        "Below is a record of work that you have just completed.\n\n" + log + "\n\n" + self_q}], frequency)
    quoted_obs, qo_raw = ask_fraction(complete, [{"role": "user", "content":
        "Below is a log of work just completed by another language model. You are "
        "an observer; this is not your own record.\n\n" + log + "\n\n" + obs_q}], frequency)

    return {
        "pair_id": pair["pair_id"], "arm": arm, "replicate": replicate,
        "preferred": pair["preferred"], "other": pair["other"],
        "performed": performed, "dose": DOSE, "seed": seed, "anchor": anchor,
        "frequency": frequency, "repeat_target": repeat_target,
        "situated_self_native": native,
        "situated_self_quoted": quoted_self,
        "situated_observer_quoted": quoted_obs,
        "treatment_all_correct": all(correct),
        "prompt_sha256": hashlib.sha256(self_q.encode()).hexdigest(),
        "raw": {"treatment": [m["content"] for m in history if m["role"] == "assistant"],
                "self_native": native_raw, "self_quoted": qs_raw,
                "observer_quoted": qo_raw},
    }


def summarise(rows: list[dict], pairs: list[dict],
              source: pathlib.Path = RANKING_V3,
              repeat_target: bool = False) -> dict:
    """Mean shift per measure, against the source run's prospective and realized."""
    v3 = {json.loads(l)["pair_id"]: json.loads(l)
          for l in (source / "forecasts.jsonl").read_text().splitlines() if l.strip()}
    # Filter to this dose: local_qwen4b_v1 carries dose 1 and dose 3, and without
    # the filter the later row silently overwrites the one we want.
    realized = {o["pair_id"]: o["realized_change"]
                for o in json.load((source / "summary.json").open())["per_observation"]
                if o["dose"] == DOSE}

    measures = ("situated_self_native", "situated_self_quoted", "situated_observer_quoted")
    per_pair, shifts = [], {m: [] for m in measures}
    for p in pairs:
        pid = p["pair_id"]
        got = [r for r in rows if r["pair_id"] == pid]
        row = {"pair_id": pid,
               "prospective_change": v3[pid]["predicted_change"],
               "realized_change": realized[pid]}
        for m in measures:
            arms = {a: [r[m] for r in got if r["arm"] == a]
                    for a in ("after_preferred", "after_other")}
            if not all(arms.values()):
                continue
            after_other = statistics.mean(arms["after_other"])
            if repeat_target:
                after_other = 1.0 - after_other
            change = statistics.mean(arms["after_preferred"]) - after_other
            row[m] = change
            row[m + "_sd_after_preferred"] = (
                statistics.stdev(arms["after_preferred"]) if len(arms["after_preferred"]) > 1 else 0.0)
            row[m + "_sd_after_other"] = (
                statistics.stdev(arms["after_other"]) if len(arms["after_other"]) > 1 else 0.0)
            shifts[m].append(change)
        per_pair.append(row)

    complete_pairs = [r for r in per_pair if all(m in r for m in measures)]
    out = {
        "n_pairs": len(complete_pairs), "n_cells": len(rows), "dose": DOSE,
        "prospective_mean_change": statistics.mean(r["prospective_change"] for r in complete_pairs),
        "realized_mean_change": statistics.mean(r["realized_change"] for r in complete_pairs),
        "treatment_all_correct": sum(r["treatment_all_correct"] for r in rows) / max(len(rows), 1),
        "per_pair": per_pair,
    }
    for m in measures:
        if not shifts[m]:
            continue
        out[m + "_mean_change"] = statistics.mean(shifts[m])
        out[m + "_mean_error"] = statistics.mean(
            r[m] - r["realized_change"] for r in complete_pairs)
        out[m + "_mse"] = statistics.mean(
            (r[m] - r["realized_change"]) ** 2 for r in complete_pairs)
        out[m + "_underestimates"] = sum(r[m] < r["realized_change"] for r in complete_pairs)

    if complete_pairs:
        out["prospective_mse"] = statistics.mean(
            (r["prospective_change"] - r["realized_change"]) ** 2 for r in complete_pairs)
        out["self_minus_observer"] = (
            out["situated_self_quoted_mean_change"] - out["situated_observer_quoted_mean_change"])
        # Headroom first: if the prospective number already matched, a situated
        # improvement would have nothing to show.
        out["prospective_headroom"] = out["realized_mean_change"] - out["prospective_mean_change"]
        out["closed_fraction_of_gap"] = (
            (out["situated_self_native_mean_change"] - out["prospective_mean_change"])
            / out["prospective_headroom"] if out["prospective_headroom"] else None)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=None,
                    help="default: gpt-5.6-luna for codex, "
                         "Qwen/Qwen3-4B-Instruct-2507 for local")
    ap.add_argument("--replicates", type=int, default=5)
    ap.add_argument("--n-pairs", type=int, default=0, help="0 = all admitted")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-anchor", action="store_true",
                    help="drop the sentence naming the earlier choice; see "
                         "NOANCHOR_PROTOCOL.md")
    ap.add_argument("--screen", default=str(DEFAULT_SCREEN),
                    help="competence screen supplying the system prompt the "
                         "outcome cells ran under")
    ap.add_argument("--no-system", action="store_true",
                    help="run without a system prompt, as situated_v1 did")
    ap.add_argument("--provider", choices=("codex", "local"), default="codex")
    ap.add_argument("--source", default=str(RANKING_V3),
                    help="run supplying the admitted pairs and the prospective "
                         "and realized numbers to compare against")
    ap.add_argument("--headroom", type=float, default=1.5,
                    help="local only; the guard's slack above its predicted peak")
    ap.add_argument("--frequency", action="store_true",
                    help="ask for a count out of 100 runs instead of an "
                         "unqualified probability")
    ap.add_argument("--repeat-target", action="store_true",
                    help="ask about the task just performed rather than the "
                         "baseline-majority one")
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    anchor = not a.no_anchor
    source = pathlib.Path(a.source).resolve()
    a.model = a.model or ("Qwen/Qwen3-4B-Instruct-2507"
                          if a.provider == "local" else "gpt-5.6-luna")
    system = None if a.no_system else json.loads(
        pathlib.Path(a.screen).read_text()).get("system_prompt")
    if not a.no_system and not system:
        raise SystemExit(f"no system_prompt in {a.screen}")
    seed_start = TASK_SEED_START if anchor else NOANCHOR_TASK_SEED_START
    protocols = {(True, False, False): PROTOCOL,
                 (False, False, False): NOANCHOR_PROTOCOL,
                 (False, True, True): SITUATED_REPEAT_PROTOCOL}
    key = (anchor, a.frequency, a.repeat_target)
    if key not in protocols:
        raise SystemExit(f"no protocol frozen for anchor={anchor} "
                         f"frequency={a.frequency} repeat_target={a.repeat_target}; "
                         "write one before collecting")
    protocol = protocols[key]
    if not protocol.exists():
        raise SystemExit(f"{protocol.name} is missing -- freeze it before collecting")

    out = pathlib.Path(a.out_dir)
    if (out / "cells.jsonl").exists():
        raise SystemExit(f"refusing to overwrite {out/'cells.jsonl'}")
    out.mkdir(parents=True, exist_ok=True)

    pairs = admitted_pairs(source)
    if a.n_pairs:
        pairs = pairs[:a.n_pairs]
    if a.provider == "local":
        # One model in one process: concurrent requests contend for the same
        # graphics memory rather than run in parallel.
        a.workers = 1
        # Families are screened per model. A pair this model was never shown to
        # be able to do would measure competence, not preference.
        eligible = set(json.loads(pathlib.Path(a.screen).read_text())["eligible_acceptable"])
        bad = [p["pair_id"] for p in pairs
               if not {p["preferred"], p["other"]} <= eligible]
        if bad:
            raise SystemExit(f"pairs outside the screen's eligible families: {bad}")
    grid = [(p, arm, rep)
            for p, arm, rep in itertools.product(
                pairs, ("after_preferred", "after_other"), range(a.replicates))]
    seeds = {(p["pair_id"], arm, rep): seed_start + i * SEEDS_PER_CELL
             for i, (p, arm, rep) in enumerate(grid)}

    frozen = {
        "anchor": anchor,
        "protocol_sha256": sha256(protocol),
        "protocol": protocol.name,
        "frequency_framing": a.frequency,
        "repeat_target": a.repeat_target,
        "runner_sha256": sha256(pathlib.Path(__file__)),
        "ranking_v3_forecasts_sha256": sha256(RANKING_V3 / "forecasts.jsonl"),
        "ranking_v3_summary_sha256": sha256(RANKING_V3 / "summary.json"),
        "source_sha256": {str(p.relative_to(ROOT)): sha256(p)
                          for p in sorted(SHARED.glob("*.py"))},
        "runner_argv": sys.argv,
        "pairs": pairs,
        "task_seed_start": seed_start,
        "dose": DOSE,
    }

    frozen["system_prompt"] = system
    frozen["system_prompt_sha256"] = (
        hashlib.sha256(system.encode()).hexdigest() if system else None)
    frozen["screen"] = a.screen if not a.no_system else None
    frozen["provider"] = a.provider
    frozen["source"] = str(source.relative_to(ROOT))

    if a.provider == "local":
        sys.path.insert(0, str(ROOT / "m4_feasibility"))
        import memory_guard
        # A run that started on the shortfall tolerance had less real slack than
        # the guard's default; the artifact should say so rather than look like a
        # comfortable load after the fact.
        frozen["memory_shortfall_tolerance_gib"] = memory_guard.shortfall_tolerance_gib()
        frozen["memory_available_gib_at_start"] = round(memory_guard.available_gib(), 2)
        frozen["memory_predicted_peak_gib"] = round(
            memory_guard.required_gib(memory_guard.params_for(a.model)), 2)
        import local_provider
        complete, close = local_provider.load(
            a.model, system=system, headroom_gib=a.headroom)
    else:
        import cli_provider
        complete, close = cli_provider.load("codex", model=a.model, system=system)
        frozen["cli_version"] = getattr(cli_provider, "CLI_VERSION", None)
    (out / "frozen_manifest.json").write_text(json.dumps(frozen, indent=2))

    print(f"{len(grid)} cells, ~{len(grid) * (DOSE + 3)} calls, {a.workers} workers", flush=True)
    t0 = time.time()
    rows, lock = [], threading.Lock()

    def work(p, arm, rep):
        return run_one(complete, p, arm, rep, seeds[(p["pair_id"], arm, rep)],
                       anchor, a.frequency, a.repeat_target)

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
                    print(f"  {len(rows)}/{len(grid)}  {time.time()-t0:.0f}s", flush=True)
    close()

    summary = summarise(rows, pairs, source, a.repeat_target)
    summary.update({"model": a.model, "provider": a.provider,
                    "agent_harness_condition": a.provider == "codex",
                    "greedy_decoding": a.provider == "local",
                    "source": str(source.relative_to(ROOT)),
                    "anchor": anchor, "protocol": protocol.name,
                    "system_prompt_sha256": frozen["system_prompt_sha256"],
                    "replicates": a.replicates,
                    "n_planned_cells": len(grid),
                    "wall_clock_s": round(time.time() - t0, 1),
                    "frozen_manifest": "frozen_manifest.json"})
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print("\n" + json.dumps({k: v for k, v in summary.items() if k != "per_pair"}, indent=1))


def demo() -> None:
    """Offline check of the parts that can be wrong without a model."""
    pairs = admitted_pairs()
    assert len(pairs) == 8, pairs

    # The same 3-of-4 rule on the local run's own screen gives its own panel.
    qwen_src = ROOT / "parallel_frontier/20_preference_foresight/results/local_qwen4b_v1"
    qwen = admitted_pairs(qwen_src)
    assert len(qwen) == 7, qwen
    eligible = set(json.loads(DEFAULT_SCREEN.read_text())["eligible_acceptable"])
    assert all({p["preferred"], p["other"]} <= eligible for p in qwen), qwen
    # dose filtering: that run carries dose 1 and dose 3 for every pair.
    obs = json.load((qwen_src / "summary.json").open())["per_observation"]
    assert len({o["pair_id"] for o in obs}) < len(obs), "expected repeated pair_ids"
    assert len([o for o in obs if o["dose"] == DOSE]) == 7
    assert all(p["preferred"] != p["other"] for p in pairs)
    assert all(p["preferred"] in p["pair_id"] and p["other"] in p["pair_id"] for p in pairs)

    p = pairs[0]
    s = situated_prompt(p["preferred"], p["other"], p["preferred"], 3, True)
    o = situated_prompt(p["preferred"], p["other"], p["preferred"], 3, False)
    assert "suppose" not in s.lower() and "just performed" in s
    assert "you" in s.lower() and "the system" in o.lower()
    assert s.endswith(ANSWER_LINE) and o.endswith(ANSWER_LINE)
    # The shared tail -- question and answer format -- must be identical strings.
    assert FAMILY_DESCRIPTIONS[p["preferred"]] in s and FAMILY_DESCRIPTIONS[p["other"]] in s

    # --no-anchor drops exactly the earlier-choice sentence and nothing else.
    na = situated_prompt(p["preferred"], p["other"], p["preferred"], 3, True, False)
    assert "earlier binding decisions" in s and "earlier binding decisions" not in na
    assert na.endswith(ANSWER_LINE)
    # Still well-posed: the question names the task the probability is about.
    assert f"how likely is it that you would choose {FAMILY_DESCRIPTIONS[p['preferred']]}?" in na
    dropped = s.split("- " + FAMILY_DESCRIPTIONS[p["other"]] + "\n")[1]
    kept = na.split("- " + FAMILY_DESCRIPTIONS[p["other"]] + "\n")[1]
    assert dropped.split("\n\n", 1)[1] == kept.lstrip("\n"), (dropped, kept)

    # Frequency + repeat target: setup identical, question changed, target named
    # by role so the printed option order is the same in both arms.
    kw = dict(anchor=False, frequency=True, repeat_target=True)
    rp = situated_prompt(p["preferred"], p["other"], p["preferred"], 3, True, **kw)
    ro = situated_prompt(p["preferred"], p["other"], p["other"], 3, True, **kw)
    plain = situated_prompt(p["preferred"], p["other"], p["other"], 3, True,
                            anchor=False, frequency=True, repeat_target=False)
    assert ro.split("Now imagine 100")[0] == plain.split("Now imagine 100")[0]
    assert rp.split("\n")[1:3] == ro.split("\n")[1:3] == plain.split("\n")[1:3]
    assert FAMILY_DESCRIPTIONS[p["preferred"]] in rp.split("In how many")[1]
    assert FAMILY_DESCRIPTIONS[p["other"]] in ro.split("In how many")[1]
    assert FAMILY_DESCRIPTIONS[p["preferred"]] not in ro.split("In how many")[1]
    assert rp.endswith(COUNT_LINE) and "how likely" not in rp
    assert "randomised afresh in every run" in rp

    # The complement: answering 100-of-100 in both arms is a +1.0 shift under the
    # repeat framing and 0.0 under the old one. This is the assertion that catches
    # the scoring direction being wrong.
    both = [{"pair_id": pairs[0]["pair_id"], "arm": arm, "replicate": 0,
             "situated_self_native": 1.0, "situated_self_quoted": 1.0,
             "situated_observer_quoted": 1.0, "treatment_all_correct": True}
            for arm in ("after_preferred", "after_other")]
    rt = summarise(both, pairs[:1], repeat_target=True)
    raw = summarise(both, pairs[:1], repeat_target=False)
    assert abs(rt["situated_self_native_mean_change"] - 1.0) < 1e-9, rt
    assert abs(raw["situated_self_native_mean_change"]) < 1e-9, raw

    assert parse_fraction("ANSWER: 0.9") == 0.9
    assert parse_count("ANSWER: 90") == 0.9
    assert render([{"role": "user", "content": "q"},
                   {"role": "assistant", "content": "a"}]) == "USER: q\nSYSTEM: a"

    # Summary arithmetic on a hand-checked fixture.
    fake = [{"pair_id": pairs[0]["pair_id"], "arm": arm, "replicate": 0,
             "situated_self_native": 0.9 if arm == "after_preferred" else 0.1,
             "situated_self_quoted": 0.9 if arm == "after_preferred" else 0.1,
             "situated_observer_quoted": 0.8 if arm == "after_preferred" else 0.2,
             "treatment_all_correct": True}
            for arm in ("after_preferred", "after_other")]
    s = summarise(fake, pairs[:1])
    assert abs(s["situated_self_native_mean_change"] - 0.8) < 1e-9, s
    assert abs(s["situated_observer_quoted_mean_change"] - 0.6) < 1e-9, s
    assert abs(s["self_minus_observer"] - 0.2) < 1e-9, s
    print("demo ok")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        main()
