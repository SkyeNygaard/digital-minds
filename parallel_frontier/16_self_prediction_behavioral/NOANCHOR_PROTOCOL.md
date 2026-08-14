# Does naming the earlier choice cause the forecast error?

Frozen before the first model call of `results/situated_noanchor_v1`.

## The problem this tests

Every forecast prompt in this project contains one sentence:

> In earlier binding decisions you chose: {baseline-majority task}.

The binding choice itself contains no such sentence. `choice_prompt` lists two
options and asks. So the forecast is elicited under a pull toward consistency
that is absent when the behaviour is measured.

This is not hypothetical. Situated replies in `results/situated_v1` give that
sentence as their reason: "Given the earlier binding decisions, I would be fairly
likely to choose doubling: about 0.8."

If that sentence is doing the work, then part of the headline gap is an artifact
of asking the question differently from how the behaviour was measured, rather
than a failure of self-knowledge.

## Design

`results/situated_v1` repeated exactly, with that one sentence deleted and
nothing else changed: same 8 pairs, same 2 arms, same 5 repeats, same three
question framings, same dose, same answer format. Fresh task seeds (80,000+),
disjoint from `ranking_v3` (40,000-41,023) and `situated_v1` (60,000-60,639).

The question still names the task the probability is about, so it remains
well-posed without the anchor.

## Frozen prediction and how to read it

The realized shift is +0.891, from a retention of 0.969 after the
baseline-majority task and 0.078 after the alternative. The anchored situated
forecast was +0.223.

If the anchor inflates the after-alternative arm, deleting it should pull that
arm down toward 0.078, which raises the measured shift toward +0.891.

| Outcome | Reading |
|---|---|
| Shift rises substantially toward +0.891 | The anchor carries a real part of the gap. The claim narrows from "the system misreads itself" to "the system's forecast is pulled by being reminded what it chose before." |
| Shift stays near +0.223 | The anchor is not the cause. The self-knowledge reading survives an obvious and specific objection. |
| Shift falls further | Unexpected; would need its own explanation before anything is claimed. |

Prior written before the run: some movement, but not most of the gap. A single
sentence carrying a difference between 0.71 and 0.078 would be surprising.

Either of the first two outcomes is worth having. This is a robustness check on
an existing claim, not a new claim.

## Diagnostics

Same as `SITUATED_FORECAST_PROTOCOL.md`: all 80 planned cells recorded, arms
balanced 40/40, every forecast parsed from an explicit `ANSWER:` line in [0, 1],
treatment work fully correct in at least 95% of cells.

## Limits

- Codex sampling is not seeded.
- Fresh task items, so this shares the design of the outcome cells but not their
  draws.
- Eight pairs reusing task families, as throughout.
- Comparing two runs collected at different times in an unseeded harness; a
  difference smaller than the within-arm spread in `situated_v1` (0.134 and
  0.191) should not be read as an effect.
