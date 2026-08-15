# Behavioral self-prediction of future consequential choice

Every run in this directory is a **diagnostic**. The confirmation is
`parallel_frontier/20_preference_foresight/results/ranking_v3`, which found a
+0.290 forecast against a +0.891 observed shift. Nothing here is an independent
confirmation of that, and none of it is presented as one. What these runs do is
attack it: each takes one objection to the confirmation and tries to make the
result go away.

Read `RESULTS.md` at the repository root for the findings. This file is the index
of what is in this directory and what each piece found.

## The original branch plan, and what happened to it

The plan was: fork a textual history, have the model predict its own next binding
choice, have a peer observer predict the same thing from the same public history,
and compare. **The peer-observer half was never run as designed.** What exists is
`self_vs_observer_v1`, which changes the *framing* of the log between "your own
record" and "another system's record" while asking Luna both times. That tests
self-reference framing, not privileged access, and it sits at a ceiling: a
trivial always-repeat rule scores as well as the model does.

The stated kill rule — "if self/peer information is effectively identical,
preserve that ceiling" — was applied. `run_external_predictor.py` is the start of
a real external-predictor run and is deliberately **not run**: it has no frozen
protocol and refuses to start, and its docstring says why a Qwen3-4B comparison
could only be read in one direction.

## Runners

| File | What it does |
|---|---|
| `run_situated_forecast.py` | Performs the work for real, then asks about the next choice. `--no-anchor`, `--frequency`, `--repeat-target`, `--unrelated-history`. |
| `run_context_forecast.py` | Cold forecasts, no work performed. Same four question options plus `--ranking-panel` and `--reanalyse`. |
| `run_intent.py` | Behavioural, not a forecast: does the effect survive telling the system its tasks were randomly assigned? |
| `run_self_vs_observer.py` | The binary self/observer framing check. |
| `run_external_predictor.py` | **Not run.** See above. |

Each runner picks its protocol from the run's own settings and **refuses to start
when no protocol is frozen for the combination**. That guard exists because three
early runs recorded the same protocol hash for three different designs; they now
each carry a `reanalysis_current.json` recording the error.

## Runs, in the order they were collected

| Result | Asked | Found |
|---|---|---|
| `situated_v1` | situated forecast, no system prompt | superseded — missed the outcome cells' system prompt |
| `situated_noanchor_v1` | as above, reminder deleted | superseded, same reason |
| `situated_sys_v1` | situated forecast, correct system prompt | +0.247 against +0.891. Being in the situation does not help Luna. |
| `situated_sys_noanchor_v1` | situated, reminder deleted | moves +0.060. The reminder is worth little once the work is present. |
| `situated_qwen_v1` | the situated question on Qwen3-4B | +0.788 against +1.000. Qwen recovers most of it; Luna does not. |
| `self_vs_observer_v1` | first-person vs third-person framing of one log | 0.018 apart, at a ceiling. Reported without being leaned on. |
| `context_forecast_v1` | can it forecast the three context presentations? | forecasts span 0.10; behaviour spans 1.18. Has a `reanalysis_current.json`. |
| `prospective_noanchor_v1` | cold forecast, reminder deleted | +0.290 → +0.524. Two fifths of the headline gap was the reminder. |
| `intent_v1` | does the effect survive "these were randomly assigned"? | superseded — the two conditions drew different task items |
| `frequency_v1` | cold, asked as a count out of 100 runs | +0.417 |
| `noanchor_frequency_v1` | cold, both repairs at once | +0.526. The two repairs are one repair. |
| `intent_matched_v1` | the intent test with task items matched | +0.781 → +0.625. The disclaimer is worth −0.156, not the −0.250 first reported. |
| `repeat_target_v1` | cold, asked plainly: will you repeat what you just did? | +0.450. Answers 0.725 and 0.726 — the same either way. |
| `situated_repeat_v1` | that plain question, with the work actually present | +0.141. Showing it the work makes the estimate **worse**. |
| `unrelated_history_v1` | control: three *unrelated* tasks, then the cold question | separates "seeing the evidence" from "having worked at all" |

## Discipline, as actually practised

- **Binding.** Chosen tasks are executed, not just named.
- **Counterbalanced.** Labels and presentation order are balanced within every
  arm, and in `intent_matched_v1` the task items are shared between conditions —
  which `intent_v1` promised and did not do.
- **Predictions frozen first.** Every protocol here states its predictions and
  how to read each outcome before collection. The scoreboard across the whole
  project is 43 thresholds, 11 failed; the failures are in `RESULTS.md` with the
  numbers they changed.
- **Collected once.** Where a run was repeated it was because a design flaw was
  found in it. Both versions stay on disk and the superseded one is labelled.
- **Pairs are dependent.** The eight pairs share task families, so a pair-level
  confidence interval over them is descriptive, not an independent-sample test.
- **No inference to consciousness or welfare** from choice behaviour.

## Offline checks

Every runner has a `--demo` that needs no model calls and asserts the parts that
can be silently wrong: panel reconstruction, that prompt variants differ by
exactly what they claim to, that the printed option order is identical across
arms, and that the scoring direction is right — including that a model answering
"100 out of 100" in both arms scores +1.0 under the repeat framing and 0.0 under
the older one.

```bash
for f in run_situated_forecast run_context_forecast run_intent; do
  ../../.venv/bin/python $f.py --demo
done
```
