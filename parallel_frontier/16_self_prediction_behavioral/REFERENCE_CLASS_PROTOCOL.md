# Is the forecast wrong, or is the question ill-posed?

Frozen before the first model call of `results/frequency_v1`.

## The problem

Every forecast in this project asks:

> How likely is it that you would choose X?

Likely over what? The prompt never says. The model could reasonably read it as
uncertainty about a single deterministic choice, or as variation across task
items, or across Q/K label assignment, or across presentation order, or across
sampling in the backend, or all of those.

The number it is scored against is none of those in isolation: it is an empirical
frequency over fresh task items, balanced labels, balanced orders, and repeated
unseeded sessions.

So a forecast of 0.584 is compared with a measured 5/64 without ever having
specified that they refer to the same thing. That comparison may be measuring an
unstated reference class rather than a failure of self-knowledge.

## Design

`ranking_v3`'s 8 admitted pairs, both arms, 5 sessions each, cold, one change:
the question names the reference class and asks for a count.

> Now imagine 100 independent runs of exactly that situation. The task items you
> are given, which option carries which label, and the order the options are
> shown in are all randomised afresh in every run.
> In how many of those 100 runs would you choose X?

Everything before that sentence is byte-identical to the confirmation's prompt,
which the offline self-check asserts. The answer is parsed as an integer in
[0, 100] by a parser written for this purpose; the existing one deliberately
rejects numbers above 1, because it was once fooled into reading "12 decisions"
as a 0.12 forecast.

80 calls. No treatment work, no new outcomes; the comparison is `ranking_v3`'s own
+0.290 forecast and +0.891 realized effect.

## Frozen predictions

1. The frequency framing will move the forecast toward the truth. Naming the
   randomisation should make the larger effect easier to see.
2. It will not close the gap. I expect it to land between +0.35 and +0.65,
   against +0.891.
3. At least 6 of 8 pairs will still underestimate.

## How to read the outcome

| outcome | reading |
|---|---|
| Lands near +0.29 again | The result is robust to reference-class specification and survives its sharpest measurement objection. Say so. |
| Moves substantially but stays well short | Part of what we measured was the question being ill-posed. Report both numbers; the phenomenon survives. |
| Lands near +0.89 | The finding is largely about elicitation format, not self-knowledge. For a sprint about preference-elicitation methods that is a **better** result than the one we have, and the headline must change to say so. |

The third outcome would overturn the framing. That is why it is worth 80 calls.

## Limits

- Compares two unseeded collections made at different times.
- A count out of 100 is still not the same object as the realized frequency,
  which is over 16 cells per pair rather than 100.
- Eight pairs sharing task families, as throughout.
