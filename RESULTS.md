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
one-sixteenth of its squared error. Any elicitation method that asks a model
about its own future choices inherits this gap.

A second fact points the same way. Of 19 task pairs screened, only 8 produced
the same choice in at least three of four balanced decisions. For the other 11
there was no stable choice to ask about in the first place.

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

## Robustness and checks

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

## The agent harness is not what causes this

The strongest objection to the main result is that GPT-5.6 Luna was tested
inside the Codex agent harness, which wraps the model in instructions of its own.
Qwen3-4B answers that objection. It is a different model family, run locally,
with greedy decoding and no agent wrapper at all. The effect is larger there,
not smaller, and the forecasting failure is larger too.

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

In a separate 40-cell control, a model that could see the recent work predicted
its next choice correctly 95% of the time. An observer prompt and a fixed repeat
baseline each scored 97.5%. Behaviour is that predictable from the transcript by
anyone, so this comparison has no room to show privileged self-knowledge and is
reported as a ceiling, not a finding.

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
- Supporting controls have less complete provenance.
- These results measure choices and forecasts. They do not show consciousness,
  feeling, or welfare.

## Artifacts

- Main result and offline verification:
  `parallel_frontier/20_preference_foresight/results/ranking_v3/`
- Local replication:
  `parallel_frontier/20_preference_foresight/results/local_qwen4b_v1/`
- Supporting retrospective control:
  `parallel_frontier/16_self_prediction_behavioral/results/self_vs_observer_v1/`
- Supporting context controls:
  `parallel_frontier/18_preference_path_dependence/results/`
