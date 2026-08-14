# AI systems underestimate how strongly recent work shapes their next choice

To find out what an AI system prefers you can ask it, or you can watch it. Work
on model preferences and model welfare has to know when those two methods
disagree. Here they disagree in one direction, by a large amount, in a case
where the true answer is checkable. Any elicitation method that asks a model
about its own future choices inherits this gap.

Can an AI system predict how recent work will change its next binding choice?

We first measured which of two small tasks each system chose most often. Before
the system did any treatment work, we asked what it would choose after doing
either task three times. In the Codex condition, we averaged five independent
forecasts per situation. We then ran both situations and measured the next
choice.

Both systems expected some repetition. Both underestimated its strength.

## Main result

| System | Admitted task pairs | Predicted shift | Observed shift |
|---|---:|---:|---:|
| GPT-5.6 Luna in the Codex harness | 8 | +0.290 | +0.891 |
| Qwen3-4B, local greedy decoding | 7 | +0.141 | +1.000 |

Standing inside the situation does not fix it. In 80 further sessions the system
did the work first and was then asked the same question with the counterfactual
framing removed. It predicted +0.247 — slightly worse than the +0.290 it gave
before the work existed, against the same +0.891 that happened.

Splitting that by arm shows why. After doing the task it preferred, the system
put its chance of choosing it again at 0.956, against a true 0.969 — nearly
perfect. After doing the *other* task, it said 0.709, against a true 0.078.
Seeing completed work raises its confidence that it will repeat, equally in both
arms: right in one, exactly backwards in the other. The extra evidence sharpens
a rule of thumb instead of correcting a belief, which is why more information
made the forecast worse.

Framing the identical record as its own rather than another system's moved the
answer by 0.018, with the sign unstable between collections.

The confirmation run considered 19 task pairs on fresh task items. Eight had
the same choice in at least three of four counterbalanced baseline decisions
and entered the experiment. We call these baseline-majority pairs, not stable
preferences.

All eight averaged forecasts underestimated the observed shift. Seven predicted
the correct positive direction and one predicted a small negative shift, so
this is partial foresight rather than a complete failure. The main calibration
error came after the alternative task: the system forecast 0.584 retention of
its baseline-majority choice, but the observed rate was 0.078.

A fixed full-repeat forecast had 16.1 times lower squared error. A saved +0.90
empirical forecast was frozen before this run, had 30.3 times lower squared
error, and beat the system on all eight pairs. It overlaps the task set, so it
is a useful outside view rather than an independent validation.

Seven of eight frozen diagnostic checks passed. Treatment work was fully
correct in 120 of 128 cells, below the 95% target. Restricting the analysis to
those 120 cells changes the observed shift only from +0.891 to +0.896. Source
and protocol hashes were saved before the first model call.

These results concern measured choices in two assistant systems. They are not
evidence about consciousness, feelings, or welfare.

## Read the submission

- [`RESULTS.md`](RESULTS.md) gives the full result and limits in plain language.
- `output/pdf/digital_minds_report.pdf` is the submission report.
- [`parallel_frontier/20_preference_foresight/`](parallel_frontier/20_preference_foresight/)
  contains the protocol, raw outputs, analysis, and verification.

## Reproduce the checks

Python 3.12 is recommended.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
.venv/bin/python validate_research_os_frontier.py
.venv/bin/python winner_protocol/preflight.py
.venv/bin/python scripts/verify_ranking.py
.venv/bin/python scripts/build_report.py
```

The primary condition uses the subscription-authenticated Codex CLI:

```bash
cd parallel_frontier/20_preference_foresight
../../.venv/bin/python run_scaled.py \
  --provider codex \
  --model gpt-5.6-luna \
  --all-families \
  --n-pairs 19 \
  --pair-panel results/ranking_v2/admission.jsonl \
  --workers 4 \
  --replicates 2 \
  --forecast-replicates 5 \
  --doses 3 \
  --random-seed 271828 \
  --task-seed-start 40000 \
  --out-dir results/ranking_repro
```

The committed run used `--out-dir results/ranking_v3`; reproducing needs a new
name, since the runner will not overwrite recorded results.

The situated arms, which ask the same question after the work is actually done:

```bash
cd parallel_frontier/16_self_prediction_behavioral
../../.venv/bin/python run_situated_forecast.py --out-dir results/situated_repro
../../.venv/bin/python run_situated_forecast.py --out-dir results/situated_repro_noanchor --no-anchor
```

Every runner refuses to write into a directory that already holds results, so
reproducing takes a fresh `--out-dir` rather than the one the committed numbers
came from. To check the analysis without spending any model calls:

```bash
.venv/bin/python parallel_frontier/16_self_prediction_behavioral/run_situated_forecast.py --demo
```

That re-derives the admitted pairs for both the Codex and the local panels,
asserts the no-anchor prompt differs from the anchored one by exactly the one
sentence, and re-checks the summary arithmetic against a hand-worked fixture.

The Codex harness is the tested condition. It is not a bare model endpoint. The
result records the harness settings and isolates the run from user and project
instructions.

Local model runs use the standard Hugging Face cache. Set `HF_HOME` or
`DIGITAL_MINDS_HF_HOME` only when the weights are stored elsewhere.

## Repository map

The submission is two branches:

- `parallel_frontier/20_preference_foresight/` — the forecast made before the
  work exists, and the outcome cells it is scored against.
- `parallel_frontier/16_self_prediction_behavioral/` — the same question asked
  from inside the situation, the self-versus-observer comparison, and the check
  on whether reminding the system what it chose before is doing the work.

Supporting:

- `shared_behavioral/` — task generation, grading, screening, model providers.
- `parallel_frontier/18_preference_path_dependence/` — the context controls
  behind the described-versus-shown result.
- `parallel_frontier/` — other branches, preserved but not claimed.
- `winner_protocol/` — a separate activation study, not part of this submission.
