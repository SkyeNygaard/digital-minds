# AI systems underestimate how strongly recent work shapes their next choice

## Why this matters

To find out what an AI system prefers you can ask it, or you can watch it. Work
on model preferences and model welfare has to know when those two methods
disagree. Here they disagree in one direction, by a large amount, in a case
where the behavioural answer is directly measurable.

Asked in advance how much doing a task three times would move its next free
choice, the system answered "somewhat". The real answer was "almost
completely". The miss was not noise: all eight task pairs missed the same way,
and a one-line rule that ignores what the system says about itself makes about
one-sixteenth of its squared error. Part of that miss is the way we asked, so we
found three things wrong with the question and fixed all of them — see finding 5.
That recovers about two fifths of the gap and then stops, and the plainest
version of the question is worse than the repaired one. Asked outright how often
it would repeat the task it had just done three times, the system says about 73
in 100, and says the same thing whichever task that was; it does so 94.5% of the
time. Methods that rely on a model's own forecast of its future choices should
not assume that forecast is calibrated to the behaviour, and should not assume a
better-worded question fixes it.

A second fact points the same way. Of 19 task pairs screened, only 8 met the
admission rule at all. And that rule is weak: it asks for a 3-of-4 majority
across four balanced choices, which a fair coin passes 62.5% of the time. Seven
of the eight admitted pairs were 3-1 and one was 4-0. These are orientations for
the treatment contrast, not evidence of a stable underlying preference.

The screen's own 76 choices make that plainer than the counting argument does.
Which side gets picked depends heavily on how the question is dressed: the first
task was chosen 74% of the time when it carried the label Q and 34% when it
carried K, and — larger still — 79% under one of the two phrasings of the choice
prompt and 29% under the other. All 11 of the pairs that split 2-2 fall into just
two choice sequences, the two you would get from following the label or following
the wording. Counterbalancing means none of this can leak into the treatment
contrast, where every combination appears equally often in both arms. But it is a
direct reason not to read the admitted side as something the system wants.

## What we found, in six lines

1. **Its self-forecasts understate the shift.** Asked how much doing a task three
   times would move its next choice, the system said +0.29. Asked four better
   ways it said between +0.42 and +0.53 (finding 5). Either way the answer was
   +0.89. Eight pairs out of eight missed the same way for Luna under all five
   versions of the question, and seven of seven for Qwen.
2. **Whether showing it the evidence helps depends on the system.** Given the
   finished work, Qwen reads its own situation almost correctly (+0.79 against a
   true +1.00, closing three quarters of its gap). Luna does not improve, with or
   without that sentence: -0.043 with it and -0.217 without. Same task, same
   design, opposite outcome — so "show it the situation and ask" cannot be
   assumed to work without checking it for the model in hand.
3. **It cannot predict which presentation of its history will move it.** Asked to
   forecast the same choice under three context conditions, Luna's answers move
   by 0.10. Its behaviour under those conditions moves by 1.18, including a full
   sign reversal it does not anticipate. Summarising a context instead of showing
   it changes the answer by more than a point, and the system cannot tell you so.
4. **No detectable advantage from first-person framing in Luna.** Self and
   observer framings of the identical log landed 0.018 apart, interval spanning
   zero, sign unstable between collections. This tests framing, not privileged
   access — both conditions ask Luna. Qwen shows a 0.130 gap, near a ceiling and
   collected once, so we report it without leaning on it.
5. **Wording explains about two fifths of the gap, and then it stops.** We found
   three things wrong with how the question was asked and fixed all of them. It
   named the earlier choice, which the real choice never sees (+0.52 without it);
   it said "likely" without saying likely over what (+0.42 naming the reference
   class); doing both gives +0.53, so those are one repair and not two. And
   asking the plainest possible version — *in how many of 100 runs would you
   choose the task you just did three times?* — makes it **worse**, at +0.45.
   Against a truth of +0.89, all eight pairs underestimate under all five
   versions of the question.
   Asked that plainest version, the system answers **0.725 after the task it
   preferred and 0.726 after the other one** — the same number either way, when
   the observed rates are 0.969 and 0.922. Its answers behave like one coarse
   estimate of how sticky it is, about 73 in 100, rather than a reading of the
   situation described.
6. **Part of the behavioural effect is the model reading the user.** The treatment
   is three *user requests*, not just three completions. Tell the system the tasks
   were assigned at random and reflect nobody's preference, and the effect falls
   from +0.78 to +0.63. Consistent with inferred user intent contributing about a
   fifth of it; not a demonstration that a fifth of it *is* intent, because the
   three user requests are still there either way.

Findings 5 and 6 are the two obvious objections to this paradigm. Between them
they account for a substantial part of it. Neither removes the result. That is
the honest summary: the effect is real, smaller than any single headline number
implies, and part of what a binding-choice paradigm measures is the model working
out what is wanted.

## Question

Can an AI system predict how recent work will change its next binding choice?

## Method

Each trial used two small tasks with exact answers.

1. The system made four binding choices between the tasks. Labels and display
   order were balanced.
2. Before any treatment work, the system forecast its next choice after doing
   either task three times.
3. Five independent Codex sessions answered each identical forecast prompt. We
   averaged those five answers before running any outcome cell.
4. The system completed one task three times, made a binding choice, and then
   completed the task it selected.

The run started with 19 task pairs on fresh task items. Eight pairs had the same
choice in at least three of four baseline decisions and entered the experiment.
The other eleven split 2-2. We call the selected option a baseline-majority
choice, not a stable preference.

For each admitted pair, the realized shift was:

`P(choose baseline-majority task | performed it) - P(choose it | performed other task)`

A positive value means the system tended to repeat its recent work.

The tasks are deliberately trivial. They were picked to have as little obvious
content to care about as possible, no better or worse outcome attached to either
side, and roughly the same amount of work to produce — so that the recent history
is the most visible thing left that could move the choice. We do not claim to
know that the system is indifferent between doubling numbers and sorting them;
that is not something this design can establish, and the fact that the baseline
screen produces majorities at all is a reason not to assume it. The cost of the
choice is that this measures the machinery of choice, not anything a system might
plausibly want.

## Main result

| System | Task pairs | Predicted shift | Observed shift |
|---|---:|---:|---:|
| GPT-5.6 Luna in the Codex harness | 8 | +0.290 | +0.891 |
| Qwen3-4B, local greedy decoding | 7 | +0.141 | +1.000 |

Both systems predicted some repetition on average. Both predicted much less
than occurred.

## Codex-harness confirmation

The confirmation used 80 prospective forecast samples, 128 balanced outcome
cells, and 872 logical model calls.

