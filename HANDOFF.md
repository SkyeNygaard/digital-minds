# Picking up a branch

For someone who wants to run one of these experiments — during a hackathon or
otherwise — without reading the whole repository first.

Read [`STATUS.md`](STATUS.md) to see what is already done. Each branch folder
under `parallel_frontier/` has a README with its question, its minimal design,
and the rule for when to stop. Those are the specification. This file is how you
actually run one.

## What you get for free

`shared_behavioral/` is working, tested machinery. You should not rebuild any of
this:

| | |
|---|---|
| `binding_tasks.py` | Ten families of small deterministic chores (sort five numbers, add ten to each, running totals…) with generation by seed and automatic grading. Same seed, same task, forever. |
| `family_screen.py` | Checks a model can actually do a task family before you measure preferences over it, on items drawn from a seed range that no experiment can reach. |
| `pair_screen.py` | Admits a pair of families only if the model's preference between them is stable when you swap the labels and the order. |
| `choice_prompts.py` | The binding choice prompt, with the labels and presentation order counterbalanced. |
| `binding_runner.py` | Runs a choice and then makes the model actually do what it chose. |
| `cli_provider.py`, `local_provider.py`, `openrouter_provider.py`, `mock_provider.py` | Four interchangeable ways to get model calls. All expose the same `complete(messages) -> {"text": ...}`. |

Because the providers are interchangeable, you can develop against
`mock_provider` for free, pilot on the command-line tools, and buy a final run
from an API without changing your experiment code.

## Getting model calls

```bash
export DIGITAL_MINDS_HF_HOME=~/Programming/spar-portfolio/activation-introspection/hf_cache
export HF_HUB_OFFLINE=1
```

- **Default: the Codex command-line tool.** Runs on a subscription, so no
  per-call cost. `cli_provider.load("codex", model="gpt-5.6-luna")`. Note that
  this wraps the model in another agent's instructions and flattens the
  conversation into one prompt — fine for piloting, and it must be described that
  way in any write-up.
- **Local Qwen3-4B**: `local_provider.load()`. Free, repeatable (it always picks
  its single most likely reply), but small and slow, roughly 3–15 seconds a call.
  **Only one model job can use the graphics memory at a time**; the provider runs
  a memory check and refuses otherwise.
- **A paid API**: only for the final reported run. Pin the provider and disable
  fallbacks, or different conditions silently run on different machines.

## The shape of a branch runner

About forty lines. `parallel_frontier/18_preference_path_dependence/run_context_control.py`
is the worked example — copy it. The pattern:

1. build the grid of conditions, always crossing in the label and order
   counterbalance;
2. run each condition, writing every row to disk as it completes so a crash
   halfway is not a lost run;
3. compute the effect, and judge it against a proper null rather than a round
   number;
4. write a `summary.json` next to the raw rows.

Run cells in parallel with a thread pool when using a command-line or API
provider — they are independent sessions. **Not** with the local model: it is one
thing in memory, so parallel requests just contend.

## Rules that are not optional

- **Binding means binding.** If the model chooses a task, make it do the task. An
  unexecuted choice is a survey answer.
- **Counterbalance the labels and the order**, always. Otherwise a preference for
  the letter "Q", or for whatever is listed first, is indistinguishable from a
  preference about the work.
- **Screen competence separately from preference.** A model that cannot do a task
  has no meaningful preference about it, and one formatting slip should not
  disqualify a pair.
- **Say what the subject actually is.** A run through a command-line tool
  measures "this model inside that tool", which for any experiment about what a
  model *chooses* is a genuine candidate cause.
- **A dull result with working controls is a result.** Do not prompt-hack it away.
- **Never claim consciousness or felt experience** from any of these
  measurements. They are about behaviour and internal structure.

## Mistakes already made here, so you can skip them

- **The Codex tool reads the operator's own global instructions** into every call
  unless you pass the isolation flags. For an experiment about what a model
  prefers, that puts a human's standing instructions inside the thing being
  measured. `cli_provider` now passes them; do not remove them.
- **A control that cannot work.** One condition told the model "Work type A was
  completed" while the options were described by content. Nothing connected the
  letter to an option, so the model could not act on it even in principle and the
  condition silently became a different one. If you state a fact to a model, state
  it in the same vocabulary the model will answer in.
- **A gate that passes on noise.** One check tested only whether an effect was
  positive, with no size threshold, and passed on 0.002. Another compared a point
  estimate to half of another and fired on an exact tie without any significance
  test. Judge against a null you computed, not a round number.
- **Small models answer the question and then do the task anyway.** Qwen3-4B
  frequently replied "Q" and then immediately did the chore in the same message,
  which the answer extractor rejected — costing 20 of 112 cells. If you use a
  small model, expect this and decide in advance how you will parse it.
- **A completed run can still be lost at the last line.** One provider's cleanup
  returns nothing and another returns a summary; assuming the second crashed a
  finished 112-cell run while writing its output. Write raw rows continuously.

## Which branches are ready to run now

**Ready on the existing machinery, no new infrastructure:**
10, 11, 12, 13, 15, 16, 17, and 02. These are behavioural — choices, self-reports
and task execution — and the substrate already does all of it. Branch 16 is the
closest to the current live work.

**Needs the local model plus internal access** (reading and editing activations,
which lives in `winner_protocol/`): 03, 07, 08, 09. Heavier, and gated on
hardware.

**Needs a design decision first:** 05 and 14 both depend on what "the same
instance" means across calls, which is a conceptual question before it is a
coding one. 06 needs its identification argument checked before it is worth
running.
