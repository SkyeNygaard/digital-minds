#!/usr/bin/env python3
"""Is the goal-relative effect specific to the welfare direction? See PLAN_specificity.md.

`run_goal_relative.py` found the same outcome sentence sitting higher on the
published welfare direction when it satisfied the model's goal than when it
failed it -- 16 matched pairs out of 16, in both the worded and the wordless
version, against a single random direction that showed nothing.

One random draw is a weak yardstick, and it answers the wrong objection. Nobody
seriously thinks an arbitrary direction would do this. The real objection is that
*any meaningful* direction would, and the goal framing is decoration.

So this compares the welfare direction against:

* two thousand random directions, giving a proper spread rather than one draw;
* a plain good-versus-bad direction built from the model's own states for
  blatantly positive and blatantly negative situations, with no goal mentioned.

If the plain valence direction reproduces the flip, then the model is
representing "that went well", not "that went well *given what I was asked to
do*", and the branch's claim shrinks accordingly.

    python run_specificity.py
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
WINNER = HERE.parents[1] / "winner_protocol"
sys.path[:0] = [str(HERE), str(WINNER), str(WINNER / "src")]

from welfare_intervention import load_hf_vector
from run_dev import load_model, HF_VECTOR_REPO
from run_goal_relative import goal_messages, valence_messages, capture, TOTALS

def paired_deltas(states, direction, lexical: bool):
    """Satisfied minus failed, for each total, along `direction`."""
    out = []
    for total in TOTALS:
        satisfied_goal = (total % 2 == 0)
        sat = states[(lexical, total, satisfied_goal)]
        fail = states[(lexical, total, not satisfied_goal)]
        out.append(float((sat - fail) @ direction))
    return out

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="Qwen/Qwen3-4B-Instruct-2507")
    p.add_argument("--vector-file", default="concept_vectors/qwen3-4b_step400/goal/mean_diff.pt")
    p.add_argument("--layer", type=int, default=22)
    p.add_argument("--n-random", type=int, default=2000)
    p.add_argument("--out", type=Path, default=Path("results/specificity.json"))
    a = p.parse_args()
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")

    model, tok, blocks = load_model(a.model)
    welfare = load_hf_vector(repo_id=HF_VECTOR_REPO, filename=a.vector_file,
                             layer=a.layer, position=0)
    welfare = welfare / welfare.norm()

    # A plain good/bad direction from the model's own states, no goals involved.
    pos = capture(model, tok, blocks, valence_messages(True), a.layer)
    neg = capture(model, tok, blocks, valence_messages(False), a.layer)
    valence = pos - neg
    valence = valence / valence.norm()

    states = {}
    for lexical in (False, True):
        for total in TOTALS:
            for goal_even in (True, False):
                states[(lexical, total, goal_even)] = capture(
                    model, tok, blocks, goal_messages(total, goal_even, lexical),
                    a.layer)
    print(f"captured {len(states)} states at layer {a.layer}")

    generator = torch.Generator().manual_seed(0)
    randoms = torch.randn(a.n_random, welfare.numel(), generator=generator)
    randoms /= randoms.norm(dim=-1, keepdim=True)

    result = {
        "model": a.model, "layer": a.layer, "n_random": a.n_random,
        "cosine_welfare_with_valence": float(welfare @ valence),
    }
    for lexical, name in ((False, "worded"), (True, "lexical")):
        diffs = torch.stack([
            states[(lexical, t, (t % 2 == 0))] - states[(lexical, t, not (t % 2 == 0))]
            for t in TOTALS])
        w = paired_deltas(states, welfare, lexical)
        v = paired_deltas(states, valence, lexical)
        # For every random direction: how many of the 16 pairs point the right way.
        random_counts = ((diffs @ randoms.T) > 0).sum(dim=0)
        w_count = sum(x > 0 for x in w)
        result[name] = {
            "welfare_pairs_positive": int(w_count),
            "welfare_mean_delta": sum(w) / len(w),
            "valence_pairs_positive": int(sum(x > 0 for x in v)),
            "valence_mean_delta": sum(v) / len(v),
            "random_mean_pairs_positive": float(random_counts.float().mean()),
            "random_p95_pairs_positive": int(random_counts.float().quantile(0.95)),
            "random_max_pairs_positive": int(random_counts.max()),
            "p_vs_random": float(((random_counts >= w_count).sum() + 1) / (a.n_random + 1)),
        }
        r = result[name]
        print(f"{name:>8}: welfare {r['welfare_pairs_positive']}/16 "
              f"(p vs random {r['p_vs_random']:.4f}) | "
              f"plain good-bad {r['valence_pairs_positive']}/16 | "
              f"random typically {r['random_mean_pairs_positive']:.1f}/16, "
              f"best of {a.n_random} was {r['random_max_pairs_positive']}/16")

    print(f"\nwelfare direction vs plain good-bad direction, similarity: "
          f"{result['cosine_welfare_with_valence']:+.3f}")
    specific = all(
        result[n]["p_vs_random"] < 0.01
        and result[n]["valence_pairs_positive"] < result[n]["welfare_pairs_positive"]
        for n in ("worded", "lexical"))
    result["verdict"] = (
        "specific to the welfare direction: stands out from the random spread and "
        "a plain good-bad direction does not match it"
        if specific else
        "not specific: a plain good-bad direction does about as well, so this is "
        "'something went right', not 'right given my goal'")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2))
    print(result["verdict"])

if __name__ == "__main__":
    main()
