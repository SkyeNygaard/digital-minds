# AI systems underestimate how strongly recent work shapes their next choice

## Question

Can an AI system predict how recent work will change its own next choice?

## Method

Each trial used two small, automatically graded tasks.

1. We measured which task the system preferred. Labels and display order were
   balanced.
2. Before any treatment work, we asked what it would choose after completing
   either task three times.
3. We made the system complete one of those tasks three times.
4. We gave it a binding choice and made it complete the selected task.

For each pair, the realized shift was:

`P(choose preferred | performed preferred) - P(choose preferred | performed other)`

A positive value means the system tended to repeat its recent work.

## Main result

| System | Task pairs | Predicted shift | Observed shift |
|---|---:|---:|---:|
| GPT-5.6 Luna in the Codex harness | 13 | +0.340 | +0.827 |
| Qwen3-4B, local greedy decoding | 7 | +0.141 | +1.000 |

Both systems predicted some repetition. Both predicted much less than occurred.

## Primary experiment

The Codex-harness condition used 13 stable task pairs, 208 balanced treatment
cells, and 1,218 model calls.

- Mean predicted shift: **+0.340**
- Mean observed shift: **+0.827**
- Mean forecast error: **-0.487**
- Forecasts that underestimated the shift: **13 of 13**
- Treatment cells with all three tasks correct: **198 of 208**
- Post-choice tasks correct: **206 of 208**

Removing the 10 cells with at least one incorrect treatment task changes the
mean observed shift only from +0.827 to +0.832.

This is partial foresight, not a complete failure. Eleven of 13 forecasts had
the correct positive direction; the other two predicted zero. The mean forecast
captured 41% of the mean observed shift. Its squared error was 57% lower than a
fixed no-shift forecast.

A fixed forecast of full repetition had mean squared error 0.041. The system's
own forecasts had mean squared error 0.300. The fixed forecast therefore had
7.3 times lower squared error without using any outcomes from this run.

The pair-ranking result is uncertain. Pearson correlation between forecast and
outcome was +0.34. A two-sided permutation check gave p = .26. Leaving out one
task family at a time gave correlations from +0.12 to +0.51. This is suggestive,
but it is not enough to claim that the forecasts reliably rank the task pairs.

## Checks and scope

The saved plan and recorded cells match exactly. All 208 planned cells are
present. Labels, display order, and treatment arms are balanced. Every label and
order block has a positive observed shift.

Six of seven checks set before the run passed. The failed check required a mean
forecast error of at most -0.50. The result was -0.487. We therefore make the
narrow claim that the system underestimated the shift. We do not claim that it
failed to anticipate the direction.

The model, CLI version, reasoning setting, isolation flags, system prompt,
random seed, planned cell order, cell seeds, replicate IDs, and raw replies are
saved with the result.

The run used an intermediate uncommitted runner revision, so its exact source
hash was not captured. After the run, deterministic planned-cell seeds and
analysis metadata were added from the saved artifacts and run log. Numeric
outcomes were not changed. The offline verifier checks the complete grid, seed
mapping, raw replies, and reported metrics.

## Local replication

Qwen3-4B ran locally with greedy decoding and no agent wrapper. The clean
dose-three subset contains seven task pairs and 55 usable cells out of 56
planned.

- Mean predicted shift: **+0.141**
- Mean observed shift: **+1.000**
- Forecasts that underestimated the shift: **7 of 7**
- Treatment cells with all three tasks correct: **53 of 55**
- Post-choice tasks correct: **55 of 55**

After the preferred task, the model chose it again in 28 of 28 usable cells.
After the other task, it retained the original preference in 0 of 27 cells.

Several dose-one groups had missing choices because the local model added
unrequested work after its answer. We report the nearly complete dose-three
subset instead of filling missing cells after seeing the result.

## Supporting retrospective control

In a separate 40-cell control, a model that could see the recent work predicted
its next choice correctly 95% of the time. An observer prompt and a fixed repeat
baseline each scored 97.5%. Once the record was visible, simple repetition was
enough to predict the choice. Forecasting the size of the effect before the work
was harder.

This control saved cell outcomes but not the full provider settings or raw
replies now recorded by the primary run. It is supporting evidence, not a second
fully reproducible primary result.

## Limits

- The study covers two instruction-tuned assistant systems.
- The primary condition is GPT-5.6 Luna inside the Codex agent harness. The
  harness adds instructions and flattens multi-turn context. It is not a bare
  model endpoint.
- Sampling in the Codex harness is not seeded.
- The tasks are small and deterministic.
- Most observed effects are near the maximum.
- Task pairs share families, so pair-level observations are dependent.
- The results measure choices and forecasts. They do not show consciousness,
  feeling, or welfare.

## Artifacts

- Primary result and offline verification:
  `parallel_frontier/20_preference_foresight/results/ranking_v2/`
- Local replication:
  `parallel_frontier/20_preference_foresight/results/local_qwen4b_v1/`
- Supporting retrospective control:
  `parallel_frontier/16_self_prediction_behavioral/results/self_vs_observer_v1/`
