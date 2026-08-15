# Intent test, rerun with the task items actually matched

Frozen before the first model call of `results/intent_matched_v1`. Supersedes
`INTENT_PROTOCOL.md` for the reported number; `intent_v1` stays on disk as
collected.

## Why this is being rerun

`INTENT_PROTOCOL.md` says the two conditions differ by one clause and that
"everything after that is byte-identical ... the same three task prompts". That
was not true of `intent_v1`. The runner built its cell list as a product over
pair x arm x condition x replicate and then numbered the task seeds along that
list, so moving from `requested` to `assigned` also moved the seed. Checked
against the raw cells: **0 of 32 matched cells share a seed** — for
`add_ten|double_numbers`, after-preferred, the two conditions used seeds 100000
and 100016. The two conditions were asked to double different numbers.

That does not by itself invalidate the −0.250 difference: which five integers
appear has no obvious relation to which condition a cell is in, and the effect
was unchanged on the largest set of pairs sharing no task family. But the
sentence in the writeup is false as it stands, and a diagnostic whose whole
claim is "one clause and nothing else" has to actually hold the rest fixed.

The second problem is resolution. Two replicates quantise each pair's shift to
steps of 0.5, and the result rests on 4 of 8 pairs moving by exactly one step.

## What changed

1. Task seed, Q/K label and presentation order are now fixed by
   (pair, arm, replicate). The two conditions share all three. The runner's
   offline self-check asserts this for every cell, so the failure that produced
   `intent_v1` cannot recur silently.
2. 4 replicates instead of 2. Per-pair shifts land in steps of 0.25, and each
   pair still gets a balanced 2x Q/QK and 2x K/KQ.
3. Nothing else. Same 8 pairs, same two preambles byte for byte, same choice
   prompt, same fresh seed block (100,000+), same model and harness.

128 cells, ~640 calls, roughly 11 minutes.

## Frozen predictions

1. `requested` reproduces `intent_v1`'s +0.812 within 0.15, and stays below the
   confirmation's +0.891. If it does not, the runs are not comparable and
   nothing below should be read.
2. `assigned` is lower than `requested`. The difference is at least −0.10.
3. The difference is smaller than `intent_v1`'s −0.250 in magnitude. Stated
   plainly so it can be scored: matched task items remove one source of noise
   between the conditions, and I expect a slightly smaller and better-resolved
   estimate rather than a larger one. I have been wrong about a movement's size
   before — the prospective no-anchor prediction was off by fourfold.
4. More than 4 of 8 pairs show a nonzero drop, because the step is now 0.25.

## How to read the outcome

| outcome | reading |
|---|---|
| difference near −0.25, most pairs move | The intent contribution is real and `intent_v1`'s number survives matching. Report it, with the wording limit below. |
| difference between −0.10 and −0.20 | Real but smaller than reported. Correct the number; finding 6 stays, weaker. |
| difference near zero | `intent_v1`'s result was an artifact of unmatched task items. Finding 6 is withdrawn. |
| difference well past −0.40 | Intent-following is a larger part of the paradigm than reported, and the headline has to say so. |

## What this design still cannot show

Even with matched items this is **not** a decomposition of the effect into
"intent" and "not intent". The `assigned` condition still delivers three
consecutive user-role requests for the task; the disclaimer only denies that
they express a preference. It also adds words, adds a claim about randomisation,
and may make the model treat the exchange as an experiment. So the finding this
run can support is:

> Telling the system the repeated tasks were randomly assigned and wanted by
> nobody reduces the measured effect by *d*, which is consistent with inferred
> user intent contributing to it.

Not "*d* of the effect **is** user intent". The writeup must use the first
wording whatever the number turns out to be.

Other limits, unchanged from `INTENT_PROTOCOL.md`: the clause sits four turns
before the choice, so a model that stopped attending to it would show no
difference for reasons unrelated to intent; Codex sampling is not seeded; the 8
pairs share task families, so a pair-level t interval over them is descriptive,
not an independent-sample test.
