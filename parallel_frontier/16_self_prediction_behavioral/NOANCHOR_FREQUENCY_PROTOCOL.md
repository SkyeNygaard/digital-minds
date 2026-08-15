# Both forecast repairs at once

Frozen before the first model call of `results/noanchor_frequency_v1`.

## The missing cell

Two things are wrong with the prompt that produced the +0.290 headline, and each
has now been fixed on its own:

| what the forecast prompt does | mean forecast | truth |
|---|---:|---:|
| names the earlier choice, asks "how likely" | +0.290 | +0.891 |
| drops the earlier choice, asks "how likely" | +0.524 | +0.891 |
| names the earlier choice, asks for a count out of 100 | +0.417 | +0.891 |
| **drops it and asks for a count** | **not run** | +0.891 |

Without the fourth row the honest claim is only "neither repair on its own closes
the gap". That is a weaker statement than it sounds, because the two repairs may
be fixing the same mistake: both of them move the *after-other* arm and barely
touch the after-preferred arm, which is what you would expect if both simply stop
the model reasoning "but I picked the other one before, so maybe I stay". If they
overlap, doing both changes little. If they are independent, doing both should
land near +0.65. Neither is currently known.

This is the last forecast condition worth collecting: it is the best-specified
version of the question we know how to ask on this panel, so whatever it says is
what the paper should quote as the ceiling for prospective self-forecasting here.

## Design

`--ranking-panel --no-anchor --frequency`. Identical to `frequency_v1` except
that the sentence naming the earlier choice is dropped, which is the same single
deletion `prospective_noanchor_v1` made. Same 8 pairs, both arms, 5 independent
Codex sessions per cell, 80 cells, 80 calls, about 2 minutes. No treatment work
is executed — this is prospective only.

Scored against `ranking_v3`'s realized +0.891 and its own +0.290 forecast, so it
is directly comparable to the three rows above.

## Frozen predictions

1. Above +0.524 — doing both repairs is at least as good as the better one alone.
2. Below +0.891. The gap narrows but does not close.
3. **Below +0.651**, the sum of the two separate improvements. The repairs
   overlap rather than add, because both act on the same arm.
4. At least 6 of the 8 pairs still underestimate their realized effect.
5. Most of the change from +0.290 is again in the after-other arm: that arm moves
   by more than 0.15, the after-preferred arm by less than 0.10.

## How to read the outcome

| result | reading |
|---|---|
| +0.85 or above | **The framing changes.** The forecasting gap was mostly how we asked. The finding becomes a result about elicitation format — which for a sprint on preference-elicitation methods is a better result than the one we have, and the headline must say so. |
| +0.60 to +0.85 | Most of the gap was elicitation. Report the residual honestly and stop leading with +0.290 alone. |
| +0.52 to +0.60 | The two repairs overlap, as predicted. A substantial residual gap survives the best-specified question we can ask. This is the strongest version of the current finding. |
| at or below +0.524 | The repairs interfere. Something about combining them makes the answer worse; report it and do not treat any single row as the true forecast. |

## Limits fixed in advance

- The forecast still asks about the **baseline-majority** task, not "the task you
  just did". In the after-other arm that makes the question awkward — you just
  did Y three times, how likely are you to choose X — even though it is the
  arithmetic complement of the natural question. A cleaner instrument would ask
  about repeating the recent task directly. That is a fourth change and would
  confound this one, so it is named here as follow-up, not folded in.
- The 8 pairs share task families, so a t interval over them is descriptive.
- Codex sampling is not seeded; the five sessions per cell are the only spread
  estimate.
- Same harness as every other Luna run here: the model is wrapped in agent system
  instructions and the message list is flattened to one prompt.
