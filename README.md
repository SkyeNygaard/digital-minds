# AI systems underestimate how strongly recent work shapes their next choice

Can an AI system predict how recent work will change its own next choice?

We gave each system a choice between two small tasks. We measured which task it
preferred. Before any treatment work, we asked what it would choose after
completing either task three times. We then made it do the work and measured its
next binding choice.

Both systems predicted some repetition. Both predicted much less than occurred.

## Main result

| System | Stable task pairs | Predicted shift | Observed shift |
|---|---:|---:|---:|
| GPT-5.6 Luna in the Codex harness | 13 | +0.340 | +0.827 |
| Qwen3-4B, local greedy decoding | 7 | +0.141 | +1.000 |

In the primary run, all 13 forecasts underestimated the observed shift. The
forecasts still showed partial foresight: 11 had the correct positive direction,
and they beat a fixed no-shift forecast. But a fixed full-repeat forecast had
7.3 times lower squared error than the system's own forecasts.

Six of seven checks set before the primary run passed. The failed effect-size
check missed its cutoff narrowly. The result therefore supports a narrow claim
about underestimating the strength of repetition, not a claim that the system
failed to predict the direction.

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
```

The primary condition uses the subscription-authenticated Codex CLI:

```bash
cd parallel_frontier/20_preference_foresight
../../.venv/bin/python run_scaled.py \
  --provider codex \
  --model gpt-5.6-luna \
  --all-families \
  --n-pairs 19 \
  --workers 4 \
  --replicates 2 \
  --doses 3 \
  --out-dir results/ranking_v2
```

The Codex harness is the tested condition. It is not a bare model endpoint. The
result records the harness settings and isolates the run from user and project
instructions.

Local model runs use the standard Hugging Face cache. Set `HF_HOME` or
`DIGITAL_MINDS_HF_HOME` only when the weights are stored elsewhere.

## Repository map

- `parallel_frontier/20_preference_foresight/` is the submitted experiment.
- `shared_behavioral/` contains task generation, grading, screening, and model
  providers.
- `parallel_frontier/` preserves supporting and alternative experiments.
- `winner_protocol/` preserves a separate activation study. It is not part of
  the submission claim.
