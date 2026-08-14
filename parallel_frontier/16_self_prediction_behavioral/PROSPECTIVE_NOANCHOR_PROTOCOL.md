# Does the consistency reminder cause the headline gap?

Frozen before the first model call of `results/prospective_noanchor_v1`.

## The objection this closes

The headline number is a prospective forecast of +0.290 against a realized
+0.891. That forecast prompt contains one sentence the binding choice does not:

> In earlier binding decisions you chose: X.

So the forecast is elicited under a pull toward consistency that is absent when
the behaviour is measured. And the largest part of the error is precisely a
failure to predict how completely the alternative work overrides X — the one
thing that sentence points at.

We tested this once already, but in the *situated* condition, where the work is
already present. That is not where the headline number comes from. This tests it
in the prospective condition, which is.

## Design

`ranking_v3`'s 8 admitted pairs, both arms, 5 independent sessions, prospective
only, `full_history` framing, one sentence deleted and nothing else changed.
80 calls. No treatment work is executed and no outcomes are collected; the
comparison is against `ranking_v3`'s own forecasts and realized effects.

## Frozen predictions

1. The no-anchor forecast will remain well below +0.891. The situated version of
   this check moved +0.060 of a +0.644 gap, and there is no reason to expect the
   prospective version to move much more.
2. At least 6 of 8 pairs will still underestimate.
3. The mean will move toward the truth rather than away.

## How to read the outcome

| outcome | reading |
|---|---|
| Forecast stays near +0.290 | The reminder is not the cause. The headline claim is clean and this objection is closed. |
| Forecast rises somewhat, still far below +0.891 | The reminder contributes; the gap does not depend on it. Report both numbers. |
| Forecast approaches +0.891 | The headline is substantially an artifact of the prompt asymmetry, and the claim must be narrowed to "a forecast asked this way is miscalibrated". |

The third outcome would be the most important result in the project and would
require rewriting the main claim. That is the point of running it.

## Limits

- Compares two unseeded collections made at different times, so this bounds the
  reminder's contribution rather than measuring it exactly.
- No new outcome cells; `ranking_v3`'s realized effects are the comparison.
- Eight pairs sharing task families, as throughout.
