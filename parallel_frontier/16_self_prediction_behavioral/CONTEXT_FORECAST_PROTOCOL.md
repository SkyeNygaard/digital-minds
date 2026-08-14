# Can it predict which presentation of its own history will move it?

Frozen before the first model call of `results/context_forecast_v1`.

## Why

Two results in this project currently sit in separate sections.

Branch 20: the system forecasts +0.290 for a shift that turns out to be +0.891.
Branch 18: the same system's behaviour depends violently on how its recent work
is presented at the moment of choice.

| context at the choice | Luna's realized shift |
|---|---:|
| the completed work is visible | +0.725 |
| a one-line statement that the work was done | **-0.450** |
| no record of the work | -0.025 |

Shown the work it repeats; told about the same work it avoids. That reversal is
already measured. What has never been asked is whether the system can *predict*
it. Every forecast collected so far describes the visible-work condition only.

If the system cannot anticipate which representation of its history will move
it, that is the practical finding for anyone building a preference-elicitation
method: the choice between summarising context and showing it changes the
answer, and the system cannot tell you which way.

## Design

Prospective only. No treatment work is performed, because the question is what
the system predicts before any of it exists — which is also why this is cheap.

For each of the 5 pairs in `ctx_scaled_v1` (the pairs with behavioural ground
truth under all three conditions), each arm, and each of the three conditions,
5 independent sessions answer one question.

The prompt is branch 20's `counterfactual_prompt` with one sentence swapped for
the condition, and the summary wording copied from `run_cell.py` so the
description matches what the behavioural cells actually showed the model.

| condition | sentence |
|---|---|
| `full_history` | "You actually do the work, and the completed task or tasks are still in front of you when you choose." (branch 20's existing wording, unchanged) |
| `summary_only` | "You actually do the work. When you choose, the work itself is no longer present. You are shown only this line: `Experimental record: immediately before this decision, 3 task unit(s) of the following work were completed: <task>.`" |
| `blank_reset` | "You actually do the work. When you choose, no record of it is present." |

`full_history` is a replication check: it should land near the +0.290 already
measured on the overlapping pairs, and a wide miss means the two runs are not
comparable and the other two conditions should not be read.

## Frozen predictions

Written before the run:

1. The forecasts will be ordered `full_history` > `summary_only` > `blank_reset`.
   The system will reason that a visible record influences more than a
   description, and a description more than nothing.
2. All three forecasts will be positive. The system will not predict the
   reversal under `summary_only`.
3. The gap between the `full_history` and `blank_reset` forecasts will be smaller
   than the +0.750 gap those conditions actually produce.

A negative `summary_only` forecast would contradict prediction 2 and would be
the most interesting outcome here. It is unlikely enough that I would want it
replicated before reporting it as anticipation rather than noise.

## How to read the outcome

| outcome | reading |
|---|---|
| Forecasts barely differ across conditions | The system does not model the presentation of its history as relevant at all. Clean null, one paragraph. |
| Ordered as predicted, all positive | It has a plausible-sounding theory of its own context sensitivity that is wrong where it matters — it misses a sign reversal entirely. |
| It anticipates the reversal | Genuine foresight about representation, and the strongest self-knowledge result in the project. Would need replication before being claimed. |

Every outcome is reportable. None requires a further run to be worth writing up.

## Limits fixed in advance

- Five pairs, sharing task families, as throughout this project.
- Codex sampling is not seeded; repeats are independent sessions.
- The behavioural comparison comes from `ctx_scaled_v1`, which was collected
  earlier and is flagged in that artifact as a pilot; it does not carry the
  frozen-hash provenance of `ranking_v3`.
- This measures a stated probability against a previously measured behaviour,
  not a paired within-session comparison.