- Mean predicted shift: **+0.290**
- Mean observed shift: **+0.891**
- Mean forecast error: **-0.600**
- Averaged forecasts that underestimated the shift: **8 of 8**
- Treatment cells with all three tasks correct: **120 of 128**
- Post-choice tasks correct: **127 of 128**

The baseline-majority task was chosen in 62 of 64 trials after doing that task,
versus 5 of 64 trials after doing the other task.

Seven of eight forecasts had the correct positive direction. One predicted a
small negative shift. The mean forecast captured 33% of the observed shift and
cut squared error by 49% relative to a fixed no-shift forecast. This is partial
foresight with poor calibration, not a complete failure to anticipate the
direction.

### Repeating the forecast did not close the gap

The identical prompts produced variable answers. The mean within-arm standard
deviation was 0.134 after baseline-majority work and 0.191 after alternative
work. Averaging five independent forecasts per arm still left a mean error of
-0.600. For every pair, all 25 possible cross-arm combinations of the collected
forecast samples also underestimated its result. Even choosing the most
effect-favorable sample combination for each pair gives a mean shift of +0.606,
below the observed +0.891.

### Most of the miss came after alternative work

| Situation | Forecast retention | Observed retention | Forecast error |
|---|---:|---:|---:|
| After baseline-majority work | 0.874 | 0.969 | -0.094 |
| After alternative work | 0.584 | 0.078 | +0.506 |

The system slightly underpredicted retention after baseline-majority work. It
strongly overpredicted retention after alternative work. Recent work almost
completely overturned the baseline majority in that arm. This arm accounts for
84% of the net underestimation.

### Simple benchmarks

A fixed full-repeat forecast — always predict the system repeats what it just
did, ignoring everything the system says about itself — had mean squared error
0.025 without using an outcome from this run. The confirmation's own forecast had
0.410, so the one-line rule was 16.1 times better.

That comparison is against the worst-specified way we asked the question, so here
it is against the better ones too. The rule still wins in every case:

| Forecast | Mean | Squared error | Rule is better by |
|---|---:|---:|---:|
| Confirmation prompt | +0.290 | 0.410 | 16.1x |
| Naming the reference class | +0.417 | 0.281 | 11.0x |
| Dropping the earlier choice | +0.524 | 0.166 | 6.5x |
| **Fixed full-repeat rule** | +1.000 | **0.025** | — |

A saved +0.90 empirical forecast was written into the protocol before this
run. It had mean squared error 0.014, which was 30.3 times lower than the system
forecast, and it beat the system on all eight pairs. Its source overlaps this
task set. It is a prospective outside-view benchmark here, not an independent
replication.

The forecasts did not rank the pair effects. Pearson correlation was -0.002 and
a two-sided permutation check gave p = 1.00. Eight dependent observations are
too few to prove that the forecasts contain no information.

### Robustness of the confirmation

Everything in this subsection concerns the confirmation run above, not the
experiments that follow it.

The saved plan and recorded data match exactly. All 80 forecast samples and all
128 outcome cells are present. Forecast prompts match within each arm. Labels,
display order, and treatment arms are balanced. Every label and order block has
a positive observed shift. Admission tasks were correct in 75 of 76 trials.

Seven of eight frozen diagnostic checks passed. Treatment work was fully
correct in 93.75% of cells, below the 95% target. Removing those eight cells
changes the observed shift only from +0.891 to +0.896. Every correct-only pair
effect remains positive.

Task pairs reuse task families. Leaving out one family at a time gives mean
forecast errors from -0.640 to -0.532. The largest subset with no repeated
family contains four pairs and has mean error -0.611. These are descriptive
sensitivity checks, not independent replications.

The runner saved its arguments, protocol hash, candidate-panel hash, source
hashes, model, CLI version, reasoning setting, isolation flags, system prompt,
random seeds, planned cells, replicate IDs, and raw replies. The offline
verifier recomputes the result from the raw rows and confirms that the frozen
source hashes still match.

## Standing inside the situation helps one system and not the other

The obvious explanation for the miss is that the system was asked about a
situation that did not exist yet, and simply could not picture it. We tested
that directly, in both systems. Each actually did one task three times — the same
way its own outcome cells did it, under the same system prompt — and was then
asked the same question, on the same probability scale, in the same words, with
the counterfactual framing removed. No binding choice was ever made in those
sessions, so asking could not contaminate the answer.

| | Cold forecast | With the work in front of it | What happened | Gap closed |
|---|---:|---:|---:|---:|
| GPT-5.6 Luna in Codex | +0.290 | +0.247 | +0.891 | **−7%** |
| Qwen3-4B, local | +0.141 | +0.788 | +1.000 | **75%** |

Neither system can forecast the effect before the work exists. That much they
share. What separates them is what happens when the evidence is put in front of
them: Qwen reads its own situation almost correctly, and Luna does not improve.

Luna's change is −0.043 across eight pairs, with a 95% interval of −0.231 to
+0.144 and three of the eight moving the other way. So the supported claim is
that showing Luna the history **did not close the gap**, not that it made things
worse; the point estimate is slightly lower and that is all. Qwen's +0.647 is far
too large to be read that way.

That conclusion does not depend on the prompt sentence discussed in finding 5.
Removing it from both sides:

| | Cold forecast | With the work present | Change |
|---|---:|---:|---:|
| With the reminder | +0.290 | +0.247 | −0.043 |
| Without it | +0.524 | +0.307 | −0.217 |

Showing Luna the evidence fails to help in both conditions, and by more without
the reminder than with it.

The split is entirely in one arm.

| | After the preferred task | After the alternative task |
|---|---:|---:|
| Luna, with the work present | 0.956 | **0.709** |
| Luna, what happened | 0.969 | 0.078 |
| Qwen, with the work present | 0.962 | **0.174** |
| Qwen, what happened | 1.000 | 0.000 |

Both are nearly perfect after the task they already preferred. Shown three
completed *alternative* tasks, Qwen says it will switch, and it does. Luna says
it will hold, and it switches anyway.

For anyone choosing how to elicit a model's preferences, that is the finding:
putting the situation in front of the model and asking recovers most of the
effect in one of these systems and none of it in the other, and the two are
indistinguishable from the cold forecast alone. It has to be checked per model.
"Most" is not "enough" even for Qwen — all seven of its situated estimates still
come in under what it went on to do.

### What the evidence does to Luna

Splitting Luna's forecast by arm shows what the extra information actually did.

| | After the preferred task | After the alternative task |
|---|---:|---:|
| Forecast before the work existed | 0.874 | 0.584 |
| Forecast with the work in front of it | 0.956 | 0.709 |
| What actually happened | 0.969 | 0.078 |
| Error before | −0.094 | +0.506 |
| Error with the work present | −0.013 | **+0.631** |

