# AI systems underestimate how strongly recent work shapes their next choice

**Digital Minds Research Sprint, 14–16 August 2026. Anchor track: 4, Preference
Elicitation Methods.** The project measures the same context-dependent choice
tendency two ways — by asking and by watching — and spends most of its effort on
why the two disagree. Five
wordings of the verbal question and two versions of the behavioural one are
compared against the same checkable outcome. It also bears on track 3,
Introspection & Self-Report Reliability, since the verbal side is the system
forecasting its own future choice, but the contribution is about the measuring
instruments rather than about what the system can introspect.

To find out what an AI system prefers you can ask it, or you can watch it. Work
on model preferences and model welfare has to know when those two methods
disagree. Here they disagree in one direction, by a large amount, in a case
where the behavioural answer is directly measurable. Methods that rely on a
model's own forecast of its future choices should not assume that forecast is
calibrated to the behaviour.

The shortest version: asked outright how often it would repeat a task it had just
performed three times, the system answers **0.725 after one task and 0.726 after
the other** — the same estimate whichever task it just did. It then repeats that
task 96.9% and 92.2% of the time. Five different wordings of the question, two of
them repairing defects we found in it, all land in a narrow band well under what
happens.

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

Whether standing inside the situation fixes it depends on the system. Each did
the work first and was then asked the same question with the counterfactual
framing removed.

| System | Cold forecast | With the work present | What happened | Gap closed |
|---|---:|---:|---:|---:|
| GPT-5.6 Luna in Codex | +0.290 | +0.247 | +0.891 | −7% |
| Qwen3-4B, local | +0.141 | +0.788 | +1.000 | 75% |

Neither gets the size of the effect right cold. Only one can read it off
the evidence.
The split is entirely in one arm: shown three completed *alternative* tasks,
Qwen says it will switch and does (0.174 against an observed 0.000), while Luna says
it will hold and switches anyway (0.709 against an observed 0.078). Both are nearly
perfect after the task they already preferred. Luna's change from its own cold
forecast is -0.043, well inside noise, so the claim is that showing it the
history did not close the gap, not that it made things worse.

So putting the situation in front of a model and asking recovers most of the
effect in one of these systems and none of it in the other, and the cold forecast
does not tell you which you have. "Most" is not "enough": all seven of Qwen's
situated estimates still come in under what it went on to do.

Framing the identical record as its own rather than another system's moved
Luna's answer by 0.018, interval spanning zero, sign unstable between
collections. Both conditions ask Luna, so this tests self-reference framing and
not privileged access. Qwen shows a 0.130 gap, near a ceiling and collected
once.

The confirmation run considered 19 task pairs on fresh task items. Eight had
the same choice in at least three of four counterbalanced baseline decisions
and entered the experiment. That rule is weak — a fair coin passes it 62.5% of
the time, and seven of the eight admitted pairs were 3-1 splits. These are
orientations for the treatment contrast, not stable preferences.

All eight averaged forecasts underestimated the observed shift. Seven predicted
the correct positive direction and one predicted a small negative shift, so
this is partial foresight rather than a complete failure.

Part of that miss is how we asked, so we found three things wrong with the
question and fixed all of them. Deleting the sentence that names the earlier
choice raises the cold forecast from +0.290 to +0.524; naming the reference class
gives +0.417; doing both gives +0.526, so those two are one repair, not two. And
asking the plainest version — in how many of 100 runs would you choose the task
you just did three times — is *worse*, at +0.450. All eight pairs underestimate
under all five versions.

Asked that plainest version the system answers **0.725 after the task it picked
before and 0.726 after the other one**, against observed rates of 0.969 and
0.922. Its answers behave like one coarse estimate of how sticky it is, near 73
in 100: within this panel they barely move with which task it just did, and they
sit well under the 94.5% of the time it actually repeats.

A fixed full-repeat forecast — always predict the system repeats what it just
did — had 16.1 times lower squared error than the confirmation prompt, and still
6.5 times lower than the best-calibrated forecast we collected. A saved +0.90
empirical forecast was frozen before this run, had 30.3 times lower squared
error, and beat the system on all eight pairs. It overlaps the task set, so it
is a useful outside view rather than an independent validation.

Seven of eight frozen diagnostic checks passed. Treatment work was fully
correct in 120 of 128 cells, below the 95% target. Restricting the analysis to
those 120 cells changes the observed shift only from +0.891 to +0.896. Source
and protocol hashes were saved before the first model call.

The other obvious objection is that the treatment is three *user requests*, not
just three completions, so an assistant working out what the user wants has a
reason to continue that has nothing to do with preference. Telling the system its
three tasks were assigned at random and reflect nobody's preference lowers the
behavioural effect from +0.781 to +0.625 — about a fifth of it. That is
consistent with inferred user intent contributing, and it is not a demonstration
that a fifth of the effect *is* intent: the three user requests are still there
in both conditions. The effect is real, smaller than any single headline number
suggests, and part of what a binding-choice paradigm measures is the model
reading what the user wants.

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
