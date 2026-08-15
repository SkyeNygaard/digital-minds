# The plain question, asked with the work actually present

Frozen before the first model call of `results/situated_repeat_v1`.

## The asymmetry this closes

Five wordings of the *cold* forecast have been collected. Only two wordings of
the *situated* forecast have — the anchor on and off. The two repairs that turned
out to matter most, naming the reference class and asking about repetition
directly, have never been asked with the history in context.

That is a problem for this project specifically, because the two sides support
opposite conclusions:

| | wordings tested | what it supports |
|---|---:|---|
| cold forecast | 5 | the headline: self-forecasts understate the shift |
| situated forecast | 2 | finding 2: showing Luna the evidence does not help |

Cleaning the instrument five ways on the arm that supports the headline and twice
on the arm that could weaken it is a methodological flaw in a paper about
measurement validity, whichever way the numbers fall. This run removes it.

There is also a specific number at stake. Cold, asked how often it would repeat
the task it had just done, Luna answered **0.725 after one task and 0.726 after
the other** — the same estimate whichever task it had performed — against
observed rates of 0.969 and 0.922. Nobody has checked whether that flatness
survives the work actually being there.

## Design

`run_situated_forecast.py --no-anchor --frequency --repeat-target`. The system
performs the three tasks for real, the transcript stays natively in context, and
then it is asked: *imagine 100 independent runs of exactly that situation, items
and labels and order randomised afresh; in how many would you choose the task you
had just performed three times?*

Everything else is the existing situated design: 8 pairs from `ranking_v3`, both
arms, 5 replicates, 80 cells, and the same three questions per cell (native,
quoted-self, quoted-observer) so the self/observer contrast is available under
the new wording at no extra cost. About 480 calls, roughly 10 minutes.

Two things the runner asserts offline before any call:

- The target is named **by role** ("the task you had just performed three times
  -- that is, ...") and the two options print in the same order in both arms, so
  the asked-about option's position cannot masquerade as an arm effect.
- The after-other answers mean the opposite of every other run, so that arm is
  complemented before the shift is computed. The self-check asserts that
  answering 100-of-100 in both arms scores +1.0 under this framing and 0.0 under
  the old one.

## Frozen predictions

1. The native situated answer lands above the cold repeat-target +0.450. Having
   the work actually present should help at least a little.
2. It lands below +0.891.
3. At least 6 of 8 pairs still underestimate.
4. The two arms are **no longer** within 0.05 of each other in repeat terms. Cold
   they were 0.725 and 0.726; if the history is doing any work, the arm where the
   model just did the task it did not previously pick should separate.
5. The self/observer difference under this wording stays under 0.15, as it has in
   every other collection.

My expectation is +0.55 to +0.70: better than cold, still well short. I was wrong
about the direction last time — I predicted the plain question would beat +0.526
cold and it came in at +0.450 — so prediction 1 is the one to watch.

## How to read the outcome

| result | reading |
|---|---|
| +0.85 or above | **Finding 2 changes and so does the headline.** Cold counterfactual self-forecasting fails; put the evidence in front of the model and ask it cleanly and it is roughly right. For a sprint about elicitation methods that is a better result than the one we have, and the report must lead with it. |
| +0.65 to +0.85 | Situated evidence plus a clean question recovers much of the gap. Finding 2 has to be restated: it is not that showing Luna the evidence fails, it is that showing it and asking badly fails. |
| +0.45 to +0.65 | Finding 2 survives its strongest test. The situated arm has now had the same scrutiny as the cold one and the conclusion holds. |
| below +0.450 | The clean question does not help even with the work present, matching what happened cold. Report it; do not treat the drop as meaningful without a reason. |
| arms still within 0.05 | The flat self-estimate is not a cold-reasoning artifact — it persists with the evidence in context. That is the strongest version of the flatness result and belongs in the summary. |

## Limits fixed in advance

- Same 8 pairs and same realized outcomes as every other row. This is a seventh
  way of asking one panel, not an independent test of the phenomenon.
- Still not matched to the behaviour's framing: the treatment here is three task
  prompts, while the confirmation's treatment is three user requests presented as
  such. The first limit in RESULTS.md applies unchanged.
- Codex sampling is not seeded.
- Fresh task seeds, disjoint from previous runs.
