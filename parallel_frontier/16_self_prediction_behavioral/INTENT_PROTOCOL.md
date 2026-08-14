# Is the effect path dependence, or is it following the user?

Frozen before the first model call of `results/intent_v1`.

## The objection this tests

The treatment is not simply "the model did task X three times". It is **three
user requests for X**, each followed by the model's own reply, and then a free
choice. An assistant trained to infer and satisfy user intent has a complete
explanation for choosing X next that has nothing to do with preference or path
dependence:

> The user has asked for X three times. Continuing with X is presumably wanted.

Nothing collected so far separates those. If intent-following is the driver, then
the binding-choice paradigm is measuring instruction-following, and calling the
result a revealed preference is wrong.

One piece of existing evidence argues against the simple version: told in a fresh
context that it just did X three times, Luna moves *away* from X (-0.450). Pure
intent-following should not reverse. But that is an inference from a different
condition, not a test.

## Design

Two conditions, identical except for one clause in an opening turn.

Both conditions begin with a user turn before the first task:

| condition | opening turn |
|---|---|
| `requested` | "You will now be given three tasks to complete. Please work through them." |
| `assigned` | "You will now be given three tasks to complete. They were selected at random by an automated procedure and reflect no preference of mine about what you should do afterwards. Please work through them." |

Everything after that is byte-identical to the confirmation's treatment: the same
three task prompts, the model's own replies appended, then the same binding
choice prompt, then the chosen task actually performed. **The choice prompt is
not touched**, because it is the measurement instrument.

The manipulation is deliberately placed at the start rather than at the choice,
so the context in which the choice is made differs only by what came before it.
That is also this design's main weakness: the clause is four turns away by the
time the choice happens.

8 pairs from `ranking_v3`, both arms, both conditions, 2 replicates, labels and
presentation order counterbalanced across replicates. 64 cells, ~320 calls.

## Frozen predictions

1. `requested` will reproduce the confirmation's effect, somewhere near +0.891.
   If it does not, the two runs are not comparable and nothing else here should
   be read.
2. `assigned` will remain large — above +0.6. My expectation is that the effect
   survives, because Qwen shows +1.000 without an agent wrapper and because the
   summary-only reversal is not what intent-following predicts.
3. The difference between conditions will be smaller than +0.3.

## How to read the outcome

| outcome | reading |
|---|---|
| Both near +0.89 | Intent-following is not required. The path-dependence reading is much better supported and "revealed choice" language is earned. |
| `assigned` drops a lot but stays positive | Both mechanisms contribute. Report the decomposition; stop calling it preference. |
| `assigned` collapses toward zero | The paradigm is measuring instruction-following, not preference. That is a more important result than the one we currently have, and the headline must change to say so. |

The third outcome would overturn the project's framing. It is the reason to run
this rather than another forecast condition.

## Limits fixed in advance

- One clause, four turns before the choice. A model that has stopped attending to
  it would show no difference for reasons unrelated to intent.
- Two replicates per cell rather than the confirmation's counterbalanced sixteen,
  so per-pair estimates are coarser.
- Codex sampling is not seeded.
- Fresh task seeds (100,000+), disjoint from every previous run.
