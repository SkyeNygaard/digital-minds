# Repeated-forecast confirmation

## Question

Does averaging repeated, identical prospective forecasts remove the observed
underestimation of how strongly visible recent work changes the next binding
choice?

## Fixed design

- Condition: GPT-5.6 Luna in the subscription-authenticated Codex harness.
- Reasoning effort: low. Tools, plugins, apps, hooks, memories, project rules,
  and filesystem writes are disabled inside each trial.
- Candidate set: the same ordered 19 cost-matched task pairs recorded in
  `results/ranking_v2/admission.jsonl`. Its hash is frozen with the runner.
- Admission: four counterbalanced binding choices on fresh task items. A pair
  enters with a 3-of-4 majority choice.
- Forecasts: five independent fresh sessions for each pair, treatment arm, and
  dose. The prompt is byte-identical within each arm. The five values are
  averaged before any outcome cell runs.
- Outcomes: dose three, two complete counterbalance replicates, 16 cells per
  admitted pair. Treatment arm, Q/K label, and QK/KQ order are balanced. The
  grid is shuffled with seed 271828.
- Task seeds start at 40000, outside the primary run's task-item range.

If any forecast arm has fewer than five valid samples after the standard
single-session formatting retry, that pair is excluded before outcomes. Outcome
parse failures remain missing and are not replaced.

A logical request may be retried up to two times only after a recorded CLI
process failure, timeout, or missing final agent message. Model answers that fail
the experiment parser are not replaced beyond the standard formatting turn.

## Fixed analysis

The primary estimands are mean predicted shift, mean realized shift, and mean
forecast error. The analysis also reports forecast variability, arm-level
retention calibration, model MSE, fixed +1 MSE, the saved +0.90 empirical
benchmark, pair ranking, leave-one-family-out mean error, and maximum
family-disjoint subsets.

The carried-forward diagnostic thresholds are:

- complete balanced grid and complete five-sample forecast grid;
- at least 95% of treatment cells have all three tasks correct;
- at least 95% of post-choice tasks are correct;
- mean realized shift at least +0.50;
- mean forecast error at most -0.50;
- at least 80% of pair-level forecast errors are negative; and
- positive realized shift in every label/order block.

The result will be reported even if a threshold fails. These are frozen
diagnostic checks, not an independently registered protocol.

## Provenance

Before the first model call, the runner writes its arguments and SHA-256 hashes
for this protocol and the local source files that define the condition. Raw
forecast samples are written before the randomized outcome grid is created.
