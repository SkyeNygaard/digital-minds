# What has actually been run, and what is parked

One page, so nothing gets lost again.

Status words mean:

- **LIVE** — the current work.
- **SUPPORTING** — not a paper of its own, but the current work needs it.
- **PARKED** — real work, real result, deliberately set aside. Revival condition
  given.
- **CLOSED** — do not restart without new information. Reason given.
- **SCAFFOLD** — design and sometimes code exist, never run against a model.

---

## LIVE

### 20 — Preference foresight
**Does a model know how its own choices will change?** Ask it to predict what it
will pick after being made to do a task; then make it do the task and give it a
binding choice.

**Result (GPT-5.6 Luna, 5 pairs, 420 calls):** it repeats whatever it just did
(+0.85 out of a possible 1.0, every one of 10 conditions positive), predicts
almost no change (+0.03), and is too low in every single condition. Its
predictions carry no information about where the change is larger. Ignoring the
model and guessing "it will repeat" is **32x more accurate** than its own
forecast. Full write-up in `parallel_frontier/20_preference_foresight/RESULT_scaled_v1.md`.

**Replicated on a second model (Qwen3-4B, local, no agent wrapper, deterministic
decoding, 550 calls):** realised change **+1.00 in every one of 10 observations**,
predicted **+0.16**, error **−0.84** — nearly identical to the large model's
−0.82. Two models sharing almost nothing — different size, maker and setup — give
the same result, which answers both "it is that one model" and "it is the
wrapper". 20 of 112 cells were lost because the small model answered the choice
and then did the chore in the same reply; arm balance among survivors 47/45.

---

## SUPPORTING

### 18 — Told versus shown
Same treatment, but the model either sees the work it just did, is only told
about it in words, or gets a fresh start.

**Result:** shown, the effect is large and solid. **Told the same fact, it
roughly halves and is no longer distinguishable from nothing** — and what remains
comes from one of two pairs. Fresh start, nothing.

**Why it matters:** it decides whether branch 20 may say the model *acquired a
preference* or only that it *continues a visible pattern*. On current evidence,
the second. **This is the one supporting experiment worth more calls** — two
pairs is too thin to settle the word choice the whole write-up depends on.

### 19 — Self-knowledge of existing preferences
Predicting which task it will choose, with no experience manipulation — the
static version of branch 20.

**Result (Qwen3-4B, 7 pairs admitted):** its own forecasts score **worse than a
baseline that ignores the model and predicts the average**, on both a plain
numeric and a structured elicitation, with negative correlation between forecast
and outcome. Same direction as branch 20, on a different model and a simpler
question.

**Note the tension worth writing about:** published work finds models predict
themselves *better* than an outside model can. Both of our branches find the
opposite. The likely reconciliation is that the published result trains models to
predict themselves, while we ask cold. Say so rather than claiming a refutation.

### 04 — Binding budgets and executed work
**Its headline is dead; its machinery is load-bearing.** The economic-consistency
measure was retired twice — once in `DEPRECATED_CCEI_HEADLINE.md`, then again
independently when a simulated coin-flipping agent scored *better* than the model
on three of four conditions, and no grid size fixed it. The limitation is
structural: making choices consequential is what caps how many you can collect.

What survives and is used everywhere: task families, competence screening, pair
admission, and the rule that a chosen task is actually performed.

**Revive if:** the test moves to 3–4 task types rather than 2. Consistency tests
gain power sharply with more goods. That is a new design, not a retune.

---

## PARKED

### 01 — Goal-relative welfare — DOWNGRADED by its own control
Does the welfare direction represent *how things are going relative to the
model's goal*? Identical outcome sentence, opposite goals.

**What it looked like:** the same outcome sat higher on the welfare direction
when it satisfied the goal than when it failed it, **16 matched pairs out of
16**, in both the worded and the wordless version, against one random direction
that showed nothing.

**What the control found:** that is not evidence of anything specific.

- Against **2000** random directions rather than one, 16/16 is unremarkable:
  roughly 15% of random directions also score 16/16 in the worded version
  (p = 0.15), and 4.5% in the wordless one. The sixteen paired differences share
  a large common component, so they are nowhere near independent — the "16 out of
  16, that's one in 65,000" reading was simply wrong.
- A **plain good-versus-bad direction**, built from the model's own states for
  "every step succeeded" versus "every step failed" and never mentioning goals,
  scores **16/16 and 14/16** — as well as the welfare direction. And it is
  essentially unrelated to it (similarity +0.011).

**What survives:** the model does internally distinguish goal-met from goal-
missed. That is real but unsurprising, and it is not carried by the welfare
direction in particular — a wide family of directions picks it up.

**What does not:** the claim that the published welfare direction encodes
*goal-relative* welfare. Not supported here.

**Lesson worth keeping:** counting how many matched pairs point the right way is
not a significance test when the pairs share structure. The null has to be built
from directions, not from coin flips. This is the same mistake as the two gate
defects in branches 18 and 20, in a third costume.

### winner_protocol — Reporting an imposed welfare state
Can a model report a welfare state that was pushed into it, through an arbitrary
label learned in context?

**Result:** no, at exactly chance — with every control passing. The model does the
same task perfectly when the state is visible (48/48); the state is genuinely
present where the answer is produced (recoverable 87% of the time, about a
1-in-2000 fluke, and it survives removing the pushed-in direction itself); the
output is well formed. So the information is there and goes unused.

**Why parked:** a clean negative result about a different question. Including it
in the preference submission would dilute both.

**Revive if:** submitting a second, mechanistic piece. Also worth revisiting with
a *trained* readout rather than a simple one — the null is currently scoped to a
simple linear reader.

---

## CLOSED

Nothing is formally closed. The two dead headlines (04's consistency measure, and
the single-token version of the welfare readout) are recorded above and in
`parallel_frontier/RESEARCH_OS_LEDGER.md` with their reasons.

---

## SCAFFOLD — designed, never run

Branches 02, 03, 05–17. Each has a README stating its question, its minimal
design and its stopping rule; some have analysis code. None has been run against
a model. **[`HANDOFF.md`](HANDOFF.md) is how to pick one up** — what the shared
machinery already does, the shape of a runner, and the mistakes already made
here.

Readiness, so nobody starts with a blocked one:

- **Runnable on the existing machinery** — 02, 10, 11, 12, 13, 15, 16, 17.
  All behavioural: choices, self-reports, executed work.
- **Needs the local model and internal access** — 03, 07, 08, 09.
- **Needs a design decision first** — 05 and 14 turn on what "the same instance"
  means across calls; 06 needs its identification argument checked.

Most relevant if the current line dies:

- **16 — self-prediction of behaviour** — nearest neighbour to branch 20.
- **13 — persona versus measurement** — whether a surface persona moves a
  measurement that is supposed to be about the model itself.
- **05 — persistence and individuation** — whether a state survives within one
  conversation lineage but not a recomputation.

Everything else is a genuine alternative if the preference line collapses, and
should be re-read rather than assumed.
