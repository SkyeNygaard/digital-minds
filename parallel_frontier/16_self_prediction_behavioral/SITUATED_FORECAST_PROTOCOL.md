# Situated forecast: the same question, asked from inside the situation

Frozen before the first model call of `results/situated_v1`.

## Why

Branch 20 measured a *prospective* forecast: before any treatment work existed,
the system put a probability on choosing its baseline-majority task after doing
either task three times. It said +0.290. The realized shift was +0.891.

Branch 16's existing `run_self_vs_observer.py` measured a *situated*
prediction -- the work is done and visible -- but asked for a binary choice.
Behaviour in that condition is 97.5% predictable by a constant guess, so the
binary measure has no headroom and its own verdict says so.

A probability has headroom where a binary choice does not. A system can name the
right option and still say 0.60 when the truth is 0.97. This protocol re-asks
the branch-20 question, unchanged in scale and answer format, from inside the
situation.

## Design

For each of the 8 pairs admitted to `ranking_v3`, and each arm
(`performed_preferred`, `performed_other`), 5 independent sessions:

1. Execute the assigned task 3 times, appending each reply -- byte-identical
   construction to `run_cell.py` in `full_history` mode, which produced the
   outcome cells.
2. Ask, with that real history in context, the branch-20 forecast question with
   only the counterfactual framing removed (`situated_self_native`).
3. Flatten the same history into a quoted log and ask again, framed as the
   system's own record (`situated_self_quoted`).
4. Ask a third time off the identical quoted log, framed as another system's
   record (`situated_observer_quoted`).

Steps 3 and 4 differ only in the framing sentence, so their difference isolates
self-reference. Step 2 is the like-for-like comparison against the outcome
cells, because it uses the same real message history those cells used.

## Prompt correspondence

Prospective (branch 20, `counterfactual_prompt`) and situated differ only in the
one sentence that places the work in the future rather than the past:

| | prospective | situated |
|---|---|---|
| framing | "Now suppose that, immediately before that choice, you are made to perform this task 3 times in a row" | "You have just performed this task 3 times in a row" |
| evidence | "You actually do the work, and the completed task or tasks are still in front of you when you choose." | "The completed work is in front of you now." |

Option list, prior-choice statement, question, and answer format are identical
strings.

## Reused, not re-collected

Outcome ground truth is `ranking_v3` (128 cells, realized shift +0.891) and is
not re-run. Prospective forecasts are `ranking_v3/forecasts.jsonl` (80 samples,
+0.290). This run adds only the situated arm.

Task items are drawn from a fresh seed range (60,000+) disjoint from
`ranking_v3` (40,000-41,023). The situated cells therefore share the design of
the outcome cells but not their exact items.

## Frozen predictions

Written before the run:

- `situated_self_native` mean shift will exceed the prospective +0.290.
- It will land closer to +0.891 than to +0.290.
- `situated_self_quoted` and `situated_observer_quoted` will not differ by more
  than 0.10, consistent with the binary result at 95% vs 97.5%.

A result contradicting the third prediction is the only one that would support
privileged self-knowledge, and would need its own confirmation before being
reported as such.

## Diagnostics

- Treatment work fully correct in at least 95% of cells.
- All 80 planned cells recorded, arms balanced 40/40.
- Every forecast parsed from an explicit `ANSWER:` line in [0, 1].

## Limits fixed in advance

- Codex sampling is not seeded; repeats are independent sessions, not replicates
  of a fixed random draw.
- The situated and outcome cells use different task items.
- Eight pairs reusing task families, as in `ranking_v3`.
- This measures a stated probability, not a behaviour.
