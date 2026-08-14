# Plan: the one control that finishes branch 01

Written before running.

## Where this branch stands

Researchers have published a direction inside the model that behaves like "how
well things are going". We asked a sharper question: is it about how well things
are going **relative to what the model was told to achieve**?

The test keeps the outcome sentence identical and flips the goal. "The final
total is 7" is a success if the goal was an odd total and a failure if it was an
even one — same sentence, opposite meaning. Across sixteen matched pairs the
outcome sat higher on the welfare direction when it satisfied the goal than when
it failed it, **sixteen times out of sixteen**. It was still sixteen out of
sixteen in a version where the words "even" and "odd" were replaced by
meaningless labels, so no success-or-failure wording appears anywhere. Every goal
word is used equally often on the winning and losing side, so the effect cannot
be the words themselves.

## The hole

We compared against exactly **one** randomly chosen direction, which showed
nothing. That rules out "any direction whatsoever would do this". It does not
rule out the more serious objection: **maybe any *meaningful* direction would do
this**, and there is nothing special about the welfare one.

If a plain good-versus-bad direction — nothing to do with goals — shows the same
flip, then the result is about the model noticing something went right, and the
"relative to its goal" framing is unearned.

## What I am running

Two comparisons, both on exactly the same recorded internal states, so nothing
about the model or the prompts changes.

1. **Against many random directions, not one.** Two thousand of them, to see
   where the welfare direction falls in that spread. One random draw is a noisy
   yardstick; this is the proper one.
2. **Against a plain good-versus-bad direction.** I build it from the model's own
   states for blatantly good and blatantly bad situations — "every step has
   succeeded" versus "every step has failed" — with no mention of goals. Then I
   ask whether *that* direction also separates goal-success from goal-failure.

I also record the two directions' similarity to each other, which says directly
whether the welfare direction is just a valence direction wearing a different
name.

About two minutes on the laptop's graphics memory. No cost.

## What each outcome means

- **The welfare direction stands out from the random spread, and the plain
  good-bad direction does *not* reproduce the flip.** The goal-relative claim is
  earned, the branch is finished, and it is a submittable result.
- **Both directions show it.** Then what we found is that the model represents
  "something went right", not "something went right *for me, given my goal*". A
  weaker but still perfectly honest result, and the write-up says so.
- **The welfare direction sits inside the random spread.** The sixteen-out-of-
  sixteen was an artefact of comparing against a single unlucky draw, and the
  branch stays parked. Worth two minutes to find out.

The second and third outcomes are the reason to run it. I would rather find this
now than have a reviewer find it.
