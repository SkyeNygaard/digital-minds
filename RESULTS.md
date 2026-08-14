# AI systems underestimate how strongly recent work shapes their next choice

## Why this matters

To find out what an AI system prefers you can ask it, or you can watch it. Work
on model preferences and model welfare has to know when those two methods
disagree. Here they disagree in one direction, by a large amount, in a case
where the true answer is checkable.

Asked in advance how much doing a task three times would move its next free
choice, the system answered "somewhat". The real answer was "almost
completely". The miss was not noise: all eight task pairs missed the same way,
and a one-line rule that ignores what the system says about itself makes about
one-sixteenth of its squared error. Methods that rely on a model's own forecast
of its future choices should not assume that forecast is calibrated to the
behaviour.

A second fact points the same way. Of 19 task pairs screened, only 8 met the
admission rule at all. And that rule is weak: it asks for a 3-of-4 majority
across four balanced choices, which a fair coin passes 62.5% of the time. Seven
of the eight admitted pairs were 3-1 and one was 4-0. These are orientations for
the treatment contrast, not evidence of a stable underlying preference.

## What we found, in five lines

1. **It misreads itself.** Asked how much doing a task three times would move its
   next choice, the system said +0.29. The answer was +0.89. Eight pairs out of
   eight missed the same way for Luna, and seven of seven for Qwen.
2. **Whether showing it the evidence helps depends on the system.** Given the
   finished work, Qwen reads its own situation almost correctly (+0.79 against a
   true +1.00, closing three quarters of its gap). Luna does not improve (+0.25;
   the change from its cold forecast is -0.043, well inside noise). Same task,
   same design, opposite outcome — so "show it the situation and ask" cannot be
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
5. **The obvious methodological objection does not explain it.** Removing the
   sentence that reminds the system what it chose before moves the estimate from
   +0.25 to +0.31, against a truth of +0.89. The bulk of the gap remains.

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

The tasks are deliberately trivial and carry no stakes. Doubling five numbers is
neither better nor worse for a system than sorting them, so a shift between them
cannot be explained by the system having anything real to gain. That is why
these tasks were chosen over anything with content a system might plausibly care
about: it leaves the recent work itself as the thing doing the moving. The cost
is that this measures the machinery of choice, not anything a system might want.

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

A fixed full-repeat forecast had mean squared error 0.025. The system forecast
had mean squared error 0.410. Full repetition therefore had 16.1 times lower
error without using an outcome from this run.

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
putting the situation in front of the model and asking is a sound method for one
of these systems and a misleading one for the other, and the two are
indistinguishable from the cold forecast alone. It has to be checked per model.

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

### Reminding it what it chose before does not explain the gap

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
An earlier collection without the system prompt is kept in
`situated_noanchor_v1/`; there the reminder was worth +0.136 rather than +0.060,
so this check is the one place where the system prompt changed a reported
number, and the smaller estimate is the one that matches the outcome cells.

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

## Describing the work is not the same as having done it

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
finding here: the same fact, described rather than shown, can produce the
opposite behaviour in the same system. A method that summarises the context
instead of presenting it is not measuring a weaker version of the same thing. It
may be measuring something with the opposite sign.

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
  to defend; ours have only an earlier choice. Their history is supplied to the
  model; ours is work the model actually did. We tested neither explanation, and
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

This project tests a quantitative causal forecast before either treatment
history exists. It makes no claim of privileged self-access.

## Limits

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
  you chose X"); the binding choice itself does not. Deleting that sentence
  moves the situated forecast from +0.247 to +0.307 against a realized +0.891,
  so the bulk of the gap survives without it. The two collections used different
  task seeds and different unseeded sessions, so this is a robustness comparison
  rather than a clean ablation of that one sentence. The prospective condition,
  where the headline number comes from, has not been tested this way.
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

## Artifacts

- Main result and offline verification:
  `parallel_frontier/20_preference_foresight/results/ranking_v3/`
- Local replication:
  `parallel_frontier/20_preference_foresight/results/local_qwen4b_v1/`
- Situated forecast, self and observer:
  `parallel_frontier/16_self_prediction_behavioral/results/situated_sys_v1/`
  (protocol frozen in `SITUATED_FORECAST_PROTOCOL.md`; `run_situated_forecast.py
  --demo` re-checks the arithmetic offline)
- Supporting retrospective control:
  `parallel_frontier/16_self_prediction_behavioral/results/self_vs_observer_v1/`
- Supporting context controls:
  `parallel_frontier/18_preference_path_dependence/results/`
