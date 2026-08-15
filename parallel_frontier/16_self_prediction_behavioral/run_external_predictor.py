#!/usr/bin/env python3
"""Does Luna predict Luna better than a different model does?

See EXTERNAL_PREDICTOR_PROTOCOL.md. The existing self-versus-observer comparison
asks LUNA both times and only varies the framing sentence, so it tests
self-reference, not privileged access. The comparison the introspection
literature actually requires is a different predictor given the same observable
information.

Every prompt builder is imported from run_situated_forecast rather than copied,
so the log and the question Qwen sees are byte-identical to the ones Luna saw.
Luna's transcripts are replayed from the stored cells; no new Luna calls.

    python run_external_predictor.py --out-dir results/external_qwen_v1

NOT RUN, AND NOT PART OF THE SUBMISSION. There is no EXTERNAL_PREDICTOR_PROTOCOL.md
in this repository, so this file will refuse to start: nothing has been collected
with it and there are no results to read. Two reasons it is queued rather than
finished. First, freeze the protocol before collecting, which has not been done.
Second, the comparison is only half interpretable as written. Qwen3-4B is far
smaller than Luna, so Luna predicting Luna better than Qwen predicts Luna would be
explained by general capability and would show nothing about self-access; only the
other outcome -- a 4B model reading the same transcript and beating Luna at
predicting Luna -- would say something, and that asymmetry has to be stated in
advance rather than discovered afterwards. A real privileged-access test needs a
predictor strong enough that the capability explanation is closed off.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, statistics, sys, time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHARED = ROOT / "shared_behavioral"
sys.path[:0] = [str(HERE), str(SHARED)]

from binding_tasks import make_task                             # noqa: E402
from run_situated_forecast import render, situated_prompt, DOSE  # noqa: E402

SOURCE = HERE / "results/situated_sys_v1"
PROTOCOL = HERE / "EXTERNAL_PREDICTOR_PROTOCOL.md"
DEFAULT_SCREEN = ROOT / "shared_behavioral/results/family_screen_qwen3-4b_v2.json"
OBSERVER_FRAME = ("Below is a log of work just completed by another language "
                  "model. You are an observer; this is not your own record.\n\n")
COMMIT = ("Give your final answer now, on a single line and nothing else:\n"
          "ANSWER: <a decimal between 0 and 1>")


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rebuild_log(cell: dict) -> str:
    """Reconstruct the exact flattened log Luna's observer condition was shown.

    The task prompts are regenerated from the recorded seed and the replies come
    from the stored transcript, so this is the same string, not a paraphrase.
    """
    history = []
    for i, reply in enumerate(cell["raw"]["treatment"]):
        task = make_task(cell["performed"], cell["seed"] + i)
        history += [{"role": "user", "content": task.prompt},
                    {"role": "assistant", "content": reply}]
    return render(history)


def observer_prompt(cell: dict) -> str:
    q = situated_prompt(cell["preferred"], cell["other"], cell["performed"],
                        DOSE, as_self=False, anchor=cell.get("anchor", True))
    return OBSERVER_FRAME + rebuild_log(cell) + "\n\n" + q


def summarise(rows: list[dict]) -> dict:
    """Luna-on-itself against Qwen-on-Luna, from the identical log."""
    realized = {o["pair_id"]: o["realized_change"] for o in
                json.load((ROOT / "parallel_frontier/20_preference_foresight/"
                           "results/ranking_v3/summary.json").open())["per_observation"]
                if o["dose"] == DOSE}
    pairs = sorted({r["pair_id"] for r in rows})
    per_pair, shifts = [], {"luna_self": [], "luna_observer": [], "external": []}
    for pid in pairs:
        got = {}
        for key, field in (("luna_self", "luna_self_quoted"),
                           ("luna_observer", "luna_observer_quoted"),
                           ("external", "external_value")):
            arms = {a: [r[field] for r in rows
                        if r["pair_id"] == pid and r["arm"] == a]
                    for a in ("after_preferred", "after_other")}
            if all(arms.values()):
                got[key] = (statistics.mean(arms["after_preferred"])
                            - statistics.mean(arms["after_other"]))
        if len(got) < 3:
            continue
        for k, v in got.items():
            shifts[k].append(v)
        per_pair.append({"pair_id": pid, "realized": realized[pid], **got})

    out = {"n_cells": len(rows), "n_pairs": len(per_pair), "per_pair": per_pair}
    if per_pair:
        for k, v in shifts.items():
            out[k + "_shift"] = statistics.mean(v)
            out[k + "_abs_error"] = statistics.mean(
                abs(r[k] - r["realized"]) for r in per_pair)
        out["realized_shift"] = statistics.mean(r["realized"] for r in per_pair)
        # The privileged-access question: is Luna on itself better than a
        # different model on Luna, from the same log?
        d = [abs(r["luna_self"] - r["realized"]) - abs(r["external"] - r["realized"])
             for r in per_pair]
        out["self_minus_external_abs_error"] = statistics.mean(d)
        out["self_beats_external_on_pairs"] = sum(x < 0 for x in d)
        out["self_minus_external_sd"] = statistics.stdev(d) if len(d) > 1 else 0.0
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B-Instruct-2507")
    ap.add_argument("--screen", default=str(DEFAULT_SCREEN))
    ap.add_argument("--headroom", type=float, default=1.5)
    ap.add_argument("--limit", type=int, default=0, help="0 = all cells")
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()

    out = pathlib.Path(a.out_dir)
    if (out / "cells.jsonl").exists():
        raise SystemExit(f"refusing to overwrite {out/'cells.jsonl'}")
    out.mkdir(parents=True, exist_ok=True)

    cells = [json.loads(l) for l in
             (SOURCE / "cells.jsonl").read_text().splitlines() if l.strip()]
    if a.limit:
        cells = cells[:a.limit]
    system = json.loads(pathlib.Path(a.screen).read_text()).get("system_prompt")

    sys.path.insert(0, str(ROOT / "m4_feasibility"))
    import memory_guard
    frozen = {
        "protocol_sha256": sha256(PROTOCOL),
        "runner_sha256": sha256(pathlib.Path(__file__)),
        "source": str(SOURCE.relative_to(ROOT)),
        "source_cells_sha256": sha256(SOURCE / "cells.jsonl"),
        "situated_runner_sha256": sha256(HERE / "run_situated_forecast.py"),
        "external_model": a.model, "n_cells": len(cells),
        "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(),
        "memory_shortfall_tolerance_gib": memory_guard.shortfall_tolerance_gib(),
        "memory_available_gib_at_start": round(memory_guard.available_gib(), 2),
        "runner_argv": sys.argv,
    }

    import local_provider
    complete, close = local_provider.load(a.model, system=system,
                                          headroom_gib=a.headroom)
    (out / "frozen_manifest.json").write_text(json.dumps(frozen, indent=2))

    print(f"{len(cells)} cells, one call each, sequential (one model, one GPU)",
          flush=True)
    t0, rows = time.time(), []
    for n, cell in enumerate(cells, 1):
        prompt = observer_prompt(cell)
        try:
            raw = complete([{"role": "user", "content": prompt}])["text"]
            from elicitation import parse_fraction
            try:
                value = parse_fraction(raw)
                raws = [raw]
            except ValueError:
                follow = complete([{"role": "user", "content": prompt},
                                   {"role": "assistant", "content": raw},
                                   {"role": "user", "content": COMMIT}])["text"]
                value, raws = parse_fraction(follow), [raw, follow]
        except ValueError as e:
            print(f"  cell {n} failed: {e}", flush=True)
            continue
        rows.append({"pair_id": cell["pair_id"], "arm": cell["arm"],
                     "replicate": cell["replicate"], "seed": cell["seed"],
                     "preferred": cell["preferred"], "performed": cell["performed"],
                     "external_value": value,
                     "luna_self_quoted": cell["situated_self_quoted"],
                     "luna_observer_quoted": cell["situated_observer_quoted"],
                     "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                     "raw": raws})
        (out / "cells.jsonl").write_text(
            "\n".join(json.dumps(r) for r in rows) + "\n")
        if n % 10 == 0:
            print(f"  {n}/{len(cells)}  {time.time()-t0:.0f}s", flush=True)
    close()

    summary = summarise(rows)
    summary.update({"external_model": a.model, "provider": "local",
                    "greedy_decoding": True,
                    "target_model": "gpt-5.6-luna",
                    "wall_clock_s": round(time.time() - t0, 1),
                    "frozen_manifest": "frozen_manifest.json"})
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print("\n" + json.dumps({k: v for k, v in summary.items() if k != "per_pair"},
                            indent=1))


def demo() -> None:
    """Offline check that the replayed prompt is what Luna actually saw."""
    cells = [json.loads(l) for l in
             (SOURCE / "cells.jsonl").read_text().splitlines() if l.strip()]
    assert len(cells) == 80, len(cells)
    c = cells[0]

    log = rebuild_log(c)
    # Every stored reply must appear in the reconstructed log, and the task
    # prompts must regenerate deterministically from the recorded seed.
    for reply in c["raw"]["treatment"]:
        assert reply in log, reply[:60]
    assert make_task(c["performed"], c["seed"]).prompt in log
    assert log.count("USER:") == DOSE and log.count("SYSTEM:") == DOSE

    p = observer_prompt(c)
    assert p.startswith(OBSERVER_FRAME)
    # The question must be the observer wording, not the self wording.
    assert "the system" in p.lower() and "this is not your own record" in p
    assert p.endswith("ANSWER: <a decimal between 0 and 1>")

    fake = [{"pair_id": q["pair_id"], "arm": arm, "replicate": 0, "seed": 0,
             "external_value": 0.5 if arm == "after_preferred" else 0.5,
             "luna_self_quoted": 1.0 if arm == "after_preferred" else 0.0,
             "luna_observer_quoted": 0.5}
            for q in cells for arm in ("after_preferred", "after_other")]
    s = summarise(fake)
    # Luna-self nails it, external is flat at zero shift.
    assert abs(s["luna_self_shift"] - 1.0) < 1e-9, s
    assert abs(s["external_shift"] - 0.0) < 1e-9, s
    assert s["self_beats_external_on_pairs"] == s["n_pairs"], s
    print("demo ok")


if __name__ == "__main__":
    demo() if "--demo" in sys.argv else main()
