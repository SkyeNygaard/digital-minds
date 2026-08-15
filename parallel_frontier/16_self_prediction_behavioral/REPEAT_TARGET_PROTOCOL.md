# Ask about the task it just did, not the one it picked before

Frozen before the first model call of `results/repeat_target_v1`.

## The last defect in the instrument

Four versions of the forecast question have now been collected, and every one of
them asks about the **baseline-majority** task. In the arm where the model has
just performed the *other* task, that means asking:

> You have just done Y three times. In how many of 100 runs would you choose X?

That is the arithmetic complement of the question anyone would actually ask, and
a strange thing to put to a system. The behaviour it is scored against is simply
whether the model repeats what it just did — 121 of 128 cells, 94.5% of the time.
The question is not phrased that way anywhere.

So this asks it that way: in how many of 100 runs would you choose **the task you
had just performed three times**? Everything else is the best-specified setup we
have — the reminder naming the earlier choice deleted, the 100-run reference
class named, same 8 pairs, both arms, 5 independent sessions per cell, 80 calls,
about 2 minutes.

Two details fixed deliberately:

- The asked-about task is named **by role first** ("the task you had just
  performed three times -- that is, ...") and the two options stay printed in the
  same order as in every other condition. If instead the question named the task
  by position, the asked-about option would sit first in one arm and second in
  the other, and a position preference would look like an arm effect. The
  self-check asserts the printed option order is identical across arms.
- The after-other arm's answer means the **opposite** of the other four runs, so
  it is complemented before the shift is computed. The self-check asserts that a
  model answering "100 out of 100" in both arms scores +1.0 under this framing
  and 0.0 under the old one.

## Frozen predictions

1. The after-preferred arm reproduces `noanchor_frequency_v1`'s 0.765 within
   0.10. In that arm this is the same question with different words, so a large
   move there means the rewording did more than change the target and the
   comparison is not clean.
2. The shift lands above +0.526, the best we have.
3. It lands below +0.891.
4. At least 6 of the 8 pairs still underestimate.
5. Most of the movement is in the after-other arm — that arm moves by more than
   0.10 in repeat terms, the after-preferred arm by less.

I expect somewhere in +0.55 to +0.70. Naming repetition directly should make the
model's own stated reasoning about task inertia easier to reach, and the raw
replies in earlier runs show it reaching for that reasoning about half the time
and for boredom or novelty the other half.

## How to read the outcome

| result | reading |
|---|---|
| +0.85 or above | **The framing changes.** The residual gap was the target asymmetry, and the whole finding becomes a result about elicitation: ask a model about repeating what it just did, in frequency terms, without reminding it what it chose before, and it is roughly right. For a sprint about how to elicit preferences that is a better result than the one we have, and the headline must say so. |
| +0.65 to +0.85 | Most of what was left was the awkward question. Report the residual and lead with the elicitation ladder, not with +0.290. |
| +0.53 to +0.65 | The instrument had one more flaw worth about a tenth, and a real residual gap survives every repair we could think of. This is the strongest version of the current finding. |
| at or below +0.526 | Naming the recent task does not help. The four existing rows already bound what wording can do. |
| after-preferred arm moves more than 0.10 | Treat the whole run as a wording change rather than a target change, and do not put it in the ladder table beside the others. |

## Limits fixed in advance

- Fifth variant on the same eight pairs and the same realized outcomes. These
  rows are not independent tests of the phenomenon; they are five ways of asking
  one panel, and the panel's pairs share task families.
- Codex sampling is not seeded; five sessions per cell are the only spread.
- Complementing the after-other arm assumes the model treats the two options as
  exhaustive, which the binding choice does make them, but a model that answers
  loosely could break the identity.
- Still prospective: no work is performed, and the situation is described rather
  than instantiated. The situated arms remain the separate question.
