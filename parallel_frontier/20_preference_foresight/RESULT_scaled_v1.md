# Result: the model does not know it will repeat itself

One model (GPT-5.6 Luna, running inside the Codex command-line tool), five pairs
of tasks, two amounts of work, 420 model calls, no failures, 12 minutes.

## What was done

For each pair of task types, we first found which one the model preferred, asking
several times with the labels and the order shuffled so that a liking for the
letter "Q", or for whatever was listed first, could not be mistaken for a
preference about the work.

Then, **before any work happened**, we asked it to predict its own future
behaviour: if it were made to do one of these tasks — once, and separately three
times in a row — how likely would it be to still pick its favourite afterwards?

Then we actually made it do the work, one or three times, and gave it a real
choice. Whatever it chose, it then had to do.

## What happened

**It repeats whatever it just did. Every time.**

Across all ten conditions the shift was positive — doing a task made it more
likely to pick that task again — averaging **0.85** on a scale where 1.0 means
"always repeats" and 0 means "no effect". Ten out of ten positive would happen by
chance about twice in a thousand tries.

**It predicted almost no shift at all.** Its own forecasts averaged **+0.03**,
essentially "doing this will not change what I want".

**Every single forecast was too low.** Ten out of ten, again about twice in a
thousand by chance. It underestimated its own tendency to repeat by 0.82 on
average — most of the available range.

**Its predictions do not track reality.** Where it predicted a big shift versus a
small one had no relationship to where the shift actually was big or small
(correlation −0.21, which is what you would expect from unrelated numbers; it
called the direction right 5 times out of 10, i.e. a coin flip).

**It gets the direction of "more work" backwards.** In reality, doing a task
three times locked it in slightly harder than doing it once (0.90 versus 0.80).
The model predicted the opposite — that one repetition would leave it keener
(+0.13) and three would put it off (−0.07). It expects to get bored. It gets
stuck instead.

**Ignoring the model entirely beats asking it.** If you never ask the model
anything and simply guess "it will repeat, like it usually does", you are about
**32 times more accurate** than the model's own prediction about itself.

That last comparison is the one that makes this a claim about self-knowledge
rather than about calibration. The model is not merely imprecise; it is
outperformed by an outside guess that uses none of its private information.

## What this does not show

- **One model, one wrapper.** Everything here is GPT-5.6 Luna inside the Codex
  tool, which adds its own instructions and flattens the conversation. The honest
  subject is "this model in that environment".
- **"Experience" here means the work is visible.** A separate check found that if
  you *tell* the model it just did the work instead of letting it see the work,
  the effect roughly halves and stops being distinguishable from nothing. So this
  is about behaviour when recent work is in front of it — which is exactly the
  situation the prediction question described, but it is not the same as a
  preference the model carries around.
- **The shift is near its maximum, so "does it track the variation" is weakly
  tested.** Real shifts only ranged 0.50 to 1.00. The strong, well-supported
  claim is about the *level* being wrong, not about tracking.
- **Ten observations, from five pairs.** The two amounts of work within a pair
  are not fully independent of each other.