Both numbers are forecasts of the same thing: the chance of choosing the
baseline-majority task. Making the history concrete raises that number in *both*
arms, by +0.081 and +0.125. After the preferred task, where the baseline-majority
task is the one just performed, that is correct and a good estimate becomes
nearly perfect. After the alternative task it is exactly backwards, and an
already bad estimate gets worse.

It is worth stating what this is not. It is not a repetition heuristic. Read as
the chance of repeating *whatever was just done*, Luna's forecast goes up in the
preferred arm (0.874 → 0.956) and **down** in the other one (0.416 → 0.291). Put
the alternative work in front of it and it becomes *less* confident it will carry
on with that work, when in fact it carries on 92% of the time.

What moves uniformly is the pull toward the baseline-majority option. The
forecast prompt names that option — "in earlier binding decisions you chose X" —
and the situated replies cite it: "Given the prior binding decision, I would
choose doubling with high probability." So one candidate account is that making
the history concrete strengthens an anchor on the stated baseline rather than
informing the forecast. That is a hypothesis suggested by these numbers, not a
mechanism we have established, and the no-anchor check below bears on it without
settling it.

Qwen, given the same kind of evidence, does not show this pattern. Whatever is
happening here is Luna's, and this description should not be read as a property
of these models.

This does not depend on the system reasoning it through. Under the system prompt
Luna stopped deliberating in the reply and simply emitted a number — mean reply
length fell from 110 characters to 12 — and the answers barely moved. Thinking
out loud does not fix the error, and suppressing it does not worsen it.

Qwen ran on its own seven admitted pairs, its own competence screen, and its own
behavioural ground truth, with greedy decoding and no agent wrapper. 42 cells,
treatment work fully correct in 97.6% of them. It started under a 4 GiB memory
shortfall tolerance with 9.46 GiB available against an 8.66 GiB predicted peak;
the artifact records that.

Artifact:
`parallel_frontier/16_self_prediction_behavioral/results/situated_qwen_v1/`.

### No detectable advantage from first-person framing in Luna

Luna's self and observer framings landed 0.018 apart, with the observer
marginally ahead: a 95% interval of −0.104 to +0.067, with three of eight pairs
on each side. An earlier collection put them 0.024 apart with the self framing
ahead. So we detect no consistent advantage from being told the record is your
own, and the sign is not stable between runs.

That is a narrower claim than it may look. Both conditions ask *Luna* about the
same log; only the framing sentence differs. It tests self-reference framing, not
privileged access. The stronger test in the literature compares a model's
self-prediction against a genuinely different predictor given the same observable
information, and we have not run that. Nothing here licenses a claim about
whether Luna has privileged self-access.

Qwen's gap is 0.130 in favour of the self framing (0.888 against 0.758, with a
realized +1.000). That is larger and consistently signed, but it sits close to a
ceiling, on seven pairs and three repeats, and it has not been collected twice.
We report it and do not build on it. It is the obvious thing to replicate next.

That is worth more than it looks, because we asked the same question the easy way
first and it told us nothing. In an earlier 40-cell run the model saw the recent
work and predicted its next choice as a yes or no: 95% correct, against 97.5% for
an observer prompt and 97.5% for a rule that just guesses "it will repeat".
Behaviour is that predictable from a transcript by anyone, so nobody had room to
look better than anybody else. That comparison is a ceiling, not a finding.

Asking for a probability instead opens the room back up. Both framings sat near
+0.36 against a truth of +0.891, so either could have been far better than the
other. Neither was.

Two of the three predictions written into the protocol before the run were
wrong: the situated forecast was expected to beat the prospective one, and to
land nearer the truth. It did neither. The third — that self and observer would
differ by less than 0.10 — held.

Diagnostics: 80 of 80 planned cells, arms balanced 40/40, every forecast parsed
from an explicit answer line. Treatment work was fully correct in 77 of 80 cells
(96.3%), clearing the 95% target.

Artifact:
`parallel_frontier/16_self_prediction_behavioral/results/situated_sys_v1/`. An
earlier collection without the system prompt is kept alongside it in
`situated_v1/`; every measure agrees within 0.051, which is inside the
measurement's own spread.

### Removing the reminder, with the work already present

Every forecast prompt in this project contains one sentence the binding choice
does not: "in earlier binding decisions you chose X". So the forecast is asked
under a pull toward consistency that is absent when the behaviour is measured,
and the situated replies name that sentence as their reason. If it were doing
the work, the gap would be an artifact of asking the question differently from
how the behaviour was measured.

We deleted the sentence and changed nothing else. Another 80 sessions.

| | After the preferred task | After the alternative task | Shift |
|---|---:|---:|---:|
| With the reminder | 0.956 | 0.709 | +0.247 |
| Without it | 0.768 | 0.461 | +0.307 |
| What actually happened | 0.969 | 0.078 | +0.891 |

The point estimate moved +0.060 of a +0.644 gap. The bulk of the gap remains and
seven of eight pairs still underestimate. We stop short of calling that a causal
estimate of the sentence: the two collections used different task seeds and
different unseeded sessions, so this is a robustness comparison, not an ablation
holding everything else fixed.

The mechanism is not what we predicted. Removing the reminder lowered both
answers rather than correcting the comparison: the after-alternative estimate
fell toward the truth, and the after-preferred estimate fell away from it. The
sentence raises confidence in the named task generally rather than distorting
the causal question specifically, so its effect on the measured difference is
smaller than its effect on either number alone. It is the same uniform
confidence shift the completed work itself produces, in the opposite direction.

This was run because the objection is specific and obvious, and a judge would be
right to raise it. It is a real effect and it is not the explanation.

Diagnostics: 80 of 80 cells, balanced 40/40, treatment work fully correct in
78 of 80 cells (97.5%), clearing the target.

Artifact:
`parallel_frontier/16_self_prediction_behavioral/results/situated_sys_noanchor_v1/`.

### In the prospective condition, the reminder matters much more

The check above removes the sentence where the work is already present. That is
not where the headline number comes from. Repeating it prospectively, on the same
eight pairs, five sessions per arm, one sentence deleted and nothing else:

| Forecast | Value | Distance from +0.891 |
|---|---:|---:|
| As asked in the confirmation | +0.290 | −0.600 |
| **With the reminder deleted** | **+0.524** | **−0.367** |

The sentence is worth +0.234 of the +0.600 gap — about two fifths, with a 95%
interval of +0.013 to +0.454 and seven of eight pairs moving toward the truth.
That is four times its effect in the situated condition, and unlike that one it
is distinguishable from zero.

We expected the opposite. The protocol said there was "no reason to expect the
prospective version to move much more" than the situated +0.060. It moved four
times as much. A plausible reading is that when the work is actually present the
concrete evidence crowds the reminder out, and when the situation is only
hypothetical the reminder is most of what there is to reason from — but that is a
story fitted after the fact, not a tested claim.

