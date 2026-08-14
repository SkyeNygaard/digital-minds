# Plan: does the model know which situations will move it most?

Written before running.

## What prompted this

Comparing two experiments that happened to use the same five pairs of chores, the
model's predictions lined up well with how much each pair actually shifted it
(correlation 0.87). That would mean it has *partial* self-knowledge: right about
the ordering, badly wrong about the direction and the size — it predicted a
slight move away where the real move was strongly towards.

That is a better and more precise finding than "it knows nothing". But I do not
believe it yet, for a specific reason.

## Why I do not believe it yet

The same quantity — how much a given pair shifts the model — was measured twice,
and the two measurements disagree. One run used eight observations per pair and
found shifts bunched at 0.75 to 1.00. The other used sixteen and found 0.38 to
1.00. Same pairs, same amount of work, different answers.

So the per-pair number is too noisy at this size for a five-point correlation to
mean anything. With five points, one pair moving changes the answer completely.
The 0.87 and the earlier −0.21 are both consistent with "we cannot tell yet".

## What I am running

Two changes, both aimed at the same weakness:

1. **More pairs.** The pair list was cut to five arithmetic chores because the
   small local model cannot do character-level tasks such as reversing a string
   or alphabetising words. The large model can. Opening the list to all ten
   families gives far more pairs, and more points is the only thing that fixes a
   five-point correlation.
2. **More observations per pair**, so each pair's shift is measured precisely
   enough to be ranked at all.

Predictions are still collected before any work happens, and only for pairs that
pass the stability screen.

Roughly 900 calls, four at a time, about half an hour.

## What each outcome means

- **The ranking holds with more pairs.** Partial self-knowledge: the model knows
  which situations will move it, and is wrong about which way. That becomes the
  centre of the write-up, and it is a more interesting claim than a flat failure.
- **The ranking disappears.** The 0.87 was five-point luck. The finding reverts to
  the simpler one — the model is wrong about its own change and its predictions
  carry no usable information — which is still solid and already replicated on
  two models.
- **The pairs mostly fail the stability screen.** Character-level chores may not
  produce stable preferences. Then we learn the method's limits and stay with
  five pairs, reporting the correlation as untested.

I do not need a particular answer here. The current claim in the write-up does
not depend on it — this decides whether we can say something *stronger*.
