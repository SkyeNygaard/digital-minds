# Plan: does knowing it is *you* help?

Written before running.

## The question

Published work reports that a model predicting its own behaviour beats a
different model trying to predict it — evidence of some privileged access to
itself. Our results point the other way: every self-forecast we have measured has
been worse than a trivial guess that ignores the model.

Those can both be true, because they are not the same test. So run the direct
one.

## The design

We put the model in a situation we already know shifts its choices: it does one
kind of chore three times, then picks what to do next. Then we fork three ways
from **exactly the same transcript**:

1. **Self** — a fresh session is shown the transcript as its own, and asked what
   it will choose next.
2. **Observer** — a fresh session is shown the identical transcript, described as
   a log of *another* system, and asked what that system will choose next.
3. **Reality** — the choice is actually made, and the chosen chore is actually
   done.

The only difference between the first two is whether the record is presented as
the model's own. Everything else — the model, the transcript, the question — is
held fixed.

Note this is deliberately a *tighter* comparison than the published one, which
used a second, different model as the observer. Using the same model as its own
observer holds ability constant, so anything left is about self-reference rather
than about one model being smarter than another.

## What each outcome means

- **Self beats observer.** Knowing the record is yours helps. That supports the
  published finding and complicates ours — we would then say self-knowledge
  exists but is swamped by a large behavioural effect the model cannot see.
- **They are the same.** There is no privileged access here; the model predicting
  itself is just reading a transcript, like anyone else. This is what our other
  results predict, and it sharpens the story considerably.
- **Observer beats self.** Being told it is you makes prediction *worse* —
  presumably because the model reasons about what it would sensibly do rather
  than what the transcript implies. That would be the most interesting outcome and
  the one most worth writing up.

All three are reportable. Roughly 280 calls, about fifteen minutes.