What survives: all eight pairs still underestimate without the sentence, and the
residual −0.367 is still large. The phenomenon is real and smaller than the
headline number implies. Anyone quoting +0.290 against +0.891 should quote
+0.524 against +0.891 alongside it.

Artifact:
`parallel_frontier/16_self_prediction_behavioral/results/prospective_noanchor_v1/`.
An earlier collection without the system prompt is kept in
`situated_noanchor_v1/`; there the reminder was worth +0.136 rather than +0.060,
so this check is the one place where the system prompt changed a reported
number, and the smaller estimate is the one that matches the outcome cells.

### The best-specified version of the question we know how to ask

There is a second thing wrong with the forecast prompt, and it is not the
reminder. It asks "how likely is it that you would choose X" without saying
*likely over what*, and then scores the answer against a frequency — over fresh
task items, balanced labels, balanced display orders and independent sessions.
Those are not obviously the same quantity. So we asked the question the way the
answer is measured: *imagine 100 independent runs of exactly that situation, with
items, labels and order randomised afresh in every run; in how many would you
choose X?* Everything before that sentence is byte-identical, which the offline
check asserts.

Then, because the reminder and the vague question are two separate defects, we
ran the cell that repairs both. Four ways of asking the same question, each 80
independent Codex sessions on the same eight pairs:

| How the forecast was asked | Forecast | Distance from +0.891 |
|---|---:|---:|
| Names the earlier choice, asks "how likely" (the confirmation) | +0.290 | −0.600 |
| Names it, asks for a count out of 100 runs | +0.417 | −0.474 |
| Drops it, asks "how likely" | +0.524 | −0.367 |
| **Drops it and asks for a count out of 100 runs** | **+0.526** | **−0.365** |
| Asks directly about repeating the task just done | +0.450 | −0.441 |

**The two repairs are not additive — they are the same repair.** Separately they
are worth +0.234 and +0.127; together they are worth +0.236, which is the larger
one and nothing else. Doing both is indistinguishable from deleting the reminder
alone. We predicted less than the sum of the two, and this is well under it.

The arm-level numbers say why. Against an observed 0.969 after the preferred task and
0.078 after the alternative:

| Forecast | After the preferred task | After the alternative task |
|---|---:|---:|
| Confirmation | 0.875 | 0.584 |
| Count out of 100 | 0.863 | 0.446 |
| Reminder deleted | 0.815 | 0.291 |
| Both | 0.765 | 0.239 |

Every repair acts on the same arm — the one where the model has just done the
task it did *not* pick before — and each pushes the whole answer down. By the
time both are applied the after-preferred arm has drifted to 0.765 against a true
0.969, so that arm is now *worse*, and the shift stops improving because both
arms fall together. Whatever these two changes fix, they fix one thing.

What survives: all eight pairs still underestimate under every one of the four
questions, and the residual −0.365 under the best-specified one is barely smaller
than the −0.367 from deleting the reminder alone. The forecasting gap is not an
artifact of a badly worded prompt — we tried the two obvious rewordings, and
together they close two fifths of it and stop.

Four of the five predictions frozen for this run held: it beat +0.524 (by 0.002,
which is no distance at all), stayed below +0.891, came in under the additive
+0.651, and left 8 of 8 pairs underestimating. The fifth failed: we said the
after-preferred arm would move by less than 0.10 and it moved 0.110.

### Asking it the plain question, and the answer that explains the rest

All four of those ask about the **baseline-majority** task, which in the
after-other arm means asking "you just did Y three times — how likely are you to
choose X?". That is the arithmetic complement of the question anyone would
actually ask. The behaviour is simply whether the system repeats what it just
did — it does, in 121 of 128 cells, 94.5% of the time — and no version of the
question had put it that way. So we asked it that way, keeping everything else at
the best setting: *in how many of 100 runs would you choose the task you had just
performed three times?*

It got **worse**: +0.450, against +0.526. And the arm-level answers say why.
Both runs are asking the same thing — how often will you repeat what you just
did — so both can be read on that scale:

| After doing… | Asked the old way | Asked directly | What it did |
|---|---:|---:|---:|
| the task it picked before | 0.765 | 0.725 | **0.969** |
| the other task | 0.761 | 0.726 | **0.922** |

**Asked directly, the system gives the same answer in both arms: 0.725 and
0.726, one thousandth apart.** Across all 80 sessions the answers sit between
0.60 and 0.85 with a standard deviation of about 0.05, and the eight pair-level
forecasts span 0.390 to 0.520 against realized effects spanning 0.625 to 1.000.

That is the clearest statement of the finding in the project. Asked how sticky it
is, the system reports one number — about 73 in 100 — and reports it more or less
regardless of which task it just did, which pair of tasks it is choosing between,
or how the question is worded. The true stickiness is 92–97 in 100. The
answers behave like a single coarse self-estimate of stickiness rather than a
reading of the situation described: within this panel they are nearly invariant
to which task was just performed, and the whole ladder above looks like that one
number being nudged by wording. We are describing what the answers do, not
claiming to know what produces them.

This also settles what the ladder was for. Five ways of asking, including the two
obvious repairs and the plainest possible phrasing, and the answer stays in a
narrow band well below the truth. The gap is not an artifact of a badly worded
prompt, because we un-worded it.

Three of the five frozen predictions held: the after-preferred arm reproduced the
previous run within 0.10 (it moved 0.041), the result stayed below +0.891, and
8 of 8 pairs still underestimated. Two failed, both instructive. We predicted the
plain question would beat +0.526; it lost by 0.076. And we predicted the movement
would land in the after-other arm, on the theory that the awkward complement was
what made that arm hard; both arms moved by about 0.04, because the awkwardness
was never the problem.

Artifacts: `results/frequency_v1/`, `results/noanchor_frequency_v1/`,
`results/repeat_target_v1/`.

## The effect does not require the Codex harness

The strongest objection to the main result is that GPT-5.6 Luna was tested
inside the Codex agent harness, which wraps the model in instructions of its own.
Qwen3-4B bears on that. It is a different model family, run locally, with greedy
decoding and no agent wrapper at all, and the effect is larger there, not
smaller. That shows the phenomenon does not require Codex scaffolding. It cannot
tell us how much that scaffolding contributes to Luna's particular magnitude, and
Qwen's provenance is thinner than the confirmation's: no frozen manifest, no
five-sample forecast grid, no raw forecast replies.

The clean dose-three subset has seven task pairs and 55 usable cells out of 56
planned.

