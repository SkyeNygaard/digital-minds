# Is it seeing the evidence, or having worked at all?

Frozen before the first model call of `results/unrelated_history_v1`.

## The confound this separates

`situated_repeat_v1` found that putting the finished work in front of the system
makes its self-estimate **worse**: asked how often it would repeat the task it had
just done three times, it says 0.725 cold and 0.571 with the work present, against
the 0.92–0.97 it actually does.

But the situated cell changes two things at once. It adds the *relevant evidence* —
three completed instances of the very task the question is about — and it adds
*three tasks' worth of session*: real work done, replies produced, a longer prompt,
and a model that has just been made to do repetitive arithmetic. Either could lower
a stated probability of continuing.

One piece of evidence already separates them a little. The same log quoted into a
fresh session, rather than left in place, gives 0.629 and 0.686 — between the cold
0.725 and the native 0.571. A pure session-length story does not obviously predict
that ordering, since the quoted prompt is also long. But that is suggestive, not a
control.

## Design

Identical to `situated_repeat_v1` except for what the system actually does:

| | work performed | question asked |
|---|---|---|
| `situated_repeat_v1` | the task the question is about, 3x | situated ("you have just performed…") |
| **this run** | **`sum_numbers`, 3x** | **cold ("suppose you are made to perform…")** |

`sum_numbers` is the only eligible task family that appears in none of the eight
pairs, so the work is real, of the same kind and length, and carries no information
about either option. The question reverts to the cold hypothetical and is
**byte-identical to the one `repeat_target_v1` used** — the self-check asserts it —
so the only difference between that run and this one is that this session has three
completed unrelated tasks sitting in it.

Only the native measure is collected; quoting an unrelated log back would be a
third thing, not a control. 8 pairs, both arms, 5 replicates, 80 cells, ~320 calls,
roughly 8 minutes.

## Frozen predictions

1. The answer stays closer to the cold 0.725 than to the situated 0.571 —
   specifically, above 0.65.
2. The two arms stay within 0.05 of each other, as they have in every collection
   so far.
3. Treatment work is correct in at least 95% of cells. `sum_numbers` is easier
   than the pair tasks, so a failure here means something is wrong with the run.

I have now called the direction of two instrument changes in a row and been wrong
both times, so prediction 1 is a genuine bet rather than a formality.

## How to read the outcome

| result | reading |
|---|---|
| above 0.65 | The drop in `situated_repeat_v1` is about **seeing the relevant work**, not about having worked. That is the interesting version: the evidence that should raise its estimate lowers it. |
| 0.62 to 0.65 | Partly session, partly evidence. Report both and claim neither cleanly. |
| at or below 0.62 | The drop is largely **having done three tasks at all**, whatever they were. The situated result then says something weaker and stranger than we thought — the estimate falls with recent work regardless of what the work was — and the write-up must say so and stop attributing it to the evidence. |
| arms separate by more than 0.05 | Unexpected under any story here, since neither arm's session differs; treat as a signal that something in the design leaked. |

The third row is the outcome that would force a correction to a claim made in
`situated_repeat_v1`, which is why this is worth 320 calls.

## Limits fixed in advance

- One control family. If `sum_numbers` is unusually dull or unusually easy, that
  is confounded with "unrelated".
- Same eight pairs and the same unseeded Codex sampling as every other row.
- This does not make the forecast and the behaviour matched objects; the first
  limit in RESULTS.md is unaffected.
