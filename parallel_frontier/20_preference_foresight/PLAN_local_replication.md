# Plan: repeat the whole thing on a small model running here

Written before running.

## What I am doing

Exactly the same experiment as the one that produced the result — same five task
pairs, same one-versus-three amounts of work, same shuffling of labels and order,
same predictions asked before any work happens — but with a much smaller model
(Qwen3-4B) running directly on this machine instead of a large model reached
through a command-line tool.

## Why this is the most useful thing to run next

The finding so far has one big soft spot: everything came from a single model,
reached through a wrapper that adds its own instructions and squashes the
conversation into one prompt. Two objections follow, and I cannot answer either
from the data we have:

1. **Maybe it is that one model.** One model doing something is an anecdote.
2. **Maybe it is the wrapper, not the model.** The tool we used inserts its own
   text around every request. For an experiment about what a model chooses, the
   wrapper is a genuine suspect.

Running it here kills both objections at once, because this model is loaded
directly with nothing wrapped around it, and it is a completely different model —
smaller, from a different maker, and open. If the same mismatch shows up in both,
it is a property of language models rather than of one product.

It is also free and repeatable: the model picks its single most likely reply every
time, so the run can be reproduced exactly.

## What each outcome would mean

- **Same pattern — repeats what it just did, predicts it will not.** The finding
  holds across a 100-fold difference in model size and across two completely
  different setups. This is the outcome that makes it a real phenomenon and it is
  what I would build the submission around.
- **It repeats itself but its predictions are fine.** Then the failure to predict
  is specific to the larger model, which is interesting in the opposite
  direction — it would suggest bigger models are worse at this, not better.
- **It does not repeat itself at all.** Then the effect belongs to the larger
  model or its wrapper, and the honest headline shrinks to a claim about one
  system. Better to know now than during the sprint.
- **It cannot do the task well enough to measure.** Possible: this model is small.
  It might not give a usable probability when asked to predict itself, or might
  not hold a steady preference for the screening step to detect. That is a null
  result about the method, not about models, and I will say so rather than
  dressing it up.

## Cost and care

About 400 model calls, roughly 40 minutes, no money — it runs on the laptop's
graphics memory.

Two safety points specific to running here. Only one model job can use the
graphics memory at a time, so a memory check runs first and refuses if anything
else is loaded or if there is not enough room. And the requests must go one at a
time rather than four at once, unlike the previous run, because the model is a
single thing in memory rather than four independent sessions.

The task instructions have to be word-for-word the ones this model was checked
against. It scores 0 out of 16 and 16 out of 16 on the *same* questions depending
on that wording, so a mismatch would mean the tasks were never shown to be doable
here. The script refuses to start if they differ.
