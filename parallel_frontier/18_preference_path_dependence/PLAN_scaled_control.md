# Plan: settle "shown" versus "told" properly

Written before running.

## The question, and why it decides the wording of the whole write-up

When a model does a chore three times and then picks again, it picks the same
chore. The question is whether that is because it now *wants* that chore, or
simply because its own recent work is sitting in front of it and carrying on is
the obvious thing to write next.

We separate them by changing only what the model can see at the moment of
choosing, never what it actually did:

- **shown** — the record of the work it just did is in front of it;
- **told** — a fresh start, plus one plain sentence saying which work was just
  completed;
- **neither** — a fresh start and no mention of it. Nothing should happen here;
  it is there to prove the setup is not leaking the answer some other way.

If being *told* is enough, the model is reacting to the fact of having done the
work, and calling it a preference is fair. If only being *shown* works, then it
is continuing a visible pattern, and the honest headline is that an apparent
preference can be manufactured by what is sitting in the context window.

## Why the current version cannot settle it

We ran this on two pairs of chores. Shown: a large, solid effect. Told: about
half the size, and **not distinguishable from no effect at all** — and the half
that showed up came from one of the two pairs while the other sat at chance.

That is the worst possible state: too big to dismiss, too small to claim. It
needs more of the same, not something different.

## What I am running

The same three conditions on all five pairs of chores that passed screening, and
twice over, so each condition gets forty observations instead of eight. Nothing
else changes — same amount of work, same shuffling of labels and order.

Roughly 1,200 model calls, four at a time, about fifty minutes. It runs on the
network, so it does not interfere with the small-model run using the laptop's
graphics memory.

## What each outcome means

- **Told works too.** The model responds to knowing what it did, not just seeing
  it. "Experience changes what the model wants" becomes defensible, and the paper
  gets stronger and simpler.
- **Only shown works.** The effect is pattern continuation. The write-up changes
  to "an apparent preference produced entirely by recent context" — which is
  arguably the more interesting and more useful finding, and is certainly the
  more honest one.
- **Neither works at this scale.** The original result was two-pair luck. That
  would be bad news, and much better found now than by a judge.
- **The fresh-start condition shows an effect.** Something is leaking — the
  randomisation or the label shuffling. Everything would need re-checking.

Any of the first three is publishable. I do not need a particular answer, which
is the point of running it.
