# Digital Minds

Research on model welfare, revealed preference and introspective self-knowledge.
Separate from the SPAR portfolio: different goal, different deliverable, and — as
measured below — no shared code.

**[`STATUS.md`](STATUS.md) is the one page that says what has been run, what
is parked and why, and what would revive it.** Read that first.

Then [`START_HERE.md`](START_HERE.md), then
[`parallel_frontier/RESEARCH_OS_LEDGER.md`](parallel_frontier/RESEARCH_OS_LEDGER.md).

## Layout

| | |
|---|---|
| `parallel_frontier/` | 20 research branches, each with a README stating its terminal claim and kill rules. The ledger records what was promoted, downgraded and pruned, and why. |
| `shared_behavioral/` | The substrate branches 04/18/19/20 sit on: binding task families, competence screening, pair admission, and interchangeable `complete(messages)` providers for the Codex/Claude CLIs, a local MPS model, and OpenRouter. |
| `winner_protocol/` | The vGOLD activation work — structured reporting of an imposed welfare state. See its `DECISION_LEDGER.md` and `results/README.md`. |
| `m4_feasibility/` | `memory_guard`, the local-run memory/process check. |
| `PLAIN_SUMMARY.md` | The results so far, written for someone with no context. |

## Relationship to the SPAR portfolio

`~/Programming/spar-portfolio` is separate work. The projects were checked for
coupling before being split, and share **no code**: nothing imports across the
boundary in either direction, `winner_protocol/src/welfare_intervention.py`
deliberately re-implements rather than reuse the portfolio's `introspect.hooks`,
and this repo carries its own memory guard in `m4_feasibility/memory_guard.py`
rather than importing the portfolio's `introspect.preflight`.

What the two genuinely share is machine-level and not versionable:

- **the ~17 GB Hugging Face cache** holding `Qwen3-4B-Instruct-2507` and the
  `davidafrica/functional-wellbeing` vectors — set `DIGITAL_MINDS_HF_HOME`;
- **a Python environment** with torch, transformers and pandas;
- **one GPU.** Never run two MPS jobs at once on this machine; each repo has its
  own guard for that reason.

Submodules were considered and rejected: a submodule shares *code*, and there is
none to share. An environment variable is the whole of the coupling.

## Running

```bash
export DIGITAL_MINDS_HF_HOME=~/Programming/spar-portfolio/activation-introspection/hf_cache
export HF_HUB_OFFLINE=1
```

Behavioral branches default to the Codex CLI harness; the honest subject of such
a run is "the model inside the Codex agent environment", and the runners record
it that way. Activation work needs the local weights and the memory guard.