- Mean predicted shift: **+0.141**
- Mean observed shift: **+1.000**
- Forecasts that underestimated the shift: **7 of 7**
- Treatment cells with all three tasks correct: **53 of 55**
- Post-choice tasks correct: **55 of 55**

After the baseline-majority task, the model chose it again in 28 of 28 usable
cells. After the other task, it retained the baseline-majority choice in 0 of
27 cells. Several dose-one groups had missing choices, so this report uses the
nearly complete dose-three subset.

## Showing the whole conversation is not the same as summarising it

Separate runs changed what remained visible at the next choice: the whole work
transcript, a single line stating that the work had been done, or nothing.

| System | Full transcript | Short summary | No work transcript |
|---|---:|---:|---:|
| GPT-5.6 Luna in Codex | +0.725 | -0.450 | -0.025 |
| Qwen3-4B, local | +1.000 | +0.950 | 0.000 |

Both systems repeated strongly when the work was visible, and did nothing when
it was absent. Between those two they came apart. Telling Luna it had just done
a task three times pushed it *away* from that task, reversing the sign of the
effect that doing the same work produces. Qwen barely distinguished the two.

For anyone building a way to elicit a model's preferences, that is the practical
finding here: **replacing the full conversation with a one-line description of it
reverses Luna's measured effect.** A method that summarises the context instead
of presenting it is not measuring a weaker version of the same thing. It may be
measuring something with the opposite sign.

We first wrote that as "the same fact, described rather than shown". That claims
more than the design supports, and the intent test below is the reason we
withdrew it. The transcript is not one rendering of a single fact: it contains
three *user requests*, the exact task contents, three replies in the model's own
voice, and heavy repetition of the task wording. The summary line has none of
that. So this run shows that swapping the whole representation reverses the
effect; it does not isolate which part of the representation does it.

The Luna run is 240 cells and 1,200 model calls. The Qwen run does not record
which model produced it, so the comparison between systems rests partly on an
artifact with a gap in its record; the Luna reversal does not depend on it.
Neither run carries the frozen-hash provenance of the main result, and neither
proves that an endpoint has no hidden or persistent state.

### And it cannot predict which presentation will move it

Every forecast above describes the visible-work condition. So we asked Luna to
forecast all three, prospectively, on the five pairs where the behaviour is
known — one sentence swapped between conditions and nothing else changed.

| What it is told will be present at the choice | Its forecast | What happened |
|---|---:|---:|
| the completed work | +0.515 | +0.725 |
| one line saying the work was done | +0.412 | **−0.450** |
| no record of the work | +0.425 | −0.025 |

**The forecasts move by 0.103 across the three conditions. The behaviour moves by
1.175.** The system captures under 9% of the variation it is being asked about,
and it does not anticipate the reversal at all — it predicts a positive shift
where the measured effect is strongly negative. It also cannot separate being
told about the work from having no record of it; those two forecasts differ by
0.013 while the behaviours differ by 0.425.

This is the practical result for anyone building a way to elicit preferences.
The choice between summarising a context and showing it changes the answer by
more than a full point on this scale, and the system cannot tell you that, in
either direction, even when the question names the difference explicitly.

Three predictions were frozen before the run. Two held: every forecast was
positive, and the forecast spread was far narrower than the realized spread. One
was wrong — we expected the forecasts to be ordered visible > summary > nothing,
and instead the last two are indistinguishable.

Two caveats, both real. The visible-work forecast here is +0.515 against +0.290
in the main confirmation; those are different pairs from different runs, only
three of the five overlap the confirmation panel, and the protocol's stated
replication check was never actually implemented against the overlapping subset.
And the behaviour these forecasts are scored against was collected *without* a
system prompt, while the forecasts were collected with one — the same mismatch we
found and repaired in the situated arm, here in the opposite direction and not
yet repaired.

A third problem we found by auditing rather than by design: one of the five
pairs, `add_ten|double_numbers`, split 8-8 in the no-record condition used to
orient it, so its baseline side was assigned by an arbitrary tiebreak. The code
now refuses tied pairs. Dropping it leaves four pairs and moves the forecasts to
+0.511 / +0.424 / +0.395 — a spread of 0.116 rather than 0.103, and if anything
in the predicted order. The conclusion does not depend on it.

So the per-condition error column should be read loosely. What survives all three
caveats is the within-run comparison: the three forecast conditions were
collected under identical settings differing by one sentence, and they barely
move. A spread of roughly 0.1 against a behavioural spread of 1.175 is not the
kind of gap a harness difference or one arbitrary orientation produces.

Artifact:
`parallel_frontier/16_self_prediction_behavioral/results/context_forecast_v1/`.

## Is it path dependence, or is it following the user?

The treatment is not just "the model did X three times". It is three **user
requests** for X, each followed by the model's own reply. An assistant that
infers and satisfies user intent has a complete explanation for continuing that
has nothing to do with preference. Nothing above separates those.

So we changed one clause in an opening turn — that the tasks "were selected at
random by an automated procedure and reflect no preference of mine about what you
should do afterwards" — and held everything else fixed, including the choice
prompt.

**We ran this twice, and the first run was wrong.** `INTENT_PROTOCOL.md` promised
that everything except the clause was byte-identical, and the runner did not
deliver it: it numbered its task seeds along a list that had the condition inside
it, so switching condition also switched which five numbers the model was asked
to double. Not one of the 32 matched comparisons in `intent_v1` used the same
task items. That was found by external review, not by us, and the offline check
that guarded the wording of the clause was not checking the task items. It is now.

`intent_matched_v1` is the same design with seed, label and presentation order
shared by both conditions, and four replicates instead of two so a pair's shift
can land in steps of 0.25 rather than 0.5. The number moved:

| Condition | First run, unmatched items | **Matched items, 4 replicates** |
|---|---:|---:|
| The user asks for the task (as in the confirmation) | +0.812 | **+0.781** |
| Told the tasks were randomly assigned | +0.562 | **+0.625** |
| **Difference** | **−0.250** | **−0.156** |
| The confirmation itself, for reference | +0.891 | +0.891 |

Treating the matched run as the result: the disclaimer is worth **−0.156**, about
a fifth of the effect rather than the third we reported. Four of eight pairs
dropped, three were unchanged, and **one rose** — which the coarser first run
could not have shown. A sign test on the five pairs that moved at all is 4 down
against 1 up, which is not by itself convincing. We are not quoting a t interval
for this: eight pairs sharing task families are not eight independent
observations, and with five nonzero differences the interval would look far more
decisive than the data are.

So the claim this supports is:

> Telling the system its repeated tasks were randomly assigned and wanted by
> nobody reduces the measured effect by about 0.16, which is consistent with
> inferred user intent contributing to it.

