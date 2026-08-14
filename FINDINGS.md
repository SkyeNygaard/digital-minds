# What we found

## The setup

Give a model two kinds of small chore. Find which it prefers, asking repeatedly
with the labels and the order shuffled so that liking the letter "Q", or whatever
is listed first, cannot be mistaken for liking the work. Then — **before anything
happens** — ask it to predict what it would choose after being made to do one of
them. Then actually make it do that work, and give it a real choice it has to
carry out.

## Five findings

**1. Models repeat whatever they just did.** Between +0.81 and +1.00 on a scale
where 1.0 means "always repeats", and positive in every single condition tested.
It overrides the preference the model expressed minutes earlier.

**2. They do not see it coming.** Their own forecasts average about zero — "this
won't change what I want" — and were **too low in every single condition**, on
both models, about twice in a thousand by chance.

**3. Their forecasts carry no information about where the effect is larger.**
With eleven pairs of chores, the relationship between what they predicted and
what happened is −0.16: none. They call the direction right about half the time,
which is a coin flip. An earlier five-pair estimate suggested they might rank
correctly; more pairs killed it.

**4. Ignoring the model beats asking it.** Guess "it will repeat, like it usually
does" and you are roughly **36 times more accurate** than the model's own
prediction about itself. This is what makes it a claim about self-knowledge
rather than about calibration: the model is outperformed by a guess that uses
none of its private information.

**5. The failure is anticipation, not prediction.** Show a model the record of
what it just did and ask what it will choose next, and it gets it right 95% of
the time — but so does the same model told the record belongs to someone else,
and so does simply guessing "repeat" (97.5%). Given the situation, the model
reads it correctly. Asked beforehand what that situation would do to it, it gets
the direction wrong.

## Replication

Findings 1–4 hold on two systems that share almost nothing: a large model reached
through a command-line agent tool, and a small open model (Qwen3-4B) running
locally with nothing wrapped around it and no randomness. Different size, maker,
and setup; the same result.

## What did not replicate, and is therefore not claimed

We found that the large model **reverses** when it is *told* it just did the work
rather than *shown* the record — it avoids the task instead of repeating it. That
was clean and significant, and it looked like a mechanism.

The small model shows no reversal at all: told is almost as effective as shown.
So this is a difference between models, not a general property, and it is not the
headline. Recorded, not built on.

## Limits, stated plainly

- Two models. Both are instruction-tuned assistants.
- The chores are small and deterministic. Nothing here speaks to preferences over
  anything that matters.
- The effect is near its maximum in most conditions, which limits how well
  "does it know *how much* it will change" can be tested.
- Nothing here is evidence about consciousness, feeling, or welfare. These are
  measurements of choices and predictions.
