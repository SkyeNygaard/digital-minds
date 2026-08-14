# Plan: the scaled run

Written before running anything, so it can be vetoed.

## Where we are

We can already show two things, on two task pairs:

1. **Doing a task changes what the model picks next, completely.** After doing one
   kind of task three times, it chose that kind every single time; after doing the
   other kind, it never did. Eight out of eight.
2. **The model did not see this coming.** Asked beforehand what it would do in
   exactly that situation, it said it would probably switch away — 20% likely to
   stick with its favourite after doing it three times. It stuck with it 100% of
   the time.

That gap is the interesting thing. The model expects to get bored of a task and
instead gets stuck on it.

Two problems stop this being a result:

- **Only two pairs of tasks.** Two numbers cannot show that a mismatch is
  systematic rather than luck.
- **The effect is pinned at its maximum.** Both pairs came out at "always
  repeats". If the answer is always the same, there is nothing for a prediction to
  be right or wrong *about* — we can only say the model is wrong on average, not
  whether it tracks anything. To ask "does it know how much its preference will
  shift", the shift has to vary.

There is also an honest caveat we already measured: the effect needs the model to
be able to *see* the work it just did. Told about the same work in words instead,
the effect roughly halves and stops being distinguishable from nothing. So the
safe claim is about what the model does when its own recent work is in front of
it — which is exactly the situation the prediction question describes.

## What I want to run

All ten available task pairs, and crucially **two different amounts of work**:
doing the task once, and doing it three times.

For each pair:

- establish which task it prefers, with the labels and the order swapped around
  so a preference for the letter "Q" or for whatever is listed first cannot
  masquerade as a preference for the work;
- **before any work happens**, ask it to predict, separately, what it would
  choose after doing one task and after doing three;
- then actually make it do one or three, and record the binding choice;
- make it do the task it chose, so choosing is not free.

That is 760 model calls. Running four at a time, roughly 35 minutes.

## Why one-versus-three is the whole point

It gives the answer room to vary. If doing something once shifts the choice a
little and three times shifts it a lot, then there is a real quantity to predict,
and we can ask a much better question than "was the model right":

**Does the model know that more of a thing moves it more?**

A model can be badly wrong about the overall level and still track the direction
correctly. Those are different kinds of self-knowledge and worth separating.

## What each outcome would mean

- **Doses differ, and the model's predictions track them.** Genuine partial
  self-knowledge. The strongest result, and it would need saying carefully.
- **Doses differ, and the predictions do not track them.** The model cannot tell
  how much its own behaviour will move. This is the result I expect, and it is
  the cleanest version of the headline.
- **Both doses pin at "always repeats".** The effect saturates even after a
  single task. Then the prediction question stays unanswerable in this design and
  we need weaker manipulations — shorter tasks, or more similar pairs — before
  the sprint. Worth knowing in 35 minutes rather than after building on it.
- **No effect at all on the wider set of pairs.** The first two pairs were a
  fluke. That would kill the project, and it is much better to learn it now.

## The comparison that makes it a real claim

Being wrong is not by itself interesting — a model could be wrong in a way anyone
could have predicted. So we also check how well the shift could have been guessed
*without* asking the model: from how strongly it preferred the task to begin with.
This costs no extra calls, since we already collect that. If a simple outside
guess does as well as the model's own forecast, then asking a model about itself
adds nothing, which is the honest version of this finding.

## What I am not doing yet

Not scaling the "told versus shown" comparison. It is the more interesting
mechanism question, but it needs its own sample size, and the headline does not
depend on it. If the main run works, that is the natural second study.