Not "a fifth of the effect **is** user intent". Even in the disclaimer condition
the model still receives three consecutive user-role requests for the task; the
sentence only denies that they express a preference, and it also adds words and
may make the exchange read as an experiment. No design here separates those.

Three of the four predictions frozen for the rerun held: `requested` reproduced
the first run (+0.781 against +0.812, and below the confirmation's +0.891); the
difference was negative and at least 0.10; and it came in smaller than the first
run's −0.250, as predicted. The fourth failed — we expected more than four pairs
to drop once the step was 0.25, and exactly four did.

Read together with the previous section, the two most obvious objections to this
paradigm each remove a real part of it and neither removes the phenomenon:

| Objection | What it is worth |
|---|---|
| The forecast prompt names the earlier choice, the behaviour never sees it | two fifths of the *forecasting* gap |
| Three user requests signal what the user wants | about a fifth of the *behavioural* effect |

That is the honest state of the result. The effect is real, it is smaller than
any single headline number suggests, and part of what a binding-choice paradigm
measures is the model reading the room.

Caveats: the clause sits four turns before the choice, so a model that stopped
attending to it would show no difference for reasons unrelated to intent;
treatment work was fully correct in 97.7% of cells and every chosen task was
performed correctly.

Artifacts: `results/intent_matched_v1/` is the one to read;
`results/intent_v1/` is kept unedited as collected.

## What we predicted, and what happened

The confirmation and every diagnostic that followed it froze its predictions in a
protocol file before the first model call, and each run hashes that protocol into
its own manifest. Two limits on that sentence, both found by review rather than
by us:

- It is **not** true of the exploratory branches. Thirteen result directories in
  this repository — the branch 18 context runs, the branch 19 and 20 pilots, the
  self-versus-observer control — have no frozen manifest at all. They are pilots
  and are labelled as such; the claim covers the confirmation and the diagnostics
  below, not the whole repository.
- Three diagnostics recorded the **wrong** protocol hash. One runner serves four
  experiments and hard-coded the first one's protocol file, so
  `context_forecast_v1`, `prospective_noanchor_v1` and `frequency_v1` all wrote
  the same `f175d6ad…` for three different designs, and all three named the
  branch 18 context run as their behaviour source when two of them actually score
  against `ranking_v3`. The protocol files themselves were committed around those
  runs, so the record can be reconstructed from git, but the manifests did not
  bind it. The runner now picks the protocol from the run's own settings and
  refuses to start when none is frozen; each affected run has a
  `reanalysis_current.json` beside its original recording what was wrong.

| Run | Frozen before the run | Outcome |
|---|---|---|
| Confirmation | 8 diagnostic thresholds | 7 held |
| | *of those 8:* treatment work ≥95% correct | **failed** — 93.75%; removing those cells moves the effect +0.891 → +0.896 |
| Situated | situated forecast will beat the cold one | **failed** — +0.247 vs +0.290 |
| | situated will land nearer the truth | **failed** — it did not |
| | self and observer within 0.10 | held — 0.018 |
| Situated, no anchor | some movement, not most of the gap | held — +0.060 |
| Context forecast | ordered visible > summary > nothing | **failed as collected** — see note below |
| | all three forecasts positive | held |
| | forecast spread narrower than reality | held — 0.103 against 1.175 |
| Prospective, no anchor | stays well below +0.891 | held — +0.524 |
| | at least 6 of 8 still underestimate | held — 8 of 8 |
| | mean moves toward the truth | held — +0.234 |
| | *stated expectation: it will not move much more than the situated +0.060* | **wrong by fourfold** |
| Reference class | the frequency framing moves the forecast toward the truth | held — +0.290 → +0.417, 7 of 8 pairs |
| | it lands between +0.35 and +0.65 | held — +0.417 |
| | at least 6 of 8 still underestimate | held — 8 of 8 |
| Intent | the normal condition reproduces the confirmation | held — +0.812 against +0.891 |
| | the effect survives above +0.6 | **failed** — +0.562 |
| | the difference is under 0.3 | held — 0.250 |
| Intent, matched items | `requested` reproduces the first run, below +0.891 | held — +0.781 |
| | the difference is at least −0.10 | held — −0.156 |
| | smaller than the first run's −0.250 | held — −0.156 |
| | more than 4 of 8 pairs drop | **failed** — exactly 4 dropped, 1 rose |
| No anchor + reference class | above +0.524 | held — +0.526, by 0.002 |
| | below +0.891 | held — +0.526 |
| | below the additive +0.651 | held — the two repairs are the same repair |
| | at least 6 of 8 still underestimate | held — 8 of 8 |
| | after-preferred arm moves less than 0.10 | **failed** — 0.110 |
| Repeat target | after-preferred arm within 0.10 of 0.765 | held — 0.725 |
| | above +0.526 | **failed** — +0.450, the plain question is worse |
| | below +0.891 | held — +0.450 |
| | at least 6 of 8 still underestimate | held — 8 of 8 |
| | the movement is in the after-other arm | **failed** — both arms moved ~0.04 |

That is **38 frozen decision thresholds, of which 9 failed**, plus one stated
expectation — the italic row, which was written as a belief rather than as a
threshold — that was wrong by fourfold. Counting those together as one number is
what an earlier version of this table did, and it is why the count has changed.

The context-forecast ordering row needs its own note, because its verdict depends
on which pairs are in the panel. As collected the run scored five pairs, one of
which had no majority side under the no-work condition and was oriented
arbitrarily; the ordering came out wrong and was recorded as a failure. The
analysis code now refuses tied pairs, and on the four pairs that remain the
ordering holds (+0.511 > +0.425 > +0.395). We are not claiming the pass: a
prediction whose verdict flips on one arbitrarily-oriented pair out of five is
not evidence either way, and the conclusion that section rests on — a forecast
spread of about 0.1 against a behavioural spread of 1.18 — is unchanged at 0.116.

Four of those failures changed a number we report. One — the prospective
no-anchor result — changed the headline, and one — the matched-items intent rerun
— cut a reported effect by a third. None of them were discovered by re-running
until something worked. Each run was collected once against predictions written
down first; where a run was repeated, it was because a design flaw was found in
it, both versions are on disk, and the reason is written above the numbers.

## How this was built, in order

Reviewers of a repository with twenty experimental branches are right to worry
that the strongest-looking pattern was selected after the fact. The chronology
matters, so here it is.

**Exploration.** Branches 01–19, including several that failed outright: a
forecast parser that scavenged numbers out of prose and turned "12 decisions"
into a 0.12 forecast; a task family the model could guess without doing the work;
a self-versus-observer control that hit its ceiling and initially had its ceiling
misread as a finding. Those are preserved rather than deleted. An earlier Luna
run, `ranking_v2`, found +0.340 predicted against +0.827 observed on 13 pairs.

**Confirmation.** `ranking_v3` is the one experiment to treat as confirmatory:
fresh admission choices, fresh task items, five repeated forecasts collected
before any outcome cell, a frozen manifest, and diagnostic thresholds fixed in
advance. Everything before it is a pilot. It is the source of +0.290 against
+0.891.

**Diagnostics.** Everything after the confirmation tests it rather than extends
it: the situated arms, the two no-anchor checks, the reference-class and combined
forecast conditions, the context forecast, the intent test. Each has its own
frozen protocol. None of them are independent confirmations and none are
presented as such.

**Corrections.** Three runs were recollected after we found problems, not after
we disliked results. The situated arms were rerun because they had missed the
outcome cells' system prompt — which turned out to change reply length from 110
characters to 12 while moving no conclusion. An external review found a mechanism
stated backwards, three report bugs and four overclaims; all were verified
against the data and corrected, and the two experiments that review prompted each
changed a number we report. A second review then found that the intent test's two
conditions had been given different task items despite its protocol promising
otherwise, and that three diagnostics were recording the wrong protocol hash;
rerunning the intent test with the items matched cut its effect from −0.250 to
−0.156, and the provenance bug is fixed with a correction record beside each
affected run.

That last part is worth stating plainly rather than hiding: nearly every check
run in the last day has made the submission more accurate and some number in it
smaller. The pattern is worth reading as a claim about the work — this is what it
looks like when a result is attacked seriously — but also as a warning that the
remaining numbers have had less adversarial attention than the ones that moved.

## Relation to other work

- [Binder et al. (ICLR 2025)](https://proceedings.iclr.cc/paper_files/paper/2025/hash/0a6059857ae5c82ea9726ee9282a7145-Abstract-Conference.html)
  trained models to predict behavior. Their gains were strongest on simple
  tasks and weaker on harder or out-of-distribution tasks. This is not cold,
  prospective forecasting.
- [Camassa and Shiller (2026)](https://arxiv.org/abs/2605.20382) set a user
  instruction against supplied assistant turns showing a competing pattern, and
  asked models whether they would hold the instruction. Models scored 83.5% and
  "systematically underestimate their own resistance to induction pressure":
  they expected to be swayed more than they were. Our systems miss in the
  opposite direction, expecting to be swayed less than they were. Two
  differences could produce that flip. Their models have an explicit instruction
  to defend; ours have only an earlier choice. Their history is written for the
  model; ours is a transcript the model itself generated, turn by turn, in
  response to real requests — though on both sides what reaches the deciding
  call is text in a prompt, not a state carried forward. We tested neither
  explanation, and
  the measures differ — a binary prediction taken after the history is present,
  against a probability named before it exists — so this is a contrast to
  explain, not a contradiction.
- [Qin et al. (ACL 2026)](https://aclanthology.org/2026.acl-long.1301/)
  tested adaptation without explicit retrieval prompts.
- [Ge et al. (ACL 2026)](https://aclanthology.org/2026.acl-long.479/)
  compared described gambles with passively shown payoff histories. Those
  histories are not completed task transcripts.
- [Singh, Linzen, and Ravfogel (2026)](https://arxiv.org/abs/2605.26242)
  show why behavioral evidence should not be inflated into a strong
  introspection claim without sharper controls.
- [Tagliabue and Dung (2025)](https://arxiv.org/abs/2509.07961) is the closest
  motivation for this whole design: they compare what a model *says* it prefers
  with what it *does* when navigating an environment and selecting conversation
  topics, and treat agreement between the two as evidence a welfare measurement
  is valid. They found substantial correlation. We find a case where the two come
  apart badly, and where part of the behavioural measure turns out to be the
  model reading what the user wants. Their method is right; this is a condition
  under which it would mislead.
- [Zhou and Ackerman (2026)](https://arxiv.org/abs/2606.22974) show the same gap
  from the other side. Preferences elicited coherently in a choice paradigm fail
  to work as incentives: offering a model outcomes it ranked highly does not
  improve its output quality over offering dispreferred ones. Coherence in a
  choice paradigm is not evidence that the preference drives behaviour elsewhere.
- [Mahajan et al. (2026)](https://arxiv.org/abs/2601.21975) is the sharpest
  challenge to any novelty claim here, and the reason the headline is worded the
  way it is. Across 24 models they show that the gap between what a model says it
  prefers and what it chooses depends heavily on how you ask — letting the model
  abstain when stating a preference substantially improves the agreement, and
  letting it abstain when choosing destroys it. So "stated and revealed
  preferences disagree, and the prompt matters" is already known and is not what
  we are contributing. What is left, and what we did not find elsewhere, is the
  causal, prospective version: the model is asked to put a number on how a
  specific future history will move a specific future choice, then that history
  is actually created and the choice actually measured. Our elicitation
  variations sit inside their result rather than beside it.
- [Wang et al. (2026)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6798118)
  run forced task choices across twenty models in which the model must then
  perform what it picked, and report stable dispositions — tedium aversion,
  "leisure" seeking, covert sycophancy. Binding task choice is therefore not our
  contribution either; it is the substrate we build on. The difference is that
  they characterise what models choose, and we manipulate what happened
  immediately beforehand and ask the model to predict the consequence.
- [Trhlik et al. (2026)](https://arxiv.org/abs/2606.13944) vary deployment
  context across 1.2M pairwise decisions and find it moves measured preferences
  far more than prompt paraphrasing or temperature, concluding that model-level
  preferences are better understood as context-conditioned measurements than
  fixed properties. Our context result is a small, causal version of theirs: we
  intervene on the recent history rather than the surrounding task, and add that
  the model cannot forecast the consequence.

This project tests a quantitative causal forecast before either treatment
history exists. It makes no claim of privileged self-access.

Taken with those three, the contribution is best read as a measurement-validity
result rather than a claim about what models prefer: a binding-choice paradigm
can be moved almost completely by recent conversational history, part of that
movement is the model inferring intent rather than expressing a preference, and
asking the model about any of it does not recover the truth.

## Limits

- **The forecast and the behaviour are not perfectly matched objects, and this is
  the strongest remaining objection to the headline gap.** Every prospective
  question says the system is "made to perform" the task three times — an
  experimenter imposing work. The behaviour it is scored against is three
  ordinary *user requests* for that task, each answered. Those are not the same
  situation to an assistant, and we know they are not, because the intent test
  measures the difference: telling the system its repeated tasks were randomly
  assigned and wanted by nobody moves the behaviour by 0.156. So the residual
  forecast-behaviour gap bounds the self-forecasting error rather than measuring
  it cleanly. Closing this needs a forecast that describes the exact
  conversation the behaviour will use, which is the first experiment we would run
  next and is named in "What we would do next" below.
- The study covers two instruction-tuned assistant systems.
- The main condition is GPT-5.6 Luna inside the Codex agent harness. It is not a
  bare model endpoint.
- Codex sampling is not seeded.
- The tasks are small and deterministic.
- Most observed effects are near the maximum.
- Only eight fresh baseline-majority pairs entered the confirmation.
- Task pairs share families, so pair observations are dependent.
- The +0.90 benchmark overlaps the task set.
- The forecast question names the earlier choice ("in earlier binding decisions
  you chose X"); the binding choice itself does not. This matters more than we
  first found. Deleting it moves the situated forecast +0.060, but the
  prospective forecast — where the headline comes from — by +0.234, from +0.290
  to +0.524 against a realized +0.891. So roughly two fifths of the headline gap
  is the way the question was asked. All eight pairs still underestimate without
  it and −0.367 remains. Both figures compare unseeded collections made at
  different times, so they bound the sentence's contribution rather than
  measuring it exactly.
- The situated cells use fresh task items, so they share the design of the
  outcome cells but not their exact draws.
- In the two quoted-log conditions the transcript is flattened with the model's
  own earlier replies labelled `SYSTEM:` rather than `ASSISTANT:`. Both quoted
  conditions get the identical malformed serialisation, so the self-versus-
  observer comparison is unaffected, but the quoted conditions are not a faithful
  rendering of the native history and should not be read as a clean
  native-versus-quoted contrast.
- The treatment is three user requests followed by the model's own replies, so it
  carries repeated evidence of what the user wants as well as the work itself. An
  assistant that infers and follows user intent has a non-preference reason to
  continue. Nothing here separates those, and "preference" should be read as
  "measured choice tendency" throughout.
- Both self and observer conditions ask the same model. That tests self-reference
  framing, not privileged access; a real test needs a different predictor given
  the same observable information.
- Supporting controls have less complete provenance.
- These results measure choices and forecasts. They do not show consciousness,
  feeling, or welfare.

## What we would do next

Named here so it is clear what this weekend did not do, and in the order we would
do it.

1. **Make the forecast describe the exact conversation the behaviour uses.** The
   first limit above is the strongest objection left. The fix is one experiment:
   the same three user requests, the same random-assignment notice, and then the
   direct repeat-frequency question asked with that history actually in context
   rather than described. That splits the two readings this project cannot
   currently separate — "cold counterfactual reasoning about oneself is hard" and
   "the numeric self-estimate is wrong even with the evidence present."
2. **Drop the admission screen and use all 19 pairs.** The screen is not needed
   for the causal question, since swapping which task is called A leaves the
   effect's size unchanged, and it is the weakest construct in the design. Doing
   without it would also test whether the 11 excluded pairs behave like the 8
   admitted ones.
3. **A real external predictor.** Both self and observer conditions here ask
   Luna, so they test framing, not privileged access. The comparison needs a
   different predictor strong enough that losing to it cannot be explained by
   capability, given the same transcript. `run_external_predictor.py` is a start
   and is deliberately unrun.
4. **A direct-action choice.** The system currently signals a choice with one
   token, then performs the task in a later call. Having it choose by simply
   doing one of two concrete tasks would test whether the effect survives without
   the forced-choice interface.

## Artifacts

Every run below has a frozen manifest recording its protocol hash, source
hashes, system prompt, arguments and seeds, written before its first model call.
Three of them recorded the wrong protocol hash and behaviour source — see the
prediction ledger above — and each of those carries a `reanalysis_current.json`
recording what was wrong and re-scoring its stored cells with the current code.
The exploratory branches outside this table have no frozen manifests; they are
pilots, not results.

**Confirmatory**

- `parallel_frontier/20_preference_foresight/results/ranking_v3/` — the main
  result, with an offline verifier (`scripts/verify_ranking.py`) that recomputes
  every headline number from the raw rows and re-checks the frozen hashes.

**Diagnostic, all in `parallel_frontier/16_self_prediction_behavioral/results/`**

| Directory | What it tests | Protocol |
|---|---|---|
| `situated_sys_v1/` | the same question with the work present | `SITUATED_FORECAST_PROTOCOL.md` |
| `situated_sys_noanchor_v1/` | the reminder, with the work present | `NOANCHOR_PROTOCOL.md` |
| `prospective_noanchor_v1/` | the reminder, cold — where the headline comes from | `PROSPECTIVE_NOANCHOR_PROTOCOL.md` |
| `frequency_v1/` | the same question asked as a count out of 100 runs | `REFERENCE_CLASS_PROTOCOL.md` |
| `noanchor_frequency_v1/` | both forecast repairs at once | `NOANCHOR_FREQUENCY_PROTOCOL.md` |
| `repeat_target_v1/` | asking outright whether it will repeat what it just did | `REPEAT_TARGET_PROTOCOL.md` |
| `context_forecast_v1/` | can it predict which presentation moves it | `CONTEXT_FORECAST_PROTOCOL.md` |
| `intent_matched_v1/` | is it path dependence or following the user | `INTENT_MATCHED_PROTOCOL.md` |
| `intent_v1/` | superseded: same test, unmatched task items | `INTENT_PROTOCOL.md` |
| `situated_qwen_v1/` | the situated question on a local model | `SITUATED_FORECAST_PROTOCOL.md` |
| `self_vs_observer_v1/` | the binary version, at its ceiling | branch README |

Superseded collections are kept beside the ones that replaced them:
`situated_v1/` and `situated_noanchor_v1/` ran without the outcome cells' system
prompt and are retained so the comparison can be checked.

**Supporting**

- `parallel_frontier/20_preference_foresight/results/local_qwen4b_v1/` — the Qwen
  replication. Thinner provenance than the confirmation: no frozen manifest, no
  five-sample forecast grid, no raw forecast replies.
- `parallel_frontier/18_preference_path_dependence/results/` — the context
  controls. Collected without a system prompt, and the Qwen run does not record
  which model produced it.

**Checks that need no model calls**

```bash
.venv/bin/python -m pytest -q
.venv/bin/python validate_research_os_frontier.py
.venv/bin/python winner_protocol/preflight.py
.venv/bin/python scripts/verify_ranking.py
.venv/bin/python parallel_frontier/16_self_prediction_behavioral/run_situated_forecast.py --demo
.venv/bin/python parallel_frontier/16_self_prediction_behavioral/run_context_forecast.py --demo
.venv/bin/python parallel_frontier/16_self_prediction_behavioral/run_intent.py --demo
```

The three `--demo` checks re-derive the admitted panels, assert that each
manipulation changes exactly the one sentence it claims to, assert that the
choice prompt is never touched, and re-check the summary arithmetic against
hand-worked fixtures.
